import types
import ws_docflow.infra.pdf.pdfplumber_extractor as mod


class FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


def test_pdfplumber_extractor_ok(monkeypatch, tmp_path):
    def fake_open(_path):
        return FakePDF([FakePage("A"), FakePage("B")])

    monkeypatch.setattr(mod, "pdfplumber", types.SimpleNamespace(open=fake_open))

    from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor

    pdf = tmp_path / "ok.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out = PdfPlumberExtractor().extract(str(pdf))
    assert out == "A\nB"


def test_pdfplumber_extractor_sem_texto(monkeypatch, tmp_path):
    def fake_open(_path):
        return FakePDF([FakePage(None)])

    monkeypatch.setattr(mod, "pdfplumber", types.SimpleNamespace(open=fake_open))

    from ws_docflow.infra.pdf.pdfplumber_extractor import PdfPlumberExtractor

    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out = PdfPlumberExtractor().extract(str(pdf))
    assert out.strip() == ""  # garante retorno vazio sem explodir
