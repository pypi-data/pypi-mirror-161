import copy
import logging
import os
import pprint
from typing import Dict, List, Optional, Union

import yaml
from marshmallow import EXCLUDE, Schema, fields, validate

from gantry.const import PROD_API_URL
from gantry.exceptions import InvalidConfigError

logger = logging.getLogger(__name__)

_ConfigValueType = Union[bool, str, None, Dict]


class ConfigSchema(Schema):
    logs_location = fields.Str(allow_none=True)
    """ Location where Gantry instrumentation should be sent.
    For example, ``"https://app.gantry.io/"``
    """

    logging_level = fields.Str(
        validate=validate.OneOf(["DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"]), allow_none=True
    )
    """Set logging level for Gantry system logging."""

    environment = fields.Str()
    """Set the value for the environment label attached to data instrumented by this client."""

    api_key = fields.Str(load_default=None)
    """Set the API key used to access the API server"""

    bypass_firehose = fields.Bool(load_default=False)
    """When in development mode, optionally turn this off to send raw events to the worker
    rather than going through Firehose."""

    # https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
    send_in_background_default = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None
    send_in_background = fields.Bool(allow_none=True, load_default=send_in_background_default)
    """Set whether Gantry logging methods should run synchronously or not.
    Defaults to True, unless running in lambda.
    """


class Config:
    """
    Represents a Gantry configuration.
    Config looks for configuration in the following places, in order:

    1. Keyword arguments to `Config`. For example, `Config(logs_location='test-dir')`.
    2. Environment variables. For example, `GANTRY_LOGS_LOCATION="test-dir"`,
       or `GANTRY_WORKER__BACKEND="sqlite://"`.
    3. Configuration file `gantry.yaml`. By default, `Config` looks for the file in the
       current directory or the next two levels of parent directories. If the argument
       `project_dir` is provided, `Config` will look for the file in `project_dir` instead.
    """

    CONFIG_FILE_NAME = "gantry.yaml"
    DEFAULT: Dict[str, _ConfigValueType] = {
        "logs_location": PROD_API_URL,
        "environment": "dev",
    }
    ENVVAR_PREFIX = "GANTRY_"
    NESTED_DELIMITER = "__"

    def __init__(self, project_dir: Optional[str] = None, **kwargs):
        if not project_dir:
            # if project_dir is not specified, see if it exists as an envvar
            project_dir = os.environ.get("{}DIR".format(self.ENVVAR_PREFIX))
        config = self._load_from_file(project_dir)

        schema = ConfigSchema()

        self._update_with_envvars(config, schema)
        self._update_with_kwargs(config, kwargs)

        for k in kwargs.keys():
            # any arguments passed in by the user takes precidence
            if isinstance(config.get(k), dict):
                # merge dict configs
                config[k].update(kwargs[k])  # type: ignore
            else:
                config[k] = kwargs[k]

        schema = ConfigSchema()
        self._config = schema.load(config, unknown=EXCLUDE)

    def __getitem__(self, key: str) -> _ConfigValueType:
        return self._config[key]

    def get(self, key: str, default: Optional[str] = None) -> Optional[_ConfigValueType]:
        return self._config.get(key, default)

    @classmethod
    def _load_from_file(cls, project_dir: Optional[str] = None) -> Dict[str, _ConfigValueType]:
        config_path = None
        if project_dir is None:
            # project directory wasn't explicitly provided
            # try to find a gantry config file in current and parent directories
            current_dir = os.getcwd()

            for _ in range(3):
                maybe_config = os.path.join(current_dir, cls.CONFIG_FILE_NAME)
                if os.path.isfile(maybe_config):
                    config_path = maybe_config
                    break

                current_dir = os.path.dirname(current_dir)
        else:
            config_path = os.path.join(project_dir, cls.CONFIG_FILE_NAME)

            if not os.path.isfile(config_path):
                raise ValueError("Config file not found in project directory: %s", project_dir)

        if not config_path:
            logger.debug("Config file not found. Using default config.")
            return copy.deepcopy(cls.DEFAULT)

        with open(config_path, "r") as f:
            config = yaml.safe_load(f.read())

        merged_config = copy.deepcopy(cls.DEFAULT)
        merged_config.update(config)
        return merged_config

    def _update_with_envvars(self, config: dict, schema: ConfigSchema):
        for k, v in os.environ.items():
            if not k.startswith(self.ENVVAR_PREFIX):
                continue

            prefix_len = len(self.ENVVAR_PREFIX)
            flag_path = k[prefix_len:].lower().split(self.NESTED_DELIMITER)
            flag_container = config
            flag_schema = schema.fields

            # walk down the nested flag path to find where the flag should be set
            # for example for GANTRY_WORKER__BACKEND, flag_container should be config['worker']
            # so we can do config['worker']['backend'] = v
            for i, part in enumerate(flag_path[:-1]):
                if part in flag_container and not isinstance(flag_container[part], dict):
                    raise InvalidConfigError(
                        "Cannot set {} because {} is not a dictionary.".format(
                            k, ".".join(flag_path[: i + 1])
                        )
                    )
                c = flag_container.setdefault(part, {})
                assert isinstance(c, dict)  # tell mypy this is a dict
                flag_container = c

                if flag_schema:
                    flag_schema = _get_schema_field(flag_schema, part)

            value: Union[str, List[str]] = v
            # check if the field is supposed to be a list
            # if so, try to comma-separate the string envvar value
            if flag_schema:
                flag_schema = _get_schema_field(flag_schema, flag_path[-1])
                if flag_schema and isinstance(flag_schema, fields.List):
                    value = v.split(",")

            flag_container[flag_path[-1]] = value

    def _update_with_kwargs(self, config: dict, kwargs: dict):
        for k in kwargs.keys():
            # any arguments passed in by the user takes precidence
            if isinstance(config.get(k), dict):
                # merge dict configs
                config[k].update(kwargs[k])  # type: ignore
            else:
                config[k] = kwargs[k]

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=2)
        return pp.pformat(self._config)


def _get_schema_field(schema, field):
    if isinstance(schema, dict):
        schema = schema.get(field, None)
    else:
        schema = getattr(schema, field, None)

    if isinstance(schema, fields.Nested):
        schema = schema.schema.fields

    return schema
