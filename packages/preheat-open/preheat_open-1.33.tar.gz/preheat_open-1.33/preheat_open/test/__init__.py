import warnings
from copy import deepcopy

import pytest

import preheat_open
from preheat_open import running_in_test_mode

# Setting up a test API key, which is only valid for a dummy test installation
API_KEY = "KVkIdWLKac5XFLCs2loKb7GUitkTL4uJXoSyUFIZkVgWuCk8Uj"
ANONYMISED_API_KEY = "3xa0SeGXa4WlkrB68qGR9NoDAzVvGdiG3XAabKu6n7n5qQTDkL"
TEST_LOCATION_ID = 2756

# Warning the user that this module is not meant to be used for non test-related activities
if running_in_test_mode() is False:
    warnings.warn(
        """

The module 'preheat_open.test' is not meant to be imported and actively used, 
unless you are specifically carrying out a test.

    """
    )

SHORT_TEST_PERIOD = ("2021-05-01T00:00+02:00", "2021-05-02T00:00+02:00", "hour")


class PreheatTest:
    @pytest.fixture(autouse=True)
    def set_api_key(self):
        preheat_open.api.set_api_key(API_KEY)

    @pytest.fixture()
    def bypass_api_key(self):
        preheat_open.api.set_api_key(None)
        yield None
        preheat_open.api.set_api_key(API_KEY)

    @pytest.fixture(scope="session")
    def building_id(self):
        return TEST_LOCATION_ID

    @pytest.fixture(scope="session")
    def unit_id(self):
        return 15312

    @pytest.fixture(scope="session")
    def control_unit_id(self):
        return 15357

    @pytest.fixture(scope="session")
    def building(self, building_id):
        return preheat_open.Building(building_id)

    @pytest.fixture(scope="session")
    def building_with_data(self, building, medium_period):
        building_new = deepcopy(building)
        building_new.load_data(*medium_period)
        return building_new

    @pytest.fixture(scope="session")
    def unit(self, building, unit_id):
        return building.query_units(unit_id=unit_id)[0]

    @pytest.fixture(scope="session")
    def unit_with_data(self, unit, medium_period):
        unit_new = deepcopy(unit)
        unit_new.load_data(*medium_period)
        return unit_new

    @pytest.fixture(scope="session")
    def control_unit(self, building):
        return building.qu("control", "control_unit_custom_1")

    @pytest.fixture(scope="session")
    def weather_unit(self, building):
        return building.weather

    @pytest.fixture(scope="session")
    def short_period(self):
        start = SHORT_TEST_PERIOD[0]
        end = SHORT_TEST_PERIOD[1]
        resolution = "hour"
        return start, end, resolution

    @pytest.fixture(scope="session")
    def medium_period(self):
        start = "2021-05-01T00:00+02:00"
        end = "2021-05-07T00:00+02:00"
        resolution = "hour"
        return start, end, resolution
