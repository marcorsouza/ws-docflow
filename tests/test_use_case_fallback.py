from __future__ import annotations

from ws_docflow.core.use_cases.extract_data import ExtractDataUseCase
from ws_docflow.infra.parsers.br_dta_extrato_parser import BrDtaExtratoParser
from ws_docflow.infra.parsers.br_dta_parser import BrDtaParser


class DummyExtractor:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract(self, pdf_path: str) -> str:  # assina como TextExtractor
        return self._text


def test_use_case_fallback_extrato_primeiro():
    text_extrato = """
Dados Gerais
No. da Declaração : 25/0399908-0
Tipo : DTA - ENTRADA COMUM

Via de Transporte/Situação
Via de Transporte : RODOVIARIA

Origem
Unidade Local : 1017700 - PORTO DE RIO GRANDE
Recinto Aduaneiro : 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS

Destino
Unidade Local : 1010700 - DRF NOVO HAMBURGO
Recinto Aduaneiro : 0403201 - EADI-MULTI ARMAZENS LTDA-NOVO HAMBURGO/RS
    """.strip()

    uc = ExtractDataUseCase(
        DummyExtractor(text_extrato), [BrDtaExtratoParser(), BrDtaParser()]
    )
    doc = uc.run("fake.pdf")

    assert doc.declaracao.numero == "2503999080"
    assert doc.transporte and doc.transporte.via == "RODOVIARIA"
    assert doc.destino.unidade_local.codigo == "1010700"


def test_use_case_compat_um_unico_parser_layout_classico():
    # Layout clássico do br_dta_parser (Nº da Declaração / Tipo / Situação Atual / Origem / Destino / Participantes / Totais)
    text_classico = """
Nº da Declaração: 240125002-0
Tipo: DTA - ENTRADA COMUM

Origem
Unidade Local: 1017700 - PORTO DE RIO GRANDE
Recinto Aduaneiro: 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS
Destino
Unidade Local: 1017700 - PORTO DE RIO GRANDE
Recinto Aduaneiro: 0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A
    """.strip()

    uc = ExtractDataUseCase(DummyExtractor(text_classico), BrDtaParser())
    doc = uc.run("fake.pdf")

    assert doc.declaracao.numero == "2401250020"
    assert doc.destino.recinto_aduaneiro.codigo == "0923201"
