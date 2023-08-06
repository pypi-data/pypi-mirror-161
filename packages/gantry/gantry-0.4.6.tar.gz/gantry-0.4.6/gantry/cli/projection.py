import json
import logging
import os
import platform
import pprint
import re
import subprocess
import tempfile
from time import sleep
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

import click
import yaml

import gantry
from gantry.api_client import APIClient
from gantry.const import PROD_API_URL
from gantry.utils import generate_gantry_name

logger = logging.getLogger(__name__)

_HANDLER_FILENAME = "_gantry_handler"
_REQUIRED_DEPS = ["pandas"]
_VALID_PYVERS = ("3.6", "3.7", "3.8", "3.9")

PENDING_TASK_STATUSES = [
    "NOT_YET_STARTED",
    "BUILD_IN_PROGRESS",
    "BUILD_SUCCEEDED",
    "PUSH_SUCCEEDED",
    "PUBLISH_LAMBDA_VERSION_SUCCEEDED",
]


@click.group()
def projection():
    """
    Use this to register a new custom projection to Gantry.
    """


@projection.command(
    name="register",
    help="WARNING: this command will be DEPRECATED, please use 'projection update' command.",
)
@click.option("--filename", type=click.Path())
@click.option("--logs_location", default=PROD_API_URL, type=click.STRING)
@click.option("--api_url", default=PROD_API_URL, type=click.STRING)
@click.option("--api_key", type=click.STRING)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Enable dry run to test resulting Docker image before uploading to Gantry",
)
def register(filename, logs_location, api_url, api_key=None, dry_run=False):
    init_kwargs = {}
    if logs_location:
        init_kwargs["logs_location"] = logs_location
    if filename:
        init_kwargs["filename"] = filename
    if api_url:
        init_kwargs["api_url"] = api_url
    if api_key:
        init_kwargs["api_key"] = api_key
    gantry.init(**init_kwargs)
    if not api_url:
        click.secho("No api_url specified", fg="cyan")
    else:
        parsed_url = urlparse(api_url)
        if not parsed_url.scheme.startswith("http"):
            click.secho("API url must start with http or https", fg="cyan")
            return
        api_url = urlunparse(parsed_url)

    api_client = APIClient(origin=api_url, api_key=api_key)
    print(f"Registering custom projection to url {api_url} using logs location at {logs_location}")
    if not filename.endswith(".yaml"):
        raise click.ClickException(
            "The supplied file to gantry projection register must be a .yaml file that "
            "contains a projection definition."
        )
    with open(filename, "r") as stream:
        metric_def_dict = yaml.safe_load(stream)

    for _, metric_def in metric_def_dict.items():
        if not _register_function(api_client, metric_def, dry_run):
            return False


