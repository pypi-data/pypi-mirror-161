import datetime
import pytest
from freezegun import freeze_time

from gantry.exceptions import (
    GantryLoggingException,
)
from gantry.utils import check_event_time_in_future

CURRENT_TIME = datetime.datetime(2032, 5, 23, 0, 0, 0)
FUTURE_TIME = datetime.datetime(2042, 5, 23, 0, 0, 0)
SOME_TIME = datetime.datetime(2022, 5, 10, 17, 50, 32)
ANOTHER_TIME = datetime.datetime(2022, 5, 11, 17, 50, 32)


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("timestamp", [FUTURE_TIME])
def test_check_event_time_in_future(timestamp):
    with pytest.raises(GantryLoggingException):
        check_event_time_in_future(timestamp)


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("timestamp", [SOME_TIME, ANOTHER_TIME])
def test_check_event_time_in_past(timestamp):
    check_event_time_in_future(timestamp)
