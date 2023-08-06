from datetime import datetime

import mock
import pytest
import responses
from freezegun import freeze_time
from responses import matchers

from gantry.exceptions import GantryException
from gantry.query.core.constants import GENERIC_MESSAGE
from gantry.query.core.utils import (
    check_response,
    get_application_node_id,
    get_application_views,
    get_last_application_version,
    get_start_end_time_from_view,
    runs_on,
    same_size,
)

from ..conftest import DATA, END_TIME, END_TIME_STR, ORIGIN, START_TIME, START_TIME_STR
from tests.query.test_client import VIEWS_DATA


@pytest.mark.parametrize(
    ["response", "msg", "expected_match"],
    [
        ({"response": "not ok"}, None, GENERIC_MESSAGE),
        ({"response": "OK"}, None, GENERIC_MESSAGE),
        ({"response": 1234}, None, GENERIC_MESSAGE),
        ({"response": 1234}, "Something happened", "Something happened"),
        (
            {"response": "not ok", "error": "This is the actual error"},
            "Something happened",
            "Something happened",
        ),
        (
            {"response": "not ok", "error": "This is the actual error"},
            None,
            "This is the actual error",
        ),
    ],
)
def test_check_response_raise(response, msg, expected_match):
    with pytest.raises(GantryException, match=expected_match):
        check_response(response, msg=msg)


@pytest.mark.parametrize(
    "response",
    [
        {"response": "ok"},
    ],
)
def test_check_response_valid(response):
    check_response(response)


@pytest.mark.parametrize(
    ["supported", "invalid"],
    [
        (["bool"], "int"),
        (["bool"], "object"),
        (["bool"], "float"),
        (["bool", "float"], "int"),
        (["int", "str"], "bool"),
        (["int", "bool"], "str"),
    ],
)
def test_runs_on_invalid(supported, invalid):
    dec = runs_on(*supported)
    f = dec(lambda m: True)
    with pytest.raises(ValueError):
        f(mock.Mock(dtype=invalid))


@pytest.mark.parametrize(
    ["supported", "valid"],
    [
        (["bool"], "bool"),
        (["bool", "int"], "int"),
        (["str", "float"], "float"),
        (["str", "float"], "str"),
    ],
)
def test_runs_on_valid(supported, valid):
    dec = runs_on(*supported)
    f = dec(lambda m: True)
    assert f(mock.Mock(dtype=valid))


l_1 = list(range(1))
l_10 = list(range(10))
l_100 = list(range(100))


@pytest.mark.parametrize(
    ["args", "kwargs"],
    [
        ([l_10, l_10], {"s3": l_10}),
        ([l_10], {"s3": l_10, "s2": l_10}),
        ([], {"s1": l_10, "s3": l_10, "s2": l_10}),
    ],
)
def test_same_size_valid(args, kwargs):
    dec = same_size("s1", "s2", "s3")
    f = dec(lambda s1, s2, s3: True)
    assert f(*args, **kwargs)


@pytest.mark.parametrize(
    ["args", "kwargs"],
    [
        ([l_10, l_100], {"s3": l_10}),
        ([l_10], {"s3": l_100, "s2": l_100}),
        ([], {"s1": l_10, "s3": l_100, "s2": l_10}),
        ([], {"s1": l_10, "s3": l_100, "s2": l_1}),
    ],
)
def test_same_size_error(args, kwargs):
    dec = same_size("s1", "s2", "s3")
    f = dec(lambda s1, s2, s3: True)
    with pytest.raises(ValueError):
        f(*args, **kwargs)


@pytest.mark.parametrize("bad_params", [["other"], ["s1", "s2", "s3"]])
def test_same_size_bad_params(bad_params):
    dec = same_size(*bad_params)
    with pytest.raises(ValueError):
        _ = dec(lambda s1, s2: True)


@pytest.mark.parametrize(
    ["start_time", "end_time", "version", "content"],
    [
        (
            START_TIME,
            END_TIME,
            "1.2.3",
            {
                "end_time": "2008-09-10 23:58:23",
                "start_time": "2008-09-03 20:56:35",
                "version": "1.2.3",
            },
        ),
        (None, None, None, {}),
        (None, None, "2", {"version": "2"}),
        (
            START_TIME,
            END_TIME,
            None,
            {
                "end_time": "2008-09-10 23:58:23",
                "start_time": "2008-09-03 20:56:35",
            },
        ),
    ],
)
def test_get_application_node_id(start_time, end_time, version, content, api_client_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar/schemas".format(ORIGIN),
            json={"response": "ok", "data": DATA},
            match=[matchers.query_param_matcher(content)],
        )

        assert (
            get_application_node_id(api_client_obj, "foobar", start_time, end_time, version)
            == "ABCD1234"
        )


