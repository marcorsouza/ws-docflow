from __future__ import annotations

from typing import Protocol, Union, runtime_checkable, Dict, Any

SourceT = Union[str, bytes]


@runtime_checkable
class DocModel(Protocol):
    def model_dump(
        self,
        *,
        mode: str = "json",
        exclude_none: bool = True,
        exclude_unset: bool = True,
    ) -> Dict[str, Any]: ...


class TextExtractor(Protocol):
    def extract(self, source: SourceT) -> str: ...


class DocParser(Protocol):
    def parse(self, text: str) -> DocModel: ...
