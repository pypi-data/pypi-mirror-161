"""
Ensures backwards compatibility of the code

The contents of this module will be deprecated in future versions
"""

from preheat_open.logging import Logging


def load_parameter_old_naming(start, end, resolution, **kwargs):
    """
    Checks for old parameter namings as start_date, end_date and time_resolution and forwards them to their respective
    new namings, i.e. start, end and resolution. Use by passing both new parameters down and a kwargs. Old namings will
    be caught and values passed on while a warning about the deprication of the old namings is raised.

    :param start:
    :param end:
    :param resolution:
    :param kwargs:
    :return:
    """

    d = dict(start=start, end=end, resolution=resolution)
    for param, alt_name in {
        "start": "start_date",
        "end": "end_date",
        "resolution": "time_resolution",
    }.items():
        if alt_name in kwargs:
            d[param] = kwargs[alt_name]
            Logging().warning(
                DeprecationWarning(
                    f"Use of parameter '{alt_name}' is deprecated. Use '{param}' instead."
                )
            )
    return d["start"], d["end"], d["resolution"]
