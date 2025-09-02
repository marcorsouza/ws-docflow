from __future__ import annotations

import json
from pathlib import Path
from typer.testing import CliRunner

import ws_docflow.cli.app as cli
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

runner = CliRunner()


class FakeDocTypeErrorOnce:
    """
    Simula um model_dump que levanta TypeError quando é chamado com kwargs,
    e funciona quando chamado sem kwargs (caminho do except TypeError -> fallback).
    """

    def __init__(self):
        self.called = 0

    def model_dump(self, **kwargs):
        self.called += 1
        # 1ª chamada: com kwargs → TypeError
        if self.called == 1:
            raise TypeError("unexpected kwarg")
        # 2ª chamada (fallback sem kwargs) → sucesso
        return {"ok": True, "via": "fallback"}


def test_parse_model_dump_typeerror_fallback(monkeypatch, tmp_path: Path):
    pdf = tmp_path / "ok.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    def fake_run(self, source):
        return FakeDocTypeErrorOnce()

    # quando o arquivo EXISTE, o app usa a classe do core; patch no método lá
    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    result = runner.invoke(cli.app, ["parse", str(pdf)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["via"] == "fallback"


def test_parse_object_without_model_dump_raises_clean_error(
    monkeypatch, tmp_path: Path
):
    pdf = tmp_path / "ok2.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    class NoDump:
        pass

    def fake_run(self, source):
        # retorna objeto que NÃO tem model_dump → cai no except geral do parse_cmd
        return NoDump()

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    result = runner.invoke(cli.app, ["parse", str(pdf)])
    # deve sair com código != 0 e mensagem amigável
    assert result.exit_code != 0
    assert "Falha ao processar" in (result.stdout + result.stderr)
