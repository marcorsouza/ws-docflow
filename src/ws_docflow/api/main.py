from __future__ import annotations

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from ws_docflow.infra.logging import logger as log
from .routes import router as api_router  # rotas em arquivo separado
from .routes import health_router

app = FastAPI(
    title="ws-docflow API",
    version="0.1.0",
    description="🚢 **ws-docflow** — Extração de dados de PDFs aduaneiros (DTA/Extrato)",
)

# CORS (ajuste conforme necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logs (tempo de resposta)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    log.info(f"🚀 {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        dur_ms = (time.perf_counter() - start) * 1000
        log.info(f"✅ {response.status_code} {request.url.path} ⏱️ {dur_ms:.1f} ms")
        return response
    except Exception as exc:
        dur_ms = (time.perf_counter() - start) * 1000
        log.exception(f"❌ 500 {request.url.path} ⏱️ {dur_ms:.1f} ms - erro: {exc}")
        raise


# monta /api/*
app.include_router(api_router, prefix="/api")
app.include_router(health_router)
