from eveuniverse.tools.testdata import ModelSpec, create_testdata

from django.test import TestCase

from . import test_data_filename


class CreateEveUniverseTestData(TestCase):
    def test_create_testdata(self):
        testdata_spec = [
            ModelSpec(
                "EveType",
                ids=[44992, 22436, 621],
            ),
            ModelSpec(
                "EveSolarSystem", ids=[30000142, 30002187, 30002510],
            ),
            ModelSpec("EveRegion", ids=[10000002,10000002, 10000003], include_children=True),
        ]
        create_testdata(testdata_spec, test_data_filename())
