import atexit
import json
import logging
import logging.handlers
from queue import Queue
from typing import Callable, Collection, Iterator, List, Optional

from gantry.api_client import APIClient
from gantry.logger.consumer import BatchConsumer
from gantry.query.core.utils import check_response
from gantry.serializers import EventEncoder

logger = logging.getLogger(__name__)


def _batch_iterator_factory(
    collection: Collection, batch_size: int
) -> Callable[[], Iterator[List]]:
    if batch_size <= 0:
        raise ValueError(f"Batch size needs to be a positive int, not {batch_size}")

    def _iterator():
        size = len(collection)
        for ndx in range(0, size, batch_size):
            yield collection[ndx : min(ndx + batch_size, size)]  # noqa: E203

    return _iterator


class BaseLogStore:
    def log(self, application: str, event: dict) -> None:
        """
        Logs a prediction or feedback event.

        Args:
            application: Name of the application
            event: Data to logs as event body
        """
        self.log_batch(application, [event])

    def log_batch(self, application: str, events: List[dict]) -> None:
        pass

    def ping(self) -> bool:
        pass


class APILogStore(BaseLogStore):
    BATCH_SIZE = 20

    def __init__(
        self,
        location: str,
        api_key: Optional[str] = None,
        send_in_background: bool = True,
        bypass_firehose: bool = False,
        consumer_factory=BatchConsumer,
    ):
        """
        Send logged events directly to the Gantry API.
        This is the recommended log store when using the local Gantry stack.

        Args:
            location (str): Gantry API host URI
            api_key (str, Optional): Gantry API Key, retrieved from the dashboard.
            send_in_background (bool, true by default): Whether to send events
                in a background thread.
            bypass_firehose (bool, false by default): Bypass firehose streaming
                and send directly to DB.
            consumer_factory: Used only for testing. Never use parameter in production.
        """
        self._api_client = APIClient(location, api_key=api_key)

        self._bypass_firehose = bypass_firehose

        self.num_consumer_threads: int = 1
        self.send_in_background = send_in_background
        self.queue: Queue = Queue()

        self.consumers = []
        self._consumer_factory = consumer_factory

        if self.send_in_background:
            # On program exit, allow the consumer thread to exit cleanly.
            # This prevents exceptions and a messy shutdown when the
            # interpreter is destroyed before the daemon thread finishes
            # execution.
            atexit.register(self._join)
            for _ in range(self.num_consumer_threads):
                consumer = self._consumer_factory(self.queue, self.consumer_func)
                self.consumers.append(consumer)
                consumer.start()

    def ping(self) -> bool:
        """
        Pings the API to check if it is up and running. Returns True if alive, else False.
        """
        try:
            # Cannot use /healthz/* endpoints as those will be answered by nginx
            # need to use /.
            # See https://linear.app/gantry/issue/ENG-2978/revisit-ping-in-sdk
            response = self._api_client.request("GET", "/api/ping")
            check_response(response)
            return True
        except Exception as e:
            logger.error(f"Error during ping: {e}")
            return False

    def consumer_func(self, batch):
        # Catch all errors and do not raise in order
        # for thread consumer to continue running.
        try:
            return self.send_batch_as_raw_events(batch, as_raw=True)
        except Exception as e:
            logger.error("Internal error sending batches: %s", e)

    def send_batch_as_raw_events(self, batch: List, as_raw: bool = False) -> None:
        if as_raw:
            data = b",".join(batch)
            data = bytes('{"events": [', "utf8") + data + bytes("]}", "utf8")
        else:
            data = json.dumps({"events": batch}, cls=EventEncoder).encode("utf8")

        params = {}
        if self._bypass_firehose:
            params["bypass-firehose"] = "true"

        response = self._api_client.request(
            "POST",
            "/api/v1/ingest/raw",
            data=data,
            params=params,
            headers={"Content-Type": "application/json"},
        )

        if response.get("response") != "ok":
            logger.error("Failed to log events. Response = %s", response)

    def log_batch(self, application: str, events: List[dict]) -> None:
        if not self.send_in_background:
            logger.info("Sending batch synchronously")
            batch_iterator_builder = _batch_iterator_factory(events, APILogStore.BATCH_SIZE)
            for batch in batch_iterator_builder():
                self.send_batch_as_raw_events(batch)
        else:
            for e in events:
                self.queue.put(e)

    def _join(self):
        """
        Ends the consumer thread once the queue is empty.
        Blocks execution until finished
        """
        for consumer in self.consumers:
            consumer.pause()
            try:
                consumer.join()
            except RuntimeError:
                # consumer thread has not started
                pass
