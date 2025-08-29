# src/ws_docflow/core/use_cases/extract_data.py
from __future__ import annotations

from typing import Iterable, List, Sequence, Union

from ws_docflow.core.ports import TextExtractor, DocParser

SourceT = Union[str, bytes]


class ExtractDataUseCase:
    """
    Orquestra a extração de texto e o parsing.
    Agora aceita um único parser OU uma sequência de parsers, tentando em fallback.
    """

    def __init__(
        self,
        extractor: TextExtractor,
        parser_or_parsers: Union[DocParser, Sequence[DocParser]],
    ) -> None:
        self.extractor = extractor
        # normaliza para lista interna
        if isinstance(parser_or_parsers, Iterable) and not isinstance(
            parser_or_parsers, (str, bytes)
        ):
            self.parsers: List[DocParser] = list(
                parser_or_parsers
            )  # já é sequência de parsers
        else:
            self.parsers = [parser_or_parsers]  # um único parser

    def run(self, source: SourceT) -> any:
        text = self.extractor.extract(source)  # mantém igual
        last_err: Exception | None = None

        for parser in self.parsers:
            try:
                return parser.parse(text)
            except Exception as exc:
                # guarda e tenta o próximo parser
                last_err = exc
                continue

        # se nenhum parser conseguiu, propaga o último erro para facilitar o debug
        if last_err:
            raise last_err
        raise RuntimeError("Nenhum parser configurado.")
