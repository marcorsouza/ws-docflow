# tests/api/test_main.py
from __future__ import annotations

import base64
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

import ws_docflow.api.main as api_main
import ws_docflow.api.routes as api_routes


class FakeDoc:
    """Objeto fake para simular retorno do use case (Pydantic-like)."""

    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def model_dump(
        self, mode: str = "json", exclude_none: bool = True, exclude_unset: bool = True
    ):
        return self._payload


class FakeUC:
    """Substitui ExtractDataUseCase dentro do módulo da API."""

    def __init__(self, extractor, parsers):
        # podemos inspecionar/guardar se necessário
        self.extractor = extractor
        self.parsers = parsers

    def run(self, source: str | bytes):
        # Apenas valida se o "PDF" começa com %PDF (tolerando espaços antes),
        # que é a mesma checagem feita no main._run_parse_from_bytes.
        if isinstance(source, (bytes, bytearray)):
            data = bytes(source)
        elif isinstance(source, str):
            # quando cair no fallback via arquivo temporário, o main abre por caminho;
            # aqui não vamos reler o arquivo; apenas devolvemos algo estático de sucesso.
            data = b"%PDF from path"
        else:
            raise TypeError("source inválido no FakeUC.run")

        # Tolerar espaços/brancos antes do header
        if not (data.startswith(b"%PDF") or data.lstrip().startswith(b"%PDF")):
            raise ValueError("Conteúdo não parece PDF no FakeUC")

        # Simula payload do parser (campos exemplo do projeto)
        payload = {
            "origem": {
                "unidade_local": {
                    "codigo": "1017700",
                    "descricao": "PORTO DE RIO GRANDE",
                },
                "recinto_aduaneiro": {
                    "codigo": "0301304",
                    "descricao": "TECON RIO GRANDE",
                },
            },
            "destino": {
                "unidade_local": {
                    "codigo": "1010700",
                    "descricao": "DRF NOVO HAMBURGO",
                },
                "recinto_aduaneiro": {
                    "codigo": "0403201",
                    "descricao": "EADI MULTI ARMAZENS",
                },
            },
            "beneficiario": {
                "documento": "08.325.039/0001-90",
                "nome": "SS INDUSTRIA METALURGICA DE TELAS LTDA",
            },
            "transportador": {
                "documento": "13.233.554/0001-80",
                "nome": "MULTI EXPRESS BRASIL TRANSPORTES DE CARGAS LTDA",
            },
            "totais_origem": {
                "tipo": "ARMAZENAMENTO",
                "valor_total_usd": 57024.00,
                "valor_total_brl": 308585.37,
            },
        }
        return FakeDoc(payload)


@pytest.fixture(autouse=True)
def patch_use_case(monkeypatch):
    monkeypatch.setattr(api_routes, "ExtractDataUseCase", FakeUC)
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_main.app)


def test_parse_b64_ok(client: TestClient):
    # PDF bytes com espaços antes do header (para cobrir a tolerância do main)
    pdf_bytes = b"   %PDF-1.7\n%Mock PDF content for tests\n"
    payload = {
        "filename": "teste.pdf",
        "content_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }
    resp = client.post("/api/parse-b64", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "origem" in data and "destino" in data
    assert data["origem"]["unidade_local"]["codigo"] == "1017700"


def test_parse_ok_multipart(client: TestClient):
    pdf_bytes = b"%PDF-1.4\n%Mock PDF content\n"
    files = {"file": ("arquivo.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/api/parse", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "beneficiario" in data and "transportador" in data
    assert data["totais_origem"]["valor_total_usd"] == 57024.00


def test_parse_b64_invalido(client: TestClient):
    # base64 inválido (caracteres fora do alfabeto)
    payload = {"content_base64": "###nao-e-base64###"}
    resp = client.post("/api/parse-b64", json=payload)
    # Pydantic deve retornar 422 de validação
    assert resp.status_code == 422
    msg = resp.text.lower()
    assert "content_base64" in msg


def test_parse_nao_pdf_bytes(client: TestClient):
    # bytes que não começam (nem após strip) com %PDF
    pdf_like = b"NOT_A_PDF"
    files = {"file": ("arquivo.pdf", pdf_like, "application/pdf")}
    resp = client.post("/api/parse", files=files)
    assert resp.status_code == 415
    assert (
        "pdf válido" in resp.text.lower()
        or "conteúdo não parece ser um pdf válido" in resp.text.lower()
    )
