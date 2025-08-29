# src/ws_docflow/infra/pdf/pdfplumber_extractor.py
import pdfplumber
from ws_docflow.core.ports import TextExtractor


class PdfPlumberExtractor(TextExtractor):
    def extract(self, pdf_path: str) -> str:
        parts: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                if t:
                    parts.append(t)
        return "\n".join(parts).strip()