def _register_function(api_client: APIClient, metric_def: dict, dry_run: bool) -> bool:
    click.secho("Registering a custom projection with definition:", fg="cyan")
    click.secho(pprint.pformat(metric_def))

    click.secho("Creating projection function bundle...", fg="cyan")
    metric_or_proj_name, def_type = _get_name_and_type(metric_def)
    runtime_lang = "python"  # we only support python right now
    runtime_version = _get_runtime_version(metric_def.get("python_version"))
    # TODO: support building docker images here
    # if the zip file is too large, our upload request may fail
    image_name = _package_function(
        metric_or_proj_name,
        def_type,
        metric_def["entrypoint"],
        metric_def["function_name"],
        metric_def.get("requirements", []),
        runtime_version,
    )

    metric_def["runtime"] = {"lang": runtime_lang, "version": runtime_version}
    metric_def["handler"] = {"file_name": _HANDLER_FILENAME, "func_name": "handler"}

    if dry_run:
        click.secho("Dry run complete", fg="cyan")
        return True

    # see where we should upload the zip file based on Gantry's configuration
    resp_content = api_client.request(
        "GET",
        "/api/v1/metrics/pre-upload",
        params={"name": metric_or_proj_name},
    )

    # check that our runtime is supported
    if runtime_version not in resp_content["accepted_runtimes"].get(runtime_lang, []):
        click.secho(
            "Registering projection failed. "
            "Runtime {} {} is not supported. Accepted runtimes are:".format(
                runtime_lang, runtime_version
            ),
            fg="red",
        )
        click.secho(pprint.pformat(resp_content["accepted_runtimes"]))
        return False

    with tempfile.TemporaryDirectory() as tmpdirname:
        if resp_content.get("upload_url"):
            uploading_message = "Uploading function bundle... "
            click.secho(uploading_message, nl=False)

            _upload_package(image_name, resp_content["upload_url"])

            metric_def["s3_key"] = resp_content["s3_key"]
            files = None
        else:
            package_zip = _save_package(image_name, tmpdirname)
            files = {"file": open(package_zip, "rb")}

        waiting_message = "Sending request... "
        click.secho(waiting_message, nl=False)
        resp_content = api_client.request(
            "POST",
            "/api/v1/metrics",
            data={"metric": json.dumps(metric_def)},
            files=files,
        )

    click.echo("\b" * len(waiting_message), nl=False)

    if resp_content["response"] == "error":
        click.secho("Registering projection failed.\n >>>> Error message: ", fg="red", nl=False)
        click.secho(resp_content["error"])
    else:
        click.secho("Registering projection succeeded!", fg="green")

    return True


def _get_name_and_type(metric_def: dict) -> Tuple[str, str]:
    if "metric_name" in metric_def:
        raise ValueError(
            "We currently do not support custom metrics, please name the field 'metric_name' "
            "to 'projection_name'"
        )
        # return metric_def["metric_name"], "metric"
    elif "projection_name" in metric_def:
        return metric_def["projection_name"], "projection"
    raise ValueError(
        "There was an error: 'projection_name' must be specified in the configuration yaml!"
    )


_METRIC_HANDLER_TMPL = """
import pandas as pd

# in case module_path has dashes
from importlib import import_module
module = import_module("{module_path}")
func = module.{function_name}

def handler(event, context):
    args = [pd.Series(arg) for arg in event['args']]
    return func(*args)
"""

_PROJECTION_HANDLER_TMPL = """
# in case module_path has dashes
from importlib import import_module
module = import_module("{module_path}")
func = module.{function_name}

def handler(event, context):
    args = event['args']
    return func(*args)
"""

_DOCKERFILE_TMPL = """
FROM public.ecr.aws/lambda/python:{runtime_version}

RUN yum update -y && \
  yum install -y make glibc-devel gcc-c++ patch zip curl && \
  rm -Rf /var/cache/yum

RUN pip install --target "${{LAMBDA_TASK_ROOT}}" {requirements}

COPY . "${{LAMBDA_TASK_ROOT}}"

WORKDIR "${{LAMBDA_TASK_ROOT}}"

CMD [ "{handler}" ]
"""


def _generate_handler(entrypoint: str, function_name: str, def_type: str):
    module_path = entrypoint.replace("/", ".")
    module_path = re.sub(r"\.py$", "", module_path)

    # TODO: aws lambda has a 6MB payload limit. support getting data from s3
    handler_type_to_handler_tmpl = {
        "projection": _PROJECTION_HANDLER_TMPL,
        "metric": _METRIC_HANDLER_TMPL,
    }

    handler = handler_type_to_handler_tmpl[def_type].format(
        module_path=module_path, function_name=function_name
    )

    return handler


