from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner

import ws_docflow.cli.app as cli
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

runner = CliRunner()

# ... (demais testes iguais) ...


def test_parse_out_csv_file(monkeypatch, tmp_path: Path):
    # cria PDF real
    pdf = tmp_path / "ok.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    class FakeDoc:
        def model_dump(self, mode="json", **kwargs):
            return {
                "origem": {"unidade_local": {"codigo": "123", "descricao": "PORTO"}},
                "beneficiario": {"documento": "11.222.333/0001-44", "nome": "ACME"},
                "totais_origem": {"valor_total_usd": 1.23, "valor_total_brl": 10.0},
            }

    def fake_run(self, source):
        return FakeDoc()

    # patch no core para robustez
    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    out_csv = tmp_path / "saida.csv"
    result = runner.invoke(
        cli.app, ["parse", str(pdf), "--format", "csv", "--out", str(out_csv)]
    )
    assert result.exit_code == 0, result.output
    content = out_csv.read_text(encoding="utf-8")
    assert "origem_unidade_local_codigo" in content
    assert "beneficiario_documento" in content
