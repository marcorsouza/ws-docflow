# src/ws_docflow/infra/parsers/br_dta_parser.py
from __future__ import annotations

import re
from decimal import Decimal
from typing import Dict

from ws_docflow.core.ports import DocParser
from ws_docflow.core.domain.models import (
    DocumentoDados,
    Localidade,
    UnidadeLocal,
    RecintoAduaneiro,
    Participante,
    TotaisOrigem,
)

# -----------------------
# Utilidades / helpers
# -----------------------

_CODE_DESC = re.compile(r"^(\d{7})\s*-\s*(.+)$")
DOC_MASK = re.compile(
    r"^(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})\s*-\s*(.+)$"
)


def _split_code_desc(raw: str) -> Dict[str, str]:
    """
    Divide 'NNNNNNN - DESCRIÇÃO' em {'codigo': ..., 'descricao': ...}
    """
    m = _CODE_DESC.match(raw.strip())
    if not m:
        raise ValueError(f"Formato inválido: {raw!r}. Esperado 'NNNNNNN - DESCRIÇÃO'.")
    return {"codigo": m.group(1), "descricao": m.group(2)}


def parse_money_ptbr(raw: str) -> Decimal:
    """
    Converte '1.611.283,47' -> Decimal('1611283.47')
    """
    s = raw.strip().replace(".", "").replace(",", ".")
    return Decimal(s)


# -----------------------
# Regex (line-based)
# -----------------------

# Bloco Origem/Destino (ancoras por linha e tolerância a linhas em branco)
_ORIG_DEST_REGEX = re.compile(
    r"""
    ^\s*Origem\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Unidade\s+Local:\s*(?P<orig_ul>[^\r\n]+)\r?\n
    ^\s*Recinto\s+Aduaneiro:\s*(?P<orig_ra>[^\r\n]+)\r?\n
    (?:\s*\r?\n)*
    ^\s*Destino\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Unidade\s+Local:\s*(?P<dest_ul>[^\r\n]+)\r?\n
    ^\s*Recinto\s+Aduaneiro:\s*(?P<dest_ra>[^\r\n]+)
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# Beneficiário / Transportador
_PARTICIPANTES_REGEX = re.compile(
    r"""
    ^\s*CNPJ/CPF\s+do\s+Benefici[aá]rio:\s*(?P<benef>[^\r\n]+)\r?\n
    ^\s*CNPJ/CPF\s+do\s+Transportador:\s*(?P<transp>[^\r\n]+)
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# Totais na origem
_TOTAIS_REGEX = re.compile(
    r"""
    ^\s*Tratamento\s+na\s+Origem\s+Totais\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Tipo:\s*(?P<tipo>[^\r\n]+)\r?\n
    ^\s*Valor\s+Total\s+do\s+Tr[aâ]nsito\s+em\s+D[oó]lar\s+Americano:\s*(?P<usd>[0-9\.\,]+)\r?\n
    ^\s*Valor\s+Total\s+do\s+Tr[aâ]nsito\s+em\s+Real:\s*(?P<brl>[0-9\.\,]+)
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)


# -----------------------
# Parser
# -----------------------


class BrDtaParser(DocParser):
    """
    Parser para documentos BR (DTA) extraindo:
    - Origem/Destino (Unidade Local + Recinto)
    - Participantes: Beneficiário / Transportador (CNPJ/CPF + nome)
    - Totais na origem: Tipo, valor USD, valor BRL
    """

    def parse(self, text: str) -> DocumentoDados:
        # Origem/Destino (obrigatório)
        m = _ORIG_DEST_REGEX.search(text)
        if not m:
            raise ValueError("Blocos Origem/Destino não encontrados no texto.")

        oul = UnidadeLocal(**_split_code_desc(m.group("orig_ul")))
        ora = RecintoAduaneiro(**_split_code_desc(m.group("orig_ra")))
        dul = UnidadeLocal(**_split_code_desc(m.group("dest_ul")))
        dra = RecintoAduaneiro(**_split_code_desc(m.group("dest_ra")))

        doc = DocumentoDados(
            origem=Localidade(unidade_local=oul, recinto_aduaneiro=ora),
            destino=Localidade(unidade_local=dul, recinto_aduaneiro=dra),
        )

        # Participantes (opcional)
        p = _PARTICIPANTES_REGEX.search(text)
        if p:
            benef_raw = p.group("benef").strip()
            transp_raw = p.group("transp").strip()
            if DOC_MASK.match(benef_raw):
                doc.beneficiario = Participante.from_raw(benef_raw)
            if DOC_MASK.match(transp_raw):
                doc.transportador = Participante.from_raw(transp_raw)

        # Totais (opcional)
        t = _TOTAIS_REGEX.search(text)
        if t:
            tipo_raw = t.group("tipo").strip().upper()
            tipo = "ARMAZENAMENTO" if "ARMAZENAMENTO" in tipo_raw else "DESCONHECIDO"

            usd = brl = None
            try:
                usd = parse_money_ptbr(t.group("usd"))
                brl = parse_money_ptbr(t.group("brl"))
            except Exception:
                # mantém None se falhar parsing monetário
                pass

            doc.totais_origem = TotaisOrigem(
                tipo=tipo,
                valor_total_usd=usd,
                valor_total_brl=brl,
            )

        return doc
