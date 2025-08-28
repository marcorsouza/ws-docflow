# src/ws_docflow/models.py
from __future__ import annotations

import re
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


Codigo7 = Annotated[
    str, StringConstraints(pattern=r"^\d{7}$", min_length=7, max_length=7)
]


class UnidadeLocal(BaseModel):
    codigo: Codigo7 = Field(..., description="Código de 7 dígitos da unidade local")
    descricao: str

    @classmethod
    def from_raw(cls, raw: str) -> "UnidadeLocal":
        """
        Ex.: '1017700 - PORTO DE RIO GRANDE'
        """
        m = re.match(r"^(\d{7})\s*-\s*(.+)$", raw.strip())
        if not m:
            raise ValueError(f"Formato inválido para Unidade Local: {raw!r}")
        return cls(codigo=m.group(1), descricao=m.group(2))


class RecintoAduaneiro(BaseModel):
    codigo: Codigo7 = Field(..., description="Código de 7 dígitos do recinto")
    descricao: str

    @classmethod
    def from_raw(cls, raw: str) -> "RecintoAduaneiro":
        """
        Ex.: '0301304 - INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS'
        """
        m = re.match(r"^(\d{7})\s*-\s*(.+)$", raw.strip())
        if not m:
            raise ValueError(f"Formato inválido para Recinto Aduaneiro: {raw!r}")
        return cls(codigo=m.group(1), descricao=m.group(2))


class Localidade(BaseModel):
    unidade_local: UnidadeLocal
    recinto_aduaneiro: RecintoAduaneiro


class DocumentoDados(BaseModel):
    origem: Localidade
    destino: Localidade
