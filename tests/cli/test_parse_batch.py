# tests/cli/test_parse_batch.py
from __future__ import annotations

import json
from pathlib import Path
from typer.testing import CliRunner

from ws_docflow.cli.app import app
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

runner = CliRunner()


def test_parse_batch_json_stdout(tmp_path: Path, monkeypatch):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.pdf").write_bytes(b"%PDF-1.4\n")
    (d / "b.pdf").write_bytes(b"%PDF-1.4\n")

    class FakeDoc:
        def __init__(self, payload):
            self._payload = payload

        def model_dump(self, mode="json", **kwargs):
            return self._payload

    def fake_run(self, source):
        # payload distinto por arquivo
        return FakeDoc({"ok": True, "source": str(source)})

    # patch no método run do core — robusto para qualquer caminho da CLI
    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    result = runner.invoke(app, ["parse-batch", str(d)])
    assert result.exit_code == 0, result.output

    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) == 2
    assert all(item.get("ok") is True for item in data)


def test_parse_batch_csv_out(tmp_path: Path, monkeypatch):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.pdf").write_bytes(b"%PDF-1.4\n")
    (d / "b.pdf").write_bytes(b"%PDF-1.4\n")

    class FakeDoc:
        def model_dump(self, mode="json", **kwargs):
            return {
                "origem": {"unidade_local": {"codigo": "123", "descricao": "PORTO"}},
                "beneficiario": {"documento": "11.222.333/0001-44", "nome": "ACME"},
                "totais_origem": {"valor_total_usd": 1.23, "valor_total_brl": 10.0},
            }

    def fake_run(self, source):
        return FakeDoc()

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    out_csv = tmp_path / "out.csv"
    result = runner.invoke(app, ["parse-batch", str(d), "--format", "csv", "--out", str(out_csv)])
    assert result.exit_code == 0, result.output
    assert out_csv.exists()
    content = out_csv.read_text(encoding="utf-8")
    assert "origem_unidade_local_codigo" in content
    assert "beneficiario_documento" in content
