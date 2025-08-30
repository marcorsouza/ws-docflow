# tests/api/core/test_extract_data_use_case.py
from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase
from ws_docflow.core.ports import TextExtractor, DocParser


class DummyExtractor(TextExtractor):
    def extract(self, source):  # bytes | str -> str
        return "TEXTO DO PDF"


class FakeDoc:
    def __init__(self, payload):
        self._p = payload

    def model_dump(self, mode="json", exclude_none=True, exclude_unset=True):
        return self._p


class ParserA(DocParser):
    # faça o primeiro parser FALHAR com exceção (sinaliza "não reconheci")
    def parse(self, text):
        raise ValueError("A não reconheceu")

    def try_parse(self, text):
        raise ValueError("A não reconheceu")


class ParserB(DocParser):
    # segundo parser reconhece e retorna um doc válido (pydantic-like)
    def parse(self, text):
        return FakeDoc({"parser": "B"})

    def try_parse(self, text):
        return FakeDoc({"parser": "B"})


def test_use_case_fallback():
    uc = ExtractDataUseCase(DummyExtractor(), [ParserA(), ParserB()])
    doc = uc.run(b"%PDF-1.4 ...")
    assert doc is not None
    assert hasattr(doc, "model_dump")
    assert doc.model_dump()["parser"] == "B"
