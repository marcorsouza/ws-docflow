# src/ws_docflow/cli/app.py
from __future__ import annotations

import json
import typer

from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor
from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser
from ws_docflow.infra.parsers.br_dta_extrato_parser import BrDtaExtratoParser
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

app = typer.Typer(help="CLI do ws-docflow", no_args_is_help=True, add_completion=False)

# Atualize aqui quando fizer bump de versão via Commitizen
__WS_DOCFLOW_VERSION__ = "0.4.1"


def _version_callback(value: bool):
    if value:
        typer.echo(f"ws-docflow {__WS_DOCFLOW_VERSION__}")
        raise typer.Exit(code=0)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Mostra a versão",
        callback=_version_callback,
        is_eager=True,
    ),
):
    # Typer exige uma função callback; não precisa fazer nada aqui
    pass


@app.command("parse")
def parse_cmd(pdf_path: str = typer.Argument(..., help="Caminho do arquivo PDF")):
    """
    Lê o PDF, extrai texto com pdfplumber e tenta múltiplos parsers em fallback:
      1) Extrato: layout 'Dados Gerais / Via de Transporte/Situação'
      2) Clássico: layout 'Trânsito Aduaneiro - Extrato da Declaração de Trânsito'
    Imprime JSON (sem campos None/vazios).
    """
    try:
        extractor = PdfPlumberExtractor()
        parsers = [BrDtaExtratoParser(), BrDtaParser()]  # ordem importa!
        uc = ExtractDataUseCase(extractor, parsers)

        doc = uc.run(pdf_path)

        # serialização “limpa”: sem None/unset
        data = doc.model_dump(mode="json", exclude_none=True, exclude_unset=True)

        # garante floats/Decimal serializáveis no json.dumps
        typer.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    except Exception as exc:
        # erro “legível” para o usuário, mantendo exit code != 0
        typer.secho(
            f"[ws-docflow] Falha ao processar '{pdf_path}': {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
