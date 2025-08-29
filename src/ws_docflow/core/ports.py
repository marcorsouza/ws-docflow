from typing import Protocol


class TextExtractor(Protocol):
    def extract(self, pdf_path: str) -> str: ...


class DocParser(Protocol):
    def parse(self, text: str): ...