def _package_function(
    name: str,
    def_type: str,
    entrypoint: str,
    function_name: str,
    deps: List[str],
    runtime_version: str,
) -> str:
    packages = []
    for dep in deps:
        packages.append(f"'{dep}'")
    packages += _REQUIRED_DEPS

    handler_content = _generate_handler(entrypoint, function_name, def_type)
    handler_filename = "{}.py".format(_HANDLER_FILENAME)
    with open(handler_filename, "w") as f:
        f.write(handler_content)
    handler = "{}.handler".format(_HANDLER_FILENAME)
    try:
        dockerfile = _DOCKERFILE_TMPL.format(
            runtime_version=runtime_version, requirements=" ".join(packages), handler=handler
        )
        tag = generate_gantry_name(name)

        # build via subprocess so we get nice familiar docker output
        proc = subprocess.run(
            ["docker", "buildx", "build", "--platform", "linux/amd64", "-t", tag, "-f", "-", "."],
            input=dockerfile.encode("utf-8"),
        )
        if proc.returncode != 0:
            raise Exception("Failed to build Docker image for custom projection function")
    finally:
        os.remove(handler_filename)

    click.secho("Function packaged as {}".format(tag), fg="cyan")

    return tag


def _upload_package(image_name: str, presigned_url: str) -> None:
    proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "bash",
            image_name,
            "-c",
            f"zip -qr function.zip . && curl --upload-file function.zip '{presigned_url}'",
        ]
    )
    if proc.returncode != 0:
        raise Exception("Failed to upload function package for custom projection function")


def _save_package(image_name: str, dirname: str) -> str:
    output_filename = os.path.join(dirname, "function.zip")
    proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{dirname}:/mnt",
            "--entrypoint",
            "zip",
            image_name,
            "-r",
            "/mnt/function.zip",
            ".",
        ]
    )
    if proc.returncode != 0:
        raise Exception("Failed to create function package for custom projection function")

    return output_filename


def _get_runtime_version(version: Optional[str] = None) -> str:
    if not version:
        version_tuple = platform.python_version_tuple()
        version = "{}.{}".format(version_tuple[0], version_tuple[1])

        if version not in _VALID_PYVERS:
            version = _VALID_PYVERS[-1]
            click.secho("Defaulting to Python version {}".format(version), fg="yellow")

    return version


class DependenciesInstallError(Exception):
    pass


@projection.command("update")
@click.option("--projection-dir", type=click.Path())
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Enable dry run to verify inputs before actually submitting a custom projection to Gantry",
)
def update(projection_dir, dry_run):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client

    click.secho("Parsing custom projection configs...", nl=False, fg="cyan")
    projection = _get_custom_projection_configs(projection_dir)
    click.secho("SUCCESS", fg="cyan")

    click.secho("Validate custom projection definition...", nl=False, fg="cyan")
    valid_config, err_msgs = _validate_custom_projection_configs(api_client, projection)
    if not valid_config:
        click.secho("FAILED.", fg="red")
        if err_msgs:
            click.secho("Please fix the following issue(s):", fg="red")
            for err in err_msgs:
                click.secho(f"\t{err}")

        raise click.ClickException("Invalid projection definition")
    click.secho("SUCCESS", fg="cyan")

    if dry_run:
        click.secho("Dry run complete.", fg="cyan")
        return True

    click.secho("Set up upload location...", nl=False, fg="cyan")
    retrieved, resp = _get_s3_destination(api_client, projection)
    if not retrieved:
        click.secho("FAILED.", fg="red")
        err_msg = resp.get("error", "")
        raise click.ClickException(f"Fail to set up upload location {err_msg}")
    click.secho("SUCCESS", fg="cyan")

    upload_url, s3_key = resp["upload_url"], resp["s3_key"]

    click.secho("Upload new definition...", nl=False, fg="cyan")
    zip_file = "function.zip"
    uploaded, err_msg = _upload_function_zip(zip_file, projection_dir, upload_url)
    if not uploaded:
        click.secho("FAILED.", fg="red")
        raise click.ClickException(f"Fail to upload new projection definition: {err_msg}")
    click.secho("SUCCESS", fg="cyan")

    click.secho("Submit build custom projection request...", nl=False, fg="cyan")
    request_sent, task_id, err_msg = _async_update_custom_projection(api_client, s3_key, projection)
    if not request_sent:
        click.secho("FAILED.", fg="red")
        raise click.ClickException(f"Request to build custom projection failed: {err_msg}")
    click.secho(f"SUCCESS. Task {task_id} has been submitted.", fg="cyan")

    click.secho("Check build progress...", nl=False, fg="cyan")

    _call_get_logs(api_client, task_id)


