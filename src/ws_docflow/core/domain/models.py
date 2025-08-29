from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints

# ---------------------------------
# Tipos / Constraints
# ---------------------------------
Codigo7 = Annotated[
    str, StringConstraints(pattern=r"^\d{7}$", min_length=7, max_length=7)
]
DocIdBR = Annotated[
    str,
    StringConstraints(
        # aceita CNPJ 00.000.000/0000-00 e CPF 000.000.000-00
        pattern=r"^(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})$"
    ),
]


# ---------------------------------
# Modelos básicos
# ---------------------------------
class UnidadeLocal(BaseModel):
    codigo: Codigo7 = Field(..., description="Código de 7 dígitos da unidade local")
    descricao: str

    @classmethod
    def from_raw(cls, raw: str) -> "UnidadeLocal":
        # Ex.: "1017700 - PORTO DE RIO GRANDE"
        m = re.match(r"^(\d{7})\s*-\s*(.+)$", raw.strip())
        if not m:
            raise ValueError(f"Formato inválido para Unidade Local: {raw!r}")
        return cls(codigo=m.group(1), descricao=m.group(2))


class RecintoAduaneiro(BaseModel):
    codigo: Codigo7 = Field(..., description="Código de 7 dígitos do recinto")
    descricao: str

    @classmethod
    def from_raw(cls, raw: str) -> "RecintoAduaneiro":
        # Ex.: "0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS"
        m = re.match(r"^(\d{7})\s*-\s*(.+)$", raw.strip())
        if not m:
            raise ValueError(f"Formato inválido para Recinto Aduaneiro: {raw!r}")
        return cls(codigo=m.group(1), descricao=m.group(2))


class Localidade(BaseModel):
    unidade_local: UnidadeLocal
    recinto_aduaneiro: RecintoAduaneiro


class Participante(BaseModel):
    documento: DocIdBR  # CNPJ/CPF mascarado
    nome: str

    @classmethod
    def from_raw(cls, raw: str) -> "Participante":
        # Ex.: "90.102.609/0001-64 - TABONE INDUSTRIA E COMERCIO DE PLASTICOS LTDA"
        m = re.match(
            r"^(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})\s*-\s*(.+)$",
            raw.strip(),
        )
        if not m:
            raise ValueError(f"Formato inválido para Participante: {raw!r}")
        return cls(documento=m.group(1), nome=m.group(2))


class TotaisOrigem(BaseModel):
    # Mantém compat com os PDFs que trazem "Tipo: ARMAZENAMENTO"
    tipo: Literal["ARMAZENAMENTO", "OUTRO", "DESCONHECIDO"] = "DESCONHECIDO"
    valor_total_usd: Optional[Decimal] = None
    valor_total_brl: Optional[Decimal] = None


# ---------------------------------
# Novos blocos opcionais
# ---------------------------------
class Transporte(BaseModel):
    # Ex.: "RODOVIARIA"
    via: Optional[str] = None


class Situacao(BaseModel):
    # Campos opcionais pois podem não existir no extrato
    solicitada_em: Optional[datetime] = None
    solicitada_por_cpf: Optional[str] = None
    registrada_em: Optional[datetime] = None
    registrada_por_cpf: Optional[str] = None
    veiculos_informados: Optional[bool] = None
    dossies_vinculados: List[str] = []


# ---------------------------------
# Informações da declaração
# ---------------------------------
class DeclaracaoInfo(BaseModel):
    # defaults vazios para compatibilidade retro
    numero: str = Field("", description="Número da DTA sem hífen")
    tipo: str = Field("", description="Tipo da DTA, ex.: 'DTA - ENTRADA COMUM'")


# ---------------------------------
# Documento principal
# ---------------------------------
class DocumentoDados(BaseModel):
    # Compatibilidade retro: defaults permitem instanciar apenas com origem/destino
    declaracao: DeclaracaoInfo = Field(default=DeclaracaoInfo(numero="", tipo=""))

    # Campo livre (string) para status textual quando existir (ex.: “CONCESSAO ...”)
    situacao_atual: str = ""

    origem: Localidade
    destino: Localidade
    beneficiario: Optional[Participante] = None
    transportador: Optional[Participante] = None
    totais_origem: Optional[TotaisOrigem] = None

    # Novos campos (opcionais; só aparecem no extrato quando existirem)
    transporte: Optional[Transporte] = None
    situacao: Optional[Situacao] = None
