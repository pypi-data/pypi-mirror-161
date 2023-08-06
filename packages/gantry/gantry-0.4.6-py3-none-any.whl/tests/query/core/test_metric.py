import mock
import pandas as pd
import pytest
import responses
from responses import matchers

from gantry.query.core.metric import GantryMetric

from ..conftest import END_TIME, ORIGIN, START_TIME, to_tz_time


@pytest.fixture
def gantry_metric_obj(api_client_obj):
    return GantryMetric(api_client_obj)


@pytest.mark.parametrize("data_nodes_size", [0, 3, 5])
def test_metric_query_invalid_data_nodes(data_nodes_size, gantry_metric_obj, series_obj_factory):
    test_data_nodes = [series_obj_factory("str") for _ in range(data_nodes_size)]
    with pytest.raises(ValueError):
        gantry_metric_obj._metric_query(
            data_nodes=test_data_nodes,
            stat="this-is-not-used",
            num_points=1,
        )


@pytest.mark.parametrize("num_points", [-2, -1, 0])
def test_metric_query_invalid_num_points(num_points, gantry_metric_obj, series_obj_factory):
    series_obj_1 = series_obj_factory("str")
    series_obj_2 = series_obj_factory("str")
    with pytest.raises(ValueError):
        gantry_metric_obj._metric_query(
            data_nodes=[series_obj_1, series_obj_2],
            stat="this-is-not-used",
            num_points=num_points,
        )


def test_metric_query(gantry_metric_obj, series_obj_factory_with_filters):
    series_obj_1 = series_obj_factory_with_filters("float", [1, 2, 3])
    series_obj_2 = series_obj_factory_with_filters("bool", [1, 2, 3])
    data = {
        "start_time": to_tz_time(START_TIME),
        "end_time": to_tz_time(END_TIME),
        "num_points": 10,
        "queries": {
            "query_label": {
                "query_type": "data_node_ids",
                "model_node_id": "ABCD1234",
                "stat": "stat",
                "stat_kwargs": {"foo": "bar"},
                "filters": [1, 2, 3],
                "start_time": to_tz_time(START_TIME),
                "end_time": to_tz_time(END_TIME),
                "data_node_ids": ["abc123", "abc123"],
            },
        },
    }
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/time_series/query".format(ORIGIN),
            json={"response": "ok", "data": {"query_label": {"points": 12345}}},
            match=[matchers.json_params_matcher(data)],
        )

        assert (
            gantry_metric_obj._metric_query(
                [series_obj_1, series_obj_2], stat="stat", num_points=10, stat_kwargs={"foo": "bar"}
            )
            == 12345
        )


def test_check_comparable_invalid_series_filters(
    gantry_metric_obj, series_obj_factory, api_client_obj, query_info_obj
):
    parent_dataframe_1 = mock.Mock(api_client=api_client_obj, query_info=query_info_obj)
    parent_dataframe_2 = mock.Mock(api_client=api_client_obj, query_info=query_info_obj)
    parent_dataframe_1.filters = ["some-filter"]
    parent_dataframe_2.filters = ["some-other-filter"]

    series_obj_1 = series_obj_factory("str", parent_dataframe=parent_dataframe_1)
    series_obj_2 = series_obj_factory("str", parent_dataframe=parent_dataframe_2)

    with pytest.raises(ValueError):
        gantry_metric_obj._metric_query(
            data_nodes=[series_obj_1, series_obj_2],
            stat="this-is-not-used",
        )


