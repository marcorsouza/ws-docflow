# src/ws_docflow/infra/pdf/pdfplumber_extractor.py
from __future__ import annotations

import io
from typing import Union

import pdfplumber
from ws_docflow.core.ports import TextExtractor


class PdfPlumberExtractor(TextExtractor):
    def extract(self, source: Union[str, bytes]) -> str:
        """
        Extrai texto de um PDF a partir de:
          - caminho de arquivo (str)
          - conteúdo bruto em bytes
        """
        parts: list[str] = []

        if isinstance(source, bytes):
            pdf_stream = io.BytesIO(source)
            pdf = pdfplumber.open(pdf_stream)
        elif isinstance(source, str):
            pdf = pdfplumber.open(source)
        else:
            raise TypeError(
                f"Tipo de entrada inválido para PdfPlumberExtractor: {type(source)}"
            )

        with pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text:
                    parts.append(text)

        return "\n".join(parts).strip()
