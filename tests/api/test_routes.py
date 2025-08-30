from fastapi.testclient import TestClient
from ws_docflow.api.main import app
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

client = TestClient(app)


class FakeDoc:
    def __init__(self, payload):
        self._p = payload

    def model_dump(self, mode="json", exclude_none=True, exclude_unset=True):
        return self._p


def test_api_parse_ok(monkeypatch, tmp_path):
    def fake_run(self, source):
        return FakeDoc({"ok": True})

    monkeypatch.setattr(ExtractDataUseCase, "run", fake_run)
    f = tmp_path / "a.pdf"
    f.write_bytes(b"%PDF-1.4\n")
    with f.open("rb") as fh:
        r = client.post("/api/parse", files={"file": ("a.pdf", fh, "application/pdf")})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_api_parse_sem_arquivo():
    r = client.post("/api/parse", files={})  # falta o campo file
    assert r.status_code in (400, 422)  # depende do validador


def test_api_parse_b64_invalido():
    r = client.post(
        "/api/parse-b64", json={"filename": "x.pdf", "content_base64": "XXXX"}
    )
    assert r.status_code in (400, 415, 422, 500)
