import mock
import pytest
import responses
from click.testing import CliRunner

from gantry.api_client import APIClient
from gantry.cli.projection import (
    _package_function,
    _register_function,
    _save_package,
    _upload_package,
    register,
)

ACCEPTED_RUNTIMES = {"python": ["3.6", "3.7", "3.8", "3.9"]}


@mock.patch("gantry.cli.projection._save_package")
@mock.patch("gantry.cli.projection.APIClient.request")
@mock.patch("gantry.cli.projection._package_function")
def test_custom_projection_cli(mock_package_function, mock_client_request, mock_save_package):
    # TODO: This test doesn't actually cover a lot of functionality that
    # we would ideally test
    filename = "tests/cli/custom-projections/custom-projections.yaml"
    logs_location = "http://localhost:5001"
    api_url = logs_location
    api_key = "TESTAPIKEY"

    mock_get_response = {"accepted_runtimes": ACCEPTED_RUNTIMES, "response": "ok"}
    mock_client_request.return_value = mock_get_response
    mock_save_package.return_value = "tests/cli/custom-projections/custom-projections.yaml"

    runner = CliRunner()
    cli_args = [
        "--filename",
        filename,
        "--logs_location",
        logs_location,
        "--api_url",
        api_url,
        "--api_key",
        api_key,
    ]

    result = runner.invoke(register, cli_args)
    assert result.exit_code == 0
    assert "Registering projection succeeded!" in result.output
    mock_save_package.assert_called_once()
    mock_package_function.assert_called_once()


@mock.patch("gantry.cli.projection._upload_package")
@mock.patch("gantry.cli.projection.APIClient.request")
@mock.patch("gantry.cli.projection._package_function")
def test_custom_projection_cli_upload(
    mock_package_function, mock_client_request, mock_upload_package
):
    # TODO: This test doesn't actually cover a lot of functionality that
    # we would ideally test
    filename = "tests/cli/custom-projections/custom-projections.yaml"
    logs_location = "http://localhost:5001"
    api_url = logs_location
    api_key = "TESTAPIKEY"

    mock_get_response = {
        "accepted_runtimes": ACCEPTED_RUNTIMES,
        "upload_url": "example_url",
        "s3_key": "test_key",
        "response": "ok",
    }
    mock_client_request.return_value = mock_get_response

    runner = CliRunner()
    cli_args = [
        "--filename",
        filename,
        "--logs_location",
        logs_location,
        "--api_url",
        api_url,
        "--api_key",
        api_key,
    ]

    result = runner.invoke(register, cli_args)
    assert result.exit_code == 0
    assert "Registering projection succeeded!" in result.output
    mock_upload_package.assert_called_once()
    mock_package_function.assert_called_once()


@mock.patch("gantry.cli.projection.subprocess")
def test_register_function_invalid_runtime(mock_subprocess):
    mock_subprocess.run.return_value.returncode = 0

    host = "https://test-api"
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            "{}/api/v1/metrics/pre-upload".format(host),
            json={
                "accepted_runtimes": ACCEPTED_RUNTIMES,
                "upload_url": "example_url",
                "s3_key": "test_key",
                "response": "ok",
            },
            headers={"Content-Type": "application/json"},
        )

        api_client = APIClient(origin=host)

        metric_def = {
            "application": "test_func",
            "projection_name": "winnie_auc",
            "function_name": "winnie_auc",
            "function_args": ["inputs.input1", "outputs"],
            "entrypoint": "custom_projections.py",
            "python_version": "2.7",
        }

        register_result = _register_function(api_client, metric_def, False)

        assert not register_result
        mock_subprocess.run.assert_called_once()


@mock.patch("gantry.cli.projection.subprocess")
def test_register_function_dry_run(mock_subprocess):
    mock_subprocess.run.return_value.returncode = 0

    host = "https://test-api"
    api_client = APIClient(origin=host)

    metric_def = {
        "application": "test_func",
        "projection_name": "winnie_auc",
        "function_name": "winnie_auc",
        "function_args": ["inputs.input1", "outputs"],
        "entrypoint": "custom_projections.py",
        "python_version": "2.7",
    }

    register_result = _register_function(api_client, metric_def, True)

    assert register_result
    mock_subprocess.run.assert_called_once()


_DOCKERFILE = """
FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && \
  yum install -y make glibc-devel gcc-c++ patch zip curl && \
  rm -Rf /var/cache/yum

RUN pip install --target "${LAMBDA_TASK_ROOT}" 'scikit-learn>=0.23.2' 'pandas>=1.1.3' pandas

COPY . "${LAMBDA_TASK_ROOT}"

WORKDIR "${LAMBDA_TASK_ROOT}"

CMD [ "_gantry_handler.handler" ]
"""


@mock.patch("gantry.cli.projection.subprocess")
def test_package_function(mock_subprocess):
    mock_subprocess.run.return_value.returncode = 0

    _package_function(
        "test-function",
        "projection",
        "entry.py",
        "main_func",
        ["scikit-learn>=0.23.2", "pandas>=1.1.3"],
        "3.9",
    )

    mock_subprocess.run.assert_called_once()

    call_args = mock_subprocess.run.call_args
    assert call_args.kwargs["input"] == _DOCKERFILE.encode("utf-8")


@mock.patch("gantry.cli.projection.subprocess")
def test_upload_package(mock_subprocess):
    mock_subprocess.run.return_value.returncode = 0

    image_name = "dummy-image"
    presigned_url = "https://dummy-s3.com?signature=asdf"

    _upload_package(image_name, presigned_url)

    mock_subprocess.run.assert_called_once()

    call_args = mock_subprocess.run.call_args
    assert call_args.args[0] == [
        "docker",
        "run",
        "--rm",
        "--entrypoint",
        "bash",
        image_name,
        "-c",
        f"zip -qr function.zip . && curl --upload-file function.zip '{presigned_url}'",
    ]


@mock.patch("gantry.cli.projection.subprocess")
def test_save_package(mock_subprocess, tmp_path):
    mock_subprocess.run.return_value.returncode = 0

    image_name = "dummy-image"

    filename = _save_package(image_name, str(tmp_path))

    mock_subprocess.run.assert_called_once()

    call_args = mock_subprocess.run.call_args
    assert call_args.args[0] == [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{tmp_path}:/mnt",
        "--entrypoint",
        "zip",
        image_name,
        "-r",
        "/mnt/function.zip",
        ".",
    ]

    assert filename.startswith(str(tmp_path))


def test_custom_projection_cli_error_cases():
    filename = "tests/cli/custom-projections/unsupported-custom-projections.yaml"
    logs_location = "http://localhost:5001"
    api_url = logs_location
    api_key = "TESTAPIKEY"

    runner = CliRunner()
    cli_args = [
        "--filename",
        filename,
        "--logs_location",
        logs_location,
        "--api_url",
        api_url,
        "--api_key",
        api_key,
    ]
    with pytest.raises(ValueError):
        runner.invoke(register, cli_args, catch_exceptions=False)

    filename = "tests/cli/custom-projections/unsupported-no-name-custom-projections.yaml"
    cli_args[1] = filename
    with pytest.raises(ValueError):
        runner.invoke(register, cli_args, catch_exceptions=False)
