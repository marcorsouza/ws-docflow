import json
import typer
from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor
from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase

app = typer.Typer(help="CLI do ws-docflow", no_args_is_help=True, add_completion=False)


def _version_callback(value: bool):
    if value:
        typer.echo("ws-docflow 0.2.0")
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
): ...


@app.command("parse")
def parse_cmd(pdf_path: str = typer.Argument(..., help="Caminho do arquivo PDF")):
    uc = ExtractDataUseCase(PdfPlumberExtractor(), BrDtaParser())
    doc = uc.run(pdf_path)
    data = doc.model_dump(mode="json")
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
