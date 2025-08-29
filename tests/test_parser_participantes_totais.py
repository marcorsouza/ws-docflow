# tests/test_parser_participantes_totais.py
from ws_docflow.parser import extract_from_text


def test_participantes_e_totais():
    text = """
    Origem
    Unidade Local: 1017700 - PORTO DE RIO GRANDE
    Recinto Aduaneiro: 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS
    Destino
    Unidade Local: 1017700 - PORTO DE RIO GRANDE
    Recinto Aduaneiro: 0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A

    Beneficiário/Transportador
    CNPJ/CPF do Beneficiário: 90.102.609/0001-64 - TABONE INDUSTRIA E COMERCIO DE PLASTICOS LTDA
    CNPJ/CPF do Transportador: 87.951.448/0001-79 - TRANSCONTINENTAL LOGISTICA S/A - EM RECUPERACAO JUDICIAL

    Tratamento na Origem Totais
    Tipo: ARMAZENAMENTO
    Valor Total do Trânsito em Dólar Americano: 1.611.283,47
    Valor Total do Trânsito em Real: 9.198.334,00
    """
    doc = extract_from_text(text)

    assert doc.beneficiario is not None
    assert doc.beneficiario.documento == "90.102.609/0001-64"
    assert "TABONE INDUSTRIA" in doc.beneficiario.nome

    assert doc.transportador is not None
    assert doc.transportador.documento == "87.951.448/0001-79"

    assert doc.totais_origem is not None
    assert str(doc.totais_origem.valor_total_usd) == "1611283.47"
    assert str(doc.totais_origem.valor_total_brl) == "9198334.00"
    assert doc.totais_origem.tipo == "ARMAZENAMENTO"
