import datetime

from celery import shared_task
from eveuniverse.models import EveRegion, EveSolarSystem, EveType

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger
from esi.models import Token

from marketmanager.app_settings import (
    MARKETMANAGER_CLEANUP_DAYS_ORDER, MARKETMANAGER_CLEANUP_DAYS_STRUCTURE,
    MARKETMANAGER_TASK_PRIORITY_BACKGROUND, MARKETMANAGER_TASK_PRIORITY_ORDERS,
    MARKETMANAGER_TASK_PRIORITY_STRUCTURES,
    MARKETMANAGER_TASK_PRIORITY_WATCH_CONFIGS,
    MARKETMANAGER_TYPESTATISTICS_MINIMUM_ORDER_COUNT,
    MARKETMANAGER_WEBHOOK_COLOUR_ERROR, MARKETMANAGER_WEBHOOK_COLOUR_SUCCESS,
    MARKETMANAGER_WEBHOOK_COLOUR_WARNING, discord_bot_active, fittings_active,
)
from marketmanager.models import (
    ManagedWatchConfig, Order, PublicConfig, StatisticsConfig, Structure,
    TypeStatistics, WatchConfig,
)
from marketmanager.providers import (
    get_characters_character_id_orders, get_corporations_corporation_id_orders,
    get_corporations_corporation_id_structures,
    get_markets_region_id_orders_paged, get_markets_structures_structure_id,
    get_universe_structures, get_universe_structures_structure_id,
)
from marketmanager.task_helpers import (
    create_embed_supply, fifth_percentile, get_corp_token,
    get_matching_privateconfig_token, get_random_market_token,
    is_existing_order, median, weighted_average,
)

if fittings_active():
    from marketmanager.fittings import update_managed_watch_config_fittings

if discord_bot_active():
    from aadiscordbot.tasks import send_message

from . import __version__

logger = get_extension_logger(__name__)


@shared_task
def fetch_public_market_orders():
    """Fetch&Save Public Market Orders for configured regions
    bulk calls fetch_markets_region_id_orders(region_id: int)"""
    logger.debug("fetch_public_market_orders(), Fetching configured regions")
    for region in PublicConfig.objects.get(id=1).fetch_regions.all():
        logger.debug(f"fetch_public_market_orders(), Queuing up celery task for region {region.id}")
        fetch_markets_region_id_orders.apply_async(args=[region.id, 'buy'], priority=MARKETMANAGER_TASK_PRIORITY_ORDERS)
        fetch_markets_region_id_orders.apply_async(args=[region.id, 'sell'], priority=MARKETMANAGER_TASK_PRIORITY_ORDERS)


@shared_task
def fetch_markets_region_id_orders(region_id: int, order_type: str = "all"):
    logger.debug(f"fetch_markets_region_id_orders({region_id})")
    order_eve_region = EveRegion.objects.get(id=region_id)
    if order_type == 'buy':
        current_orders = Order.objects.filter(
            eve_region=order_eve_region,
            is_buy_order = True,
        )
    elif order_type == 'sell':
        current_orders = Order.objects.filter(
            eve_region=order_eve_region,
            is_buy_order = False,
        )
    else:
        current_orders = Order.objects.filter(
        eve_region=order_eve_region,
        )

    current_page = 1
    total_pages = 1
    while current_page <= total_pages:
        new_orders = []
        updated_orders = []
        order_page, order_page_headers = get_markets_region_id_orders_paged(region_id, current_page, order_type)
        total_pages = int(order_page_headers.headers['X-Pages'])
        current_page += 1
        for order in order_page:
            existing_order = is_existing_order(order, current_orders)
            if existing_order is not False:
                if existing_order.price != order["price"] or existing_order.volume_remain != order["volume_remain"]:
                    existing_order.price = order["price"]
                    existing_order.volume_remain = order["volume_remain"]
                    updated_orders.append(existing_order)
                else:
                    # It is an existing order, but hasnt changed, so nothing
                    pass
            else:
                order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
                    id=order["type_id"],
                    enabled_sections=[EveType.Section.MARKET_GROUPS]
                )
                new_order = Order(order_id=order["order_id"])
                new_order.eve_type = order_eve_type
                new_order.duration = order["duration"]
                new_order.is_buy_order = order["is_buy_order"]
                new_order.issued = order["issued"]
                new_order.location_id = order["location_id"]
                new_order.min_volume = order["min_volume"]
                new_order.price = order["price"]
                new_order.range = order["range"]
                new_order.eve_solar_system_id=order["system_id"]
                new_order.eve_region = order_eve_region
                new_order.volume_remain = order["volume_remain"]
                new_orders.append(new_order)
        try:
            Order.objects.bulk_create(new_orders, batch_size=500)
            Order.objects.bulk_update(updated_orders, batch_size=500, fields=['price', 'volume_remain'])
        except Exception as e:
            logger.error(e)


