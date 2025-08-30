# src/ws_docflow/cli/app.py
from __future__ import annotations

import json
import logging
import typer

from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor
from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser
from ws_docflow.infra.parsers.br_dta_extrato_parser import BrDtaExtratoParser
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

# --- Logger (Rich) -----------------------------------------------------------
try:
    # usa configuração central baseada em RichHandler
    from ws_docflow.infra.logging import logger as log  # type: ignore
except Exception:
    # fallback seguro caso o módulo ainda não exista
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    log = logging.getLogger("ws_docflow")
# -----------------------------------------------------------------------------


app = typer.Typer(help="CLI do ws-docflow", no_args_is_help=True, add_completion=False)

# Atualize aqui quando fizer bump de versão via Commitizen
__WS_DOCFLOW_VERSION__ = "0.4.1"


def _version_callback(value: bool):
    if value:
        typer.echo(f"ws-docflow {__WS_DOCFLOW_VERSION__}")
        raise typer.Exit(code=0)


def _set_level(verbose: bool, quiet: bool) -> None:
    """
    Ajusta o nível de log global conforme flags.
    """
    if verbose and quiet:
        typer.echo("Use apenas uma das flags: --verbose ou --quiet", err=True)
        raise typer.Exit(code=2)

    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    if quiet:
        level = logging.WARNING

    logging.getLogger().setLevel(level)
    log.setLevel(level)


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
def parse_cmd(
    pdf_path: str = typer.Argument(..., help="Caminho do arquivo PDF"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Aumenta verbosidade (DEBUG)"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Reduz verbosidade (WARNING)"
    ),
):
    """
    Lê o PDF, extrai texto com pdfplumber e tenta múltiplos parsers em fallback:
      1) Extrato: layout 'Dados Gerais / Via de Transporte/Situação'
      2) Clássico: layout 'Trânsito Aduaneiro - Extrato da Declaração de Trânsito'
    Imprime JSON (sem campos None/vazios).
    """
    _set_level(verbose, quiet)

    try:
        log.info("[bold cyan]🚀 ws-docflow[/] iniciando parse")
        log.debug(f"Arquivo de entrada: {pdf_path}")

        extractor = PdfPlumberExtractor()
        parsers = [BrDtaExtratoParser(), BrDtaParser()]  # ordem importa!
        uc = ExtractDataUseCase(extractor, parsers)

        doc = uc.run(pdf_path)

        # serialização “limpa”: sem None/unset
        data = doc.model_dump(mode="json", exclude_none=True, exclude_unset=True)

        log.info("[green]✅[/] Extração concluída com sucesso")
        # garante floats/Decimal serializáveis no json.dumps
        typer.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    except Exception as exc:
        # erro “legível” para o usuário, mantendo exit code != 0
        # em DEBUG, mostra traceback completo
        if logging.getLogger().level <= logging.DEBUG:
            log.exception(f"🐞 Erro ao processar '{pdf_path}': {exc}")
        else:
            log.error(f"[red]🚨 Falha ao processar[/] '{pdf_path}': {exc}")

        typer.secho(
            f"❌ [ws-docflow] Falha ao processar '{pdf_path}': {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
