from __future__ import annotations

from typing import List

import pdfplumber

from ws_docflow.core.ports import TextExtractor


class PdfPlumberExtractor(TextExtractor):
    """
    Extrai texto de PDFs usando pdfplumber.
    Retorna todo o texto concatenado com quebras de linha entre páginas.
    """

    def extract_text(self, file_path: str) -> str:
        pages_text: List[str] = []
        # abre o PDF e extrai texto página a página
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                # normaliza newlines, remove espaços à direita
                txt = "\n".join(line.rstrip() for line in txt.splitlines())
                pages_text.append(txt)
        # separa páginas com 2 quebras para preservar blocos/headers
        return "\n\n".join(pages_text)
