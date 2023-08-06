"""
Various helper functions
"""
from datetime import date, datetime, timedelta, timezone
from typing import Any, List, Optional, Union

import dateutil.parser
from dateutil.tz import tzutc

from preheat_open import TIMEZONE

utc = timezone.utc


def timestep_start(step: str, t: datetime) -> datetime:

    if step in ["second", "1s"]:
        t_start = t.replace(microsecond=0)
    elif step == "15s":
        sec_start = int(t.second / 15) * 15
        t_start = t.replace(microsecond=0, second=sec_start)
    elif step == "30s":
        sec_start = int(t.second / 30) * 30
        t_start = t.replace(microsecond=0, second=sec_start)
    elif step in ["minute", "1min"]:
        t_start = t.replace(microsecond=0, second=0)
    elif step == "5min":
        min_start = int(t.minute / 5) * 5
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "15min":
        min_start = int(t.minute / 15) * 15
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "30min":
        min_start = int(t.minute / 30) * 30
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "hour":
        t_start = t.replace(microsecond=0, second=0, minute=0)
    elif step == "day":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0)
    elif step == "month":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
    elif step == "year":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0, day=1, month=1)
    else:
        raise Exception("Unknown step: " + step)

    return t_start


def now(step=None, tz=TIMEZONE) -> datetime:
    t = datetime.now(tz=tz)
    if step is None:
        return t
    else:
        return timestep_start(step, t)


def __enforce_imports():
    date.today() + timedelta(days=2)


def datetime_convert(param: Union[datetime, str]) -> datetime:
    if isinstance(param, datetime):
        dt = param
    elif isinstance(param, str):
        dt = dateutil.parser.parse(param)
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=TIMEZONE)
    else:
        raise TypeError(f"No conversion from type: {type(param)}")

    return dt if dt.tzinfo is not None else dt.astimezone(TIMEZONE)


def sanitise_datetime_input(t: Union[datetime, str]) -> datetime:

    if isinstance(t, str):
        out = datetime_convert(t)
    else:
        out = t
    return out.astimezone(tzutc())


def time_resolution_aliases(resolution: str) -> Optional[str]:
    if resolution in ["minute", "5min"]:
        return "5T"
    elif resolution == "hour":
        return "H"
    elif resolution == "day":
        return "D"
    elif resolution == "week":
        return "W"
    elif resolution == "month":
        return "MS"
    elif resolution == "year":
        return "YS"
    else:
        return None


def convenience_result_list_shortener(result: List[Any]) -> Union[List[Any], Any, None]:
    n_results = len(result)
    if n_results > 1:
        return result
    elif n_results == 0:
        return None
    else:
        return result[0]


def list_to_string(list2use: List, separator: str = ",") -> str:
    """
    Helper function to turn list into string, e.g. comma separated (default).
    """

    if isinstance(list2use, list):
        res = separator.join(map(str, list2use))
    else:
        raise TypeError("Input list2use must be a list")
    return res
