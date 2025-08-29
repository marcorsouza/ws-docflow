from __future__ import annotations
import pdfplumber

from ws_docflow.core.ports import TextExtractor


class PdfPlumberExtractor(TextExtractor):
    def extract(self, path: str) -> str:
        texts = []
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                texts.append(p.extract_text() or "")
        return "\n".join(texts)
