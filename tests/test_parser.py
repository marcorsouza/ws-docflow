# tests/test_parser.py
from src.ws_docflow.parser import extract_from_text
from src.ws_docflow.models import DocumentoDados


def test_extract_from_text_minimo():
    text = """
    Origem
    Unidade Local: 1017700 - PORTO DE RIO GRANDE
    Recinto Aduaneiro: 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS
    Destino
    Unidade Local: 1017700 - PORTO DE RIO GRANDE
    Recinto Aduaneiro: 0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A
    """
    doc = extract_from_text(text)
    assert isinstance(doc, DocumentoDados)
    assert doc.origem.unidade_local.codigo == "1017700"
    assert doc.origem.recinto_aduaneiro.codigo == "0301304"
    assert doc.destino.recinto_aduaneiro.codigo == "0923201"
