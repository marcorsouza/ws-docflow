from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner

from ws_docflow.cli.app import app

runner = CliRunner()


def test_parse_json_tmpfile(tmp_path: Path, monkeypatch):
    # fake do use case p/ não depender de PDF real
    class FakeDoc:
        def model_dump(self, mode="json"):
            return {"beneficiario": {"documento": "00.000.000/0000-00", "nome": "X"}}

    class FakeUC:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, source):
            return FakeDoc()

    # monkeypatch no módulo que é importado em app.py
    import ws_docflow.cli.app as app_mod

    app_mod.ExtractDataUseCase = lambda *a, **k: FakeUC()

    out_file = tmp_path / "res.json"
    result = runner.invoke(app, ["parse", "dummy.pdf", "--out", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert '"beneficiario"' in out_file.read_text(encoding="utf-8")


def test_parse_csv_stdout(monkeypatch):
    class FakeDoc:
        def model_dump(self, mode="json"):
            return {
                "origem": {"unidade_local": {"codigo": "123", "descricao": "PORTO"}},
                "totais_origem": {"valor_total_usd": 1.23, "valor_total_brl": 10.0},
            }

    class FakeUC:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, source):
            return FakeDoc()

    import ws_docflow.cli.app as app_mod

    app_mod.ExtractDataUseCase = lambda *a, **k: FakeUC()

    result = runner.invoke(app, ["parse", "dummy.pdf", "--format", "csv"])
    assert result.exit_code == 0
    out = result.stdout
    assert "origem_unidade_local_codigo" in out
    assert "123" in out
