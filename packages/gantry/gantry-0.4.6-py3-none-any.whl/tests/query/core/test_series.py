import json

import mock
import pandas as pd
import pytest
import responses
from pandas.testing import assert_frame_equal
from responses import matchers

from gantry.exceptions import GantryException, QueryError
from gantry.query.core import dataframe
from gantry.query.core.queryframe import QueryInfo

from ..conftest import END_TIME, MULTIPLE_FEATURES_INT_DATA, ORIGIN, START_TIME


def test_series_filters_property_getter(series_obj_factory, api_client_obj, query_info_obj):
    filters = ["filter-1", "filter-2", "filter-3"]
    parent_dataframe = mock.Mock(api_client=api_client_obj, query_info=query_info_obj)
    parent_dataframe.filters = filters

    series_obj = series_obj_factory("str", parent_dataframe=parent_dataframe)
    assert series_obj.filters == filters


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_mean(mock_query, series_obj):
    mock_query.return_value = 0.5
    assert series_obj.mean() == 0.5
    mock_query.assert_called_once_with("mean")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_mean_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.mean()
    mock_query.assert_called_once_with("mean")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_std(mock_query, series_obj):
    mock_query.return_value = 0.6
    assert series_obj.std() == 0.6
    mock_query.assert_called_once_with("stddev")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_std_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.std()
    mock_query.assert_called_once_with("stddev")


@mock.patch("gantry.query.core.dataframe.GantrySeries.quantile")
def test_median(mock_query, series_obj):
    mock_query.return_value = {0.5: 0.7}
    assert series_obj.median() == 0.7
    mock_query.assert_called_once_with([0.5])


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries.quantile")
def test_median_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.median()
    mock_query.assert_called_once_with([0.5])


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_count(mock_query, series_obj):
    mock_query.return_value = 100
    assert series_obj.count() == 100
    mock_query.assert_called_once_with("total")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_len(mock_query, series_obj):
    mock_query.return_value = 100
    assert len(series_obj) == 100
    mock_query.assert_called_once_with("total")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_count_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.count()
    mock_query.assert_called_once_with("total")


@pytest.mark.parametrize("datatype", ["int", "float"])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_min(mock_query, datatype, series_obj_factory):
    series_obj = series_obj_factory(datatype)
    mock_query.return_value = 1
    assert series_obj.min() == 1
    mock_query.assert_called_once_with("minimum")


@pytest.mark.parametrize("invalid_datatype", ["str", "bool", "category"])
def test_min_invalid_datatype(invalid_datatype, series_obj_factory):
    with pytest.raises(ValueError):
        series_obj = series_obj_factory(invalid_datatype)
        _ = series_obj.min()


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_min_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.min()
    mock_query.assert_called_once_with("minimum")


@pytest.mark.parametrize("datatype", ["int", "float"])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_max(mock_query, datatype, series_obj_factory):
    series_obj = series_obj_factory(datatype)
    mock_query.return_value = 1000
    assert series_obj.max() == 1000
    mock_query.assert_called_once_with("maximum")


@pytest.mark.parametrize("invalid_datatype", ["str", "bool", "category"])
def test_max_invalid_datatype(invalid_datatype, series_obj_factory):
    with pytest.raises(ValueError):
        series_obj = series_obj_factory(invalid_datatype)
        _ = series_obj.max()


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_max_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.max()
    mock_query.assert_called_once_with("maximum")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_histogram(mock_query, series_obj):
    mock_query.return_value = {"a": 10}
    assert series_obj.histogram() == {"a": 10}
    mock_query.assert_called_once_with("category_percents")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_histogram_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.histogram()
    mock_query.assert_called_once_with("category_percents")


@pytest.mark.parametrize("vals", [[0.5], [1, 2, 3], []])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_quantile(mock_query, vals, series_obj):
    mock_query.return_value = {1: 10}
    assert series_obj.quantile(vals) == {1.0: 10}
    mock_query.assert_called_once_with("quantiles", {"quantile_vals": vals})


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_quantile_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.quantile()


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_pdf(mock_query, series_obj):
    mock_query.return_value = [1, 2, 3]
    pd.testing.assert_frame_equal(series_obj.pdf(), pd.DataFrame([1, 2, 3]))
    mock_query.assert_called_once_with("pdf")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_pdf_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.pdf()
    mock_query.assert_called_once_with("pdf")


@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_cdf(mock_query, series_obj):
    mock_query.return_value = [1, 2, 3]
    pd.testing.assert_frame_equal(series_obj.cdf(), pd.DataFrame([1, 2, 3]))
    mock_query.assert_called_once_with("cdf")


