"""
This module defines the basics of the interaction with Neogrid's web API
"""
import json
import os
from datetime import datetime
from io import StringIO
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from dateutil.tz import gettz
from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry

import preheat_open

from .logging import Logging
from .singleton import Singleton

BASE_URL = "https://api.neogrid.dk/public/api/v1"
MAX_CIDS_PER_REQ = 3
MAX_POINTS_PER_REQ = 90000
MAX_IDS_AND_CIDS_PER_REQUEST = 100

GET_TIMEOUT_SECONDS = 60
PUT_TIMEOUT_SECONDS = 10

# Perhaps we can steal this from the OS?
TIMEZONE = gettz("Europe/Copenhagen")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

USER_LEVEL_CONFIGURATION_FILE = os.path.expanduser("~/.preheat/config.json")
MACHINE_LEVEL_CONFIGURATION_FILE = os.path.expanduser("/etc/preheat/config.json")
MACHINE_LEVEL_CONFIGURATION_FILE_OPT = os.path.expanduser(
    "/etc/opt/preheat/config.json"
)


def configuration_file_path() -> str:
    """

    :return:
    :rtype:
    """
    if os.path.exists(USER_LEVEL_CONFIGURATION_FILE):
        out = USER_LEVEL_CONFIGURATION_FILE
    elif os.path.exists(MACHINE_LEVEL_CONFIGURATION_FILE_OPT):
        out = MACHINE_LEVEL_CONFIGURATION_FILE_OPT
    elif os.path.exists(MACHINE_LEVEL_CONFIGURATION_FILE):
        out = MACHINE_LEVEL_CONFIGURATION_FILE
    else:
        raise MissingConfigurationFile()
    return out


class APIKeyMissingError(Exception):
    pass


class AccessDeniedError(Exception):
    pass


class APIDataExtractError(Exception):
    pass


class MissingConfigurationFile(Exception):
    pass


def api_string_to_datetime(t: str) -> datetime:
    """

    :param t:
    :type t:
    :return:
    :rtype:
    """
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")


def datetime_to_api_string(t: datetime) -> str:
    """

    :param t:
    :type t:
    :return:
    :rtype:
    """
    return t.isoformat()


def ids_list_to_string(list2use: List, separator: str = ",") -> str:
    """Helper function to turn list into string, e.g. comma separated (default).

    :param list2use:
    :type list2use:
    :param separator:
    :type separator:
    :return:
    :rtype:

    """

    if isinstance(list2use, list):
        res = separator.join(map(str, list2use))
    elif isinstance(list2use, pd.Series):
        res = separator.join(map(str, list2use.to_list()))
    elif isinstance(list2use, np.ndarray):
        res = separator.join(map(str, list2use.tolist()))
    else:
        res = str(list2use)

    return res


def load_configuration() -> Dict:
    """

    :return:
    :rtype:
    """
    config = None
    try:
        # Prefer config file in user home dir, else use the global config file
        config_file = configuration_file_path()
        if os.path.exists(config_file):
            Logging().info(f"Loading config from {config_file}")
            with open(config_file, "r") as fp:
                config = json.load(fp)
    except:
        config = None

    return config


