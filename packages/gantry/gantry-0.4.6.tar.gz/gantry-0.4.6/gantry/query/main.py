import datetime
import os
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from gantry.api_client import APIClient
from gantry.const import PROD_API_URL
from gantry.query import globals
from gantry.query.client import GantryQuery
from gantry.query.core.dataframe import GantryDataFrame  # noqa
from gantry.query.globals import _query_alias, validate_init


def init(backend: str = PROD_API_URL, api_key: Optional[str] = None):
    """
    Initialize the Query functionality. Initialization should happen before any Query call.

    Example:

    .. code-block:: python

       import gantry.query as gquery

       gquery.init(api_key="foobar")

    Args:
        backend (str): The backend URL. Defaults to the Gantry production URL.
        api_key (str): The API key. Users can fetch the API key from the dashboard.
    """
    parsed_origin = urlparse(backend)
    if parsed_origin.scheme not in ("http", "https"):
        raise ValueError(
            "Invalid backend. http or https backends " + "supported. Got {}".format(backend)
        )

    # Check environment if api_key is not provided
    api_key = os.environ.get("GANTRY_API_KEY") if api_key is None else api_key

    if not api_key:
        raise ValueError(
            """
            No API key provided. Please pass the api_key parameter or set the GANTRY_API_KEY
            environment variable.
            """
        )

    api_client = APIClient(backend, api_key)
    globals._Query = GantryQuery(api_client)  # type: ignore[union-attr]


@_query_alias
def list_applications() -> List[str]:
    validate_init()
    return globals._Query.list_applications()  # type: ignore[union-attr]


@_query_alias
def list_application_versions(application: str) -> List[Tuple[int, str]]:
    validate_init()
    return globals._Query.list_application_versions(**locals())  # type: ignore[union-attr]


@_query_alias
def list_application_environments(application: str) -> List[str]:
    validate_init()
    return globals._Query.list_application_environments(**locals())  # type: ignore[union-attr]


@_query_alias
def query(
    application: str,
    start_time: Optional[Union[str, datetime.datetime]] = None,
    end_time: Optional[Union[str, datetime.datetime]] = None,
    version: Optional[Union[int, str]] = None,
    environment: Optional[str] = None,
    filters: Optional[List[Dict]] = None,
    view: Optional[str] = None,
) -> GantryDataFrame:
    validate_init()
    return globals._Query.query(**locals())  # type: ignore[union-attr]


@_query_alias
def set_reference(
    application: str,
    version: Union[int, str],
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    reference_name: str,
    tags: Optional[dict] = None,
):
    validate_init()
    return globals._Query.set_reference(**locals())  # type: ignore[union-attr]


@_query_alias
def get_current_feedback_schema(application: str):
    validate_init()
    return globals._Query.get_current_feedback_schema(**locals())  # type: ignore[union-attr]


@_query_alias
def update_feedback_schema(application, feedback_fields: List[Dict[str, str]], create: bool = True):
    validate_init()
    return globals._Query.update_feedback_schema(**locals())  # type: ignore[union-attr]


@_query_alias
def add_feedback_field(application: str, feedback_field: Dict[str, str]) -> int:
    validate_init()
    return globals._Query.add_feedback_field(**locals())  # type: ignore[union-attr]


@_query_alias
def get_current_metric_schema(application: str):
    validate_init()
    return globals._Query.get_current_metric_schema(**locals())  # type: ignore[union-attr]


@_query_alias
def update_metric_schema(application: str, metrics: List[dict], create: bool = True):
    validate_init()
    return globals._Query.update_metric_schema(**locals())  # type: ignore[union-attr]


@_query_alias
def add_metric(application: str, metric: dict) -> int:
    validate_init()
    return globals._Query.add_metric(**locals())  # type: ignore[union-attr]


@_query_alias
def list_application_views(
    application: str,
    version: Optional[Union[str, int]] = None,
    environment: Optional[str] = None,
) -> List[str]:
    validate_init()
    return globals._Query.list_application_views(**locals())  # type: ignore[union-attr]


@_query_alias
def print_application_info(application: str):
    validate_init()
    return globals._Query.print_application_info(**locals())  # type: ignore[union-attr]
