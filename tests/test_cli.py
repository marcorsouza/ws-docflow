# tests/test_cli.py
from typer.testing import CliRunner
from ws_docflow.cli import app

runner = CliRunner()


def test_parse_stub():
    result = runner.invoke(app, ["parse", "exemplo.pdf"])
    assert result.exit_code == 0
    assert "[ws-docflow] Processando PDF: exemplo.pdf" in result.stdout
