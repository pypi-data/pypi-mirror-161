import functools
import logging
import os
import subprocess
import sys
from typing import Any, List, Union

import pandas as pd

from gantry.exceptions import GantryBatchCreationException, GantryLoggingException
from gantry.logger.stores import APILogStore, BaseLogStore

logger = logging.getLogger(__name__)


def _log_exception(func):
    """Handles all exceptions thrown by func, and logs them to prevent the
    func call from crashing.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GantryLoggingException as le:
            # this is caused by a user error
            # log the error without the stacktrace
            logger.error("Error logging data to Gantry: %s", le)
        except GantryBatchCreationException as e:
            # Blocking exception for batch creation failure
            raise e
        except Exception as e:
            # make sure our logging errors don't cause exceptions in main program
            logger.exception("Internal exception in Gantry client: %s", e)

    return wrapper


def _is_empty(data: Union[List[Any], pd.DataFrame, Any] = None) -> bool:
    """
    Check whether input data is empty or not
    Returns True if data is None or empty, False if data size >= 1
    """
    if isinstance(data, pd.DataFrame):
        return data.empty
    return True if not data else False


def _is_not_empty(data: Union[List[Any], pd.DataFrame, Any] = None) -> bool:
    return not _is_empty(data)


def _batch_fail_msg(batch_id):
    if batch_id:
        logger.info(f"Batch with id: {batch_id} FAILED")


def _check_sample_rate(sample_rate):
    assert sample_rate <= 1 and sample_rate >= 0


def _batch_success_msg(batch_id, application, log_store: Union[APILogStore, BaseLogStore]):
    if batch_id:
        if isinstance(log_store, APILogStore):
            host = log_store._api_client._host
        else:
            host = "[YOUR_GANTRY_DASHBOARD]"

        logger.info("Track your batch at {}/applications/{}/batches".format(host, application))
        logger.info("Look for batch id: {}".format(batch_id))


def progressbar(it, prefix="", count=10, size=60, out=sys.stdout):  # Python3.3+
    def show(j):
        x = int(size * j / count)
        print(
            "{}[{}{}] {}/{}".format(prefix, "#" * x, "." * (size - x), j, count),
            end="\r",
            file=out,
            flush=True,
        )

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    print("\n", flush=True, file=out)


def get_file_linecount(filepath):
    """
    'wc -l' will count the number of \n characters, but if the last line is missing the
    \n then it will miss it. So we add one if the last line is missing \n but is not empty.

    This needs to be a high performance function that works even for larger files.
    - https://stackoverflow.com/questions/845058
    - https://stackoverflow.com/questions/46258499
    """
    with open(filepath, "rb") as f:
        try:  # catch OSError in case of a one line file
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()

    line_count = int(subprocess.check_output(["wc", "-l", filepath]).split()[0])
    if len(last_line) > 0 and not last_line.endswith("\n"):
        line_count += 1
    return line_count