class ApiSession(metaclass=Singleton):
    """Singleton class to handle API connection sessions"""

    def __init__(self):

        # Adding protection against remote closing connection
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "PUT", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http_session = Session()
        http_session.mount("https://", adapter)
        http_session.mount("http://", adapter)

        self.base_url = BASE_URL
        self.session = http_session
        Logging().debug(f"Creating API session [{self.addr()}]...")

        self.set_api_key()

    def addr(self):
        """

        :return:
        :rtype:
        """
        return hex(id(self.session))

    def get_api_key(self) -> str:
        """

        :return:
        :rtype:
        """

        return self.session.headers.get("Authorization")

    def set_api_key(self, api_key: Optional[str] = None) -> None:
        """

        :param api_key:
        :type api_key:
        :return:
        :rtype:
        """
        if api_key is None:
            api_key = self._load_api_key(
                self.get_api_key().split(" ")[1]
                if self.get_api_key() is not None
                else None
            )
        else:
            Logging().debug(f"API key set manually [{self.addr()}]")
        headers = {"Authorization": "Apikey " + str(api_key)}
        self.session.headers.update(headers)

    def set_api_url(self, api_url=None):
        """
        DEPRECATED (only kept for backwards-compatibility)
        """
        Logging().warning(
            DeprecationWarning(f"Manual update of the API url is deprecated")
        )

    def api_get(
        self, endpoint, out="json", payload=None, headers=None, bare_url: bool = False
    ):
        """

        :param endpoint:
        :type endpoint:
        :param out:
        :type out:
        :param payload:
        :type payload:
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = payload if payload is not None else {}
        headers = headers if headers is not None else {}
        Logging().debug(f"GET /{endpoint} [{self.addr()}]")

        if bare_url:
            path = endpoint
        else:
            path = self.base_url + "/" + endpoint

        if out == "csv":
            headers["Accept"] = "text/csv"
        resp = self.session.get(
            path, params=payload, headers=headers, timeout=GET_TIMEOUT_SECONDS
        )

        Logging().debug(f"{resp.status_code} {resp.reason}")
        try:
            resp.raise_for_status()
        except Exception as e:
            msg = """GET - FAILED
            URL: {}
            Payload: {}
            """.format(
                path, str(payload)
            )
            Logging().error(msg, exception=e)
            raise e

        try:
            if out == "json":
                return resp.json()
            elif out == "csv":
                # Logging().debug(f"{resp.text}")
                data = StringIO(resp.text)
                return pd.read_csv(data, delimiter=";")
        except Exception as e:
            raise APIDataExtractError() from e

    def api_put(self, endpoint, json_payload=None, bare_url: bool = False) -> Response:
        """

        :param endpoint:
        :type endpoint:
        :param json_payload:
        :type json_payload:
        :return:
        :rtype:
        """
        json_payload = json_payload if json_payload is not None else {}

        Logging().info(f"PUT /{endpoint} [{self.addr()}]")

        if bare_url:
            path = endpoint
        else:
            path = self.base_url + "/" + endpoint
        r = self.session.put(path, json=json_payload, timeout=PUT_TIMEOUT_SECONDS)
        try:
            r.raise_for_status()
        except Exception as e:
            msg = """PUT - FAILED
            URL: {}
            Payload: {}
            """.format(
                path, str(json_payload)
            )
            Logging().error(msg, exception=e)
            raise e
        return r

    def api_post(self, endpoint, json_payload=None, bare_url: bool = False) -> Response:
        """

        :param endpoint:
        :type endpoint:
        :param json_payload:
        :type json_payload:
        :return:
        :rtype:
        """
        json_payload = json_payload if json_payload is not None else {}

        Logging().info(f"POST /{endpoint} [{self.addr()}]")

        if bare_url:
            path = endpoint
        else:
            path = self.base_url + "/" + endpoint
        r = self.session.post(path, json=json_payload, timeout=PUT_TIMEOUT_SECONDS)
        try:
            r.raise_for_status()
        except Exception as e:
            msg = """POST - FAILED
            URL: {}
            Payload: {}
            """.format(
                path, str(json_payload)
            )
            Logging().error(msg, exception=e)
            raise e
        return r

    def _load_api_key(self, existing):
        """Load API key from environment variable
        - if API key not present in environment variable it will be set None
        - will then break when trying to access data on a building

        :param existing:
        :type existing:
        :return:
        :rtype:

        """

        # First respect any override by set_api_key
        if os.environ.get("PREHEAT_API_KEY_OVERRIDE") is not None:
            if (
                existing is None
                or os.environ.get("PREHEAT_API_KEY_OVERRIDE") != existing
            ):
                Logging().info(f"Using API key from set_api_key() [{self.addr()}]")
            return os.environ.get("PREHEAT_API_KEY_OVERRIDE")

        # Else, try PREHEAT_API_KEY environment variable
        elif os.environ.get("PREHEAT_API_KEY") is not None:
            if existing is None or os.environ.get("PREHEAT_API_KEY") != existing:
                Logging().info(
                    f"Using API key from environment variable [{self.addr()}]"
                )
            return os.environ.get("PREHEAT_API_KEY")

        # Else, try loading configuration file
        else:
            # If config loaded, set API key accordingly to file
            if preheat_open.config is not None:
                config_keys = preheat_open.config.keys()
                if "API_KEY" in config_keys:
                    if existing is None or preheat_open.config["API_KEY"] != existing:
                        Logging().info(
                            f"Using API key from config file [{self.addr()}]"
                        )
                    return preheat_open.config["API_KEY"]
                elif "PREHEAT_API_KEY" in config_keys:
                    if (
                        existing is None
                        or preheat_open.config["PREHEAT_API_KEY"] != existing
                    ):
                        Logging().info(
                            f"Using API key from config file [{self.addr()}]"
                        )
                    return preheat_open.config["PREHEAT_API_KEY"]
                else:
                    raise Exception(
                        f"""Your configuration file is missing a 'PREHEAT_API_KEY' field"""
                    )

            # No environment variable, no config file, nothing we can do
            else:
                return str(None)

    def _load_api_url(self):
        """

        :return:
        :rtype:
        """
        if os.environ.get("PREHEAT_API_URL_OVERRIDE") is not None:
            url = os.environ.get("PREHEAT_API_URL_OVERRIDE")
            Logging().info(f"Using API url: {url} [{self.addr()}]")
            return url
        else:
            Logging().info(f"Using default API url [{self.addr()}]")
            return BASE_URL


def set_api_key(api_key: str) -> None:
    """

    :param api_key:
    :type api_key:
    :return:
    :rtype:
    """
    if api_key is None:
        if "PREHEAT_API_KEY_OVERRIDE" in os.environ:
            os.environ.pop("PREHEAT_API_KEY_OVERRIDE")
            Logging().info("API key override unset")
    else:
        os.environ["PREHEAT_API_KEY_OVERRIDE"] = api_key
        Logging().info("API key override set")
    ApiSession().set_api_key()


def api_get(endpoint: str, out: str = "json", payload=None, headers=None) -> Response:
    """

    :param endpoint:
    :type endpoint:
    :param out:
    :type out:
    :param payload:
    :type payload:
    :param headers:
    :type headers:
    :return:
    :rtype:
    """
    return ApiSession().api_get(endpoint, out, payload, headers)


def api_put(endpoint: str, json_payload=None) -> Response:
    """

    :param endpoint:
    :type endpoint:
    :param json_payload:
    :type json_payload:
    :return:
    :rtype:
    """
    return ApiSession().api_put(endpoint, json_payload)


# --------------------------------------------------
# Deprecated methods below
def set_api_url(api_url: str) -> None:
    """
    Only kept for backwards compatibility
    """
    ApiSession().set_api_url(api_url)
