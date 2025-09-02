from __future__ import annotations

import json
from pathlib import Path
from typer.testing import CliRunner

from ws_docflow.cli.app import app
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

runner = CliRunner()


def test_parse_json_tmpfile(tmp_path: Path, monkeypatch):
    # cria PDF real
    pdf = tmp_path / "ok.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    class FakeDoc:
        def model_dump(self, mode="json", **kwargs):
            return {"beneficiario": {"documento": "00.000.000/0000-00", "nome": "X"}}

    def fake_run(self, source):
        return FakeDoc()

    # patch no método run do core
    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    out_file = tmp_path / "res.json"
    result = runner.invoke(app, ["parse", str(pdf), "--out", str(out_file)])
    assert result.exit_code == 0, result.output
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["beneficiario"]["nome"] == "X"


def test_parse_csv_stdout(tmp_path: Path, monkeypatch):
    pdf = tmp_path / "ok.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    class FakeDoc:
        def model_dump(self, mode="json", **kwargs):
            return {
                "origem": {"unidade_local": {"codigo": "123", "descricao": "PORTO"}},
                "totais_origem": {"valor_total_usd": 1.23, "valor_total_brl": 10.0},
            }

    def fake_run(self, source):
        return FakeDoc()

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    result = runner.invoke(app, ["parse", str(pdf), "--format", "csv"])
    assert result.exit_code == 0, result.output
    out = result.stdout
    assert "origem_unidade_local_codigo" in out
    assert "123" in out
