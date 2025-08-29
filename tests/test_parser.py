from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser
from ws_docflow.core.domain.models import DocumentoDados


def test_extract_from_text_minimo():
    text = """
    Origem
    Unidade Local: 1017700 - PORTO DE RIO GRANDE
    Recinto Aduaneiro: 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS
    Destino
    Unidade Local: 1017700 - PORTO DE RIO GRANDE
    Recinto Aduaneiro: 0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A
    """
    parser = BrDtaParser()
    doc = parser.parse(text)
    assert isinstance(doc, DocumentoDados)
    assert doc.origem.unidade_local.codigo == "1017700"
    assert doc.origem.recinto_aduaneiro.codigo == "0301304"
    assert doc.destino.recinto_aduaneiro.codigo == "0923201"
