from datetime import timezone
from typing import Dict, List, Optional, Union

import pandas as pd

from .api import TIMEZONE
from .backwards_compatibility import load_parameter_old_naming
from .component import Component
from .data import load_box_data, load_model_data
from .helpers import (
    list_to_string,
    now,
    sanitise_datetime_input,
    time_resolution_aliases,
    timedelta,
    utc,
)
from .logging import Logging


def populate_units(unit_type, units_data):
    units = []
    # Loop over units; create and populate Unit instances
    for unit_i in units_data:
        units.append(Unit(unit_i))

    return units


class Unit(object):
    """Defines a unit in the PreHEAT sense"""

    def __init__(self, unit_type: str, unit_data: Dict, load_data_by: str = "id"):
        # Type
        self.unit_type: str = unit_type
        self.unit_subtype: Optional[str] = unit_data.pop("type", None)

        # Identifier of the unit
        self.id = unit_data.pop("id", None)
        # Name of the unit
        self.name: str = unit_data.pop("name", "{}_{}".format(self.unit_type, self.id))
        if not self.name:
            # If the name does not exist, create one out of the ID and the unit type
            self.name = "{}_{}".format(self.unit_type, self.id)

        # List of components in the unit (PreHEAT_API.Component)
        self.components: List[Component] = self.__populate_components(unit_data)

        # Time series cache
        self.data: pd.DataFrame = pd.DataFrame()

        # State cache
        self._state: pd.DataFrame = pd.DataFrame()

        # Choose how to load the data
        self.__loads_data_by = load_data_by

    def __repr__(self) -> str:
        return "{0}({1})".format(self.unit_type, self.name)

    def __populate_components(self, unit_data: Dict) -> List[Component]:
        components = []
        try:
            for key, value in unit_data.items():
                # Component properties: a dict w. key 'cid'
                if isinstance(value, dict) and "cid" in value:
                    # Let 'name' be PreHEAT name, and tag be BACNET/source name
                    value["tag"] = value["name"]
                    value["name"] = key
                    # Add PreHEAT name as description
                    components.append(Component(value))

        except TypeError:
            pass

        return components

    def load_data(
        self,
        start,
        end,
        resolution: str = "minute",
        components: Union[List, None] = None,
        **kwargs,
    ) -> None:
        start, end, resolution = load_parameter_old_naming(
            start, end, resolution, **kwargs
        )
        self._warn_if_data_is_loaded()
        if self.__loads_data_by == "id":
            self.data = load_model_data(
                self.get_all_component_ids(components=components),
                start,
                end,
                resolution,
            )
        elif self.__loads_data_by == "cid":
            self.data = load_box_data(
                self.get_all_component_cids(components=components),
                start,
                end,
                resolution,
            )
        else:
            raise ValueError("")
        self._ensure_continuity_of_data(resolution)

    def _ensure_continuity_of_data(self, resolution: str) -> None:
        if self.data.empty or (resolution == "raw"):
            return

        time_alias = time_resolution_aliases(resolution)

        if resolution in ["day", "week", "month", "year"]:
            # Reindexing to local time prior to frequency conversion
            self.data.index = self.data.index.tz_convert(TIMEZONE)
            self.data = self.data.asfreq(freq=time_alias)
            self.data.index = self.data.index.tz_convert(utc)
        else:
            self.data = self.data.asfreq(freq=time_alias)

    def _warn_if_data_is_loaded(self):
        if self.data.empty is False:
            Logging().warning(
                RuntimeWarning(
                    f"Data was already present in unit (id={self.id}, name={self.name}, type={self.unit_type})"
                )
            )

    def clear_data(self, **kwargs) -> None:
        self.data = self.data[0:0]

    def cquery(self, name: str):
        return [component for component in self.components if component.name == name][0]

    def _select_components(self, components: Union[List, None] = None) -> List:
        if components is None:
            return self.components
        else:
            if isinstance(components, str):
                components = [components]
            return [
                component
                for component in self.components
                if component.name in components
            ]

    def get_all_component_cids(
        self, prefix: bool = False, components: Union[List, None] = None
    ):
        prefix = "{}.".format(self.name) if prefix else ""
        comps = self._select_components(components=components)
        return {str(c.cid): prefix + c.name for c in comps}

    def get_all_component_ids(
        self, prefix: bool = False, components: Union[List, None] = None
    ) -> Dict:
        prefix = "{}.".format(self.name) if prefix else ""
        comps = self._select_components(components=components)
        return {str(c.id): prefix + c.name for c in comps}

    def get_all_component_details(
        self, prefix: bool = False, components: Union[List, None] = None
    ) -> List:
        prefix = "{}.".format(self.name) if prefix else ""
        comps = self._select_components(components=components)

        return [
            {
                "id": str(c.id),
                "cid": str(c.cid),
                "name": prefix + c.name,
                "stdUnitDevisor": c.std_unit_devisor,
                "stdUnit": c.std_unit,
            }
            for c in comps
        ]

    def get_component(self, name: str) -> Component:
        try:
            return [
                component for component in self.components if component.name == name
            ][0]
        except:
            raise Exception(
                "The component ({}) does not exist in the unit ({}).".format(
                    name, self.name
                )
            )

    def has_component(self, component_name: str) -> bool:
        for comp_i in self.components:
            if comp_i.name == component_name:
                return True
        return False

    def has_data(self, component=None, check_not_null: bool = True):
        if component is None:
            return len(self.data) > 0
        elif self.has_component(component) is False:
            return False
        elif self.data.empty is True:
            return False
        elif component in self.data.columns and self.data.shape[0] > 0:
            return self.data[component].notnull().any() if check_not_null else True
        else:
            return False

    # Methods to manage unit state
    def load_state(self, seconds_back: int = 300, t_now=None) -> None:
        t_now = now() if t_now is None else sanitise_datetime_input(t_now)
        # Check if recent enough to expect raw data
        if t_now > now() - timedelta(days=7):
            resolution = "raw"
        else:
            resolution = "minute"
        self._state = load_model_data(
            self.get_all_component_ids(),
            t_now - timedelta(seconds=seconds_back),
            t_now,
            resolution,
        )

    def clear_state(self, **kwargs) -> None:
        self._state = pd.DataFrame()

    def get_state(
        self,
        update: bool = False,
        estimate: str = "last",
        seconds_back: int = 300,
        t_now=None,
    ) -> pd.Series:
        if update is True:
            self.load_state(seconds_back=seconds_back, t_now=t_now)

        if (self._state is None) or (self._state.empty):
            state = pd.Series(index=self.get_all_component_ids().values(), dtype=float)
        elif estimate == "last":
            state = self._state.ffill().iloc[-1, :]
        elif estimate == "mean":
            state = self._state.mean()
        elif estimate == "median":
            state = self._state.median()
        else:
            raise Exception(f"Invalid value for estimate ({estimate})")

        return state

    def describe(
        self, display: bool = True, prefix: str = "", components: bool = True, **kwargs
    ) -> str:
        out = prefix + "[{}] {} [id={} / sub-type={}]".format(
            self.unit_type, self.name, self.id, self.unit_subtype
        )
        if components:
            out += ": " + list_to_string([c.name for c in self.components])
        if display:
            print(out)
        return out
