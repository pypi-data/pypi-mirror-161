import datetime
from collections import defaultdict

import mock
import pandas as pd
import pytest
import pytz
import responses
from freezegun import freeze_time
from responses import matchers

from gantry.query.core import queryframe

from ..conftest import END_TIME, ORIGIN, START_TIME


@pytest.fixture
def query_frame_obj(api_client_obj, query_info_obj):
    return queryframe.GantryQueryFrame(api_client_obj, query_info_obj)


def test_get_base_query_params(query_info_obj):
    assert query_info_obj.get_base_query_params() == {
        "start_time": START_TIME,
        "end_time": END_TIME,
        "version": "1.2.3",
    }


@pytest.mark.parametrize(
    ["start_time", "end_time", "expected"],
    [
        (START_TIME, END_TIME, (START_TIME, END_TIME)),
        (
            "August 14, 2015 EST",
            "July 4, 2013 PST",
            (
                datetime.datetime(2015, 8, 14, 5, 0, tzinfo=pytz.UTC),
                datetime.datetime(2013, 7, 4, 8, 0, tzinfo=pytz.UTC),
            ),
        ),
    ],
)
def test_resolve_time_strings(start_time, end_time, expected):
    assert queryframe.GantryQueryFrame.resolve_time_strings(start_time, end_time) == expected


@pytest.mark.parametrize(
    ["start_time", "end_time"],
    [
        ("abc", END_TIME),
        (START_TIME, "foobar"),
    ],
)
def test_resolve_time_strings_error(start_time, end_time):
    with pytest.raises(ValueError):
        queryframe.GantryQueryFrame.resolve_time_strings(start_time, end_time)


@pytest.mark.parametrize("env", [None, "dev"])
@pytest.mark.parametrize("n", [None, 1, 5])
def test_populate_raw_request_descending_no_pagination(n, env, api_client_obj):
    query_info_obj = queryframe.QueryInfo(
        "af0d0317-adbf-4524-b838-9dddf1c43fc8", "foobar", "1.2.3", env, START_TIME, END_TIME
    )
    query_frame_obj = queryframe.GantryQueryFrame(api_client_obj, query_info_obj)

    matcher = {}
    if env:
        matcher["tags"] = {"env": env}

    if n:
        matcher["limit"] = n

    matcher["order"] = "descending"

    expected_events = list("these-are-events")[:n] if n else list("these-are-events")
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/applications/af0d0317-adbf-4524-b838-9dddf1c43fc8/raw_data".format(ORIGIN),
            json={
                "response": "ok",
                "events": expected_events[::-1],
                "columns": "these-are-columns",
                "metadata": {
                    "count": n or 1,
                    "has_next": False,
                },
            },
            match=[matchers.json_params_matcher(matcher)],
        )

        assert (
            query_frame_obj._populate_raw_request(query_filters=[], ascending=False, n=n)
            == expected_events
        )


@pytest.mark.parametrize("env", [None, "dev"])
@pytest.mark.parametrize("n", [None, 1, 5])
def test_populate_raw_request_ascending_no_pagination(n, env, api_client_obj):
    query_info_obj = queryframe.QueryInfo(
        "af0d0317-adbf-4524-b838-9dddf1c43fc8", "foobar", "1.2.3", env, START_TIME, END_TIME
    )
    query_frame_obj = queryframe.GantryQueryFrame(api_client_obj, query_info_obj)

    matcher = {}
    if env:
        matcher["tags"] = {"env": env}

    if n:
        matcher["limit"] = n

    matcher["order"] = "ascending"

    expected_events = list("these-are-events")[:n] if n else list("these-are-events")
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/applications/af0d0317-adbf-4524-b838-9dddf1c43fc8/raw_data".format(ORIGIN),
            json={
                "response": "ok",
                "events": expected_events,
                "columns": "these-are-columns",
                "metadata": {
                    "count": n or 1,
                    "has_next": False,
                },
            },
            match=[matchers.json_params_matcher(matcher)],
        )

        assert (
            query_frame_obj._populate_raw_request(query_filters=[], ascending=True, n=n)
            == expected_events
        )


