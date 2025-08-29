from __future__ import annotations

from typing import Iterable, List, Sequence, Union, Optional

from ws_docflow.core.ports import TextExtractor, DocParser, DocModel

SourceT = Union[str, bytes]


class ExtractDataUseCase:
    """
    Orquestra a extração de texto e o parsing.
    Aceita um único parser OU uma sequência de parsers (fallback).
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
            self.parsers: List[DocParser] = list(parser_or_parsers)
        else:
            self.parsers = [parser_or_parsers]  # um único parser

    def run(self, source: SourceT) -> DocModel:
        text = self.extractor.extract(source)
        last_err: Optional[Exception] = None

        for parser in self.parsers:
            try:
                return parser.parse(text)
            except Exception as exc:
                last_err = exc
                continue

        if last_err:
            raise last_err
        raise RuntimeError("Nenhum parser configurado.")
