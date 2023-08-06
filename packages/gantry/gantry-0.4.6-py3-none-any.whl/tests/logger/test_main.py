import mock
import pytest

import gantry
from gantry.exceptions import ClientNotInitialized
from gantry.logger import main


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("ping", {}),
        ("instrument", {}),
        ("log_feedback", {}),
        ("log_feedback_event", {}),
        ("log_predictions", {}),
        ("log_prediction_event", {}),
        ("log_record", {"application": "foobar", "version": "1.2.3"}),
        ("log_records", {"application": "foobar", "version": "1.2.3"}),
    ],
)
@pytest.mark.parametrize("module", [main, gantry])
def test_uninit_client_main(module, method, params):
    with mock.patch("gantry.logger.main._CLIENT", None):
        with pytest.raises(ClientNotInitialized):
            getattr(module, method)(**params)


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("ping", {}),
        ("instrument", {}),
        ("log_feedback", {}),
        ("log_feedback_event", {}),
        ("log_predictions", {}),
        ("log_prediction_event", {}),
        (
            "log_records",
            {
                "application": "foobar",
                "version": "1.2.3",
                "inputs": [1, 2, 3],
                "outputs": [4, 5, 6],
                "feedback_keys": ["A"],
                "feedback_ids": [10],
                "feedbacks": [4, 5, 6],
                "ignore_inputs": ["A"],
                "timestamps": "today",
                "reference_name": "barbaz",
                "sort_on_timestamp": True,
                "sample_rate": 1.0,
                "as_batch": False,
            },
        ),
        (
            "log_record",
            {
                "application": "foobar",
                "version": "1.2.3",
                "inputs": [1, 2, 3],
                "outputs": [4, 5, 6],
                "feedback_keys": ["A"],
                "feedback_id": [10],
                "feedback": [4, 5, 6],
                "ignore_inputs": ["A"],
                "timestamp": "today",
                "sample_rate": 1.0,
            },
        ),
    ],
)
@pytest.mark.parametrize("module", [main, gantry])
def test_logger_methods(module, method, params):
    m = mock.Mock()
    with mock.patch("gantry.logger.main._CLIENT", m):
        getattr(module, method)(**params)
        getattr(m, method).assert_called_once_with(**params)
