import mock
import pytest
import responses
from responses import matchers

from gantry.exceptions import GantryException
from gantry.query.core.distance import GantryDistance

from ..conftest import ORIGIN, to_tz_time


@pytest.fixture
def gantry_distance_obj(api_client_obj):
    return GantryDistance(api_client_obj)


def get_query_content(series_obj_1, series_obj_2, diff_stat):
    return {
        "start_time": to_tz_time(series_obj_1.query_info.start_time),
        "end_time": to_tz_time(series_obj_1.query_info.end_time),
        "version": series_obj_1.query_info.version,
        "queries": {
            "query": {
                "query_type": "diff",
                "stat": diff_stat,
                "base": {
                    "query_type": "feature",
                    "feature": series_obj_1.name,
                    "model_node_id": series_obj_1.query_info.application_node_id,
                    "start_time": to_tz_time(series_obj_1.query_info.start_time),
                    "end_time": to_tz_time(series_obj_1.query_info.end_time),
                },
                "other": {
                    "query_type": "feature",
                    "feature": series_obj_2.name,
                    "model_node_id": series_obj_2.query_info.application_node_id,
                    "start_time": to_tz_time(series_obj_2.query_info.start_time),
                    "end_time": to_tz_time(series_obj_2.query_info.end_time),
                },
            }
        },
    }


@pytest.mark.parametrize("diff_stat", ["d1", "dinf", "ks", "kl"])
def test_diff_query(gantry_distance_obj, series_obj_1, series_obj_2, diff_stat):
    content = get_query_content(series_obj_1, series_obj_2, diff_stat)

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/aggregate/query".format(ORIGIN),
            match=[matchers.json_params_matcher(content)],
            json={"response": "ok", "data": {"query": {diff_stat: 1500}}},
        )

        assert gantry_distance_obj._diff_query(series_obj_1, series_obj_2, diff_stat) == 1500


@pytest.mark.parametrize("diff_stat", ["d1", "dinf", "ks", "kl"])
def test_diff_query_invalid_api_response(
    gantry_distance_obj, series_obj_1, series_obj_2, diff_stat
):
    content = get_query_content(series_obj_1, series_obj_2, diff_stat)

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/aggregate/query".format(ORIGIN),
            match=[matchers.json_params_matcher(content)],
            json={"response": "ok", "data": {"query": {diff_stat + "wrong_key": 1500}}},
        )

        with pytest.raises(RuntimeError):
            gantry_distance_obj._diff_query(series_obj_1, series_obj_2, diff_stat)


@pytest.mark.parametrize("diff_stat", ["d1", "dinf", "ks", "kl"])
def test_diff_query_error(gantry_distance_obj, series_obj_1, series_obj_2, diff_stat):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/aggregate/query".format(ORIGIN),
            json={
                "response": "not_ok",
            },
        )

        with pytest.raises(GantryException):
            gantry_distance_obj._diff_query(series_obj_1, series_obj_2, diff_stat)


@mock.patch("gantry.query.core.distance.GantryDistance._diff_query")
def test_d1(mock_query, gantry_distance_obj, series_obj_1, series_obj_2):
    mock_query.return_value = 0.05
    assert gantry_distance_obj.d1(series_obj_1, series_obj_2) == 0.05
    mock_query.assert_called_once_with(series_obj_1, series_obj_2, "d1")


@mock.patch("gantry.query.core.distance.GantryDistance._diff_query")
def test_dinf(mock_query, gantry_distance_obj, series_obj_1, series_obj_2):
    mock_query.return_value = 0.45
    assert gantry_distance_obj.dinf(series_obj_1, series_obj_2) == 0.45
    mock_query.assert_called_once_with(series_obj_1, series_obj_2, "dinf")


@mock.patch("gantry.query.core.distance.GantryDistance._diff_query")
def test_ks(mock_query, gantry_distance_obj, series_obj_1, series_obj_2):
    mock_query.return_value = 1e-4
    assert gantry_distance_obj.ks(series_obj_1, series_obj_2) == 1e-4
    mock_query.assert_called_once_with(series_obj_1, series_obj_2, "ks")


@mock.patch("gantry.query.core.distance.GantryDistance._diff_query")
def test_kl(mock_query, gantry_distance_obj, series_obj_1, series_obj_2):
    mock_query.return_value = 100
    assert gantry_distance_obj.kl(series_obj_1, series_obj_2) == 100
    mock_query.assert_called_once_with(series_obj_1, series_obj_2, "kl")