@pytest.mark.parametrize("error", [AttributeError, ValueError, KeyError])
@mock.patch("gantry.query.core.dataframe.GantrySeries._aggregate_query")
def test_cdf_error(mock_query, error, series_obj):
    mock_query.side_effect = error
    with pytest.raises(QueryError):
        series_obj.cdf()
    mock_query.assert_called_once_with("cdf")


def test_dtype(series_obj):
    assert series_obj._dtype() == "int"


@pytest.mark.parametrize("filters", [[], [{"some": "filter"}]])
@mock.patch("gantry.query.core.dataframe._raw_query_cached_request")
def test_aggregate_query(mock_query_data, series_obj_factory_with_filters, filters):
    content = json.dumps(
        {
            "start_time": "2008-09-03T20:56:35",
            "end_time": "2008-09-10T23:58:23",
            "version": "1.2.3",
            "queries": {
                "query": {
                    "query_type": "feature",
                    "model_node_id": "ABCD1234",
                    "stat": "some-attribute",
                    "stat_kwargs": {"some-attribute": {"a": 10}},
                    "feature": "series_name",
                    "filters": filters,
                }
            },
        },
        default=lambda x: x.isoformat(),
    )
    series_obj = series_obj_factory_with_filters("int", filters=filters)
    mock_query_data.return_value = {"response": "ok", "data": {"query": {"some-attribute": 10}}}

    assert series_obj._aggregate_query("some-attribute", {"a": 10}) == 10
    mock_query_data.assert_called_with(series_obj.api_client, content)


@pytest.mark.parametrize("filters", [[], [{"some": "filter"}]])
@mock.patch("gantry.query.core.dataframe._raw_query_cached_request")
def test_aggregate_query_error(mock_query_data, series_obj_factory_with_filters, filters):
    series_obj = series_obj_factory_with_filters("int", filters=filters)
    mock_query_data.return_value = {"response": "bad", "data": {"query": {"some-attribute": 10}}}

    with pytest.raises(
        GantryException,
        match=r"Aggregation query \[some-attribute\] failed on API with this error: Request failed",
    ):
        _ = series_obj._aggregate_query("some-attribute", {"a": 10})


def test_raw_query_cached_request(api_client_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/aggregate/query".format(ORIGIN),
            json={"response": "ok", "data": "100"},
            match=[matchers.json_params_matcher({"foo": "bar"})],
        )
        assert dataframe._raw_query_cached_request(api_client_obj, '{"foo": "bar"}') == {
            "response": "ok",
            "data": "100",
        }


@pytest.mark.parametrize("op", ["__eq__", "__gt__", "__lt__", "__ge__", "__le__"])
@pytest.mark.parametrize("invalid_filter", [[1, 2, 3], {"foo": "bar"}, object()])
def test_comparator_invalid_filter(invalid_filter, op, series_obj):
    with pytest.raises(TypeError):
        getattr(series_obj, op)(invalid_filter)


@pytest.mark.parametrize("op", ["__eq__", "__gt__", "__lt__", "__ge__", "__le__"])
def test_comparator_invalid_filter_special_case_series(op, series_obj):
    with pytest.raises(TypeError, match=r"Series cannot be compared to each other directly*"):
        getattr(series_obj, op)(series_obj)


@pytest.mark.parametrize(
    ["method", "invalid_dtypes"],
    [
        ("__gt__", ["bool", "str"]),
        ("__ge__", ["bool", "str"]),
        ("__lt__", ["bool", "str"]),
        ("__le__", ["bool", "str"]),
        ("isin", ["bool"]),
        ("contains", ["bool"]),
    ],
)
def test_comparator_invalid_type(method, invalid_dtypes, series_obj_factory):
    for invalid_dtype in invalid_dtypes:
        series_obj = series_obj_factory(invalid_dtype)
        with pytest.raises(ValueError):
            getattr(series_obj, method)(mock.Mock())


