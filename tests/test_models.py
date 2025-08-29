import pytest
from pydantic import ValidationError
from ws_docflow.core.domain.models import DeclaracaoInfo, Situacao, Transporte
from ws_docflow.core.domain.models import (
    UnidadeLocal,
    RecintoAduaneiro,
    Localidade,
    DocumentoDados,
)


@pytest.mark.parametrize(
    "raw,codigo,descricao",
    [
        ("1017700 - PORTO DE RIO GRANDE", "1017700", "PORTO DE RIO GRANDE"),
        ("0301304-ALGUMA COISA", "0301304", "ALGUMA COISA"),
        (
            "0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A",
            "0923201",
            "TRANSCONTINENTAL LOGÍSTICA_S.A",
        ),
    ],
)
def test_unidade_local_from_raw_valido(raw, codigo, descricao):
    ul = UnidadeLocal.from_raw(raw)
    assert ul.codigo == codigo
    assert ul.descricao == descricao
    assert len(ul.codigo) == 7 and ul.codigo.isdigit()


@pytest.mark.parametrize(
    "raw,codigo,descricao",
    [
        (
            "0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS",
            "0301304",
            "INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS",
        ),
    ],
)
def test_recinto_aduaneiro_from_raw_valido(raw, codigo, descricao):
    ra = RecintoAduaneiro.from_raw(raw)
    assert ra.codigo == codigo
    assert ra.descricao == descricao
    assert len(ra.codigo) == 7 and ra.codigo.isdigit()


def test_documento_dados_valido():
    origem = Localidade(
        unidade_local=UnidadeLocal.from_raw("1017700 - PORTO DE RIO GRANDE"),
        recinto_aduaneiro=RecintoAduaneiro.from_raw(
            "0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS"
        ),
    )
    destino = Localidade(
        unidade_local=UnidadeLocal.from_raw("1017700 - PORTO DE RIO GRANDE"),
        recinto_aduaneiro=RecintoAduaneiro.from_raw(
            "0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A"
        ),
    )
    doc = DocumentoDados(
        declaracao=DeclaracaoInfo(numero="2401250020", tipo="DTA - ENTRADA COMUM"),
        situacao_atual="",
        origem=origem,
        destino=destino,
    )
    assert doc.origem.unidade_local.codigo == "1017700"
    assert doc.destino.recinto_aduaneiro.codigo == "0923201"


@pytest.mark.parametrize(
    "raw",
    [
        "101770 - PORTO DE RIO GRANDE",
        "10177001 - PORTO DE RIO GRANDE",
        "ABCDEF1 - PORTO DE RIO GRANDE",
        "1017700 PORTO DE RIO GRANDE",
        " - PORTO DE RIO GRANDE",
        "1017700 - ",
    ],
)
def test_unidade_local_from_raw_invalido(raw):
    with pytest.raises(ValueError):
        UnidadeLocal.from_raw(raw)


@pytest.mark.parametrize(
    "raw",
    [
        "030130 - TEXTO",
        "03013040 - TEXTO",
        "03A1304 - TEXTO",
        "0301304 TEXTO",
        " - TEXTO",
        "0301304 - ",
    ],
)
def test_recinto_aduaneiro_from_raw_invalido(raw):
    with pytest.raises(ValueError):
        RecintoAduaneiro.from_raw(raw)


def test_validacao_codigo7_pelo_modelo():
    with pytest.raises(ValidationError):
        UnidadeLocal(codigo="123456", descricao="X")
    with pytest.raises(ValidationError):
        RecintoAduaneiro(codigo="123456A", descricao="Y")


def test_transporte_situacao_opcionais():
    origem = Localidade(
        unidade_local=UnidadeLocal.from_raw("1017700 - PORTO DE RIO GRANDE"),
        recinto_aduaneiro=RecintoAduaneiro.from_raw(
            "0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS"
        ),
    )
    destino = Localidade(
        unidade_local=UnidadeLocal.from_raw("1017700 - PORTO DE RIO GRANDE"),
        recinto_aduaneiro=RecintoAduaneiro.from_raw(
            "0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A"
        ),
    )

    # sem transporte/situacao
    doc = DocumentoDados(
        declaracao=DeclaracaoInfo(numero="X", tipo="Y"), origem=origem, destino=destino
    )
    assert doc.transporte is None and doc.situacao is None

    # com transporte/situacao parciais
    doc2 = DocumentoDados(
        declaracao=DeclaracaoInfo(numero="X", tipo="Y"),
        origem=origem,
        destino=destino,
        transporte=Transporte(via="RODOVIARIA"),
        situacao=Situacao(veiculos_informados=False),
    )
    assert doc2.transporte.via == "RODOVIARIA"
    assert doc2.situacao.veiculos_informados is False
