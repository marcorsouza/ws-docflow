# tests/cli/test_cli_misc.py
from __future__ import annotations

from typer.testing import CliRunner
import ws_docflow.cli.app as cli

runner = CliRunner()


def test_cli_version_flag():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert "ws-docflow" in result.stdout  # imprime versão


def test_cli_invalid_format(monkeypatch):
    # Evita rodar UC real; rápido: só queremos validar erro de formato
    result = runner.invoke(cli.app, ["parse", "dummy.pdf", "--format", "xml"])
    assert result.exit_code == 2
    assert "Formato inválido" in result.stdout or result.stderr


def test_cli_verbose_and_quiet_are_mutually_exclusive():
    result = runner.invoke(cli.app, ["parse", "dummy.pdf", "--verbose", "--quiet"])
    assert result.exit_code == 2
    # a mensagem vem do _set_level
    assert "Use apenas uma das flags" in (result.stdout + result.stderr)