@pytest.mark.parametrize(
    ["start_time", "end_time", "version", "content"],
    [
        (
            START_TIME,
            END_TIME,
            "1.2.3",
            {
                "end_time": "2008-09-10 23:58:23",
                "start_time": "2008-09-03 20:56:35",
                "version": "1.2.3",
            },
        ),
        (None, None, None, {}),
        (None, None, "2", {"version": "2"}),
        (
            START_TIME,
            END_TIME,
            None,
            {
                "end_time": "2008-09-10 23:58:23",
                "start_time": "2008-09-03 20:56:35",
            },
        ),
    ],
)
@pytest.mark.parametrize("json_data", [{"response": "ok"}, {"response": "ok", "data": {}}])
def test_get_application_node_id_error(
    json_data, start_time, end_time, version, content, api_client_obj
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar/schemas".format(ORIGIN),
            json=json_data,
            match=[matchers.query_param_matcher(content)],
        )

        with pytest.raises(RuntimeError):
            _ = get_application_node_id(api_client_obj, "foobar", start_time, end_time, version)


@pytest.mark.parametrize("version", ["2", None])
@pytest.mark.parametrize(
    ["env", "expected"],
    [
        (
            "env-A",
            [{"name": "view_1", "tag_filters": {"env": "env-A"}, "other": "A"}],
        ),
        (
            "env-B",
            [
                {"name": "view_2", "tag_filters": {"env": "env-B"}, "other": "B"},
                {"name": "view_3", "tag_filters": {"env": "env-B"}, "other": "C"},
            ],
        ),
        (None, VIEWS_DATA),
    ],
)
def test_get_application_views(env, expected, version, api_client_obj):
    with responses.RequestsMock() as rsps:
        latest_version = "2"
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/barbaz/views".format(ORIGIN),
            json={"response": "ok", "data": VIEWS_DATA},
            match=[matchers.query_param_matcher({"version": latest_version})],
        )

        if not version:
            rsps.add(
                responses.GET,
                "{}/api/v1/models/barbaz/schemas".format(ORIGIN),
                json={"response": "ok", "data": {"version": latest_version}},
            )

        assert (
            get_application_views(api_client_obj, "barbaz", version=version, environment=env)
            == expected
        )


@pytest.mark.parametrize("version", [None])
def test_get_last_application_version_with_error(version, api_client_obj):
    with pytest.raises(RuntimeError):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "{}/api/v1/models/barbaz/schemas".format(ORIGIN),
                json={"response": "ok", "data": {"version": version}},
            )

            get_last_application_version(api_client_obj, "barbaz")


DATE_PARAM_FMT = "%Y-%m-%d+%H%%3A%M%%3A%S"


@pytest.mark.parametrize(["version"], ["1"])
@pytest.mark.parametrize(
    ["params"],
    [
        [{"start_time": None, "end_time": None}],
        [{"start_time": START_TIME.strftime(DATE_PARAM_FMT), "end_time": None}],
        [{"start_time": None, "end_time": END_TIME.strftime(DATE_PARAM_FMT)}],
        [
            {
                "start_time": START_TIME.strftime(DATE_PARAM_FMT),
                "end_time": END_TIME.strftime(DATE_PARAM_FMT),
            }
        ],
    ],
)
def test_get_last_application_version(version, params, api_client_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/barbaz/schemas".format(ORIGIN),
            json={"response": "ok", "data": {"version": version}},
            match=[matchers.query_param_matcher({k: v for k, v in params.items() if v})],
        )

        assert get_last_application_version(api_client_obj, "barbaz", **params) == version


@freeze_time("2012-01-14")
@pytest.mark.parametrize(
    ["view", "expected"],
    [
        (
            {
                "start_time": START_TIME_STR,
                "end_time": END_TIME_STR,
                "duration": "P1D",
            },
            (START_TIME, END_TIME),
        ),
        (
            {
                "start_time": None,
                "end_time": END_TIME_STR,
                "duration": "P1D",
            },
            (datetime(2012, 1, 14, 0, 0), datetime(2012, 1, 13, 0, 0)),
        ),
        (
            {
                "start_time": None,
                "end_time": END_TIME_STR,
                "duration": "P8DT10H24M32S",
            },
            (datetime(2012, 1, 14, 0, 0), datetime(2012, 1, 5, 13, 35, 28)),
        ),
    ],
)
def test_get_start_end_time_from_view(view, expected):
    assert get_start_end_time_from_view(view) == expected


@pytest.mark.parametrize(
    "invalid_view",
    [
        {},
        {
            "start_date": START_TIME_STR,
            "end_date": END_TIME_STR,
        },
    ],
)
def test_get_start_end_time_from_view_error(invalid_view):
    with pytest.raises(ValueError):
        get_start_end_time_from_view(invalid_view)
