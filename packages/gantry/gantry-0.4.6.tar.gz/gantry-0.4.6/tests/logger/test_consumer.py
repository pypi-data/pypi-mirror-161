from queue import Queue

import pytest

from gantry.logger import consumer

from ..conftest import TestingBatchIter, TestingBatchIterWithEmptyFlag


@pytest.fixture(scope="function")
def q():
    return Queue()


@pytest.fixture(scope="function")
def batch_consumer_factory(q):
    def wrapper(f):
        return consumer.BatchConsumer(queue=q, func=f, batch_iter=TestingBatchIter)

    return wrapper


def test_batch_iter_builder_size_limit(q):
    """Check that batch iterator caches elements
    until reaching batch_size_record_limit. Then
    returns cache in next consumed batch.
    """
    batch_iter = consumer._BatchIterBuilder(
        queue=q,
        batch_size_record_limit=50,
        single_event_limit_bytes=1000,
        batch_size_limit_bytes=1000,
        timeout_secs=0.1,
    )

    for i in range(100):
        q.put(i)

    it = iter(batch_iter)

    # First 50 items are empty until batch size gets to 50
    for i in range(50):
        assert next(it) == []

    # Batch with [b'0', b'1', ..., b'49']
    assert next(it) == [str(x).encode() for x in range(50)]

    for i in range(49):
        assert next(it) == []

    # Batch with [b'50', b'51', ..., b'99']
    assert next(it) == [str(x).encode() for x in range(50, 100)]

    # No more items in queue
    assert q.empty()


def test_batch_iter_builder_single_event_limit(q):
    """Check that batch iterator drops big events."""
    batch_iter = consumer._BatchIterBuilder(
        queue=q,
        batch_size_record_limit=1,
        single_event_limit_bytes=3,
        batch_size_limit_bytes=1000,
        timeout_secs=0.1,
    )

    q.put("1")
    q.put("333")  # This item will be ignored
    q.put("1")

    it = iter(batch_iter)

    assert next(it) == []
    assert next(it) == []
    assert next(it) == [b'"1"']
    assert next(it) == [b'"1"']

    # No more items in queue
    assert q.empty()


def test_batch_iter_builder_batch_size_limit_bytes(q):
    """Check that batch iterator flushed when cache gets big"""
    batch_iter = consumer._BatchIterBuilder(
        queue=q,
        batch_size_record_limit=100,
        single_event_limit_bytes=100,
        batch_size_limit_bytes=10,
        timeout_secs=0.1,
    )

    q.put("11")
    q.put("22")
    q.put("11")

    it = iter(batch_iter)

    assert next(it) == []
    assert next(it) == []
    assert next(it) == [b'"11"', b'"22"']
    assert next(it) == [b'"11"']

    # No more items in queue
    assert q.empty()


def test_batch_iter_builder_timeout(q):
    """Check that batch iterator timeouts while consuming on an empty queue"""
    batch_iter = consumer._BatchIterBuilder(
        queue=q,
        batch_size_record_limit=100,
        single_event_limit_bytes=100,
        batch_size_limit_bytes=10,
        timeout_secs=0.01,
    )

    it = iter(batch_iter)

    assert next(it) == []
    assert next(it) == []

    # No more items in queue
    assert q.empty()


def test_batch_iter_empty(q):
    """Batch iterator is empty if the queue
    is empty and there are no events in the cache
    """
    batch_iter = consumer._BatchIterBuilder(
        queue=q,
        batch_size_record_limit=100,
        single_event_limit_bytes=100,
        batch_size_limit_bytes=10,
        timeout_secs=0.1,
    )

    assert batch_iter.empty()

    q.put("1")
    assert not batch_iter.empty()

    it = iter(batch_iter)

    assert next(it) == []
    assert not batch_iter.empty()

    assert next(it) == [b'"1"']
    assert batch_iter.empty()


def test_batch_consumer_consume(batch_consumer_factory, q):
    """Check that the consume method uses the provided function"""
    batch = []

    def func(event):
        batch.append(event)

    for i in range(100):
        q.put(i)

    batch_consumer = batch_consumer_factory(func)
    batch_iter = iter(batch_consumer._batch_iter(q))

    for i in range(100):
        batch_consumer.consume(batch_iter)

    assert batch == [[x] for x in range(100)]


def test_batch_consumer_pause(batch_consumer_factory, q):
    batch_consumer = batch_consumer_factory(None)
    assert batch_consumer.running

    batch_consumer.pause()

    assert not batch_consumer.running


def test_batch_consumer_run(batch_consumer_factory, q):
    """Consumer 'run' method should stop executing
    after consumer is paused and the iterator reports
    emptyness.
    """
    batch_iter = TestingBatchIterWithEmptyFlag(q)
    batch_iter._empty = False

    q.put("1")
    q.put("2")
    q.put("3")

    q.put("4")
    q.put("5")

    batches = []

    def func(event):
        batches.append(event)
        # After consuming '1', '2', '3'
        # the batch iterator will report
        # it is empty, so '4' and '5'
        # won't be consumed.
        if len(batches) == 3:
            batch_iter._empty = True

    def batch_iter_factory(q):
        return batch_iter

    batch_consumer = consumer.BatchConsumer(queue=q, func=func, batch_iter=batch_iter_factory)
    batch_consumer.pause()
    batch_consumer.run()

    assert not batch_consumer.running
    assert batches == [[b'"1"'], [b'"2"'], [b'"3"']]