@pytest.mark.parametrize("dropna", [True, False])
def test_empty_results_returns_empty_df(dropna, gantry_metric_obj):
    df = gantry_metric_obj._prepare_pandas_dataframe(stat="not-used", results=[], dropna=dropna)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_accuracy_score(mock_query, num_points, dropna, gantry_metric_obj, series_obj_factory):
    stat = "accuracy_score"
    series_obj_1 = series_obj_factory("str")
    series_obj_2 = series_obj_factory("str")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.5}]
    result = gantry_metric_obj.accuracy_score(
        series_obj_1, series_obj_2, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (1, 1)
    assert result.columns.tolist() == [stat]
    assert result.index.name == "timestamp"
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.5
    mock_query.assert_called_once_with(
        [series_obj_1, series_obj_2],
        stat,
        num_points=num_points,
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@pytest.mark.parametrize("multioutput", ["uniform_average", "raw_values", None])
@pytest.mark.parametrize("squared", [False, True])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_mean_squared_error(
    mock_query, squared, multioutput, num_points, dropna, gantry_metric_obj, series_obj_factory
):

    stat = "mean_squared_error"
    series_obj_1 = series_obj_factory("float")
    series_obj_2 = series_obj_factory("float")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.99}]
    result = gantry_metric_obj.mean_squared_error(
        series_obj_1,
        series_obj_2,
        multioutput=multioutput,
        squared=squared,
        num_points=num_points,
        dropna=dropna,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.99
    mock_query.assert_called_once_with(
        [series_obj_1, series_obj_2],
        stat,
        num_points=num_points,
        stat_kwargs={"multioutput": multioutput, "squared": squared},
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_confusion_matrix(mock_query, num_points, dropna, gantry_metric_obj, series_obj_factory):
    stat = "confusion_matrix"
    series_obj_1 = series_obj_factory("int")
    series_obj_2 = series_obj_factory("int")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": [[1, 2], [3, 4]]}]
    result = gantry_metric_obj.confusion_matrix(
        series_obj_1, series_obj_2, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == [[1, 2], [3, 4]]
    mock_query.assert_called_once_with(
        [series_obj_1, series_obj_2],
        stat,
        num_points=num_points,
    )


@pytest.mark.parametrize("method", ["precision_score", "recall_score", "f1_score"])
@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_f1_score_precision_score_recall_score(
    mock_query, num_points, dropna, method, gantry_metric_obj, series_obj_factory
):
    stat = method
    average = "micro"
    series_obj_1 = series_obj_factory("int")
    series_obj_2 = series_obj_factory("int")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.5}]
    result = getattr(gantry_metric_obj, method)(
        series_obj_1, series_obj_2, average=average, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (1, 1)
    assert result.columns.tolist() == [stat]
    assert result.index.name == "timestamp"
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.5
    mock_query.assert_called_once_with(
        [series_obj_1, series_obj_2],
        stat,
        num_points=num_points,
        stat_kwargs={"average": average},
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@pytest.mark.parametrize("multioutput", ["uniform_average", "raw_values", None])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_r2_score(
    mock_query, multioutput, num_points, dropna, gantry_metric_obj, series_obj_factory
):

    stat = "r2_score"
    series_obj_1 = series_obj_factory("float")
    series_obj_2 = series_obj_factory("float")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.99}]
    result = gantry_metric_obj.r2_score(
        series_obj_1,
        series_obj_2,
        multioutput=multioutput,
        num_points=num_points,
        dropna=dropna,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.99
    mock_query.assert_called_once_with(
        [series_obj_1, series_obj_2],
        stat,
        num_points=num_points,
        stat_kwargs={"multioutput": multioutput},
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_roc_auc_score(mock_query, num_points, dropna, gantry_metric_obj, series_obj_factory):
    stat = "roc_auc_score"
    series_obj_1 = series_obj_factory("float")
    series_obj_2 = series_obj_factory("bool")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.68}]
    result = gantry_metric_obj.roc_auc_score(
        series_obj_1, series_obj_2, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.68
    mock_query.assert_called_once_with(
        [series_obj_1, series_obj_2],
        stat,
        num_points=num_points,
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@pytest.mark.parametrize(
    "func_name, stat",
    [
        ["percent_null", "percent_null"],
        ["percent_true", "percent_true"],
        ["percent_false", "percent_false"],
    ],
)
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_percent_metric(
    mock_query, func_name, stat, num_points, dropna, gantry_metric_obj, series_obj_factory
):
    series_obj_1 = series_obj_factory("bool")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.2}]
    result = getattr(gantry_metric_obj, func_name)(
        series_obj_1, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.2
    mock_query.assert_called_once_with(
        [series_obj_1],
        stat,
        num_points=num_points,
    )


@pytest.mark.parametrize("func_name", ["percent_true", "percent_false"])
def test_percent_bool_invalid_data_type(func_name, gantry_metric_obj, series_obj_factory):
    test_data_node = series_obj_factory("str")
    with pytest.raises(NotImplementedError):
        getattr(gantry_metric_obj, func_name)(
            data_node=test_data_node,
            stat="this-is-not-used",
            num_points=1,
        )
