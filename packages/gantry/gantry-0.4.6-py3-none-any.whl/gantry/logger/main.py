import datetime
import functools
import inspect
import logging
from pprint import pformat
from typing import Any, List, Optional, Union

import colorama
import pandas as pd

from gantry.config import Config
from gantry.exceptions import ClientNotInitialized
from gantry.logger.client import Gantry
from gantry.utils import format_msg_with_color

colorama.init(autoreset=True)
logger_obj = logging.getLogger(__name__)
logger_obj.addHandler(logging.NullHandler())

_CLIENT: Optional[Gantry] = None


def _client_alias(f):
    doc = "Alias for :meth:`gantry.logger.client.Gantry.{}`".format(f.__name__)
    orig_doc = inspect.getdoc(getattr(Gantry, f.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)

    f.__doc__ = doc

    # This decorator also checks that the _CLIENT
    # has been initialized
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _CLIENT is None:
            raise ClientNotInitialized()

        return f(*args, **kwargs)

    return wrapper


def init(*args, **kwargs):
    """
    Initialize the logger. Initialization should happen before submitting any data to Gantry.

    Example:

    .. code-block:: python

       import gantry

       gantry.init(api_key="foobar")

    """
    global _CLIENT

    # config_dict = config_from_file(config_file)
    # https://github.com/python/mypy/issues/6799

    config = Config(*args, **kwargs)
    _CLIENT = Gantry.from_config(config)

    s = format_msg_with_color(
        "Gantry initialized with following config", colorama.Fore.BLUE, logger_obj
    )
    logger_obj.debug(s)

    config_str = pformat(config._config)
    for line in config_str.split("\n"):
        logger_obj.debug(line)


@_client_alias
def instrument(*args, **kwargs):
    return _CLIENT.instrument(*args, **kwargs)


@_client_alias
def ping():
    return _CLIENT.ping()


@_client_alias
def log_feedback_event(*args, **kwargs):
    return _CLIENT.log_feedback_event(*args, **kwargs)


@_client_alias
def log_feedback(*args, **kwargs):
    return _CLIENT.log_feedback(*args, **kwargs)


@_client_alias
def log_file(*args, **kwargs):
    return _CLIENT.log_file(*args, **kwargs)


@_client_alias
def log_record(
    application: str,
    version: Optional[Union[int, str]] = None,
    inputs: Optional[dict] = None,
    outputs: Optional[Any] = None,
    feedback_id: Optional[dict] = None,
    feedback: Optional[dict] = None,
    feedback_keys: Optional[List[str]] = None,
    ignore_inputs: Optional[List[str]] = None,
    timestamp: Optional[datetime.datetime] = None,
    sample_rate: float = 1.0,
) -> None:
    return _CLIENT.log_record(**locals())  # type: ignore[union-attr]


@_client_alias
def log_records(
    application: str,
    version: Optional[Union[int, str, List[Union[str, int]]]] = None,
    inputs: Optional[Union[List[dict], pd.DataFrame]] = None,
    outputs: Optional[Union[List[dict], pd.DataFrame]] = None,
    feedback_keys: Optional[List[str]] = None,
    feedback_ids: Optional[List[dict]] = None,
    feedbacks: Optional[Union[List[dict], pd.DataFrame]] = None,
    ignore_inputs: Optional[List[str]] = None,
    timestamps: Optional[List[datetime.datetime]] = None,
    reference_name: Optional[str] = None,
    sort_on_timestamp: bool = False,
    sample_rate: float = 1.0,
    as_batch: bool = False,
) -> None:
    return _CLIENT.log_records(**locals())  # type: ignore[union-attr]


@_client_alias
def log_prediction_event(*args, **kwargs):
    return _CLIENT.log_prediction_event(*args, **kwargs)


@_client_alias
def log_predictions(*args, **kwargs):
    return _CLIENT.log_predictions(*args, **kwargs)


def get_client():
    return _CLIENT


def setup_logger(level: str = "INFO"):
    return Gantry.setup_logger(level)
