from __future__ import annotations
import json
from typer.testing import CliRunner
import ws_docflow.cli.app as cli
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

runner = CliRunner()


class FakeDoc:
    def __init__(self, payload):
        self._p = payload

    def model_dump(self, mode="json", exclude_none=True, exclude_unset=True):
        return self._p


def test_cli_parse_ok(monkeypatch, tmp_path):
    pdf = tmp_path / "ok.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    def fake_run(self, source):
        return FakeDoc({"ok": True, "source": str(source)})

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    result = runner.invoke(cli.app, ["parse", str(pdf)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["ok"] is True


def test_cli_parse_invalido(monkeypatch, tmp_path):
    pdf = tmp_path / "bad.pdf"
    pdf.write_bytes(b"NOT_PDF")

    def fake_run(self, source):
        # simula erro ocorrido durante o run (ex.: PDF inválido)
        raise ValueError("arquivo inválido")

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    result = runner.invoke(cli.app, ["parse", str(pdf)])
    # qualquer saída não-zero é suficiente; não dependa da mensagem
    assert result.exit_code != 0
