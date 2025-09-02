from __future__ import annotations
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ws_docflow.api.routes import health_router

def _app():
    app = FastAPI()
    app.include_router(health_router)
    return TestClient(app)

def test_health_ok():
    client = _app()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body

def test_metrics_exposes_prometheus_text():
    client = _app()
    r = client.get("/metrics")
    assert r.status_code == 200
    # formato de texto do prometheus (com '# HELP' / '# TYPE')
    text = r.text
    assert "# HELP" in text and "# TYPE" in text
