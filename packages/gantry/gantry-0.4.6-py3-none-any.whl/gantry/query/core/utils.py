import functools
from datetime import datetime
from inspect import getcallargs, getfullargspec
from typing import Optional, Tuple, Union, cast

import dateparser
import isodate

from gantry.api_client import APIClient
from gantry.exceptions import GantryException
from gantry.query.core.constants import GENERIC_MESSAGE, OK_STATUS, STATUS_PARAM


def check_response(response, msg: Optional[str] = None) -> None:
    if response.get(STATUS_PARAM) != OK_STATUS:
        # msg has priority, then response['error'] and finally
        # the generic error msg
        msg = msg or response.get("error") or GENERIC_MESSAGE
        raise GantryException(msg)


def same_size(*params):
    # Use this decorator to prevent running methods over iterables that are different sizes.
    # For example, if 'some_method(s1, s2, s3)' need s1/s2/s3 to be same size then
    # it can be decorated with '@same_size("s1", "s2", "s3")'.
    def decorator(method):
        fullargs = getfullargspec(method).args
        if not all(map(lambda x: x in fullargs, params)):
            raise ValueError(
                f"Decorator on {method} was badly parametrized {params}. This shouldn't happen. "
                "Parameters for this decorator should be a subset "
                "of the methods allowed parameters."
            )

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            provided_params = getcallargs(method, *args, **kwargs)
            sizes = {param: len(provided_params[param]) for param in params}
            if len(set(sizes.values())) != 1:
                raise ValueError(
                    f"Size mismatch on inputs: {sizes}. "
                    f"All GantrySeries passed need to be same size."
                )
            return method(*args, **kwargs)

        return wrapper

    return decorator


def runs_on(*types):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.dtype not in types:
                raise ValueError(
                    f"'{self.name}' has type '{self.datatype}'. "
                    f"'{method.__name__}' support {types} only"
                )
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


def get_application_views(
    api_client: APIClient,
    application: str,
    version=Optional[Union[str, int]],
    environment=Optional[str],
) -> list:
    version_param = version or get_last_application_version(
        api_client=api_client, application=application
    )

    response = api_client.request(
        "GET", "/api/v1/applications/" + application + "/views", params={"version": version_param}
    )
    check_response(response)

    views = response["data"]

    if environment:
        views = list(filter(lambda view: view["tag_filters"]["env"] == environment, views))

    return views


def get_last_application_version(
    api_client: APIClient,
    application: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> str:
    query_params: dict[str, Union[int, str, datetime]] = {}
    if start_time:
        query_params["start_time"] = start_time
    if end_time:
        query_params["end_time"] = end_time
    metadata_response = api_client.request(
        "GET", "/api/v1/models/" + application + "/schemas", query_params
    )
    check_response(metadata_response)
    if metadata_response.get("data", {}).get("version") is None:
        raise RuntimeError("Unkown error: couldn't fetch last application version from API.")

    return metadata_response["data"]["version"]


def get_application_node_id(
    api_client: APIClient,
    application: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    version: Optional[Union[str, int]] = None,
) -> str:
    query_params: dict[str, Union[int, str, datetime]] = {}
    if start_time:
        query_params["start_time"] = start_time
    if end_time:
        query_params["end_time"] = end_time
    if version:
        query_params["version"] = version

    metadata_response = api_client.request(
        "GET", "/api/v1/models/" + application + "/schemas", query_params
    )
    check_response(metadata_response)
    if metadata_response.get("data", {}).get("id") is None:
        raise RuntimeError("Unkown error: couldn't fetch node id from API.")

    return metadata_response["data"]["id"]


def get_start_end_time_from_view(view: dict) -> Tuple[datetime, datetime]:
    if view.get("start_time"):
        start_time = cast(datetime, dateparser.parse(view["start_time"]))
        end_time = cast(datetime, dateparser.parse(view["end_time"]))
    elif view.get("duration"):
        start_time = datetime.utcnow()
        end_time = start_time - isodate.parse_duration(view["duration"])
    else:
        raise ValueError(
            "View has invalid time configuration. Either start_time/end_time"
            " or duration need to be set"
        )

    return start_time, end_time
