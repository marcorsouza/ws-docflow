# src/ws_docflow/cli.py
from __future__ import annotations

import json
import typer
from .parser import extract_from_pdf

app = typer.Typer(
    help="CLI para extração e validação de dados de PDFs (ws-docflow).",
    no_args_is_help=True,
    add_completion=False,
)


def _version_callback(value: bool):
    if value:
        typer.echo("ws-docflow 0.1.0")
        raise typer.Exit(code=0)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Versão",
        callback=_version_callback,
        is_eager=True,
    ),
): ...


@app.command("parse")
def parse_cmd(pdf_path: str = typer.Argument(..., help="Caminho do arquivo PDF")):
    """
    Extrai dados de Origem/Destino de um arquivo PDF e imprime JSON.
    """
    doc = extract_from_pdf(pdf_path)
    typer.echo(json.dumps(doc.model_dump(), ensure_ascii=False, indent=2))
