# src/ws_docflow/parser.py
from __future__ import annotations

import re
from typing import Dict

import pdfplumber

from .models import UnidadeLocal, RecintoAduaneiro, Localidade, DocumentoDados


_ORIG_DEST_REGEX = re.compile(
    r"""
    ^\s*Origem\s*\r?\n
    (?:\s*\r?\n)*                                       # linhas em branco opcionais
    ^\s*Unidade\s+Local:\s*(?P<orig_ul>[^\r\n]+)\r?\n
    ^\s*Recinto\s+Aduaneiro:\s*(?P<orig_ra>[^\r\n]+)\r?\n
    (?:\s*\r?\n)*

    ^\s*Destino\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Unidade\s+Local:\s*(?P<dest_ul>[^\r\n]+)\r?\n
    ^\s*Recinto\s+Aduaneiro:\s*(?P<dest_ra>[^\r\n]+)
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

_CODE_DESC = re.compile(r"^(\d{7})\s*-\s*(.+)$")


def _split_code_desc(raw: str) -> Dict[str, str]:
    m = _CODE_DESC.match(raw.strip())
    if not m:
        raise ValueError(f"Formato inválido: {raw!r}. Esperado 'NNNNNNN - DESCRIÇÃO'.")
    return {"codigo": m.group(1), "descricao": m.group(2)}


def extract_from_text(text: str) -> DocumentoDados:
    """Extrai DocumentoDados a partir de texto plano do PDF."""
    m = _ORIG_DEST_REGEX.search(text)
    if not m:
        raise ValueError("Blocos Origem/Destino não encontrados no texto.")

    oul = UnidadeLocal(**_split_code_desc(m.group("orig_ul")))
    ora = RecintoAduaneiro(**_split_code_desc(m.group("orig_ra")))
    dul = UnidadeLocal(**_split_code_desc(m.group("dest_ul")))
    dra = RecintoAduaneiro(**_split_code_desc(m.group("dest_ra")))

    return DocumentoDados(
        origem=Localidade(unidade_local=oul, recinto_aduaneiro=ora),
        destino=Localidade(unidade_local=dul, recinto_aduaneiro=dra),
    )


def extract_from_pdf(pdf_path: str) -> DocumentoDados:
    """Abre o PDF, concatena o texto e delega para extract_from_text()."""
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            all_text.append(txt)
    text = "\n".join(all_text)
    return extract_from_text(text)