@pytest.mark.parametrize(
    ["method", "expected_filter"],
    [
        ("__gt__", "lower_bound"),
        ("__ge__", "inclusive_lower_bound"),
        ("__lt__", "upper_bound"),
        ("__le__", "inclusive_upper_bound"),
    ],
)
def test_valid_sortable_comparators(method, expected_filter, series_obj_factory):
    series_obj = series_obj_factory("int", parent_dataframe=mock.Mock(filters=[]))
    value = 10
    result = getattr(series_obj, method)(value)
    assert [f.filter_ for f in result.filter_objs] == [
        {expected_filter: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


def test_isin(series_obj_factory):
    series_obj = series_obj_factory("str", parent_dataframe=mock.Mock(filters=[]))
    value = ["foo"]
    result = series_obj.isin(value)
    assert [f.filter_ for f in result.filter_objs] == [
        {"category_query": value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


def test_contains(series_obj_factory):
    series_obj = series_obj_factory("str", parent_dataframe=mock.Mock(filters=[]))
    value = "foo"
    result = series_obj.contains(value)
    assert [f.filter_ for f in result.filter_objs] == [
        {"string_query": value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize("invalid_key", [object(), 1.2, 123, "some-value"])
def test_getitem_invalid_key(invalid_key, series_obj):
    with pytest.raises(ValueError):
        series_obj[invalid_key]


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_getitem(get_application_node_id_mock, metadata, series_obj_factory, api_client_obj):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
    )

    series_obj = series_obj_factory("int", df, name="A")

    filters = dataframe.Filters._from_single_filter({"foo": "bar"}, series_obj)

    new_series = series_obj[filters]
    assert new_series.name == "A"


@pytest.mark.parametrize(
    ["type_", "expected"],
    [
        ("bool", "boolean_query"),
        ("str", "string_query"),
        ("uuid", "string_query"),
        ("int", "equals"),
        ("float", "equals"),
    ],
)
def test_eq(type_, expected, series_obj_factory):
    series_obj = series_obj_factory(type_, parent_dataframe=mock.Mock(filters=[]))
    value = 10
    result = series_obj == value
    assert [f.filter_ for f in result.filter_objs] == [
        {expected: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize(
    ["type_", "expected", "other", "value"],
    [
        ("bool", "boolean_query", True, False),
        ("str", "string_query", "str", "^(?!(str)$).*$"),
        ("uuid", "string_query", "str", "^(?!(str)$).*$"),
        ("int", "not_number_query", "not_none", "not_none"),
        ("float", "not_number_query", "not_none", "not_none"),
    ],
)
def test_ne(type_, expected, other, value, series_obj_factory):
    series_obj = series_obj_factory(type_, parent_dataframe=mock.Mock(filters=[]))
    result = series_obj != other
    assert [f.filter_ for f in result.filter_objs] == [
        {expected: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize(
    ["method", "dtype", "query_type", "value"],
    [
        ("__invert__", "bool", "boolean_query", False),
        ("notnull", "any", "null_value", False),
        ("isnull", "any", "null_value", True),
    ],
)
def test_unary(method, dtype, query_type, value, series_obj_factory):
    series_obj = series_obj_factory(dtype, parent_dataframe=mock.Mock(filters=[]))
    result = getattr(series_obj, method)()
    assert [f.filter_ for f in result.filter_objs] == [
        {query_type: value, "feature_name": "series_name"}
    ]
    assert [f.series.parent_dataframe for f in result.filter_objs] == [series_obj.parent_dataframe]


@pytest.mark.parametrize("dtype", ["str", "int", "float", "other"])
def test_invalid__invert__(dtype, series_obj_factory):
    series_obj = series_obj_factory(dtype)
    with pytest.raises(ValueError):
        series_obj.__invert__()


@pytest.mark.parametrize(["method", "other"], [("__eq__", None), ("__ne__", None)])
def test_other_is_none__eq___and__ne__(method, other, series_obj_factory):
    series_obj = series_obj_factory("any")
    with pytest.raises(ValueError):
        getattr(series_obj, method)(other)


@pytest.mark.parametrize("method", ["__eq__", "__ne__"])
def test_cannot_compare_type__eq___and__ne__(method, series_obj_factory):
    series_obj = series_obj_factory("any")
    with pytest.raises(ValueError):
        getattr(series_obj, method)("not_none")


def test_filter_builder(series_obj_factory):
    series_obj = series_obj_factory("int", parent_dataframe=mock.Mock(filters=[{"bar": "baz"}]))
    res = series_obj._filter_builder("foo", "bar")
    assert [f.filter_ for f in res.filter_objs] == [{"feature_name": "series_name", "foo": "bar"}]
    assert [f.series.parent_dataframe for f in res.filter_objs] == [series_obj.parent_dataframe]
    assert series_obj.parent_dataframe.filters == [{"bar": "baz"}]


@pytest.mark.parametrize("n", [1, 5, 10, 11])
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_head(mock_df, mock_data, n, series_obj_factory):
    series_obj = series_obj_factory("int", parent_dataframe=mock.Mock(filters=[]))
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events[:n]
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(series_obj.head(n), mock_df.return_value)


@pytest.mark.parametrize("n", [1, 5, 10, 11])
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_tail(mock_df, mock_data, n, series_obj_factory):
    series_obj = series_obj_factory("int", parent_dataframe=mock.Mock(filters=[]))
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events[-n:]
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(series_obj.tail(n), mock_df.return_value)


@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_fetch(mock_df, mock_data, series_obj_factory):
    series_obj = series_obj_factory("int", parent_dataframe=mock.Mock(filters=[]))
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(series_obj.fetch(), mock_df.return_value)


@mock.patch("gantry.query.core.dataframe.GantrySeries._describe")
def test_describe(mock_series_describe, series_obj_factory):
    series_obj = series_obj_factory(
        "int",
        parent_dataframe=mock.Mock(
            query_info=QueryInfo("123", "foo", "0", "dev", START_TIME, END_TIME)
        ),
    )
    mock_series_describe.return_value = {"foo": "bar"}

    df = pd.DataFrame(
        ["foo", START_TIME, END_TIME, "bar"],
        index=["application", "from", "to", "foo"],
        columns=["series_name"],
    )
    assert_frame_equal(series_obj.describe(), df)


@pytest.mark.parametrize("dtype", ["int", "float"])
@mock.patch("gantry.query.core.dataframe.GantrySeries.__getitem__")
@mock.patch("gantry.query.core.dataframe.GantrySeries.mean")
@mock.patch("gantry.query.core.dataframe.GantrySeries.max")
@mock.patch("gantry.query.core.dataframe.GantrySeries.min")
@mock.patch("gantry.query.core.dataframe.GantrySeries.quantile")
def test_private_describe_number(
    mock_quantile,
    mock_min,
    mock_max,
    mock_mean,
    mock_get_item,
    dtype,
    series_obj_factory,
):
    series_obj = series_obj_factory(dtype, parent_dataframe=mock.Mock(filters=[]))

    mock_quantile.return_value = {0.25: 0.24, 0.5: 0.4, 0.75: 0.7}
    mock_get_item.return_value = series_obj
    mock_min.return_value = 1
    mock_max.return_value = 10
    mock_mean.return_value = 5

    series_obj.count.side_effect = [100, 1000, 10000]

    assert series_obj._describe() == {
        "count": 100,
        "max": 10,
        "mean": 5,
        "min": 1,
        "not null count": 1000,
        "null count": 10000,
        "q25": 0.24,
        "q50": 0.4,
        "q75": 0.7,
        "series type": "prediction",
        "type": dtype,
    }


@mock.patch("gantry.query.core.dataframe.GantrySeries.__getitem__")
def test_private_describe_bool(
    mock_get_item,
    series_obj_factory,
):
    series_obj = series_obj_factory("bool", parent_dataframe=mock.Mock(filters=[]))

    mock_get_item.return_value = series_obj
    series_obj.count.side_effect = [100, 1000, 10000, 50000]

    assert series_obj._describe() == {
        "count": 100,
        "not null count": 1000,
        "null count": 10000,
        "series type": "prediction",
        "type": "bool",
        "True rate": 500,
    }


@mock.patch("gantry.query.core.dataframe.GantrySeries.__getitem__")
def test_private_describe_str(
    mock_get_item,
    series_obj_factory,
):
    series_obj = series_obj_factory("str", parent_dataframe=mock.Mock(filters=[]))

    mock_get_item.return_value = series_obj
    series_obj.count.side_effect = [100, 1000, 10000]

    assert series_obj._describe() == {
        "count": 100,
        "not null count": 1000,
        "null count": 10000,
        "series type": "prediction",
        "type": "str",
    }


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_mix_filtering(get_application_node_id_mock, metadata, series_obj_factory, api_client_obj):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
    )
    s1 = series_obj_factory("int", df, name="A")
    s2 = series_obj_factory("int", df, name="B")

    series = s1[s2 > 20]
    assert series.name == "A"
    assert series.parent_dataframe.filters == [{"feature_name": "B", "lower_bound": 20}]


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_compose_filtering(
    get_application_node_id_mock, metadata, series_obj_factory, api_client_obj
):
    get_application_node_id_mock.return_value = "12345"
    df = dataframe.GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
    )

    s1 = series_obj_factory("int", parent_dataframe=df, name="A")
    s2 = s1[s1 > 20]
    s3 = s2[s2 < 10]

    # < 20 and < 10 filters
    assert s3.parent_dataframe.filters == [
        {"feature_name": "A", "lower_bound": 20},
        {"feature_name": "A", "upper_bound": 10},
    ]
