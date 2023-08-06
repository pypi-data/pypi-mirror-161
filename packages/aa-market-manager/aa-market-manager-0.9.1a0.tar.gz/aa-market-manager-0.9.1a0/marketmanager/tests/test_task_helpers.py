from datetime import datetime
from unittest.mock import Mock

from eveuniverse.models import EveRegion, EveSolarSystem, EveType

from django.test import TestCase
from django.test.testcases import TestCase

from allianceauth.authentication.models import (
    EveAllianceInfo, EveCharacter, EveCorporationInfo, User,
)
from allianceauth.tests.auth_utils import AuthUtils
from esi.models import Scope, Token

from marketmanager.models import Order
from marketmanager.task_helpers import (
    get_corp_token, get_random_market_token, is_existing_order,
)
from marketmanager.tasks import (
    fetch_all_character_orders, fetch_all_corporation_orders,
    fetch_all_corporations_structures, fetch_characters_character_id_orders,
    fetch_corporations_corporation_id_orders,
    fetch_corporations_corporation_id_structures,
    fetch_markets_region_id_orders, fetch_markets_structures_structure_id,
    fetch_public_market_orders, fetch_public_structures,
    fetch_universe_structures_structure_id,
)
from marketmanager.tests.esi.utils import _generate_token, _store_as_Token

from .testdata.load_eveuniverse import load_eveuniverse


class TestTaskHelpers(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('User1')
        AuthUtils.add_main_character(cls.user, 'Character1', '1', corp_id='2', corp_name='test_corp', corp_ticker='TEST', alliance_id='3', alliance_name='TEST')
        cls.token_1 = _store_as_Token(
            _generate_token(
                character_id=1,
                character_name="Character1",
                scopes=['esi-markets.structure_markets.v1']
            ),
            cls.user
        )

    def test_get_corp_token(self):
        scopes = ["esi-markets.read_corporation_orders.v1"]
        req_roles = ["Accountant", "Trader"]
        corporation_id = 1
        token = get_corp_token(corporation_id, scopes, req_roles)

        self.assertFalse(token)

    def test_get_random_market_token(self):
        token = get_random_market_token()
        self.assertIsInstance(token, Token)

    def test_get_random_market_token_no_tokens(self):
        Token.objects.all().delete()
        token = get_random_market_token()
        self.assertIsInstance(token, bool)
        self.assertFalse(token)


class TestTaskHelpersOrders(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_eveuniverse()
        Order.objects.create(
            order_id = "1",
            eve_type = EveType.objects.get(id = 44992),
            volume_remain = 100,
            price = 3000000,
            duration = 90,
            location_id = 60003760,
            eve_region = EveRegion.objects.get(id = 10000002),
            eve_solar_system = EveSolarSystem.objects.get(id = 30000142),
            issued = datetime.now(),
        )
        Order.objects.create(
            order_id = "2",
            eve_type = EveType.objects.get(id = 44992),
            volume_remain = 100,
            price = 3000000,
            duration = 90,
            location_id = 60003760,
            eve_region = EveRegion.objects.get(id = 10000002),
            eve_solar_system = EveSolarSystem.objects.get(id = 30000142),
            issued = datetime.now(),
        )
    def test_is_existing_order_existing(self):
        current_orders = Order.objects.all()
        order = {}
        order["order_id"] = 1
        self.assertTrue(is_existing_order(order, current_orders))

    def test_is_existing_order_not(self):
        current_orders = Order.objects.all()
        order = {}
        order["order_id"] = 3
        self.assertFalse(is_existing_order(order, current_orders))
