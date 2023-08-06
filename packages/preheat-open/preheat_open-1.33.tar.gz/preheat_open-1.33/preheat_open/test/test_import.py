def test_import():
    import preheat_open
    from preheat_open import (
        api,
        backwards_compatibility,
        building,
        building_unit,
        cache,
        component,
        control_unit,
        data,
        device,
        helpers,
        logging,
        price,
        setpoints,
        singleton,
        unit,
        unit_graph,
        weather,
        zone,
    )

    # Test top-level module
    assert isinstance(preheat_open.__version__, str)
    assert isinstance(preheat_open.__name__, str)

    # Test sub-modules
    assert isinstance(api.__name__, str)
    assert isinstance(backwards_compatibility.__name__, str)
    assert isinstance(building.__name__, str)
    assert isinstance(building_unit.__name__, str)
    assert isinstance(cache.__name__, str)
    assert isinstance(component.__name__, str)
    assert isinstance(control_unit.__name__, str)
    assert isinstance(data.__name__, str)
    assert isinstance(device.__name__, str)
    assert isinstance(helpers.__name__, str)
    assert isinstance(logging.__name__, str)
    assert isinstance(price.__name__, str)
    assert isinstance(setpoints.__name__, str)
    assert isinstance(singleton.__name__, str)
    assert isinstance(unit.__name__, str)
    assert isinstance(unit_graph.__name__, str)
    assert isinstance(weather.__name__, str)
    assert isinstance(zone.__name__, str)
