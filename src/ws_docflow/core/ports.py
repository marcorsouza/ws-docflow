from typing import Protocol, Union


SourceT = Union[str, bytes]


class TextExtractor(Protocol):
    def extract(self, source: SourceT) -> str: ...


class DocParser(Protocol):
    def parse(self, text: str): ...
