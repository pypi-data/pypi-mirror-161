import collections
import collections.abc
import datetime
import hashlib
import json
import logging
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from dateutil import parser

from gantry.exceptions import GantryLoggingException
from gantry.serializers import EventEncoder

logger = logging.getLogger(__name__)


def to_datetime(s: str) -> datetime.datetime:
    """
    Converts a string to a naive UTC datetime object
    """
    try:
        # fromisoformat is present starting in python3.7
        if s.endswith("Z"):
            dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.datetime.fromisoformat(s)
    except (AttributeError, ValueError, TypeError):
        try:
            dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception:
            dt = parser.parse(s)
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # check if datetime is already naive
        # https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
        return dt

    naive_dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return naive_dt


def to_isoformat_duration(relative_interval: datetime.timedelta) -> str:
    days = relative_interval.days
    seconds = relative_interval.seconds

    minutes, seconds = seconds // 60, seconds % 60
    hours, minutes = minutes // 60, minutes % 60
    weeks, days = days // 7, days % 7

    timedelta_str = "P"
    if weeks > 0:
        timedelta_str += str(weeks) + "W"
    if days > 0:
        timedelta_str += str(days) + "D"
    timedelta_str += "T"
    if hours > 0:
        timedelta_str += str(hours) + "H"
    if minutes > 0:
        timedelta_str += str(minutes) + "M"
    if seconds > 0:
        timedelta_str += str(seconds) + "S"

    if timedelta_str[-1] == "T":
        timedelta_str = timedelta_str[:-1]

    if len(timedelta_str) == 1:
        return "P0D"

    return timedelta_str


def to_timestamp(dt) -> float:
    """
    converts naive Datetime object to a timestamp in seconds.

    implemented for py 2 compatibility:
    https://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python
    """
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def check_event_time_in_future(event_timestamp: datetime.datetime) -> None:
    """
    Raises an error if the event timestamp is in the future.
    Note, `event_timestamp` is assumed to be in UTC.
    """
    current_time = datetime.datetime.utcnow()

    if event_timestamp > current_time:
        raise GantryLoggingException(
            "Cannot log events from the future. "
            f"Event timestep is {event_timestamp}, but current time is {current_time}. "
            "Please check your event times and re-submit all."
        )


def compute_feedback_id(inputs: Dict[str, Any], feedback_keys: Optional[List[str]] = None) -> str:
    assert isinstance(inputs, collections.abc.Mapping)
    if not feedback_keys:
        # When not specified, default to feedback_keys are all the
        # fields of inputs
        feedback_keys = list(inputs.keys())

    values = []
    for key in sorted(feedback_keys):
        input_value = inputs[key]
        # TODO change to hashable type if input_value isn't
        # hashable
        values.append(input_value)

    return hashlib.md5(
        json.dumps(values, sort_keys=True, cls=EventEncoder).encode("utf-8")
    ).hexdigest()


def clean_name(name: str) -> str:
    """Replace any non-alphanumeric characters, except '-' and '.', with '-'"""
    return re.sub(r"[^a-zA-Z0-9\-.]+", "-", name)


def generate_gantry_name(name: str, max_len: int = 64) -> str:
    prefix = "gantry-"
    suffix = "-" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]

    remaining_len = max_len - len(prefix) - len(suffix)
    trunc_name = clean_name(name)[:remaining_len].lower().strip("-")

    return prefix + trunc_name + suffix


def parse_s3_path(path: str) -> Tuple[str, str]:
    """Parses an S3 path of the form s3://bucket/path/to/obj and returns (key, path/to/obj)"""
    prefix_len = len("s3://")
    s3_path = path[prefix_len:]
    bucket, _, key = s3_path.partition("/")

    return (bucket, key)


def format_msg_with_color(msg: str, color: str, logger: logging.Logger) -> str:
    """Given a message and a colorama color, conditionally returns a formatted message if the only
    handlers of the gantry package logger are NullHandlers or StreamHandlers with sys.stderr
    or sys.stdout
    """
    # loop to short-circuit and return original message if a potential file handler is found
    for handler in logging.getLogger("gantry").handlers:
        if isinstance(handler, logging.NullHandler):
            # It is okay if handler is NullHandler
            continue
        elif isinstance(handler, logging.StreamHandler):
            # If handler is a StreamHandler make sure stream is sys.stderr or sys.stdout
            if handler.stream in (
                sys.stderr,
                sys.stdout,
            ):
                continue
        else:
            # In all other cases, we might be logging to a file so just return the original msg
            return msg
    # If we haven't short-circuited and returned original message, return the colored message
    return color + msg


def obj_by_id(els):
    obj = {}
    for el in els:
        obj[el.id] = el

    return obj
