from __future__ import annotations

import base64
import os
import tempfile
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, ConfigDict

from ws_docflow.infra.logging import logger as log
from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor
from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser
from ws_docflow.infra.parsers.br_dta_extrato_parser import BrDtaExtratoParser
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

# Routers
router = APIRouter(tags=["Parse"])
health_router = APIRouter(tags=["infra"])

# --- Prometheus (opcional) ---------------------------------------------------
HAS_PROM = False
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        generate_latest,
        Counter,
        Histogram,
        PROCESS_COLLECTOR,
        PLATFORM_COLLECTOR,
    )

    HAS_PROM = True
    # Métricas básicas (se quiser, incremente nos handlers depois)
    REQUEST_COUNT = Counter(
        "ws_docflow_requests_total",
        "Total de requisições HTTP",
        ["route", "method", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "ws_docflow_request_latency_seconds",
        "Latência das requisições HTTP",
        ["route", "method"],
    )
except Exception:
    # Sem prometheus_client instalado: /metrics responderá 501
    REQUEST_COUNT = None  # type: ignore
    REQUEST_LATENCY = None  # type: ignore
# ---------------------------------------------------------------------------


# -------- Schemas --------
class ParseBase64Request(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "documento.pdf",
                "content_base64": "JVBERi0xLjcKJcTl8uXrp/Og0MTGCjEgMCBvYmoK...",  # exemplo ilustrativo
            }
        }
    )
    filename: Optional[str] = "documento.pdf"
    content_base64: str  # PDF em base64 (sem data URI)

    @field_validator("content_base64")
    @classmethod
    def must_be_base64(cls, v: str) -> str:
        try:
            base64.b64decode(v, validate=True)
        except Exception as exc:
            raise ValueError(f"content_base64 inválido: {exc}")
        return v


# -------- Core helpers --------
def _parse_with_single(source: str | bytes, parser) -> dict:
    extractor = PdfPlumberExtractor()
    # NOTE: ExtractDataUseCase espera uma LISTA de parsers
    uc = ExtractDataUseCase(extractor, [parser])
    doc = uc.run(source)
    return doc.model_dump(mode="json", exclude_none=True, exclude_unset=True)


def _parse_with_uc(source: str | bytes) -> dict:
    """
    Tenta sequencialmente os parsers:
      1) BrDtaExtratoParser (extrato)
      2) BrDtaParser        (DTA comum)
    Cai para o próximo parser se o atual não casar.
    """
    last_err: Exception | None = None
    for parser_cls in (BrDtaExtratoParser, BrDtaParser):
        try:
            return _parse_with_single(source, parser_cls())
        except Exception as exc:
            last_err = exc
            continue
    raise (
        last_err
        if last_err
        else HTTPException(status_code=422, detail="Falha ao processar PDF.")
    )


def _run_parse_from_bytes(pdf_bytes: bytes) -> dict:
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if not pdf_bytes.startswith(b"%PDF"):
        if not pdf_bytes.lstrip().startswith(b"%PDF"):
            raise HTTPException(
                status_code=415, detail="Conteúdo não parece ser um PDF válido."
            )

    # 1) Tenta abrir direto por bytes
    try:
        return _parse_with_uc(pdf_bytes)
    except TypeError:
        # Alguns extratores pedem caminho em disco: cairá no fallback abaixo
        pass

    # 2) Fallback Windows-safe: temp file delete=False + cleanup
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        return _parse_with_uc(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# -------- Endpoints --------
@router.post(
    "/parse",
    summary="Parse de PDF (multipart/form-data)",
    responses={200: {"description": "Extração OK ✅"}},
)
async def parse_pdf(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        log.warning(f"⚠️ Content-Type inválido: {file.content_type}")
        raise HTTPException(
            status_code=415, detail="Envie um arquivo PDF válido (application/pdf)."
        )
    try:
        content = await file.read()
        data = _run_parse_from_bytes(content)
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as exc:
        log.exception(f"❌ Erro no parse multipart: {exc}")
        raise HTTPException(status_code=422, detail=f"Falha ao processar PDF: {exc}")


@router.post(
    "/parse-b64",
    summary="Parse de PDF (JSON base64)",
    responses={200: {"description": "Extração OK ✅"}},
)
def parse_pdf_base64(payload: ParseBase64Request):
    try:
        pdf_bytes = base64.b64decode(payload.content_base64, validate=True)
        data = _run_parse_from_bytes(pdf_bytes)
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as exc:
        log.exception(f"❌ Erro no parse base64: {exc}")
        raise HTTPException(
            status_code=422, detail=f"Falha ao processar PDF (base64): {exc}"
        )


@health_router.get("/health")
def health() -> dict:
    # opcional: importar versão da CLI para expor aqui também
    try:
        from ws_docflow.cli.app import __WS_DOCFLOW_VERSION__ as version
    except Exception:
        version = "unknown"
    return {"status": "ok", "version": version}


@health_router.get("/metrics")
def metrics() -> Response:
    if not HAS_PROM:
        # Sem prometheus_client instalado
        raise HTTPException(
            status_code=501,
            detail="Prometheus não habilitado. Instale 'prometheus-client' para /metrics.",
        )
    # Com prometheus: expõe o REGISTRY global e coletores padrão
    registry = CollectorRegistry()
    registry.register(PROCESS_COLLECTOR)
    registry.register(PLATFORM_COLLECTOR)
    data = generate_latest()  # do REGISTRY global
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
