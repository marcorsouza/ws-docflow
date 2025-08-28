# src/ws_docflow/cli.py
from __future__ import annotations

import typer

# mostra ajuda quando roda sem args e trata erros de uso melhor
app = typer.Typer(
    help="CLI para extração e validação de dados de PDFs (ws-docflow).",
    no_args_is_help=True,
    add_completion=False,
)


def _version_callback(value: bool):
    if value:
        # coloque a versão real aqui quando tiver
        typer.echo("ws-docflow 0.1.0")
        raise typer.Exit(code=0)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Mostra a versão e sai.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """Comandos do ws-docflow."""
    # callback raiz não precisa retornar nada


@app.command("parse")
def parse_cmd(
    pdf_path: str = typer.Argument(..., help="Caminho do arquivo PDF a processar."),
):
    """
    Extrai dados de Origem/Destino de um arquivo PDF.
    (Stub inicial: apenas imprime o caminho recebido)
    """
    typer.echo(f"[ws-docflow] Processando PDF: {pdf_path}")


if __name__ == "__main__":
    app()
