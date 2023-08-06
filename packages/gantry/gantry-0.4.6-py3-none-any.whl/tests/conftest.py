import json
import logging
import logging.handlers
import os
from pathlib import Path
from queue import Empty
from typing import Dict, List

import pytest
import yaml

from gantry.logger.client import Gantry
from gantry.logger.stores import APILogStore, BaseLogStore
from gantry.serializers import EventEncoder

TIMEOUT = 0.1


class TestingBatchIter:
    def __init__(self, queue, encode=False):
        self.queue = queue
        self.encode = encode

    def __iter__(self):
        return self

    def empty(self):
        return self.queue.empty()

    def __next__(self):
        try:
            if self.encode:
                return [
                    json.dumps(
                        self.queue.get(block=True, timeout=TIMEOUT), cls=EventEncoder
                    ).encode("utf8")
                ]

            return [self.queue.get(block=True, timeout=TIMEOUT)]
        except Empty:
            return []


class EncodedTestingBatchIter(TestingBatchIter):
    def __init__(self, queue):
        super().__init__(queue, True)


class TestingBatchIterWithEmptyFlag(TestingBatchIter):
    def __init__(self, queue, empty=True):
        super().__init__(queue, True)
        self._empty = empty

    def empty(self):
        return self._empty


class TestingBatchConsumer:
    def __init__(self, queue, func):
        self.queue = queue
        self.func = func

        self.running = None

    def pause(self):
        self.running = False

    def start(self):
        self.running = True

    def join(self):
        pass


class FileLogStore(BaseLogStore):
    """This implementation is just for testing purposes"""

    _LOGGER_NS = "gantry.stores.file_logger"
    MAX_FILE_SIZE = 1000000 * 10  # 10MB

    def __init__(self, location: str):
        self._location = Path(location).resolve()
        self._loggers: Dict[str, logging.Logger] = {}

        self._location.mkdir(parents=True, exist_ok=True)

    def _init_logger(self, prefix: str, name: str) -> logging.Logger:
        # TODO: make sure name is a valid file name
        logdir = self._location / prefix
        logdir.mkdir(parents=True, exist_ok=True)

        filepath = logdir / "{}.log".format(name)
        event_logger = logging.getLogger("{}.{}.{}".format(self._LOGGER_NS, prefix, name))
        event_logger.setLevel(logging.INFO)
        # Makes sure event_logger events are not output by the gantry logger
        event_logger.propagate = False
        match_existing_handler = [
            h
            for h in event_logger.handlers
            if (isinstance(h, logging.FileHandler) and h.baseFilename == str(filepath))
        ]
        if not match_existing_handler:
            ch = logging.handlers.RotatingFileHandler(str(filepath), maxBytes=self.MAX_FILE_SIZE)
            formatter = logging.Formatter("%(message)s")
            ch.setFormatter(formatter)
            event_logger.addHandler(ch)
        return event_logger

    def log_batch(self, name: str, events: List[dict], batch_meta: dict = None) -> None:
        for e in events:
            key: str = self._get_key(name, e)
            self._loggers[key].info(json.dumps(e, cls=EventEncoder))

    def _get_key(self, name: str, event: dict) -> str:
        has_feedback = "feedback" in event
        has_predictions = "inputs" in event
        prefix = ""

        if has_feedback and has_predictions:
            prefix = "records"
        elif has_feedback:
            prefix = "feedback"
        elif has_predictions:
            prefix = "predictions"

        key = "{}/{}".format(prefix, name)

        if key not in self._loggers:
            self._loggers[key] = self._init_logger(prefix, name)

        return key


@pytest.fixture(scope="function")
def gantry(tmp_path, ensure_gantry_config):
    import gantry.logger.main as gantry_module

    gantry_module._CLIENT = None

    yield gantry_module

    gantry_module._CLIENT = None


@pytest.fixture(scope="function")
def initialized_gantry(tmp_path, ensure_gantry_config):
    import gantry.logger.main as gantry_module

    gantry_module._CLIENT = None

    log_store = FileLogStore(str(tmp_path))

    gantry_module._CLIENT = Gantry(log_store, environment="test")

    yield gantry_module

    gantry_module._CLIENT = None


@pytest.fixture(scope="function")
def init_gantry_with_api():
    import gantry.logger.main as gantry_module

    gantry_module._CLIENT = None

    log_store = APILogStore(location="http://test-api", send_in_background=False)
    gantry_module._CLIENT = Gantry(log_store, environment="test")

    yield gantry_module

    gantry_module._CLIENT = None


@pytest.fixture(scope="function")
def config_data(tmp_path):
    return {"logs_location": str(tmp_path)}


@pytest.fixture(scope="function")
def ensure_gantry_config(tmp_path):
    """
    ensures that the gantry config file exists in tmp_path, then sets
    the gantry project directory to tmp_path
    """
    from gantry.config import Config

    config_path = tmp_path / Config.CONFIG_FILE_NAME
    if not config_path.is_file():
        with open(config_path, "w") as f:
            f.write(yaml.dump({}))

    os.environ["GANTRY_DIR"] = str(tmp_path)
