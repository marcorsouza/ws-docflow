# src/ws_docflow/core/use_cases/extract_data.py
from ws_docflow.core.ports import TextExtractor, DocParser

class ExtractDataUseCase:
    def __init__(self, extractor: TextExtractor, parser: DocParser) -> None:
        self.extractor = extractor
        self.parser = parser

    def run(self, pdf_path: str):
        text = self.extractor.extract(pdf_path)   # <-- aqui
        doc = self.parser.parse(text)
        return doc
