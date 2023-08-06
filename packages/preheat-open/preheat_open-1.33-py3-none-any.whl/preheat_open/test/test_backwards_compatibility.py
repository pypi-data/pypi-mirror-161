import pytest

from preheat_open.backwards_compatibility import load_parameter_old_naming


@pytest.mark.parametrize(
    "input_param,expected",
    [
        (
            {"start": "2022-01-01", "end": "2022-01-02", "resolution": "hour"},
            ("2022-01-01", "2022-01-02", "hour"),
        ),
        (
            {
                "start": "2022-01-01",
                "end": "2022-01-02",
                "resolution": "hour",
                "time_resolution": "minute",
            },
            ("2022-01-01", "2022-01-02", "minute"),
        ),
        (
            {
                "start": "2022-01-01",
                "end": "2022-01-02",
                "resolution": "hour",
                "start_date": "2022-01-03",
                "end_date": "2022-01-04",
            },
            ("2022-01-03", "2022-01-04", "hour"),
        ),
    ],
)
def test_load_parameter_old_naming(input_param, expected):
    if "start_date" in input_param.keys() or "time_resolution" in input_param.keys():
        with pytest.warns(DeprecationWarning):
            assert expected == load_parameter_old_naming(**input_param)
    else:
        assert expected == load_parameter_old_naming(**input_param)
