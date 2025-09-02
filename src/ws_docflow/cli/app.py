# src/ws_docflow/cli/app.py
from __future__ import annotations

import csv
import io
import json
import logging
import inspect
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import typer

from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor
from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser
from ws_docflow.infra.parsers.br_dta_extrato_parser import BrDtaExtratoParser

# ⚠️ Use SEMPRE o símbolo local (permite monkeypatch nos testes)
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

# --- Logger (Rich) -----------------------------------------------------------
try:
    from ws_docflow.infra.logging import logger as log  # type: ignore
except Exception:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    log = logging.getLogger("ws_docflow")
# -----------------------------------------------------------------------------

app = typer.Typer(help="CLI do ws-docflow", no_args_is_help=True, add_completion=False)

# Atualize via Commitizen
__WS_DOCFLOW_VERSION__ = "0.9.0"


def _version_callback(value: bool):
    if value:
        typer.echo(f"ws-docflow {__WS_DOCFLOW_VERSION__}")
        raise typer.Exit(code=0)


def _set_level(verbose: bool, quiet: bool) -> None:
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


# --------------------- Formatters (fallback local se não houver módulo dedicado) ---------------------
try:
    from ws_docflow.cli.formatters import to_json_string, to_csv_string  # type: ignore
except Exception:

    def _json_default(o: Any) -> Any:
        if isinstance(o, Decimal):
            return float(o)
        return str(o)

    def to_json_string(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)

    def _flatten_for_csv(payload: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
        origem = payload.get("origem", {}) or {}
        destino = payload.get("destino", {}) or {}
        beneficiario = payload.get("beneficiario", {}) or {}
        transportador = payload.get("transportador", {}) or {}
        totais = payload.get("totais_origem", {}) or {}
        row: dict[str, Any] = {
            # Origem
            "origem_unidade_local_codigo": (origem.get("unidade_local") or {}).get(
                "codigo"
            ),
            "origem_unidade_local_descricao": (origem.get("unidade_local") or {}).get(
                "descricao"
            ),
            "origem_recinto_codigo": (origem.get("recinto_aduaneiro") or {}).get(
                "codigo"
            ),
            "origem_recinto_descricao": (origem.get("recinto_aduaneiro") or {}).get(
                "descricao"
            ),
            # Destino
            "destino_unidade_local_codigo": (destino.get("unidade_local") or {}).get(
                "codigo"
            ),
            "destino_unidade_local_descricao": (destino.get("unidade_local") or {}).get(
                "descricao"
            ),
            "destino_recinto_codigo": (destino.get("recinto_aduaneiro") or {}).get(
                "codigo"
            ),
            "destino_recinto_descricao": (destino.get("recinto_aduaneiro") or {}).get(
                "descricao"
            ),
            # Participantes
            "beneficiario_documento": beneficiario.get("documento"),
            "beneficiario_nome": beneficiario.get("nome"),
            "transportador_documento": transportador.get("documento"),
            "transportador_nome": transportador.get("nome"),
            # Totais
            "totais_tipo": totais.get("tipo"),
            "totais_valor_total_usd": totais.get("valor_total_usd"),
            "totais_valor_total_brl": totais.get("valor_total_brl"),
        }
        return list(row.keys()), row

    def to_csv_string(payload: dict[str, Any]) -> str:
        fieldnames, row = _flatten_for_csv(payload)
        buf = io.StringIO(newline="")
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
        return buf.getvalue()


# -----------------------------------------------------------------------------------------------------


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
    pass


@app.command("parse")
def parse_cmd(
    pdf_path: str = typer.Argument(..., help="Caminho do arquivo PDF"),
    out: Optional[Path] = typer.Option(None, "--out", help="Arquivo de saída"),
    fmt: str = typer.Option(
        "json", "--format", help="Formato de saída (json|csv)", case_sensitive=False
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Aumenta verbosidade (DEBUG)"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Reduz verbosidade (WARNING)"
    ),
):
    """
    Lê o PDF, extrai e tenta múltiplos parsers (Extrato → Clássico).
    Saída: JSON (padrão) ou CSV (--format csv). Usa --out para gravar em arquivo.
    """
    _set_level(verbose, quiet)

    fmt = fmt.lower()
    if fmt not in {"json", "csv"}:
        typer.secho("Formato inválido. Use 'json' ou 'csv'.", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    try:
        log.info("[bold cyan]🚀 ws-docflow[/] iniciando parse")
        log.debug(f"Arquivo de entrada: {pdf_path}")

        extractor = PdfPlumberExtractor()
        parsers = [BrDtaExtratoParser(), BrDtaParser()]

        # ✅ SEM heurística: usa sempre o símbolo local (patchável em app_mod.ExtractDataUseCase)
        uc = ExtractDataUseCase(extractor, parsers)

        doc = uc.run(pdf_path)

        # serialização “limpa”: só passa kwargs se suportado
        model_dump = getattr(doc, "model_dump", None)
        if not callable(model_dump):
            raise TypeError("Objeto retornado não possui método model_dump()")

        sig = inspect.signature(model_dump)
        params = sig.parameters
        kwargs: dict[str, Any] = {}
        if "mode" in params:
            kwargs["mode"] = "json"
        if "exclude_none" in params:
            kwargs["exclude_none"] = True
        if "exclude_unset" in params:
            kwargs["exclude_unset"] = True

        try:
            data = model_dump(**kwargs)
        except TypeError:
            # fallback p/ dummies de teste que não aceitam kwargs
            data = model_dump()

        log.info("[green]✅[/] Extração concluída com sucesso")

        rendered = to_json_string(data) if fmt == "json" else to_csv_string(data)

        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                rendered, encoding="utf-8", newline="" if fmt == "csv" else None
            )
            typer.secho(f"Saída gravada em: {out}", fg=typer.colors.GREEN)
        else:
            typer.echo(rendered)

    except Exception as exc:
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


@app.command("parse-batch")
def parse_batch_cmd(
    dir_path: Path = typer.Argument(..., help="Diretório contendo arquivos PDF"),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Arquivo de saída (JSON/CSV)"
    ),
    fmt: str = typer.Option(
        "json",
        "--format",
        help="Formato de saída (json|csv)",
        case_sensitive=False,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Aumenta verbosidade (DEBUG)"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Reduz verbosidade (WARNING)"
    ),
):
    """
    Processa todos os PDFs de um diretório em batch.
    Saída: JSON array (padrão) ou CSV (--format csv).
    - Em caso de erro em um PDF, loga e segue para o próximo.
    - Retorna exit code 0 se ao menos um PDF foi processado com sucesso.
    """
    _set_level(verbose, quiet)

    fmt = fmt.lower()
    if fmt not in {"json", "csv"}:
        typer.secho("Formato inválido. Use 'json' ou 'csv'.", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    try:
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {dir_path}")

        log.info("[bold cyan]🚀 ws-docflow[/] iniciando parse-batch")
        pdf_files = sorted(dir_path.glob("*.pdf"))
        log.debug(f"Arquivos encontrados: {len(pdf_files)}")

        extractor = PdfPlumberExtractor()
        parsers = [BrDtaExtratoParser(), BrDtaParser()]
        # ✅ SEM heurística: símbolo local patchável
        uc = ExtractDataUseCase(extractor, parsers)

        results: list[dict[str, Any]] = []
        successes = 0

        for pdf in pdf_files:
            try:
                doc = uc.run(str(pdf))

                model_dump = getattr(doc, "model_dump", None)
                if not callable(model_dump):
                    raise TypeError("Objeto retornado não possui método model_dump()")

                sig = inspect.signature(model_dump)
                params = sig.parameters
                kwargs: dict[str, Any] = {}
                if "mode" in params:
                    kwargs["mode"] = "json"
                if "exclude_none" in params:
                    kwargs["exclude_none"] = True
                if "exclude_unset" in params:
                    kwargs["exclude_unset"] = True

                try:
                    data = model_dump(**kwargs)
                except TypeError:
                    data = model_dump()

                results.append(data)
                successes += 1
                log.debug(f"[green]OK[/] {pdf.name}")
            except Exception as exc:
                log.error(f"[red]Falha[/] em {pdf.name}: {exc}")

        # Renderização
        if fmt == "json":
            rendered = to_json_string(results)
            if out:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(rendered, encoding="utf-8")
                typer.secho(f"Saída JSON gravada em: {out}", fg=typer.colors.GREEN)
            else:
                typer.echo(rendered)
        else:
            # CSV: uma linha por documento
            try:
                from ws_docflow.cli.formatters import flatten_for_csv, write_csv_file  # type: ignore

                rows = [flatten_for_csv(d)[1] for d in results]
                if out:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    write_csv_file(str(out), rows)
                    typer.secho(f"Saída CSV gravada em: {out}", fg=typer.colors.GREEN)
                else:
                    buf = io.StringIO(newline="")
                    if rows:
                        fieldnames = list(rows[0].keys())
                        writer = csv.DictWriter(buf, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)
                    typer.echo(buf.getvalue())
            except Exception as exc:
                raise RuntimeError(f"Falha ao gerar CSV: {exc}") from exc

        # Exit code: 0 se houve ao menos 1 sucesso; 1 caso contrário
        raise typer.Exit(code=0 if successes > 0 else 1)

    except typer.Exit:
        raise
    except Exception as exc:
        if logging.getLogger().level <= logging.DEBUG:
            log.exception(f"🐞 Erro no parse-batch '{dir_path}': {exc}")
        else:
            log.error(f"[red]🚨 Falha no parse-batch[/] '{dir_path}': {exc}")
        typer.secho(
            f"❌ [ws-docflow] Falha no parse-batch '{dir_path}': {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
