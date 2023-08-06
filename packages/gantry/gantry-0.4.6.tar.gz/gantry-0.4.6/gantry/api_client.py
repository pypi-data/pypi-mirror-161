import logging
import platform
from typing import Optional
from urllib.parse import urljoin

import requests

from gantry.serializers import dict_encoder
from gantry.version import __version__

logger = logging.getLogger(__name__)

API_KEY_HEADER_NAME = "X-Gantry-Api-Key"


class APIClient:
    def __init__(self, origin: str, api_key: Optional[str] = None):
        self._host = origin
        self._api_key = api_key

        user_agent = "gantry/{} {}/{} {} {}".format(
            __version__,
            platform.python_implementation(),
            platform.python_version(),
            platform.system(),
            platform.machine(),
        )

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def request(
        self,
        method,
        path,
        params=None,
        data=None,
        files=None,
        headers=None,
        timeout=None,
        proxies=None,
        verify=None,
        json=None,
    ):
        url = urljoin(self._host, path)

        req_headers = {}
        if self._api_key:
            req_headers[API_KEY_HEADER_NAME] = self._api_key
        if headers:
            req_headers.update(headers)

        if json:
            json = dict_encoder(json)

        logger.debug("%s %s", method, url)

        response = self._session.request(
            method,
            url,
            params=params,
            data=data,
            files=files,
            headers=req_headers,
            timeout=timeout,
            proxies=proxies,
            verify=verify,
            json=json,
        )

        logger.debug("Response: [%s]", response.status_code)
        logger.debug(response.text.strip("\n"))  # Remove newlines not to mess up with tracing tools

        if response.status_code == 404:
            logger.error(
                "%s Not found. Ensure the API is running and "
                "logger is pointed at the correct address.",
                url,
            )
        elif response.status_code >= 400 and response.status_code < 500:
            logger.error(
                "%s Gantry logger error. Ensure the logger is receiving valid data. "
                "Ensure the Gantry API is running and logger is pointed at the correct address.",
                response.status_code,
            )
        elif response.status_code >= 500 and response.status_code < 600:
            logger.error(
                "Internal Gantry error. "
                "Ensure that you are sending valid data to the Gantry API."
            )

        try:
            return response.json()
        except Exception as e:
            logger.debug(f"Invalid json response: {response.text} [{str(e)}]")
            return {"response": response.status_code, "error": response.status_code}


class LocalClient(APIClient):
    """For testing purposes only"""

    def __init__(self, app, api_key=None):
        self._app = app
        self._api_key = api_key

    def request(
        self,
        method,
        path,
        params=None,
        data=None,
        headers=None,
        timeout=None,
        proxies=None,
        verify=None,
        json=None,
    ):
        if json:
            json = dict_encoder(json)

        req_headers = {}
        if self._api_key:
            req_headers[API_KEY_HEADER_NAME] = self._api_key
        if headers:
            req_headers.update(headers)

        with self._app.test_client() as c:
            response = c.open(
                method=method,
                path=path,
                query_string=params,
                data=data,
                headers=req_headers,
                json=json,
            )

            # TODO: add common error handling here
            return response.get_json()
