from __future__ import annotations
from typing import Protocol
from .domain.models import DocumentoDados


class TextExtractor(Protocol):
    def extract(self, path: str) -> str: ...


class DocParser(Protocol):
    def parse(self, text: str) -> DocumentoDados: ...
