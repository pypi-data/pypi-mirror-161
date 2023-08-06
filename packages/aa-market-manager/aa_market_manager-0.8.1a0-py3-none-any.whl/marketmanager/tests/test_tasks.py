from unittest.mock import Mock

from eveuniverse.models import EveRegion, EveSolarSystem, EveType

from django.test import TestCase
from django.test.testcases import TestCase

from allianceauth.authentication.models import (
    EveAllianceInfo, EveCharacter, EveCorporationInfo, User,
)

from marketmanager.models import Order
from marketmanager.tasks import (
    fetch_all_character_orders, fetch_all_corporation_orders,
    fetch_all_corporations_structures, fetch_characters_character_id_orders,
    fetch_corporations_corporation_id_orders,
    fetch_corporations_corporation_id_structures,
    fetch_markets_region_id_orders, fetch_markets_structures_structure_id,
    fetch_public_market_orders, fetch_public_structures,
    fetch_universe_structures_structure_id,
)

from .testdata.load_eveuniverse import load_eveuniverse


def create_testdata():
    load_eveuniverse()
    EveCharacter.objects.all().delete()
    EveCharacter.objects.create(
        character_id=1,
        character_name='Character1',
        corporation_id=1,
        corporation_name='test corp',
        corporation_ticker='TEST'
        )
    EveCharacter.objects.create(
        character_id=2,
        character_name='Character2',
        corporation_id=1,
        corporation_name='test corp',
        corporation_ticker='TEST'
        )
    Order.objects.create(
        #expired order
        eve_type = EveType.objects.get(id = 44992)
        )

class TestMarketmanagerTasks(TestCase):
    def test_garbage_collection(self):
    # Orders
    # Generic Expiry Date Passed

    # Calculated Expiry Date Passed

    # State = Expired or Cancelled

    # Stale

    # Structures
    # Stale
        self.assertTrue(True)
