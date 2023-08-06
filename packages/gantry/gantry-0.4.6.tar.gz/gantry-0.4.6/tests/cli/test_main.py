from click.testing import CliRunner

from gantry.cli.main import cli


def test_cli():
    runner = CliRunner()

    result = runner.invoke(cli)
    assert result.exit_code == 0
