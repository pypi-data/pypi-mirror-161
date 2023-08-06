from pandas import DataFrame

from preheat_open import test


class TestBuildingDevice(test.PreheatTest):
    def test_class(self, building, short_period):
        devices = building.devices

        building.load_device_data(*short_period)
        df0 = devices[0].data
        assert isinstance(df0, DataFrame)
        assert len(df0) > 1

        building.clear_device_data()
        assert devices[0].data.empty
