from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner

import ws_docflow.cli.app as cli

runner = CliRunner()


def test_cli_version_flag():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert "ws-docflow" in result.stdout


def test_cli_invalid_format():
    # dispara a validação do --format em app.py
    result = runner.invoke(cli.app, ["parse", "dummy.pdf", "--format", "xml"])
    assert result.exit_code == 2
    assert "Formato inválido" in (result.stdout + result.stderr)


def test_cli_verbose_and_quiet_mutually_exclusive():
    result = runner.invoke(cli.app, ["parse", "dummy.pdf", "--verbose", "--quiet"])
    assert result.exit_code == 2
    assert "Use apenas uma das flags" in (result.stdout + result.stderr)


def test_parse_error_path_when_file_missing_and_uc_raises(monkeypatch):
    # cobre o caminho: arquivo inexistente → usa símbolo local ExtractDataUseCase (patchável em app_mod)
    class FakeUC:
        def __init__(self, *a, **k):
            pass

        def run(self, source):
            raise RuntimeError("boom")

    import ws_docflow.cli.app as app_mod

    app_mod.ExtractDataUseCase = lambda *a, **k: FakeUC()

    result = runner.invoke(cli.app, ["parse", "dummy.pdf"])
    assert result.exit_code != 0
    # mensagem amigável da exceção
    assert "Falha ao processar" in (result.stdout + result.stderr)


def test_parse_out_csv_file(monkeypatch, tmp_path: Path):
    # cobre escrita com --out + --format csv
    class FakeDoc:
        def model_dump(self, mode="json"):
            return {
                "origem": {"unidade_local": {"codigo": "123", "descricao": "PORTO"}},
                "beneficiario": {"documento": "11.222.333/0001-44", "nome": "ACME"},
                "totais_origem": {"valor_total_usd": 1.23, "valor_total_brl": 10.0},
            }

    class FakeUC:
        def __init__(self, *a, **k):
            pass

        def run(self, source):
            return FakeDoc()

    import ws_docflow.cli.app as app_mod

    app_mod.ExtractDataUseCase = lambda *a, **k: FakeUC()

    out_csv = tmp_path / "saida.csv"
    result = runner.invoke(
        cli.app, ["parse", "dummy.pdf", "--format", "csv", "--out", str(out_csv)]
    )
    assert result.exit_code == 0, result.output
    content = out_csv.read_text(encoding="utf-8")
    assert "origem_unidade_local_codigo" in content
    assert "beneficiario_documento" in content
