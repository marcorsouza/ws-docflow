from __future__ import annotations

from ws_docflow.core.ports import DocParser, TextExtractor

from ..domain.models import DocumentoDados


class ExtractDataUseCase:
    def __init__(self, extractor: TextExtractor, parser: DocParser) -> None:
        self._extractor = extractor
        self._parser = parser

    def run(self, pdf_path: str) -> DocumentoDados:
        text = self._extractor.extract(pdf_path)
        return self._parser.parse(text)
