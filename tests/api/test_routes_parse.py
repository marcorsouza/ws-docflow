from __future__ import annotations

import base64
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ws_docflow.api.routes import router as parse_router
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase


def _app() -> TestClient:
    app = FastAPI()
    app.include_router(parse_router)
    return TestClient(app)


class FakeDoc:
    def __init__(self, payload):
        self._p = payload

    def model_dump(self, mode="json", exclude_none=True, exclude_unset=True):
        return self._p


def test_parse_pdf_success(monkeypatch):
    client = _app()

    def fake_run(self, source):
        return FakeDoc({"ok": True})

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    files = {"file": ("a.pdf", b"%PDF-1.4\n", "application/pdf")}
    r = client.post("/parse", files=files)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_parse_pdf_invalid_content_type():
    client = _app()
    files = {"file": ("a.txt", b"hello", "text/plain")}
    r = client.post("/parse", files=files)
    assert r.status_code == 415  # content-type inválido


def test_parse_pdf_invalid_bytes(monkeypatch):
    client = _app()

    def fake_run(self, source):
        return FakeDoc({"ok": True})

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    files = {"file": ("a.pdf", b"NOT_PDF", "application/pdf")}
    r = client.post("/parse", files=files)
    # helper _run_parse_from_bytes rejeita não-PDF
    assert r.status_code == 415


def test_parse_pdf_with_leading_whitespace_ok(monkeypatch):
    client = _app()

    def fake_run(self, source):
        return FakeDoc({"ok": True})

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    # _run_parse_from_bytes aceita bytes com espaços antes do %PDF
    files = {"file": ("a.pdf", b"   %PDF-1.4\n", "application/pdf")}
    r = client.post("/parse", files=files)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_parse_b64_success(monkeypatch):
    client = _app()

    def fake_run(self, source):
        return FakeDoc({"ok": True, "via": "b64"})

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    payload = {
        "filename": "x.pdf",
        "content_base64": base64.b64encode(b"%PDF-1.7\n").decode("ascii"),
    }
    r = client.post("/parse-b64", json=payload)
    assert r.status_code == 200
    assert r.json()["via"] == "b64"


def test_parse_b64_invalid_base64():
    client = _app()
    # validator deve rejeitar; FastAPI retorna 422
    payload = {"filename": "x.pdf", "content_base64": "INVALID!!"}
    r = client.post("/parse-b64", json=payload)
    assert r.status_code == 422


def test_parse_b64_uc_exception(monkeypatch):
    client = _app()

    def fake_run(self, source):
        raise RuntimeError("boom")

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)

    payload = {
        "filename": "x.pdf",
        "content_base64": base64.b64encode(b"%PDF-1.7\n").decode("ascii"),
    }
    r = client.post("/parse-b64", json=payload)
    assert r.status_code == 422
    assert "Falha ao processar PDF" in r.text