@shared_task
def fetch_all_character_orders():
    """Fetch&Save every Characters Market Orders
    bulk calls fetch_characters_character_id_orders(character_id)"""
    logger.debug("fetch_all_character_orders()")
    character_ids = Token.objects.values_list('character_id').require_scopes(
        ["esi-markets.read_character_orders.v1"])
    unique_character_ids = list(dict.fromkeys(character_ids))
    for character_id in unique_character_ids:
        logger.debug(f"fetch_all_character_orders(), Queuing up celery task for character {character_id}")
        fetch_characters_character_id_orders.apply_async(args=[character_id[0]], priority=MARKETMANAGER_TASK_PRIORITY_ORDERS)



@shared_task
def fetch_characters_character_id_orders(character_id: int, order_type: str = "all"):
    """Fetch&Save a single Characters Market Orders
    bulk called by fetch_all_character_orders()

    Parameters
    ----------
    corporation_id: int
        Should match a valid Character ID"""
    logger.debug(f"fetch_characters_character_id_orders({character_id})")
    for order in get_characters_character_id_orders(character_id):

        order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=order["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )
        order_eve_region, order_eve_region_fetched = EveRegion.objects.get_or_create_esi(
            id=order["region_id"]
        )
        try:
            order_eve_character = EveCharacter.objects.get(
                character_id=character_id
            )
        except ObjectDoesNotExist:
            EveCharacter.objects.create_character(character_id)
            order_eve_character = EveCharacter.objects.get(
                character_id=character_id
            )

        try:
            Order.objects.update_or_create(
                order_id=order["order_id"],
                defaults={
                    'eve_type': order_eve_type,
                    'duration': order["duration"],
                    'is_buy_order': order.get("is_buy_order", False),
                    'is_corporation': order["is_corporation"],
                    'issued': order["issued"],
                    'issued_by_character': order_eve_character,
                    'location_id': order["location_id"],
                    'eve_region': order_eve_region,
                    'min_volume': order["min_volume"],
                    'price': order["price"],
                    'range': order["range"],
                    'volume_remain': order["volume_remain"],
                    }
                )
        except Exception as e:
            logger.error(e)
        logger.debug(f"fetch_characters_character_id_orders({character_id}): Saved Order {order_eve_type.name}")


@shared_task
def fetch_all_corporation_orders():
    """Fetch&Save every Corporations Market Orders
    bulk calls fetch_corporations_corporation_id_orders(corporation_id)"""
    logger.debug("fetch_all_corporation_orders()")
    for corporation in EveCorporationInfo.objects.all():
        logger.debug(f"fetch_all_corporation_orders(), Queuing up celery task for corporation {corporation.id}")
        fetch_corporations_corporation_id_orders.apply_async(args=[corporation.corporation_id], priority=MARKETMANAGER_TASK_PRIORITY_ORDERS)



@shared_task
def fetch_corporations_corporation_id_orders(corporation_id: int, order_type: str = "all"):
    """Fetch&Save a Corporations Market Orders
    Is Bulk-Called by fetch_all_corporation_orders()

    Parameters
    ----------
    corporation_id: int
        Should match a valid Corporation ID"""
    logger.debug(f"fetch_corporations_corporation_id_orders({corporation_id})")
    scopes = ["esi-markets.read_corporation_orders.v1"]
    req_roles = ["Accountant", "Trader"]

    token = get_corp_token(corporation_id, scopes, req_roles)
    if token is False:
        logger.error(f"No Token for Corporation {corporation_id}")
        return
    order_eve_corporation = EveCorporationInfo.objects.get(
        corporation_id=corporation_id
    )

    for order in get_corporations_corporation_id_orders(corporation_id, token):

        order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=order["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )
        order_eve_region, order_eve_region_fetched = EveRegion.objects.get_or_create_esi(
            id=order["region_id"]
        )
        try:
            order_eve_character = EveCharacter.objects.get(
                character_id=order["issued_by"]
            )
        except ObjectDoesNotExist:
            EveCharacter.objects.create_character(order["issued_by"])
            order_eve_character = EveCharacter.objects.get(
                character_id=order["issued_by"]
            )
        try:
            Order.objects.update_or_create(
                order_id=order["order_id"],
                defaults={
                    'eve_type': order_eve_type,
                    'duration': order["duration"],
                    'is_buy_order': order.get("is_buy_order", False),
                    'is_corporation': True,
                    'issued': order["issued"],
                    'issued_by_character': order_eve_character,
                    'issued_by_corporation': order_eve_corporation,
                    'wallet_division': order["wallet_division"],
                    'location_id': order["location_id"],
                    'eve_region': order_eve_region,
                    'min_volume': order["min_volume"],
                    'price': order["price"],
                    'range': order["range"],
                    'volume_remain': order["volume_remain"],
                    }
            )
        except Exception as e:
            logger.error(e)


@shared_task()
def fetch_public_structures():
    logger.debug("fetch_public_structures()")
    for structure_id in get_universe_structures(filter="market"):
        logger.debug(f"fetch_public_structures(), Queuing up celery task for structure {structure_id}")
        fetch_universe_structures_structure_id.apply_async(args=[structure_id], priority=MARKETMANAGER_TASK_PRIORITY_STRUCTURES)

@shared_task()
def update_private_structures():
    logger.debug("update_private_structures()")
    for structure in Structure.objects.all():
        fetch_universe_structures_structure_id(structure.structure_id, public = False)

@shared_task()
def fetch_universe_structures_structure_id(structure_id: int, public = True):
    logger.debug(f"fetch_universe_structures_structure_id({structure_id})")
    if public == True:
        token = get_random_market_token()
    else:
        token = get_matching_privateconfig_token(structure_id)

    if token is False:
        logger.error(f"No Public or Private token (Public={public}) for {structure_id}")
        return

    try:
        structure = get_universe_structures_structure_id(
            structure_id,
            token
        )
    except Exception as e:
        logger.error(e)
        return

    structure_eve_solar_system, structure_eve_solar_system_fetched = EveSolarSystem.objects.get_or_create_esi(
        id=structure["solar_system_id"]
    )
    structure_eve_type, structure_eve_type_fetched = EveType.objects.get_or_create_esi(
        id=structure["type_id"],
        enabled_sections=[EveType.Section.MARKET_GROUPS]
    )
    try:
        Structure.objects.update_or_create(
            structure_id=structure_id,
            defaults={
                'name': structure["name"],
                'owner_id': structure["owner_id"],
                'solar_system': structure_eve_solar_system,
                'eve_type': structure_eve_type
            }
        )
    except Exception as e:
        logger.error(e)

@shared_task()
def fetch_all_structure_orders():
    logger.debug("fetch_all_structure_orders()")
    for structure in Structure.objects.all():
        logger.debug(f"fetch_all_structure_orders(), Queuing up celery task for structure {structure.structure_id}")
        fetch_markets_structures_structure_id.apply_async(args=[structure.structure_id], priority=MARKETMANAGER_TASK_PRIORITY_STRUCTURES)


@shared_task()
def fetch_markets_structures_structure_id(structure_id: int):
    logger.debug(f"fetch_markets_structures_structure_id({structure_id})")

    token = get_matching_privateconfig_token(structure_id)

    if token is False:
        logger.error(f"No Token PrivateConfig for structure {structure_id}")
        return

    order_eve_region = Structure.objects.get(structure_id = structure_id).solar_system.eve_constellation.eve_region
    order_eve_solar_system = Structure.objects.get(structure_id = structure_id).solar_system

    for order in get_markets_structures_structure_id(structure_id, token):

        order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=order["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )

        try:
            Order.objects.update_or_create(
                order_id=order["order_id"],
                defaults={
                    'eve_type': order_eve_type,
                    'duration': order["duration"],
                    'is_buy_order': order["is_buy_order"],
                    'issued': order["issued"],
                    'location_id': order["location_id"],
                    'eve_solar_system': order_eve_solar_system,
                    'eve_region': order_eve_region,
                    'min_volume': order["min_volume"],
                    'price': order["price"],
                    'range': order["range"],
                    'volume_remain': order["volume_remain"],
                    }
            )
        except Exception as e:
            logger.error(e)

@shared_task()
def fetch_all_corporations_structures():
    logger.debug("fetch_all_corporations_structures()")
    for corporation in EveCorporationInfo.objects.all():
        logger.debug(f"fetch_all_corporations_structures(), Queuing up celery task for corporation {corporation.corporation_id}")
        fetch_corporations_corporation_id_structures.apply_async(args=[corporation.corporation_id], priority=MARKETMANAGER_TASK_PRIORITY_STRUCTURES)



@shared_task()
def fetch_corporations_corporation_id_structures(corporation_id: int):
    logger.debug(f"fetch_corporations_corporation_id_structures({corporation_id})")
    scopes = ["esi-corporations.read_structures.v1"]
    req_roles = ["Station_Manager"]

    token = get_corp_token(corporation_id, scopes, req_roles)
    if token is False:
        logger.error(f"No Token for Corporation {corporation_id}")
        return

    for structure in get_corporations_corporation_id_structures(corporation_id, token):
        for service in structure['services']:
            if service['name'] == "market":
                structure_eve_solar_system, structure_eve_solar_system_fetched = EveSolarSystem.objects.get_or_create_esi(
                    id=structure["solar_system_id"]
                )
                structure_eve_type, structure_eve_type_fetched = EveType.objects.get_or_create_esi(
                    id=structure["type_id"],
                    enabled_sections=[EveType.Section.MARKET_GROUPS]
                )
                try:
                    Structure.objects.update_or_create(
                        structure_id=structure["structure_id"],
                        defaults={
                            'name': structure["name"],
                            'owner_id': structure["corporation_id"],
                            'solar_system': structure_eve_solar_system,
                            'eve_type': structure_eve_type
                        }
                    )
                except Exception as e:
                    logger.error(e)

@shared_task()
def run_all_watch_configs():
    for config in WatchConfig.objects.all():
        if config.config_type == "Supply":
            run_watch_config_supply.apply_async(args=[config.id], priority=MARKETMANAGER_TASK_PRIORITY_WATCH_CONFIGS)
        elif config.config_type == "Bargain":
            pass
        elif config.config_type == "Scalp":
            pass

@shared_task()
def run_watch_config_supply(id: int):
    config = WatchConfig.objects.get(id=id)

    # Initial order selection
    matching_orders = Order.objects.filter(
        eve_type = config.eve_type,
        is_buy_order = config.buy_order)

    # Optional Location Filters
    if config.structure.count() > 0 or config.solar_system.count() > 0 or config.region.count() > 0:
        matching_orders_location = matching_orders.filter(
            Q(location_id__in=config.structure.all()) | Q(eve_solar_system__in=config.solar_system.all()) | Q(eve_region__in=config.region.all()))
    else:
        matching_orders_location = matching_orders

    if config.structure_type.count() > 0 :
        valid_structures = Structure.objects.filter(eve_type__in=config.structure_type.all())
        matching_orders_location = matching_orders_location.filter(location_id__in=valid_structures.all())

    # Comparators
    ## if price is not zero, filter out all orders that dont meet minimum
    if config.price != 0 and config.buy_order == True:
        matching_orders_location_price = matching_orders_location.filter(price__gte=config.price)
    elif config.price != 0 and config.buy_order == False:
        matching_orders_location_price = matching_orders_location.filter(price__lte=config.price)
    else:
        matching_orders_location_price = matching_orders_location

    matched_volume = matching_orders_location_price.aggregate(volume=Sum('volume_remain'))["volume"]
    if matching_orders_location_price.count() > 0:
        if matched_volume >= config.volume:
            embed = create_embed_supply(
                config=config,
                matched_volume=matched_volume,
                description = "The following Supply Check reported no Errors",
                buy_order=config.buy_order,
                colour = MARKETMANAGER_WEBHOOK_COLOUR_SUCCESS)
            webhooks = config.debug_webhooks.all()
            for webhook in webhooks:
                if webhook.enabled:
                    webhook.send_embed(embed)
            channels = config.debug_channels.all()
            for channel in channels:
                send_message(channel_id=channel.id, embed=embed)

        else:
            embed = create_embed_supply(
                config=config,
                matched_volume=matched_volume,
                description = "The following Supply Check failed to return enough Volume",
                buy_order=config.buy_order,
                colour = MARKETMANAGER_WEBHOOK_COLOUR_WARNING)
            webhooks = config.webhooks.all()
            for webhook in webhooks:
                if webhook.enabled:
                    webhook.send_embed(embed)
            channels = config.channels.all()
            for channel in channels:
                send_message(channel_id=channel.id, embed=embed)
    else:
        embed = create_embed_supply(
            config=config,
            matched_volume=0,
            description = "The following Supply Check returned zero volume, This item may be out of stock or Market Manager may be incorrectly configured",
            buy_order=config.buy_order,
            colour = MARKETMANAGER_WEBHOOK_COLOUR_ERROR)
        webhooks = config.webhooks.all()
        for webhook in webhooks:
            if webhook.enabled:
                webhook.send_embed(embed)
        channels = config.channels.all()
        for channel in channels:
            send_message(channel_id=channel.id, embed=embed)



@shared_task()
def garbage_collection():
    ## Orders
    # Generic Expiry Date Passed
    order_passed_expiry_date = datetime.datetime.now() - datetime.timedelta(days = 90)
    orders_expired_by_generic_date = Order.objects.filter(issued__lt=order_passed_expiry_date)
    orders_expired_by_generic_date.delete()
    # Calculated Expiry Date Passed
    # Cant do this, property
    # orders_expired_by_calculated_date = Order.objects.filter(expiry__lt=datetime.datetime.now())
    # orders_expired_by_calculated_date.delete()
    # State = Expired or Cancelled
    orders_expired_by_state = Order.objects.filter(Q(state="Expired") | Q(state="Cancelled"))
    orders_expired_by_state.delete()
    # Stale
    order_stale_cleanup_date = datetime.datetime.now() - datetime.timedelta(days = MARKETMANAGER_CLEANUP_DAYS_ORDER)
    orders_stale = Order.objects.filter(updated_at__lt=order_stale_cleanup_date)
    orders_stale.delete()
    ## Structures
    # Stale
    structure_stale_cleanup_date = datetime.datetime.now() - datetime.timedelta(days = MARKETMANAGER_CLEANUP_DAYS_STRUCTURE)
    structures_stale = Structure.objects.filter(updated_at__lt=structure_stale_cleanup_date)
    structures_stale.delete()

@shared_task()
def update_all_type_statistics():
    logger.debug(f"update_all_type_statistics()")
    for eve_type in EveType.objects.filter(eve_market_group__isnull=False):
        if Order.objects.filter(eve_type = eve_type).count() >= MARKETMANAGER_TYPESTATISTICS_MINIMUM_ORDER_COUNT:
            calculate_type_statistics.apply_async(args=[eve_type.id], priority=MARKETMANAGER_TASK_PRIORITY_BACKGROUND)
        else:
            TypeStatistics.objects.filter(eve_type = eve_type).delete()

@shared_task
def calculate_type_statistics(type_id: int):
    eve_type = EveType.objects.get(id = type_id)
    try:
        logger.debug(f"calculate_type_statistics EveType ({eve_type.name}) Region (NEW EDEN)")
        type_statistic = TypeStatistics.objects.update_or_create(
            eve_type = eve_type,
            eve_region = None,
            defaults = {
                'buy_fifth_percentile' : fifth_percentile(eve_type = eve_type, buy_order = True),
                'sell_fifth_percentile': fifth_percentile(eve_type = eve_type, buy_order = False),
                'buy_weighted_average': weighted_average(eve_type = eve_type, buy_order = True),
                'sell_weighted_average': weighted_average(eve_type = eve_type, buy_order = False),
                'buy_median': median(eve_type = eve_type, buy_order = True),
                'sell_median': median(eve_type = eve_type, buy_order = False),
            }
        )
    except Exception as e:
        logger.error(e)

    for eve_region in StatisticsConfig.get_solo().calculate_regions.all():
        logger.debug(f"calculate_type_statistics EveType ({eve_type.name}) Region ({eve_region.name})")
        if Order.objects.filter(eve_type = eve_type, eve_region = eve_region).exists():
            try:
                type_statistic = TypeStatistics.objects.update_or_create(
                    eve_type = eve_type,
                    eve_region = eve_region,
                    defaults = {
                        'buy_fifth_percentile' : fifth_percentile(eve_type = eve_type, eve_region = eve_region, buy_order = True),
                        'sell_fifth_percentile': fifth_percentile(eve_type = eve_type, eve_region = eve_region, buy_order = False),
                        'buy_weighted_average': weighted_average(eve_type = eve_type, eve_region = eve_region, buy_order = True),
                        'sell_weighted_average': weighted_average(eve_type = eve_type, eve_region = eve_region, buy_order = False),
                        'buy_median': median(eve_type = eve_type, eve_region = eve_region, buy_order = True),
                        'sell_median': median(eve_type = eve_type, eve_region = eve_region, buy_order = False),
                    }
                )
            except Exception as e:
                logger.error(e)
        else: # Incase we have old statistics, we'd want to wipe them for objects no longer on the market
            try:
                type_statistic = TypeStatistics.objects.get(eve_type = eve_type, eve_region = eve_region).delete()
            except TypeStatistics.DoesNotExist:
                pass
            except Exception as e:
                logger.error(e)

@shared_task()
def update_managed_watch_configs():
    logger.debug("update_managed_watch_configs()")
    for managed_watch_config in ManagedWatchConfig.objects.all():
        logger.debug(f"update_managed_watch_configs(), Queuing up celery task for managed_watch_config {managed_watch_config.managed_app_reason}")
        if managed_watch_config.managed_app == 'fittings' and fittings_active() == True:
            update_managed_watch_config_fittings(managed_watch_config)