@pytest.mark.parametrize("env", [None, "dev"])
@pytest.mark.parametrize("n", [10, 53, 101])
def test_populate_raw_request_ascending_pagination(n, env, api_client_obj):
    query_info_obj = queryframe.QueryInfo(
        "af0d0317-adbf-4524-b838-9dddf1c43fc8", "foobar", "1.2.3", env, START_TIME, END_TIME
    )
    query_frame_obj = queryframe.GantryQueryFrame(api_client_obj, query_info_obj)

    total_num_events = 100
    all_events = list(range(total_num_events))
    requested_events = all_events[:n]
    up_to = n - (n // 2)  # return less than n to test pagination

    # Two matchers, one for the first page and one for the second
    first_matcher = {}
    if env:
        first_matcher["tags"] = {"env": env}
    first_matcher["limit"] = n
    first_matcher["order"] = "ascending"

    second_matcher = first_matcher.copy()
    second_matcher["offset"] = len(requested_events[:up_to])

    # Two responses, one for the first page and one for the second
    first_expected_response = {
        "response": "ok",
        "events": requested_events[:up_to],
        "columns": "these-are-columns",
        "metadata": {
            "count": total_num_events,
            "has_next": True,
        },
    }
    second_expected_response = {
        "response": "ok",
        "events": requested_events[up_to:],
        "columns": "these-are-columns",
        "metadata": {
            "count": total_num_events,
            "has_next": False,
        },
    }
    url = "{}/api/v1/applications/af0d0317-adbf-4524-b838-9dddf1c43fc8/raw_data".format(ORIGIN)

    # pagination means we need to make multiple POST requests
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            url,
            json=first_expected_response,
            match=[matchers.json_params_matcher(first_matcher)],
        )
        rsps.add(
            responses.POST,
            url,
            json=second_expected_response,
            match=[matchers.json_params_matcher(second_matcher)],
        )
        assert (
            query_frame_obj._populate_raw_request(query_filters=[], ascending=True, n=n)
            == requested_events
        )


@pytest.mark.parametrize("env", [None, "dev"])
@pytest.mark.parametrize("n", [10, 53, 101])
def test_populate_raw_request_descending_pagination(n, env, api_client_obj):
    query_info_obj = queryframe.QueryInfo(
        "af0d0317-adbf-4524-b838-9dddf1c43fc8", "foobar", "1.2.3", env, START_TIME, END_TIME
    )
    query_frame_obj = queryframe.GantryQueryFrame(api_client_obj, query_info_obj)

    total_num_events = 100
    all_events = list(range(total_num_events))
    requested_events = all_events[:n]
    up_to = n - (n // 2)  # return less than n to test pagination

    # Two matchers, one for the first page and one for the second
    first_matcher = {}
    if env:
        first_matcher["tags"] = {"env": env}
    first_matcher["limit"] = n
    first_matcher["order"] = "descending"

    second_matcher = first_matcher.copy()
    second_matcher["offset"] = len(requested_events[:up_to])

    # Two responses, one for the first page and one for the second
    first_expected_response = {
        "response": "ok",
        "events": requested_events[::-1][:up_to],
        "columns": "these-are-columns",
        "metadata": {
            "count": total_num_events,
            "has_next": True,
        },
    }
    second_expected_response = {
        "response": "ok",
        "events": requested_events[::-1][up_to:],
        "columns": "these-are-columns",
        "metadata": {
            "count": total_num_events,
            "has_next": False,
        },
    }
    url = "{}/api/v1/applications/af0d0317-adbf-4524-b838-9dddf1c43fc8/raw_data".format(ORIGIN)

    # pagination means we need to make multiple POST requests
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            url,
            json=first_expected_response,
            match=[matchers.json_params_matcher(first_matcher)],
        )
        rsps.add(
            responses.POST,
            url,
            json=second_expected_response,
            match=[matchers.json_params_matcher(second_matcher)],
        )
        assert (
            query_frame_obj._populate_raw_request(query_filters=[], ascending=False, n=n)
            == requested_events
        )


@pytest.mark.parametrize("num_events", [1, 5, 10, 20])
@pytest.mark.parametrize("column", ["A", None, "not_a_column"])
@pytest.mark.parametrize("method", ["_head", "_tail"])
@mock.patch("gantry.query.core.queryframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._dtypes", new_callable=mock.PropertyMock)
def test_head_tail(mock_dtypes, mock_populate_raw, method, column, num_events, query_frame_obj):
    columns = ["A", "B", "C"]

    def fake_populate_raw(n, ascending, query_filters):
        events = defaultdict(list)
        for c in columns:
            if c != "not_a_column":
                events[c] = list(range(num_events))
        return events

    mock_populate_raw.side_effect = fake_populate_raw
    mock_dtypes.return_value = {c: "int" for c in column} if column else {}

    if column == "not_a_column":
        with pytest.raises(ValueError):
            _ = getattr(query_frame_obj, method)(n=num_events, column=column)

    else:
        df = getattr(query_frame_obj, method)(n=num_events, column=column)

        expected = []
        for i in range(num_events):
            if column:
                expected.append({"A": i})
            else:
                expected.append({"A": i, "B": i, "C": i})

        pd.testing.assert_frame_equal(df, pd.DataFrame(expected))


