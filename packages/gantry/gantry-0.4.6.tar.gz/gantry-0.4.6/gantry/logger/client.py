import datetime
import functools
import inspect
import logging
import math
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, no_type_check
from warnings import warn

import colorama
import pandas as pd
import requests
from typeguard import typechecked

from gantry.config import Config
from gantry.exceptions import (
    GantryBatchCreationException,
    GantryException,
    GantryLoggingException,
)
from gantry.logger.constants import CHUNK_SIZE, BatchTypes, Delimiter, UploadFileType
from gantry.logger.event_builder import (
    _build_batch_meta,
    _build_feedback_event,
    _build_prediction_and_feedback_events,
    _build_prediction_event,
    _build_prediction_events,
    _create_timestamp_idx,
    _enrich_events_with_batch_id,
)
from gantry.logger.stores import APILogStore
from gantry.logger.utils import (
    _batch_fail_msg,
    _batch_success_msg,
    _check_sample_rate,
    _is_empty,
    _is_not_empty,
    _log_exception,
    get_file_linecount,
    progressbar,
)
from gantry.query.core.utils import check_response
from gantry.serializers import serializable_value
from gantry.utils import format_msg_with_color

logger = logging.getLogger(__name__)


class Gantry:
    def __init__(
        self,
        log_store: APILogStore,
        environment: str,
        logging_level: str = "INFO",
    ):
        """
        Initializes a new Gantry client to log predictions and feedback.
        Full list of arguments is defined by :class:`gantry.config.ConfigSchema`.

        Args:
            logs_store (BaseLogStore): The log store to use.
            environment (optional, str): Set the value for the environment label attached to data
                instrumented by this client.
            logging_level (options: str): Configure logging level for Gantry system.
        """
        self.context = {"environment": environment}
        self.log_store = log_store
        self.environment = environment
        self.setup_logger(level=logging_level)

    @no_type_check
    @classmethod
    def from_config(cls, config: Config):
        env = config.get("environment")
        logging_level = config.get("logging_level", "INFO")

        logs_location = config.get("logs_location") or ""
        log_location_msg = None

        # TODO: use urlparse to grab the scheme instead
        if not (logs_location.startswith("http://") or logs_location.startswith("https://")):
            logger.error("Currently only HTTP logs location supported")
            raise ValueError(
                "logger was not initialized with http endpoint. "
                "Only HTTP logs locations supported."
            )

        api_key = config.get("api_key")
        bypass_firehose = config.get("bypass_firehose", False)
        send_in_background = config.get("send_in_background", True)

        log_store = APILogStore(
            logs_location,
            api_key=api_key,
            bypass_firehose=bypass_firehose,
            send_in_background=send_in_background,
        )
        log_location_msg = "Using API for logging at URI %s"

        # Case when `logs_location=None`, we already output warning in red with special message,
        # so we don't want to output another warning
        log_location_formatted_msg = format_msg_with_color(
            log_location_msg, colorama.Fore.BLUE, logger
        )
        logger.warning(log_location_formatted_msg, logs_location)

        return cls(log_store, env, logging_level)

    def instrument(
        self,
        application: str,
        version: Optional[int] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        sample_rate: float = 1.0,
    ):
        """
        Function decorator to be used on an inference function that should be instrumented
        by Gantry.

        Example:

        .. code-block:: python

           import gantry

           gantry.init(...)

           @gantry.instrument("loan_pred", feedback_keys=['loan_id'], ignore_inputs=['loan_id'])
           def _predict(
               loan_id: str,  # id of loan, important metadata but not used in predicting
               college_degree: bool,  # if applicant has college degree
               loan_amount: float,  # in $1,000s
           ):
               ...

        Args:
            application (str): Application name. Gantry validates and monitors data by function.
            version (optional, int): Version of the function schema to use for validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
            feedback_keys (optional, list): A list of names of input features to use for feedback
                lookup. When you later provide a feedback event or label for performance metric
                calculation, you will provide the values of the features in this list for
                Gantry to look up the corresponding prediction.
            ignore_inputs (optional, list): A list of names of input features that should not be
                monitored.
            sample_rate (optional, float): Set a sampling rate to control the fraction of events
                logged by Gantry. E.g. if sample_rate is 0.3, only 30% of events are logged.
        """

        def outer(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                outputs = func(*args, **kwargs)

                if random.random() > sample_rate:
                    return outputs

                try:
                    bound_args = inspect.signature(func).bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    raw_inputs = dict(bound_args.arguments)

                    ev = _build_prediction_event(
                        self.context,
                        self.environment,
                        raw_inputs,
                        outputs,
                        application,
                        version,
                        feedback_keys,
                        ignore_inputs,
                    )
                    self.log_store.log(application, ev)
                except GantryLoggingException as le:
                    # this is caused by a user error
                    # log the error without the stacktrace
                    logger.error("Error logging data to Gantry: %s", le)
                except Exception as e:
                    # make sure our logging errors don't cause exceptions in main program
                    logger.exception("Internal exception in Gantry client: %s", e)

                return outputs

            return wrapper

        return outer

    @_log_exception
    @typechecked
    def log_file(
        self,
        application: str,
        filepath: str,
        version: Optional[Union[int, str]] = None,
        timestamp: Optional[str] = None,
        inputs: List[str] = [],
        outputs: List[str] = [],
        feedbacks: List[str] = [],
        metadata: List[str] = [],
        feedback_id: List[str] = [],
        feedback_keys: Optional[List[str]] = None,
    ):
        # Get info for tracking batch during processing.
        num_events = get_file_linecount(filepath) - 1  # Subtract the header line.
        logger.info(f"Processing {num_events} lines.")

        # Read the headers of the file, infer and build linking datastruct.
        gantry_data_link: Dict[str, Any] = {
            "file_type": UploadFileType.CSV_WITH_HEADERS.value,
            "num_events": num_events,
            "application": application,
            "version": version,
            "log_timestamp": datetime.datetime.utcnow().isoformat(),
            "timestamp": dict(),
            "inputs": dict(),
            "outputs": dict(),
            "feedback": dict(),
            "tags": {
                "env": {"val": self.environment}
            },  # This makes env.val exactly passed in rather than reference to a file column.
            "feedback_id": dict(),
            "feedback_keys": list(),
        }
        with open(filepath, "r") as f_in:
            headers_line = f_in.readline().split(Delimiter.COMMA.value)
        for col_index, raw_header in enumerate(headers_line):
            header = raw_header.strip()
            if header == timestamp or (not timestamp and header.startswith("timestamp")):
                gantry_data_link["timestamp"][header] = {"ref": col_index}
            elif header in outputs or header.startswith("output"):
                gantry_data_link["outputs"][header] = {"ref": col_index}
            elif header in feedbacks or header.startswith("feedback"):
                gantry_data_link["feedback"][header] = {"ref": col_index}
            elif header in metadata or header.startswith("metadata"):
                gantry_data_link["tags"][header] = {"ref": col_index}
            elif len(inputs) == 0 or header in inputs or header.startswith("input"):
                gantry_data_link["inputs"][header] = {"ref": col_index}

            if header in feedback_id or header == "feedback_id":
                gantry_data_link["feedback_id"][header] = {"ref": col_index}
            elif feedback_keys is not None and header in feedback_keys:
                gantry_data_link["feedback_keys"].append(header)
        if not gantry_data_link["tags"].get("env"):
            raise GantryLoggingException(
                "Please initialize gantry logger with 'environment' or specify an 'env' tag."
            )

        # Calculate part counts and generate presigned s3 urls.
        path = Path(filepath)
        object_size = os.path.getsize(filepath)  # in bytes
        total_num_parts = math.ceil(object_size / CHUNK_SIZE)

        logger.info("Initializing upload to Gantry")
        preupload_res = self.log_store._api_client.request(
            "GET",
            "/api/v1/ingest/file-preupload",
            params={"filename": path.name, "num_parts": total_num_parts},
        )
        signed_urls = preupload_res["upload_urls"]
        upload_id = preupload_res["upload_id"]
        file_key = preupload_res["key"]

        # Upload the parts.
        parts = []
        with open(filepath, "r") as f_in:
            block_read = functools.partial(f_in.read, CHUNK_SIZE)
            block_iterator = iter(block_read, "")
            part_num = 1  # AWS S3 needs part num to start with 1.
            for block in progressbar(
                block_iterator, prefix="Uploading to Gantry Bucket: ", count=total_num_parts
            ):
                # TODO: parallelize this client side?
                response = requests.put(signed_urls[part_num - 1], data=block)
                etag = str(response.headers["ETag"])
                parts.append({"ETag": etag, "PartNumber": part_num})
                part_num += 1

        logger.info("Starting Gantry Ingestion")
        # Submit file completion to gantry API.
        complete_res = self.log_store._api_client.request(
            "POST",
            "/api/v1/ingest/file",
            json={
                "upload_id": upload_id,
                "key": file_key,
                "parts": parts,
                "data_link": gantry_data_link,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        batch_id = complete_res["batch_id"]
        _batch_success_msg(batch_id, application, self.log_store)

    @_log_exception
    @typechecked
    def log_records(
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[Union[List[dict], pd.DataFrame]] = None,
        outputs: Optional[Union[List[dict], pd.DataFrame]] = None,
        feedback_keys: Optional[List[str]] = None,
        feedback_ids: Optional[List[dict]] = None,
        feedbacks: Optional[Union[List[dict], pd.DataFrame]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[List[datetime.datetime]] = None,
        reference_name: Optional[str] = None,
        sort_on_timestamp: bool = False,
        sample_rate: float = 1.0,
        as_batch: bool = False,
    ) -> None:
        """
        Function to record a batch of events containing predictions (inputs and outputs),
        feedback, or both simultaneously.

        To log predictions using this method, both inputs and outputs must be passed.
        To log feedbacks using this method, both feedback_ids and feedbacks must be passed.

        User can alternatively use :meth:`gantry.logger.client.Gantry.log_predictions`
        to log batches of predictions only or :meth:`gantry.logger.client.Gantry.log_feedback`
        to log batches of feedbacks only.

        Example:

        .. code-block:: python

           # Record an application's feedback
            gantry.log_records(
                application='foobar',
                inputs=[{'A': 100}, {'A': 101}],
                outputs=[{'B': 'foo'}, {'B': 'bar'}],
                version=1,
                feedback_keys=["A"],
                feedbacks=[{'B': 'bar'}, {'B': 'foo'}],
            )
                ...

        Args:
            application (str): Name of the application. Gantry validates and monitors data
                by function.
            version (optional, Union[int, str]): Version of the function schema to use for
                validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
            inputs (Union[List[dict], pd.Dataframe]): A list of prediction inputs. `inputs[i]`
                is a dict of the features for the i-th prediction to be logged.
            outputs (Union[List[dict], pd.Dataframe]): A list of prediction outputs. `outputs[i]`
                should be the application output for the prediction with features `inputs[i]`.
            feedback_keys (optional, List[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for
                performance metric calculation, you will provide the values of the features
                in this list for Gantry to look up the corresponding prediction.
            feedback_ids (optional, List[dict]): A list of prediction feedback ids. The i-th entry
                corresponds to the argument `feedback_ids` in
                :meth:`gantry.client.Gantry.log_predictions` for the i-th prediction event.
                **IMPORTANT: Only use this parameter if logging feedback only (no predictions).
                If inputs/outputs were also passed in this method, this parameter will be ignored.**
            feedbacks (Union[List[dict], pd.Dataframe]): A list of feedbacks. `feedbacks[i]`
                is a dict of the features for the i-th prediction to be logged.
            ignore_inputs (optional, List[str]): A list of names of input features that should not
                be monitored.
            timestamps (optional, List[datetime.datetime]): A list of prediction timestamps.
                If specified, `timestamps[i]` should be the timestamp for the i-th prediction.
                If timestamps = None (default), then the prediction timestamp defaults to the
                time when `log_records` is called.
            reference_name(optional, str): tag the data being pushed to later user in the
                dashboard.
            sort_on_timestamp (bool, defaults to False): Works when timestamps are provided.
                Sort using the given timestamp. Default to False.
            sample_rate: Used for downsampling. The probability as a float that each record
                will be sent to Gantry.
            as_batch (bool, defaults to False): Whether to add batch metadata and tracking
                in the 'batch' section of the dashboard

        """
        some_preds_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        preds_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedbacks_exist = _is_not_empty(feedbacks)

        if not preds_exist and some_preds_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        if preds_exist and feedbacks_exist:
            return self._log_predictions_and_feedbacks(
                application=application,
                inputs=inputs,
                outputs=outputs,
                feedbacks=feedbacks,
                version=version,
                feedback_keys=feedback_keys,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                reference_name=reference_name,
                sort_on_timestamp=sort_on_timestamp,
                sample_rate=sample_rate,
                as_batch=as_batch,
            )
        elif preds_exist:
            return self.log_predictions(
                application,
                inputs,
                outputs,
                version,
                feedback_keys,
                ignore_inputs,
                feedback_ids,
                timestamps,
                reference_name,
                sort_on_timestamp,
                sample_rate,
                as_batch,
            )
        elif feedbacks_exist:
            return self.log_feedback(
                application,
                feedback_ids,
                feedbacks,
                version,
                timestamps,
                sort_on_timestamp,
                sample_rate,
                as_batch,
            )
        else:
            logger.error("Tried to log_records without prediction and without feedback")

    @_log_exception
    def ping(self) -> bool:
        """
        Pings the log store API server to check if it is alive.
        Returns True if alive, False if there is an error during ping process.
        """
        return self.log_store.ping()

    @_log_exception
    def _log_predictions_and_feedbacks(
        self,
        application: str,
        inputs: Union[List[dict], pd.DataFrame],
        outputs: Union[List[dict], pd.DataFrame],
        feedbacks: Union[List[dict], pd.DataFrame],
        version: Optional[Union[int, str, List[Union[str, int]]]] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[List[datetime.datetime]] = None,
        reference_name: Optional[str] = None,
        sort_on_timestamp: bool = False,
        sample_rate: float = 1.0,
        as_batch: bool = False,
    ) -> None:
        """Internal method to log batch of predictions AND feedbacks"""
        if any(_is_empty(d) for d in [inputs, outputs, feedbacks]):
            raise GantryLoggingException(
                "In order to use log_records method, inputs/outputs/feedbacks need to be provided"
            )

        if not (len(inputs) == len(outputs) == len(feedbacks)):
            raise GantryLoggingException(
                "Size mismatch in data: {} inputs, {} outputs, {} feedbacks".format(
                    len(inputs), len(outputs), len(feedbacks)
                )
            )

        size = len(inputs)

        if timestamps is not None and len(timestamps) != size:
            raise GantryLoggingException(
                "Size mismatch in timestamps: {} data points, {} timestamps".format(
                    size, len(timestamps)
                )
            )

        if version is not None:
            if isinstance(version, (str, int)):
                version = [version] * len(inputs)
            elif len(version) != size:
                # because of typing, this is a list
                raise GantryLoggingException(
                    "Size mismatch in version: {} data points, {} versions".format(
                        size, len(version)
                    )
                )

        inputs = serializable_value(inputs)
        outputs = serializable_value(outputs)
        feedbacks = serializable_value(feedbacks)
        serialized_version: List[Union[int, str]] = serializable_value(version)

        tags = {}
        if reference_name:
            tags["env"] = "reference"
            tags["ref_name"] = reference_name

        timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, size)

        events = _build_prediction_and_feedback_events(
            application=application,
            context=self.context,
            environment=self.environment,
            timestamp_idx=timestamp_idx,
            tags=tags,
            version=serialized_version,
            inputs=inputs,
            outputs=outputs,
            feedback_keys=feedback_keys,
            feedbacks=feedbacks,
            ignore_inputs=ignore_inputs,
            sample_rate=sample_rate,
        )

        if events:
            if as_batch:
                batch = self._create_batch(
                    events_len=len(events),
                    type_=BatchTypes.RECORD.value,
                    application=application,
                )
                batch_id = batch["id"]
                _enrich_events_with_batch_id(events, batch_id)
            else:
                batch_id = None

            self.log_store.log_batch(application, events)
            _batch_success_msg(batch_id, application, self.log_store)
        else:
            logger.info("No events to log")

    @_log_exception
    @typechecked
    def log_record(
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[dict] = None,
        outputs: Optional[Any] = None,
        feedback_id: Optional[dict] = None,
        feedback: Optional[dict] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamp: Optional[datetime.datetime] = None,
        sample_rate: float = 1.0,
    ) -> None:
        """
        Function to record an event, regardless of inputs. Allows client to pass in inputs,
        predictions, and/or feedback for one record.

        Logs error for any individual failures, but does not fail unless method called with
        invalid parameters.

        To log predictions using this method, both inputs and outputs must be passed.
        To log feedback using this method, both feedback_id and feedback must be passed.

        Example:

        .. code-block:: python

           # Record an application's feedback
            gantry.log_record(
                application='foobar',
                inputs={'A': 100},
                outputs={'value': 'bar'},
                version=1,
                feedback_keys=["A"],
                feedback_id={'A': 100},
            )
                ...

        Args:
            application (str): Name of the application. Gantry validates and monitors data by
                function.
            version (optional, int): Version of the function schema to use for validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
            inputs (optional, dict): Inputs to the prediction. A dict where the keys are the feature
                names and the values are the feature values.
            outputs (optional, Any): application output on the prediction.
            feedback_id (optional, Dict[str, Any]): A dictionary mapping string keys to values on
                which the feedback id is computed for matching prediction and feedback events.
                Should be the same as the argument `feedback_id` to
                :meth:`gantry.client.Gantry.log_feedback_event` for the matching feedback event.
            feedback (optional, dict): application feedback object.
            feedback_keys (optional, list[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for performance
                metric calculation, you will provide the values of the features in this list for
                Gantry to look up the corresponding prediction.
            ignore_inputs (optional, list[str]): A list of names of input features that should not
                be monitored.
            timestamp (optional, datetime.datetime): Specify a custom timestamp for the when the
                prediction occured. Useful for recording predictions from the past. If not
                specified, then the prediction timestamp defaults to when `log_record` was
                called.
            sample_rate (optional, float): Specify the probability as a float that the event will
                be sent to Gantry.
        """
        some_pred_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        pred_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedback_exist = _is_not_empty(feedback)

        if (not pred_exist) and some_pred_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        if pred_exist and feedback_exist:
            return self._log_prediction_and_feedback_event(
                application=application,
                version=version,
                inputs=inputs,
                outputs=outputs,
                feedback=feedback,
                feedback_keys=feedback_keys,
                ignore_inputs=ignore_inputs,
                timestamp=timestamp,
                sample_rate=sample_rate,
            )
        elif pred_exist:
            return self.log_prediction_event(
                application=application,
                inputs=inputs,
                outputs=outputs,
                version=version,
                feedback_keys=feedback_keys,
                ignore_inputs=ignore_inputs,
                feedback_id=feedback_id,
                timestamp=timestamp,
                sample_rate=sample_rate,
            )
        elif feedback_exist:
            return self.log_feedback_event(
                application=application,
                feedback_id=feedback_id,
                feedback=feedback,
                feedback_version=version,
                timestamp=timestamp,
                sample_rate=sample_rate,
            )
        else:
            logger.error("Tried to log record without prediction and without feedback")

    @_log_exception
    def _log_prediction_and_feedback_event(
        self,
        application: str,
        inputs: dict,
        outputs: Any,
        feedback: Optional[dict],
        version: Optional[Union[int, str]] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamp: Optional[datetime.datetime] = None,
        sample_rate: float = 1.0,
    ) -> None:
        """Internal method to log an event with prediction AND feedback"""
        _check_sample_rate(sample_rate)
        if random.random() > sample_rate:
            return

        ev = {}

        # don't require feedback_id if they gave us all the info to compute it
        feedback_id = {k: inputs[k] for k in (feedback_keys or [])}  # type: ignore

        ev.update(
            _build_prediction_event(
                self.context,
                self.environment,
                inputs,  # type: ignore
                outputs,
                application,
                version,
                feedback_keys,
                ignore_inputs,
                feedback_id=None,
                custom_timestamp=timestamp,
            )
        )

        fev = _build_feedback_event(
            self.context,
            application,
            feedback_id,  # type: ignore
            feedback,  # type: ignore
            version,
            timestamp,
        )

        ev["metadata"].update(fev.pop("metadata"))  # update nested dict separately
        ev.update(fev)
        self.log_store.log(application, ev)

    @_log_exception
    @typechecked
    def log_feedback_event(
        self,
        application: str,
        feedback_id: dict,
        feedback: dict,
        feedback_version: Optional[Union[str, int]] = None,
        timestamp: Optional[datetime.datetime] = None,
        sample_rate: float = 1.0,
    ):
        """
        DEPRECATION WARNING:
        This method will be deprecated soon. Please use `log_record` instead.

        Endpoint to directly register a single feedback with Gantry.

        Example:

        .. code-block:: python

           # Record an application's feedback
           gantry.log_feedback_event(
               "loan_pred",
               {"loan_id": "00014"}
               {"label": True}
            )
                ...

        Args:
            feedback_id (dict): A dict where the keys are feedback keys (as specified in
                the `feedback_keys` arg of `gantry.instrument` or `log_prediction_event(s)` and
                the value matches the value in the corresponding prediction. The feedback event
                is matched to the prediction event using the values of the feedback keys.
            feedback (dict): application feedback object.
            feedback_version (optional, int or str): Specify application version.
            timestamp (optional, datetime.datetime): Record timestamp.
            sample_rate (optional, float): Specify the probability as a float that the event will
                be sent to Gantry.
        """
        warn(
            "Deprecated: this method will be soon deprecated. Use `log_record` instead",
            DeprecationWarning,
        )

        _check_sample_rate(sample_rate)
        if random.random() > sample_rate:
            return

        ev = _build_feedback_event(
            self.context, application, feedback_id, feedback, feedback_version, timestamp
        )
        self.log_store.log(application, ev)

    @_log_exception
    @typechecked
    def log_feedback(
        self,
        application: str,
        feedback_ids: List[dict],
        feedbacks: Union[List[dict], pd.DataFrame],
        feedback_version: Optional[Union[str, int]] = None,
        timestamps: Optional[List[datetime.datetime]] = None,
        sort_on_timestamp: bool = False,
        sample_rate: float = 1.0,
        as_batch: bool = False,
    ):
        """
        DEPRECATION WARNING:
        This method will be deprecated soon. Please use `log_records` instead.

        Endpoint to register a batch of feedbacks.
        Logs error for any individual failures, but does not fail unless method called with
        invalid parameters.

        Args:
            feedback_ids (list): A list of dicts. dict where the keys are feedback keys
                (as specified in the `feedback_keys` arg of `gantry.instrument` or
                `log_prediction_event(s)`) and the value matches the value in the
                corresponding prediction. The feedback event is matched to the prediction
                event using the values of the feedback keys. The i-th feedback_id maps to
                the i-th feedback.
            feedback (list): List of application feedback objects.
            feedback_version (optional, int or str): Specify application version.
            timestamps (optional, datetime.datetime): Record timestamps. The i-th timestamp
                maps to the i-th feedback.
            sort_on_timestamp (optional, boolean): Specify whether result should sort on timestamp.
            sample_rate (optional, float): Specify the probability as a float that the event will
                be sent to Gantry.
        """
        warn(
            "Deprecated: this method will be soon deprecated. Use `log_records` instead",
            DeprecationWarning,
        )

        batch_id = None
        try:
            feedback_ids = serializable_value(feedback_ids)
            feedbacks = serializable_value(feedbacks)

            timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, len(feedbacks))

            if len(feedback_ids) == len(feedbacks):
                events = []

                for idx, timestamp in timestamp_idx:
                    try:
                        if random.random() > sample_rate:
                            continue

                        events.append(
                            _build_feedback_event(
                                self.context,
                                application,
                                feedback_ids[idx],
                                feedbacks[idx],
                                feedback_version,
                                timestamp,
                                batch_id=batch_id,
                            )
                        )
                    except GantryLoggingException as le:
                        # this is caused by a user error
                        # log the error without the stacktrace
                        logger.error("Error logging data to Gantry: %s", le)
                    except Exception as e:
                        logger.error(
                            "Failed to log feedback with id {} due to {}".format(
                                feedback_ids[idx], e
                            )
                        )

                if events:
                    if as_batch:
                        batch = self._create_batch(
                            events_len=len(events),
                            type_=BatchTypes.FEEDBACK.value,
                            application=application,
                        )
                        batch_id = batch["id"]
                        _enrich_events_with_batch_id(events, batch_id)
                    else:
                        batch_id = None

                    self.log_store.log_batch(application, events)

                    _batch_success_msg(batch_id, application, self.log_store)
                else:
                    logger.info("No events to log")
            else:
                raise GantryLoggingException(
                    "Feedback_ids and feedbacks lists don't have same length."
                )
        except Exception as e:
            _batch_fail_msg(batch_id)

            raise e

    @_log_exception
    @typechecked
    def log_prediction_event(
        self,
        application: str,
        inputs: dict,
        outputs: Any,
        version: Optional[Union[int, str]] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        feedback_id: Optional[dict] = None,
        timestamp: Optional[datetime.datetime] = None,
        sample_rate: float = 1.0,
    ):
        """
        DEPRECATION WARNING:
        This method will be deprecated soon. Please use `log_record` instead.

        Endpoint to directly register a prediction with Gantry. This endpoint includes many
        of the same arguments as :meth:`gantry.client.Gantry.instrument`, but allows the user to
        specify a custom event timestamp with the `timestamp` argument to make it possible to record
        predictions from the past. While :meth:`gantry.client.Gantry.instrument` is useful
        for capturing future predictions from an application function, this method is useful
        to record previous predictions to Gantry: for example old predictions stored in a
        database.

        Example:

        .. code-block:: python

           import gantry

           gantry.init(...)

           # Record a prediction from the previous day
           gantry.log_prediction_event(
               "loan_pred",
               inputs = {"college_degree": False, "loan_amount": 6000},
               outputs = 0,
               feedback_id = {"loan_id": "00014"},
               timestamp = datetime.datetime.now() - datetime.timedelta(days=1)
            )
                ...

        Args:
            inputs (dict): Inputs to the prediction. A dict where the keys are the feature names
                and the values are the feature values.
            outputs (Any): application output on the prediction.
            feedback_id (optional, Dict[str, Any]): A dictionary mapping string keys to values on
                which the feedback id is computed for matching prediction and feedback events.
                Should be the same as the argument `feedback_id` to
                :meth:`gantry.client.Gantry.log_feedback_event` for the matching feedback event.
            timestamp (optional, datetime.datetime): Specify a custom timestamp for the when the
                prediction occured. Useful for recording predictions from the past. If not
                specified, then the prediction timestamp defaults to when `log_prediction_event` was
                called.
            **kwargs: The rest of the arguments are the same as in
                :meth:`gantry.client.Gantry.instrument`.
        """
        warn(
            "Deprecated: this method will be soon deprecated. Use `log_record` instead",
            DeprecationWarning,
        )
        _check_sample_rate(sample_rate)
        if random.random() > sample_rate:
            return

        if not isinstance(inputs, dict):
            logger.error("inputs is not a dict.")
            return

        ev = _build_prediction_event(
            self.context,
            self.environment,
            inputs,
            outputs,
            application,
            version,
            feedback_keys,
            ignore_inputs,
            feedback_id=feedback_id,
            custom_timestamp=timestamp,
        )
        self.log_store.log(application, ev)

    @_log_exception
    @typechecked
    def log_predictions(
        self,
        application: str,
        inputs: Union[List[dict], pd.DataFrame],
        outputs: Union[List[dict], List[Any], pd.DataFrame],
        version: Optional[Union[int, str, List[Union[str, int]]]] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        feedback_ids: Optional[List[dict]] = None,
        timestamps: Optional[List[datetime.datetime]] = None,
        reference_name: Optional[str] = None,
        sort_on_timestamp: bool = False,
        sample_rate: float = 1.0,
        as_batch: bool = False,
    ):
        """
        DEPRECATION WARNING:
        This method will be deprecated soon. Please use `log_records` instead.

        Endpoint for a batch version of :meth:`gantry.client.Gantry.log_prediction_event`.
        Allows for a list of predictions and registers them 1 at a time.

        Args:
            inputs (List[dict]): A list of prediction inputs. `inputs[i]` is a dict of the
                features for the i-th prediction to be logged.
            outputs (List[Any]): A list of prediction outputs. `outputs[i]` should be the
                application output for the prediction with features `inputs[i]`.
            timestamps (optional, List[datetime.datetime]): A list of prediction timestamps.
                If specified, `timestamps[i]` should be the timestamp for the i-th prediction.
                If timestamps = None (default), then the prediction timestamp defaults to the
                time when `log_predictions` is called.
            feedback_ids (optional, List[dict]): A list of prediction feedback ids. The i-th entry
                corresponds to the argument `feedback_id` in
                :meth:`gantry.client.Gantry.log_prediction_event` for the i-th prediction event.
            **kwargs: The rest of the arguments are the same as in
                :meth:`gantry.client.Gantry.instrument`.
        """
        warn(
            "Deprecated: this method will be soon deprecated. Use `log_records` instead",
            DeprecationWarning,
        )
        batch_id = None
        try:
            inputs = serializable_value(inputs)
            outputs = serializable_value(outputs)
            if version is not None and isinstance(version, (str, int)):
                version = [version] * len(inputs)
            version = serializable_value(version) if version is not None else None
            assert version is None or isinstance(version, list)  # mypy

            if len(inputs) == len(outputs):
                if timestamps and not len(timestamps) == len(inputs):
                    raise GantryLoggingException(
                        "timestamps don't have same length as inputs and outputs"
                    )
                if feedback_ids and not len(feedback_ids) == len(inputs):
                    raise GantryLoggingException(
                        "feedback_ids don't have same length as inputs and outputs"
                    )
                if version and isinstance(version, list) and not len(version) == len(inputs):
                    raise GantryLoggingException(
                        "if version is an array, it should have same length as inputs and outputs."
                        "Instead, version has length {} and inputs has length {}.".format(
                            len(version), len(inputs)
                        )
                    )

                tags = {}
                if reference_name:
                    tags["env"] = "reference"
                    tags["ref_name"] = reference_name

                timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, len(inputs))

                events = _build_prediction_events(
                    application=application,
                    inputs=inputs,
                    outputs=outputs,
                    timestamp_idx=timestamp_idx,
                    context=self.context,
                    environment=self.environment,
                    tags=tags,
                    version=version,
                    feedback_keys=feedback_keys,
                    ignore_inputs=ignore_inputs,
                    feedback_ids=feedback_ids,
                    sample_rate=sample_rate,
                    batch_id=batch_id,
                )

                if events:
                    if as_batch:
                        batch = self._create_batch(
                            events_len=len(events),
                            type_=BatchTypes.PREDICTION.value,
                            application=application,
                        )
                        batch_id = batch["id"]
                        _enrich_events_with_batch_id(events, batch_id)
                    else:
                        batch_id = None

                    self.log_store.log_batch(application, events)
                    _batch_success_msg(batch_id, application, self.log_store)
                else:
                    logger.info("No events to log")
            else:
                raise GantryLoggingException("Inputs and outputs list don't have same length.")
        except Exception as e:
            _batch_fail_msg(batch_id)

            raise e

    def _create_batch(self, events_len, type_, application, version=None):
        batch_meta = _build_batch_meta(events_len, type_)

        result = self.log_store._api_client.request(
            "POST",
            "/api/v1/applications/{}/batches".format(application),
            json={"batch": batch_meta, "version": version},
        )

        try:
            check_response(result)
        except GantryException:
            # Raise a custom exception as this one raises
            # to the main thread
            raise GantryBatchCreationException(
                "Failed to create batch: {} {}".format(result["response"], result.get("error"))
            )

        batch = result["data"]["batch"]

        return batch

    @staticmethod
    def setup_logger(level="INFO"):
        if not level:
            return

        pkg_logger = logging.getLogger("gantry")
        pkg_logger.setLevel(level)

        existing_handlers = pkg_logger.handlers
        for handler in existing_handlers:
            if isinstance(handler, logging.StreamHandler):
                return
        formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        pkg_logger.addHandler(handler)
