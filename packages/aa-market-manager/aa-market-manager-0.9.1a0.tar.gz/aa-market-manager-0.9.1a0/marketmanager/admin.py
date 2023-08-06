from eveuniverse.models import EveRegion, EveType

from django.contrib import admin

from allianceauth.services.hooks import get_extension_logger
from esi.models import Token

from marketmanager.models import (
    Channel, ManagedWatchConfig, Order, PrivateConfig, PublicConfig,
    StatisticsConfig, Structure, WatchConfig, Webhook,
)

logger = get_extension_logger(__name__)


@admin.register(PublicConfig)
class PublicConfigAdmin(admin.ModelAdmin):
    filter_horizontal = ["fetch_regions"]
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # This should filter regions to valid market regions, ie. no shattered, AT or Jove
        if db_field.name == "fetch_regions":
            kwargs["queryset"] = EveRegion.objects.filter(id__lt="11000000")
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(StatisticsConfig)
class StatisticsConfigAdmin(admin.ModelAdmin):
    filter_horizontal = ["calculate_regions"]
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # This should filter regions to valid market regions, ie. no shattered, AT or Jove
        if db_field.name == "calculate_regions":
            kwargs["queryset"] = EveRegion.objects.filter(id__lt="11000000")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(PrivateConfig)
class PrivateConfigAdmin(admin.ModelAdmin):
    list_display = ('token', 'failed', 'failure_reason')
    filter_horizontal = ["valid_corporations", "valid_structures"]
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "token":
            required_scopes = ['esi-markets.structure_markets.v1']
            kwargs["queryset"] = Token.objects.all().require_scopes(
            required_scopes
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(WatchConfig)
class WatchConfigAdmin(admin.ModelAdmin):
    list_display = ('eve_type', 'buy_order', 'volume', 'price', )
    filter_horizontal = ["structure","structure_type", "webhooks", "debug_webhooks", "solar_system", "region", "channels", "debug_channels"]
    autocomplete_fields = ['eve_type']
    list_filter = ('config_type', 'buy_order', 'webhooks', 'debug_webhooks', 'managed_watch_config')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Only items that have market groups?
        if db_field.name == "eve_type":
            kwargs["queryset"] = EveType.objects.filter(eve_market_group__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # This should filter Citadels (1657) and NPC Stations (15) as viable Structure_Types for this selection
        # This should filter regions to valid market regions, ie. no shattered, AT or Jove
        if db_field.name == "structure_type":
            kwargs["queryset"] = EveType.objects.filter(eve_group__id__in=[15, 1657])
        if db_field.name == "region":
            kwargs["queryset"] = EveRegion.objects.filter(id__lt="11000000")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('eve_type', 'price', 'eve_solar_system', 'is_buy_order', 'issued_by_character', 'issued_by_corporation', 'updated_at')


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'solar_system', 'eve_type', 'owner_id', 'pull_market', 'updated_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # This should filter Citadels (1657) and NPC Stations (15) as viable Structure_Types for this selection
        if db_field.name == "eve_type":
            kwargs["queryset"] = EveType.objects.filter(eve_group__id__in=[15, 1657])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', )

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', )

@admin.register(ManagedWatchConfig)
class ManagedWatchConfigAdmin(admin.ModelAdmin):
    list_display = ('managed_app', 'managed_app_identifier', 'managed_app_reason' )
    filter_horizontal = ["managed_structure", "managed_structure_type", "managed_webhooks", "managed_debug_webhooks", "managed_solar_system", "managed_region", "managed_channels", "managed_debug_channels"]
    list_filter = ('managed_buy_order', 'managed_webhooks', 'managed_debug_webhooks')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Only items that have market groups?
        if db_field.name == "managed_eve_type":
            kwargs["queryset"] = EveType.objects.filter(eve_market_group__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # This should filter Citadels (1657) and NPC Stations (15) as viable Structure_Types for this selection
        # This should filter regions to valid market regions, ie. no shattered, AT or Jove
        if db_field.name == "managed_structure_type":
            kwargs["queryset"] = EveType.objects.filter(eve_group__id__in=[15, 1657])
        if db_field.name == "managed_region":
            kwargs["queryset"] = EveRegion.objects.filter(id__lt="11000000")
        return super().formfield_for_manytomany(db_field, request, **kwargs)
