import json
import random
import uuid

import mock
import pytest
import responses
from mock import patch
from responses import matchers

from gantry.logger.consumer import BatchConsumer
from gantry.logger.stores import APILogStore, _batch_iterator_factory
from gantry.serializers import EventEncoder

from ..conftest import EncodedTestingBatchIter, TestingBatchConsumer

TEST_HOST = "http://test-api"


@pytest.mark.parametrize(
    ["collection", "batch_size", "expected"],
    [
        (list(range(0, 11)), 3, [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10]]),
        (list(range(0, 11)), 2, [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10]]),
        (list(range(0, 11)), 9, [[0, 1, 2, 3, 4, 5, 6, 7, 8], [9, 10]]),
        (list(range(0, 11)), 1, [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10]]),
        (list(range(0, 11)), 100, [list(range(0, 11))]),
        ([1], 100, [[1]]),
        ([1], 1, [[1]]),
    ],
)
def test_batch_factory(collection, batch_size, expected):
    assert list(_batch_iterator_factory(collection, batch_size)()) == expected


@pytest.mark.parametrize("batch_size", [0, -1, -5])
def test_batch_factory_error(batch_size):
    with pytest.raises(ValueError):
        _ = _batch_iterator_factory([1, 2, 3], batch_size)


@pytest.mark.parametrize("status_code", [200, 400, 404, 500])
def test_ping_fail(status_code):
    store = APILogStore(TEST_HOST)
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, f"{TEST_HOST}/api/ping", status=status_code)
        assert store.ping() is False


@pytest.mark.parametrize("status_code", [200])
def test_ping_success(status_code):
    store = APILogStore(TEST_HOST)
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"{TEST_HOST}/api/ping",
            status=status_code,
            json={"response": "ok"},
        )
        assert store.ping() is True


@pytest.mark.parametrize(
    ["data", "as_raw"], [(["foo", "bar", "baz"], False), ([b'"foo"', b'"bar"', b'"baz"'], True)]
)
def test_send_batch_as_raw_events(data, as_raw):
    store = APILogStore(TEST_HOST)

    content = {"events": ["foo", "bar", "baz"]}

    with responses.RequestsMock() as resp:
        resp.add(
            resp.POST,
            "{}/api/v1/ingest/raw".format(TEST_HOST),
            json={"response": "ok"},
            headers={"Content-Type": "application/json"},
            match=[matchers.json_params_matcher(content)],
        )

        store.send_batch_as_raw_events(data, as_raw=as_raw)


@pytest.mark.parametrize("send_in_background", [False, True])
def test_api_log_store(send_in_background):
    with patch("gantry.logger.stores.APIClient") as mock_client:
        instance = mock_client.return_value
        instance.request.return_value = {"response": "ok"}

        consumer_factory = lambda q, f: BatchConsumer(  # noqa
            queue=q, func=f, batch_iter=EncodedTestingBatchIter
        )

        store = APILogStore(
            TEST_HOST, send_in_background=send_in_background, consumer_factory=consumer_factory
        )

        events = []
        for i in range(10):
            ev = {
                "event_id": uuid.uuid4(),
                "data": {
                    "a": random.randint(0, 100),
                    "b": "2",
                },
            }
            events.append(ev)
            store.log("simple_test", ev)

        store._join()

        num_events_sent = 0
        for i, call_args in enumerate(instance.request.call_args_list):
            assert call_args.args[0] == "POST"
            assert call_args.args[1] == "/api/v1/ingest/raw"
            assert call_args.kwargs["data"] == json.dumps(
                {"events": [events[i]]}, cls=EventEncoder
            ).encode("utf8")

            req_data = json.loads(call_args.kwargs["data"])
            num_events_sent += len(req_data["events"])

        assert num_events_sent == 10


@pytest.mark.parametrize("send_in_background", [False, True])
def test_api_log_store_batch(send_in_background):
    with patch("gantry.logger.stores.APIClient") as mock_client:
        instance = mock_client.return_value
        instance.request.return_value = {"response": "ok"}

        consumer_factory = lambda q, f: BatchConsumer(  # noqa
            queue=q, func=f, batch_iter=EncodedTestingBatchIter
        )

        store = APILogStore(
            TEST_HOST, send_in_background=send_in_background, consumer_factory=consumer_factory
        )

        events = []
        for i in range(10):
            ev = {
                "event_id": uuid.uuid4(),
                "data": {
                    "a": random.randint(0, 100),
                    "b": "2",
                },
            }
            events.append(ev)

        store.log_batch("application", events)
        store._join()

        store._join()

        num_events = 0

        if send_in_background:
            for i, call_args in enumerate(instance.request.call_args_list):
                assert call_args.args[0] == "POST"
                assert call_args.args[1] == "/api/v1/ingest/raw"
                assert call_args.kwargs["data"] == json.dumps(
                    {"events": [events[i]]}, cls=EventEncoder
                ).encode("utf8")
                num_events += 1

            assert num_events == 10

        else:
            assert len(instance.request.call_args_list) == 1
            call_args = instance.request.call_args_list[0]
            assert call_args.args[0] == "POST"
            assert call_args.args[1] == "/api/v1/ingest/raw"
            assert call_args.kwargs["data"] == json.dumps(
                {"events": events}, cls=EventEncoder
            ).encode("utf8")


@mock.patch("gantry.logger.stores.APILogStore.send_batch_as_raw_events")
def test_consumer_func(mock_send):
    mock_send.side_effect = RuntimeError()
    consumer_factory = lambda q, f: mock.Mock()  # noqa
    batch = mock.Mock()

    store = APILogStore(TEST_HOST, consumer_factory=consumer_factory)

    # This should not raise an exception
    store.consumer_func(batch)

    mock_send.assert_called_once_with(batch, as_raw=True)


def test_consumer_creation_for_background_store():
    store = APILogStore(TEST_HOST, send_in_background=True, consumer_factory=TestingBatchConsumer)

    assert len(store.consumers) == 1
    assert store.consumers[0].func == store.consumer_func
