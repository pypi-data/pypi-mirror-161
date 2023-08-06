"""
To manage devices
"""

from typing import Dict, List, Union

from preheat_open.building_unit import BaseBuildingUnit

from .logging import Logging


class Device(BaseBuildingUnit):
    """
    A device is a grouping of signals originating from a single physical data source (device),
    which is not linked to the building model
    """

    def __init__(self, unit_type: str, unit_data: Dict, building_ref):
        unit_data_reshaped = {
            "coversBuilding": True,
            "zoneIds": [],
            "shared": False,
            "id": unit_data["id"],
            "name": unit_data["name"],
        }
        for c in unit_data["components"]:
            unit_data_reshaped[c["name"]] = c

        super().__init__(
            unit_type, unit_data_reshaped, building_ref, load_data_by="cid"
        )
