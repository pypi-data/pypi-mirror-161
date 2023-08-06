import datetime
import json
import logging
import uuid

import dateutil.parser
import pytest
from mock import MagicMock, patch

from gantry.exceptions import ClientNotInitialized
from gantry.logger.client import Gantry
from gantry.utils import compute_feedback_id


def test_global_client():
    log_store = MagicMock()
    gantry = Gantry(log_store=log_store, environment="test")

    @gantry.instrument("simple_test")
    def test(input1: int, input2: str) -> dict:
        return {"output1": 1, "output2": "2"}

    log_store.log.assert_not_called()

    fixed_uuid = uuid.uuid4()
    with patch("uuid.uuid4", return_value=fixed_uuid):
        test(1, "2")

    log_store.log.assert_called_once()

    call_args = log_store.log.call_args[0]

    assert call_args[0] == "simple_test"
    assert call_args[1]["event_id"] == fixed_uuid
    assert call_args[1]["inputs"] == {"input1": 1, "input2": "2"}
    assert call_args[1]["outputs"] == {"output1": 1, "output2": "2"}
    assert call_args[1]["metadata"]["func_name"] == "simple_test"
    assert call_args[1]["metadata"]["version"] is None


def test_global_client_not_init(gantry):
    with pytest.raises(ClientNotInitialized):

        @gantry.instrument("simple_test")
        def test(input1: int, input2: str) -> dict:
            return dict(input1=input1, input2=input2)


def test_client_sampling():
    log_store = MagicMock()
    gantry = Gantry(log_store=log_store, environment="test")

    @gantry.instrument("simple_test", sample_rate=0.3)
    def test(input1: int, input2: str) -> dict:
        return {"output1": 1, "output2": "2"}

    with patch("random.random", return_value=0.4):
        test(1, "2")

    log_store.log.assert_not_called()

    with patch("random.random", return_value=0.2):
        test(1, "2")

    log_store.log.assert_called_once()


def test_client_exception_continue(gantry, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")

    log_store = MagicMock()
    log_store.log.side_effect = Exception("Bad thing happened.")

    gantry = Gantry(log_store=log_store, environment="test")

    test_ret_val = {"output1": 1, "output2": "2"}

    @gantry.instrument("simple_test")
    def test(input1: int, input2: str) -> dict:
        return test_ret_val

    ret_val = test(1, "2")

    assert ret_val == test_ret_val
    assert "Internal exception in Gantry client" in caplog.text


def test_client_log_feedback_event(tmp_path, initialized_gantry):
    initialized_gantry.log_feedback_event("test_name", {"test_id": 1}, {"label": True})
    log_path = tmp_path / "feedback" / "test_name.log"
    assert log_path.exists()

    with log_path.open() as f:
        for i, line in enumerate(f):
            logged_feedback = json.loads(line)
            assert i == 0  # There is only 1 event.
            assert logged_feedback["feedback"]["label"]


def test_client_log_feedback(tmp_path, initialized_gantry):
    ids = [{"test_id": i} for i in range(20)]
    feedbacks = [{"label": i} for i in range(20)]
    initialized_gantry.log_feedback("test_name", ids, feedbacks, as_batch=False)

    log_path = tmp_path / "feedback" / "test_name.log"
    assert log_path.exists()

    with log_path.open() as f:
        for i, line in enumerate(f):
            logged_feedback = json.loads(line)
            assert i < 20  # There should only be 20 events.
            assert i == logged_feedback["feedback"]["label"]


def test_client_log_prediction_event(tmp_path, initialized_gantry):
    inputs = {"input1": 1, "input2": 2}
    outputs = 0
    initialized_gantry.log_prediction_event("simple_test", inputs, outputs)

    log_path = tmp_path / "predictions" / "simple_test.log"
    assert log_path.exists()

    with log_path.open() as f:
        for i, line in enumerate(f):
            logged_ev = json.loads(line)
            assert i == 0  # There is only 1 event
            assert logged_ev["log_timestamp"] == logged_ev["timestamp"]


def test_client_log_prediction_custom_timestamp(tmp_path, initialized_gantry):
    inputs = {"input1": 1, "input2": 2}
    outputs = 0

    custom_timestamp = datetime.datetime(year=2020, month=1, day=1)
    initialized_gantry.log_prediction_event(
        "simple_test", inputs, outputs, timestamp=custom_timestamp
    )

    log_path = tmp_path / "predictions" / "simple_test.log"
    assert log_path.exists()

    with log_path.open() as f:
        for i, line in enumerate(f):
            logged_ev = json.loads(line)
            assert i == 0  # Only 1 event
            assert logged_ev["timestamp"] == custom_timestamp.isoformat()
            diff = datetime.datetime.utcnow() - dateutil.parser.isoparse(logged_ev["log_timestamp"])
            assert diff < datetime.timedelta(minutes=1)  # log timestamp is recent


def test_client_log_prediction_feedback_id(tmp_path, initialized_gantry, caplog):
    inputs = {"input1": 1, "input2": 2}
    outputs = 0

    initialized_gantry.log_prediction_event(
        "simple_test", inputs, outputs, feedback_id={"id": "123"}
    )

    log_path = tmp_path / "predictions" / "simple_test.log"
    assert log_path.exists()

    with log_path.open() as f:
        for i, line in enumerate(f):
            logged_ev = json.loads(line)
            assert i == 0  # Only 1 event
            assert logged_ev["feedback_id"] == compute_feedback_id({"id": "123"})

    initialized_gantry.log_prediction_event(
        "simple_test", inputs, outputs, feedback_id={"id": "123"}, feedback_keys=["id"]
    )
    assert "Cannot specify feedback_id and feedback_keys at same time." in caplog.text


def test_client_log_predictions(tmp_path, initialized_gantry):
    _test_client_log_predictions_helper(initialized_gantry, tmp_path, False)


def test_client_log_predictions_sort_inputs(tmp_path, initialized_gantry):
    _test_client_log_predictions_helper(initialized_gantry, tmp_path, True)


def _test_client_log_predictions_helper(gantry, temp_file_path, sort_inputs):
    inputs = [{"input1": i, "input2": 2} for i in range(20)]
    outputs = [i % 2 for i in range(20)]

    gantry.log_predictions(
        "simple_test", inputs, outputs, sort_on_timestamp=sort_inputs, as_batch=False
    )

    log_path = temp_file_path / "predictions" / "simple_test.log"
    assert log_path.exists()

    with log_path.open() as f:
        for i, line in enumerate(f):
            logged_ev = json.loads(line)
            assert i < 20  # Max of 20 events
            assert logged_ev["inputs"]["input1"] == i
            assert logged_ev["outputs"] == i % 2
            assert logged_ev["metadata"]["func_name"] == "simple_test"