@pytest.mark.parametrize("num_events", [1, 5, 10, 20])
@pytest.mark.parametrize("column", ["A", None, "not_a_column"])
@mock.patch("gantry.query.core.queryframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._dtypes", new_callable=mock.PropertyMock)
def test_fetch(mock_dtypes, mock_populate_raw, column, num_events, query_frame_obj):
    columns = ["A", "B", "C"]

    def fake_populate_raw(n, ascending, query_filters):
        events = defaultdict(list)
        for c in columns:
            if c != "not_a_column":
                events[c] = list(range(num_events))
        return events

    mock_populate_raw.side_effect = fake_populate_raw
    mock_dtypes.return_value = {c: "int" for c in column} if column else {}

    if column == "not_a_column":
        with pytest.raises(ValueError):
            _ = query_frame_obj._fetch(column=column)

    else:
        df = query_frame_obj._fetch(column=column)

        expected = []
        for i in range(num_events):
            if column:
                expected.append({"A": i})
            else:
                expected.append({"A": i, "B": i, "C": i})

        pd.testing.assert_frame_equal(df, pd.DataFrame(expected))


@pytest.mark.parametrize("method", ["_head", "_tail"])
def test_head_tail_invalid_param(method, query_frame_obj):
    with pytest.raises(ValueError):
        _ = getattr(query_frame_obj, method)(n=0)


@pytest.mark.parametrize("method", ["_fetch"])
def test_fetch_invalid_param(method, query_frame_obj):
    with pytest.raises(TypeError):
        # _fetch takes no parameters
        _ = getattr(query_frame_obj, method)(n=0)


