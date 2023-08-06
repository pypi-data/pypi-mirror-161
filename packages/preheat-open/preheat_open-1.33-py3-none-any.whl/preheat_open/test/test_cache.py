import os
import uuid

from preheat_open.cache import delete_from_cache, load_from_cache, save_to_cache
from preheat_open.logging import Logging


def test_caching():

    try:
        os.chdir("/tmp")
    except Exception as e:
        Logging().warning(
            "Failed to change dir to /tmp (maybe you are on Windows) // Error: "
            + str(e)
        )

    a = "This is a test cache content"
    id = "test_cache"
    path_out = ".preheat_test_cache_" + str(uuid.uuid4())

    delete_from_cache(id, path=path_out)
    __, nok = load_from_cache(id)
    assert nok is False

    save_to_cache(a, id, path=path_out)
    a_cached, ok = load_from_cache(id, path=path_out)
    assert ok is True
    assert a_cached == a

    delete_from_cache(id, path=path_out)
    no_data, nok = load_from_cache(id, path=path_out)
    assert nok is False

    delete_from_cache(id, path=path_out)
    save_to_cache(a, id, path=path_out)
    a_cached, ok = load_from_cache(id, path=path_out)
    assert ok is True
    assert a_cached == a
    delete_from_cache(id, path=path_out)

    os.rmdir(path_out)
