# src/ws_docflow/infra/logging.py
from __future__ import annotations

import logging
import os
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as rich_traceback_install

rich_traceback_install(show_locals=False, width=120, extra_lines=1)

LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LEVEL_NUM = getattr(logging, LEVEL, logging.INFO)

console = Console(
    stderr=True,
    markup=True,
    emoji=True,  # mantém emojis 🙂
    force_terminal=True,  # ignora redirecionamento
    soft_wrap=True,
)

logging.basicConfig(
    level=LEVEL_NUM,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
)

logger = logging.getLogger("ws_docflow")
logger.setLevel(LEVEL_NUM)
