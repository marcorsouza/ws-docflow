from __future__ import annotations

from dataclasses import dataclass

from ws_docflow.core.ports import TextExtractor, DocParser
from ws_docflow.core.domain.models import DocumentoDados


@dataclass
class ExtractDataUseCase:
    """
    Caso de uso responsável por:
      1) Ler o PDF com o TextExtractor
      2) Passar o texto bruto ao DocParser
      3) Retornar um DocumentoDados validado (Pydantic)
    """
    extractor: TextExtractor
    parser: DocParser

    def run(self, file_path: str) -> DocumentoDados:
        """
        Executa a extração e o parsing a partir do caminho do arquivo PDF.
        """
        text = self.extractor.extract_text(file_path)
        parsed: DocumentoDados = self.parser.parse(text)
        return parsed