@freeze_time("2020-01-01")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._dtypes", new_callable=mock.PropertyMock)
def test_prepare_pandas_dataframe_with_timestamp(mock_dtypes, query_frame_obj):
    _dtypes = {
        "A": "int",
        "B": "int",
        "C": "str",
    }
    mock_dtypes.return_value = _dtypes

    # Compute time in ms since epoch (1/1/1970), create events
    current_unix_time = int(
        (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    )
    events = [
        {"__time": current_unix_time, "A": 1, "B": 2, "C": "foo"},
        {"__time": current_unix_time + int(1e3), "A": 23, "B": 52, "C": "bar"},
        {"__time": current_unix_time, "A": 4, "B": 2, "C": "baz"},
        {"__time": current_unix_time + int(1e5), "A": 5, "B": 2, "C": "goof"},
    ]
    df = query_frame_obj._prepare_pandas_dataframe(events)

    # Check that the index is a DatetimeIndex
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "timestamp"

    # Check that the index is sorted
    correct_times = [
        current_unix_time,
        current_unix_time,
        current_unix_time + int(1e3),
        current_unix_time + int(1e5),
    ]

    assert all(
        [
            df.index.values[i].astype("datetime64[ms]").astype("int") == correct_times[i]
            for i in range(len(df))
        ]
    )


@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._dtypes", new_callable=mock.PropertyMock)
def test_prepare_pandas_dataframe_without_timestamp(mock_dtypes, query_frame_obj):
    _dtypes = {
        "A": "bool",
        "B": "category",
        "C": "float",
        "D": "int",
        "E": "uuid",
        "F": "str",
        "G_some_none": "bool",
        "H_all_none": "str",
    }
    mock_dtypes.return_value = _dtypes

    events = [
        {
            "A": "true",
            "B": "foo",
            "C": 1.0,
            "D": 1,
            "E": "asd123",
            "F": "foo",
            "G_some_none": "true",
            "H_all_none": None,
        },
        {
            "A": "false",
            "B": "bar",
            "C": 2.0,
            "D": 2,
            "E": "345436gdfkjdn",
            "F": "bar",
            "G_some_none": None,
            "H_all_none": None,
        },
        {
            "A": "true",
            "B": "baz",
            "C": 3.0,
            "D": 3,
            "E": "sadfs3456",
            "F": "baz",
            "G_some_none": "false",
            "H_all_none": None,
        },
    ]

    df = query_frame_obj._prepare_pandas_dataframe(events)

    expected_dtypes = {
        "A": "boolean",
        "B": "category",
        "C": "float",
        "D": "int",
        "E": "object",
        "F": "string",
        "G_some_none": "boolean",
        "H_all_none": "string",
    }

    # ordered alphabetically
    assert df.columns.tolist() == list(expected_dtypes.keys())

    for actual, expected in zip(df.dtypes.tolist(), list(expected_dtypes.values())):
        assert actual == expected

    # all None column is bool but values are "not available"
    assert isinstance(df["H_all_none"].unique()[0], type(pd.NA))

    # Check that DataFrame.index is the typical RangeIndex counter
    # Contrasts the case where the index is a DatetimeIndex
    assert isinstance(df.index, pd.RangeIndex)


@pytest.mark.parametrize("column", [None, "A"])
def test_prepare_pandas_dataframe_empty(column, query_frame_obj):
    df = query_frame_obj._prepare_pandas_dataframe([], column=column)
    assert df.empty


def test_metadata(query_frame_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar/schemas".format(ORIGIN),
            json={"response": "ok", "data": "this-is-the-schema"},
            match=[
                matchers.query_param_matcher(
                    {
                        "start_time": str(START_TIME),
                        "end_time": str(END_TIME),
                        "version": "1.2.3",
                    }
                )
            ],
        )

        assert query_frame_obj.metadata == "this-is-the-schema"


@pytest.mark.parametrize(
    ["metadata", "expected"],
    [
        ({}, {}),
        (
            {
                "feedback_datanodes": [
                    {
                        "dtype": "bool",
                        "event_type": "feedback",
                        "name": "feedback.is_fraud",
                        "node_metadata": {
                            "content_retrieval": ["feedback", "is_fraud"],
                            "dtype": {"id_str": False, "is_categorical": True, "long_str": False},
                        },
                        "node_type": "identity",
                    }
                ],
                "prediction_datanodes": [
                    {
                        "dtype": "float",
                        "event_type": "prediction",
                        "name": "inputs.amt",
                        "node_metadata": {
                            "content_retrieval": ["inputs", "amt"],
                            "dtype": {"id_str": False, "is_categorical": False, "long_str": False},
                        },
                        "node_type": "identity",
                    },
                    {
                        "dtype": "bool",
                        "event_type": "prediction",
                        "name": "outputs.pred_fraud",
                        "node_metadata": {
                            "content_retrieval": ["outputs", "pred_fraud"],
                            "dtype": {"id_str": False, "is_categorical": True, "long_str": False},
                        },
                        "node_type": "identity",
                    },
                    {
                        "dtype": "str",
                        "event_type": "prediction",
                        "name": "inputs.zip",
                        "node_metadata": {
                            "content_retrieval": ["inputs", "zip"],
                            "dtype": {"is_categorical": False, "long_str": True},
                        },
                        "node_type": "identity",
                    },
                    {
                        "dtype": "str",
                        "event_type": "prediction",
                        "name": "inputs.cc_num",
                        "node_metadata": {
                            "content_retrieval": ["inputs", "cc_num"],
                            "dtype": {"is_categorical": False, "long_str": True},
                        },
                        "node_type": "identity",
                    },
                ],
                "projection_datanodes": [
                    {
                        "dtype": "float",
                        "event_type": "prediction",
                        "name": "inputs.category.CommonWordProjection",
                        "node_metadata": {
                            "dtype": {},
                            "projection_class": "CommonWordProjection",
                            "projection_init": {},
                        },
                        "node_type": "projection",
                    }
                ],
            },
            {
                "feedback.is_fraud": "bool",
                "inputs.amt": "float",
                "inputs.category.CommonWordProjection": "float",
                "inputs.cc_num": "str",
                "inputs.zip": "str",
                "outputs.pred_fraud": "bool",
            },
        ),
    ],
)
@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    new_callable=mock.PropertyMock,
)
def test_dtypes(mock_metadata, metadata, expected, query_frame_obj):
    mock_metadata.return_value = metadata
    assert query_frame_obj._dtypes == expected


def test_get_raw_data(query_frame_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/applications/af0d0317-adbf-4524-b838-9dddf1c43fc8/raw_data".format(ORIGIN),
            json="OK",
            match=[matchers.json_params_matcher({"foo": "bar"})],
        )

        assert (
            queryframe._get_raw_data(
                query_frame_obj.api_client, query_frame_obj.query_info, '{"foo": "bar"}'
            )
            == "OK"
        )
