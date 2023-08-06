from typing import Union

from eveuniverse.models import EveRegion, EveSolarSystem, EveType

from django.db.models import Sum

from allianceauth.services.hooks import get_extension_logger

from marketmanager.app_settings import fittings_active
from marketmanager.models import ManagedWatchConfig, WatchConfig

logger = get_extension_logger(__name__)

if fittings_active():
    from fittings.models import Fitting, FittingItem

    def update_managed_watch_config_fittings_fit(managed_watch_config: ManagedWatchConfig):
        try:
            existing_configs = WatchConfig.objects.filter(managed_watch_config = managed_watch_config)
            existing_configs.delete()
        except Exception as e:
            logger.error(e)

        try:
            fit = Fitting.objects.get(id=managed_watch_config.managed_app_identifier.split(".")[-1])
        except Exception as e:
            logger.error(e)

        #Ship Hull
        eve_type, eve_type_fetched = EveType.objects.get_or_create(id=fit.ship_type_type_id)
        watch_config = WatchConfig(
            config_type = "Supply",
            buy_order = False,
            eve_type = eve_type,
            volume = managed_watch_config.managed_quantity,
            jita_compare_percent = managed_watch_config.managed_jita_compare_percent,
            managed_watch_config = managed_watch_config
            )
        watch_config.save()
        watch_config.structure.set(managed_watch_config.managed_structure.all())
        watch_config.solar_system.set(managed_watch_config.managed_solar_system.all())
        watch_config.region.set(managed_watch_config.managed_region.all())
        watch_config.structure_type.set(managed_watch_config.managed_structure_type.all())
        watch_config.webhooks.set(managed_watch_config.managed_webhooks.all())
        watch_config.channels.set(managed_watch_config.managed_channels.all())
        watch_config.debug_webhooks.set(managed_watch_config.managed_debug_webhooks.all())
        watch_config.debug_channels.set(managed_watch_config.managed_debug_channels.all())
        watch_config.save

        #Ship Fittings
        for fit_item in FittingItem.objects.filter(fit = fit).values('type_id').annotate(quantity=Sum('quantity')):
            eve_type, eve_type_fetched = EveType.objects.get_or_create(id=fit_item['type_id'])
            watch_config = WatchConfig(
                config_type = "Supply",
                buy_order = False,
                eve_type = eve_type,
                volume = fit_item['quantity'] * managed_watch_config.managed_quantity,
                jita_compare_percent = managed_watch_config.managed_jita_compare_percent,
                managed_watch_config = managed_watch_config
                )
            watch_config.save()
            watch_config.structure.set(managed_watch_config.managed_structure.all())
            watch_config.solar_system.set(managed_watch_config.managed_solar_system.all())
            watch_config.region.set(managed_watch_config.managed_region.all())
            watch_config.structure_type.set(managed_watch_config.managed_structure_type.all())
            watch_config.webhooks.set(managed_watch_config.managed_webhooks.all())
            watch_config.channels.set(managed_watch_config.managed_channels.all())
            watch_config.debug_webhooks.set(managed_watch_config.managed_debug_webhooks.all())
            watch_config.debug_channels.set(managed_watch_config.managed_debug_channels.all())
            watch_config.save

    def update_managed_watch_config_fittings_doctrine():
        #lets allow doctrine selections too
        #each update_managed_watch_config_fittings_fit
        return True
