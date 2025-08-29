from typer.testing import CliRunner
from ws_docflow.cli.app import app

runner = CliRunner()


def test_parse_help_shows_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "parse" in result.stdout
