import mock
import pytest

from gantry.query.client import GantryQuery
from gantry.query.metric import main


@pytest.mark.parametrize(
    ["method", "params"],
    [
        (
            "accuracy_score",
            {"outputs": mock.Mock(), "feedback": mock.Mock(), "dropna": True, "num_points": 1},
        ),
        (
            "mean_squared_error",
            {
                "outputs": mock.Mock(),
                "feedback": mock.Mock(),
                "dropna": True,
                "num_points": 1,
                "multioutput": "uniform_average",
                "squared": True,
            },
        ),
        (
            "confusion_matrix",
            {"outputs": mock.Mock(), "feedback": mock.Mock(), "dropna": True, "num_points": 1},
        ),
        (
            "f1_score",
            {
                "outputs": mock.Mock(),
                "feedback": mock.Mock(),
                "dropna": True,
                "num_points": 1,
                "average": "micro",
            },
        ),
        (
            "r2_score",
            {
                "outputs": mock.Mock(),
                "feedback": mock.Mock(),
                "dropna": True,
                "num_points": 1,
                "multioutput": "uniform_average",
            },
        ),
        (
            "precision_score",
            {
                "outputs": mock.Mock(),
                "feedback": mock.Mock(),
                "dropna": True,
                "num_points": 1,
                "average": "micro",
            },
        ),
        (
            "recall_score",
            {
                "outputs": mock.Mock(),
                "feedback": mock.Mock(),
                "dropna": True,
                "num_points": 1,
                "average": "micro",
            },
        ),
        (
            "roc_auc_score",
            {"outputs": mock.Mock(), "feedback": mock.Mock(), "dropna": True, "num_points": 1},
        ),
        (
            "percent_null",
            {"data_node": mock.Mock(), "dropna": True, "num_points": 1},
        ),
        (
            "percent_true",
            {"data_node": mock.Mock(), "dropna": True, "num_points": 1},
        ),
        (
            "percent_false",
            {"data_node": mock.Mock(), "dropna": True, "num_points": 1},
        ),
    ],
)
@mock.patch("gantry.query.main.globals._Query", spec=GantryQuery)
def test_proxy_methods(mock_query, method, params):
    mock_query.metric = mock.Mock()
    getattr(mock_query.metric, method).return_value = "foo"
    assert getattr(main, method)(**params) == "foo"
    getattr(mock_query.metric, method).assert_called_once_with(**params)
