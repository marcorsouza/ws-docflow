from __future__ import annotations

from ws_docflow.infra.parsers.br_dta_extrato_parser import BrDtaExtratoParser


def test_extrato_dados_gerais_via_transporte_situacao():
    text = """
Dados Gerais

No. da Declaração : 25/0399908-0
Tipo : DTA - ENTRADA COMUM

Via de Transporte/Situação

Via de Transporte : RODOVIARIA
Declaração solicitada em 29/08/2025 às 16:30:23 hs,  pelo CPF : 778.857.910-68
Declaração registrada em 29/08/2025 às 16:37:40 hs,  pelo CPF : 778.857.910-68
Esta declaração ainda não tem veículo(s) informado(s)
Esta declaração possui dossiê(s) vinculado(s):  20250029718711-2

Origem

Unidade Local : 1017700 - PORTO DE RIO GRANDE
Recinto Aduaneiro : 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS

Destino

Unidade Local : 1010700 - DRF NOVO HAMBURGO
Recinto Aduaneiro : 0403201 - EADI-MULTI ARMAZENS LTDA-NOVO HAMBURGO/RS

Beneficiário/Transportador

CNPJ/CPF do Beneficiário : 08.325.039/0001-90
Nome do Beneficiário: SS INDUSTRIA METALURGICA DE TELAS LTDA
CNPJ/CPF do Transportador : 13.233.554/0001-80
Nome do Transportador: MULTI EXPRESS BRASIL TRANSPORTES DE CARGAS LTDA

Tratamento na Origem/Totais

Tipo : Armazenamento
Valor Total do Trânsito em Dólar : 57.024,00
Valor Total do Trânsito na Moeda Nacional : 308.585,37
    """.strip()

    parser = BrDtaExtratoParser()
    doc = parser.parse(text)

    # Declaração (número normalizado sem não-dígitos)
    assert doc.declaracao.numero == "2503999080"
    assert doc.declaracao.tipo.upper() == "DTA - ENTRADA COMUM"

    # Origem/Destino
    assert doc.origem.unidade_local.codigo == "1017700"
    assert "PORTO DE RIO GRANDE" in doc.origem.unidade_local.descricao
    assert doc.destino.unidade_local.codigo == "1010700"
    assert "DRF NOVO HAMBURGO" in doc.destino.unidade_local.descricao

    # Participantes
    assert doc.beneficiario is not None
    assert doc.beneficiario.documento == "08.325.039/0001-90"
    assert "TELAS LTDA" in doc.beneficiario.nome

    assert doc.transportador is not None
    assert doc.transportador.documento == "13.233.554/0001-80"
    assert "MULTI EXPRESS" in doc.transportador.nome

    # Totais
    assert doc.totais_origem is not None
    assert doc.totais_origem.tipo == "ARMAZENAMENTO"
    assert str(doc.totais_origem.valor_total_usd) == "57024.00"
    assert str(doc.totais_origem.valor_total_brl) == "308585.37"

    # Via de Transporte / Situação
    assert doc.transporte is not None and doc.transporte.via == "RODOVIARIA"
    assert doc.situacao is not None
    assert doc.situacao.solicitada_por_cpf == "778.857.910-68"
    assert doc.situacao.registrada_por_cpf == "778.857.910-68"
    assert doc.situacao.veiculos_informados is False
    assert doc.situacao.dossies_vinculados == ["20250029718711-2"]


def test_extrato_sem_campos_de_situacao_nao_quebra():
    # texto propositalmente sem datas/CPF/veículos/dossiê
    text = """
Dados Gerais
No. da Declaração : 25/0000000-0
Tipo : DTA - ENTRADA COMUM

Via de Transporte/Situação
Via de Transporte : RODOVIARIA

Origem
Unidade Local : 1017700 - PORTO DE RIO GRANDE
Recinto Aduaneiro : 0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS

Destino
Unidade Local : 1017700 - PORTO DE RIO GRANDE
Recinto Aduaneiro : 0923201 - TRANSCONTINENTAL LOGÍSTICA_S.A
    """.strip()

    parser = BrDtaExtratoParser()
    doc = parser.parse(text)

    assert doc.declaracao.numero == "2500000000"
    assert doc.transporte is not None and doc.transporte.via == "RODOVIARIA"
    # 'situacao' pode vir None se nenhum subcampo foi encontrado
    assert doc.situacao is None