@projection.command("get-logs")
@click.option("--task-id", type=click.STRING)
def get_logs(task_id):
    gantry.init()
    api_client = gantry.get_client().log_store._api_client
    _call_get_logs(api_client, task_id)


def _call_get_logs(api_client: APIClient, task_id: str):
    status = "NOT_YET_STARTED"
    i, max_attempts, interval_seconds = 0, 60, 10
    while i < max_attempts and status in PENDING_TASK_STATUSES:
        new_status, logs = _get_logs(api_client, task_id)
        if status == new_status:
            click.secho(".", nl=False, fg="cyan")
        else:
            status = new_status
            if "FAILED" in status:
                click.secho(status, fg="red")
            else:
                click.secho(status, nl=False, fg="cyan")
            if logs:
                click.secho(logs)

        i += 1
        sleep(interval_seconds)

    if i == max_attempts:
        click.secho("Closing connection, custom projection build is still in progress.")


def _upload_function_zip(
    zip_file: str, projection_dir: str, presigned_url: str
) -> Tuple[bool, str]:
    zipped, err_msg = _zip_function(projection_dir, zip_file)
    if not zipped:
        return False, err_msg

    proc = subprocess.run(["curl", "--upload-file", zip_file, presigned_url])
    if proc.returncode != 0:
        return False, "Failed to upload custom projection function"
    return True, ""


def _zip_function(projection_dir: str, zip_file: str) -> Tuple[bool, str]:
    proc = subprocess.run(["zip", "-qr", zip_file, projection_dir])
    if proc.returncode != 0:
        return False, f"Failed to zip files under {projection_dir}"
    return True, ""


def _get_custom_projection_configs(projection_dir: str) -> Dict:
    config_file = "config.yaml"
    projection = {}
    try:
        with open(f"{projection_dir}/{config_file}", "r") as stream:
            projection = yaml.safe_load(stream)
    except FileNotFoundError:
        raise ValueError(f"{config_file} not found under projection directory.")

    return projection


def _validate_custom_projection_configs(
    api_client: APIClient, projection: Dict
) -> Tuple[bool, List[str]]:
    response = api_client.request(
        "POST",
        "/api/v1/custom_projections/validate",
        data={"projection": json.dumps(projection)},
    )

    if response.get("response") == "ok":
        return True, []
    return False, response.get("errors", [])


def _get_s3_destination(api_client: APIClient, projection: Dict) -> Tuple[bool, Dict]:
    response = api_client.request(
        "GET",
        "/api/v1/custom_projections/pre-upload",
        params={
            "projection_name": projection["function_definition"]["projection_name"],
        },
    )

    if response.get("response") == "ok":
        return True, response
    return False, {}


def _async_update_custom_projection(
    api_client: APIClient, s3_key: str, projection: Dict
) -> Tuple[bool, str, str]:
    response = api_client.request(
        "POST",
        "/api/v1/custom_projections",
        data={"s3_key": s3_key, "projection": json.dumps(projection)},
    )

    if response.get("response") == "ok":
        return True, response["task_id"], ""
    return False, "", response.get("error", "Error updating custom projection")


def _get_logs(api_client: APIClient, task_id: str) -> Tuple[str, str]:
    response = api_client.request(
        "GET",
        f"/api/v1/custom_projections/logs/{task_id}",
    )
    if response.get("response") == "ok":
        return str(response["status"]), response["logs"]
    return "ERROR", "Error getting task logs"


if __name__ == "__main__":
    projection()
