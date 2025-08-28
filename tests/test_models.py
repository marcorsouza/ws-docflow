# tests/test_models.py
import pytest
from pydantic import ValidationError

from ws_docflow.models import (
    UnidadeLocal,
    RecintoAduaneiro,
    Localidade,
    DocumentoDados,
)

# ---------- Casos válidos ----------


@pytest.mark.parametrize(
    "raw,codigo,descricao",
    [
        ("1017700 - PORTO DE RIO GRANDE", "1017700", "PORTO DE RIO GRANDE"),
        (
            "0301304-ALGUMA COISA",
            "0301304",
            "ALGUMA COISA",
        ),  # sem espaço antes/depois do hífen também vale
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
    # validação de 7 dígitos numéricos
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
    doc = DocumentoDados(origem=origem, destino=destino)
    assert doc.origem.unidade_local.codigo == "1017700"
    assert doc.destino.recinto_aduaneiro.codigo == "0923201"


# ---------- Casos inválidos ----------


@pytest.mark.parametrize(
    "raw",
    [
        "101770 - PORTO DE RIO GRANDE",  # 6 dígitos
        "10177001 - PORTO DE RIO GRANDE",  # 8 dígitos
        "ABCDEF1 - PORTO DE RIO GRANDE",  # não-numérico
        "1017700 PORTO DE RIO GRANDE",  # sem hífen separador
        " - PORTO DE RIO GRANDE",  # sem código
        "1017700 - ",  # sem descrição
    ],
)
def test_unidade_local_from_raw_invalido(raw):
    with pytest.raises(ValueError):
        UnidadeLocal.from_raw(raw)


@pytest.mark.parametrize(
    "raw",
    [
        "030130 - TEXTO",  # 6 dígitos
        "03013040 - TEXTO",  # 8 dígitos
        "03A1304 - TEXTO",  # letra no código
        "0301304 TEXTO",  # sem hífen
        " - TEXTO",  # sem código
        "0301304 - ",  # sem descrição
    ],
)
def test_recinto_aduaneiro_from_raw_invalido(raw):
    with pytest.raises(ValueError):
        RecintoAduaneiro.from_raw(raw)


def test_validacao_codigo7_pelo_modelo():
    # Instanciar direto (sem from_raw) com código inválido deve falhar na validação Pydantic
    with pytest.raises(ValidationError):
        UnidadeLocal(codigo="123456", descricao="X")  # 6 dígitos
    with pytest.raises(ValidationError):
        RecintoAduaneiro(codigo="123456A", descricao="Y")  # não-numérico
