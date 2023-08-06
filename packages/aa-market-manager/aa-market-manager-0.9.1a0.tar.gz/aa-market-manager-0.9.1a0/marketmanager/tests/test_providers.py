import json
from unittest import mock

from django.test import TestCase

from marketmanager.models import Order, Structure
from marketmanager.providers import (
    get_characters_character_id_orders, get_corporations_corporation_id_orders,
    get_corporations_corporation_id_structures,
    get_markets_region_id_orders_paged, get_markets_structures_structure_id,
    get_universe_structures, get_universe_structures_structure_id,
)
