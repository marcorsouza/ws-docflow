from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from zoneinfo import ZoneInfo

from ws_docflow.core.ports import DocParser
from ws_docflow.core.domain.models import (
    DocumentoDados,
    Localidade,
    UnidadeLocal,
    RecintoAduaneiro,
    Participante,
    TotaisOrigem,
    DeclaracaoInfo,
    Transporte,
    Situacao,
)

TZ = ZoneInfo("America/Sao_Paulo")

# -----------------------
# Utilidades / helpers
# -----------------------

_CODE_DESC = re.compile(r"^(\d{7})\s*-\s*(.+)$")
DOC_MASK = re.compile(
    r"^(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})\s*-\s*(.+)$"
)


def _split_code_desc(raw: str) -> Dict[str, str]:
    m = _CODE_DESC.match(raw.strip())
    if not m:
        raise ValueError(f"Formato inválido: {raw!r}. Esperado 'NNNNNNN - DESCRIÇÃO'.")
    return {"codigo": m.group(1), "descricao": m.group(2)}


def parse_money_ptbr(raw: str) -> Decimal:
    s = (raw or "").strip().replace(".", "").replace(",", ".")
    return Decimal(s)


def _dt_brs_to_iso(d: str, t: str) -> datetime:
    # "29/08/2025", "16:30:23" -> datetime com TZ America/Sao_Paulo
    return datetime.strptime(f"{d} {t}", "%d/%m/%Y %H:%M:%S").replace(tzinfo=TZ)


# -----------------------
# Regex (line-based) — layout "Dados Gerais"
# -----------------------

# Cabeçalho da declaração
_DECL_NUM_RE = re.compile(r"No\.\s*da\s*Declara[çc][ãa]o\s*:\s*(.+)", re.IGNORECASE)
_TIPO_RE = re.compile(r"Tipo\s*:\s*(.+)", re.IGNORECASE)

# Bloco Via de Transporte/Situação
_VIA_RE = re.compile(r"Via\s+de\s+Transporte\s*:\s*([A-ZÇÃ]+)", re.IGNORECASE)
_SOL_RE = re.compile(
    r"Declara[çc][ãa]o\s+solicitada\s+em\s+(\d{2}/\d{2}/\d{4})\s+às\s+(\d{2}:\d{2}:\d{2})\s*hs,\s*pelo\s*CPF\s*:\s*([\d\.\-]+)",
    re.IGNORECASE,
)
_REG_RE = re.compile(
    r"Declara[çc][ãa]o\s+registrada\s+em\s+(\d{2}/\d{2}/\d{4})\s+às\s+(\d{2}:\d{2}:\d{2})\s*hs,\s*pelo\s*CPF\s*:\s*([\d\.\-]+)",
    re.IGNORECASE,
)
_SEM_VEIC_RE = re.compile(
    r"Esta\s+declara[çc][ãa]o\s+ainda\s+n[aã]o\s+tem\s+ve[ií]culo\(s\)\s+informado\(s\)",
    re.IGNORECASE,
)
_TEM_VEIC_RE = re.compile(
    r"Esta\s+declara[çc][ãa]o\s+tem\s+ve[ií]culo\(s\)\s+informado\(s\)",
    re.IGNORECASE,
)
_DOSS_RE = re.compile(
    r"dossi[êe]\(s\)\s+vinculado\(s\)\s*:\s*([0-9\-\s,;]+)",
    re.IGNORECASE,
)

# Origem/Destino
_ORIG_DEST_RE = re.compile(
    r"""
    ^\s*Origem\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Unidade\s+Local\s*:\s*(?P<orig_ul>[^\r\n]+)\r?\n
    ^\s*Recinto\s+Aduaneiro\s*:\s*(?P<orig_ra>[^\r\n]+)\r?\n
    (?:\s*\r?\n)*
    ^\s*Destino\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Unidade\s+Local\s*:\s*(?P<dest_ul>[^\r\n]+)\r?\n
    ^\s*Recinto\s+Aduaneiro\s*:\s*(?P<dest_ra>[^\r\n]+)
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# Participantes (linhas separadas no Extrato "Dados Gerais")
_BENEF_DOC_RE = re.compile(
    r"CNPJ/CPF\s+do\s+Benefici[aá]rio\s*:\s*([^\r\n]+)", re.IGNORECASE
)
_BENEF_NOME_RE = re.compile(
    r"Nome\s+do\s+Benefici[aá]rio\s*:\s*([^\r\n]+)", re.IGNORECASE
)
_TRANSP_DOC_RE = re.compile(
    r"CNPJ/CPF\s+do\s+Transportador\s*:\s*([^\r\n]+)", re.IGNORECASE
)
_TRANSP_NOME_RE = re.compile(
    r"Nome\s+do\s+Transportador\s*:\s*([^\r\n]+)", re.IGNORECASE
)

# Totais
_TOTAIS_RE = re.compile(
    r"""
    ^\s*Tratamento\s+na\s+Origem/Totais\s*\r?\n
    (?:\s*\r?\n)*
    ^\s*Tipo\s*:\s*(?P<tipo>[^\r\n]+)\r?\n
    ^\s*Valor\s+Total\s+do\s+Tr[aâ]nsito\s+em\s+D[oó]lar\s*:\s*(?P<usd>[0-9\.\,]+)\r?\n
    ^\s*Valor\s+Total\s+do\s+Tr[aâ]nsito\s+na\s+Moeda\s+Nacional\s*:\s*(?P<brl>[0-9\.\,]+)
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# Situação Atual (quando existir no final — opcional)
_SIT_ATUAL_RE = re.compile(
    r"^\s*Situa[çc][ãa]o\s+Atual\s*(.+?)(?:\n\s*Cargas\b|$)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)

# -----------------------
# Parser
# -----------------------


class BrDtaExtratoParser(DocParser):
    """
    Parser para o layout 'Dados Gerais / Via de Transporte/Situação' do Extrato DTA,
    extraindo:
      - Nº e Tipo da Declaração
      - Via de Transporte + Situação (solicitada/registrada, CPF, veículos, dossiês)
      - Origem/Destino
      - Beneficiário/Transportador
      - Totais na origem
      - Situação Atual (quando houver)
    Todos os campos de 'situacao' e 'transporte' são opcionais.
    """

    def _try_decl_num(self, text: str) -> str:
        m = _DECL_NUM_RE.search(text)
        if not m:
            return ""
        return re.sub(r"\D", "", m.group(1).strip())

    def _try_tipo(self, text: str) -> str:
        m = _TIPO_RE.search(text)
        return m.group(1).strip() if m else ""

    def _parse_via_situacao(
        self, text: str
    ) -> tuple[Optional[Transporte], Optional[Situacao]]:
        transp = Transporte()
        sit = Situacao()

        mv = _VIA_RE.search(text)
        if mv:
            transp.via = mv.group(1).upper()

        ms = _SOL_RE.search(text)
        if ms:
            sit.solicitada_em = _dt_brs_to_iso(ms.group(1), ms.group(2))
            sit.solicitada_por_cpf = ms.group(3)

        mr = _REG_RE.search(text)
        if mr:
            sit.registrada_em = _dt_brs_to_iso(mr.group(1), mr.group(2))
            sit.registrada_por_cpf = mr.group(3)

        if _SEM_VEIC_RE.search(text):
            sit.veiculos_informados = False
        elif _TEM_VEIC_RE.search(text):
            sit.veiculos_informados = True
        # se nenhum dos dois casar, permanece None

        md = _DOSS_RE.search(text)
        if md:
            raw = md.group(1).strip()
            tokens = re.split(r"[,\s;]+", raw)
            sit.dossies_vinculados = [t for t in tokens if t]

        # Se ambos vazios, retorna None para não criar blocos em branco
        transp_out = transp if transp.via is not None else None
        has_sit = any(
            v is not None and (v != [] if isinstance(v, list) else True)
            for v in [
                sit.solicitada_em,
                sit.solicitada_por_cpf,
                sit.registrada_em,
                sit.registrada_por_cpf,
                sit.veiculos_informados,
                getattr(sit, "dossies_vinculados", []),
            ]
        )
        sit_out = sit if has_sit else None
        return transp_out, sit_out

    def parse(self, text: str) -> DocumentoDados:
        # Nº e Tipo da Declaração
        decl_num = self._try_decl_num(text)
        tipo = self._try_tipo(text)

        # Origem/Destino
        m = _ORIG_DEST_RE.search(text)
        if not m:
            raise ValueError("Blocos Origem/Destino não encontrados no texto.")

        oul = UnidadeLocal(**_split_code_desc(m.group("orig_ul")))
        ora = RecintoAduaneiro(**_split_code_desc(m.group("orig_ra")))
        dul = UnidadeLocal(**_split_code_desc(m.group("dest_ul")))
        dra = RecintoAduaneiro(**_split_code_desc(m.group("dest_ra")))

        doc = DocumentoDados(
            declaracao=DeclaracaoInfo(numero=decl_num, tipo=tipo),
            # 'situacao_atual' pode aparecer em um bloco separado; preenchido adiante
            situacao_atual="",
            origem=Localidade(unidade_local=oul, recinto_aduaneiro=ora),
            destino=Localidade(unidade_local=dul, recinto_aduaneiro=dra),
        )

        # Beneficiário/Transportador — no "Dados Gerais" vêm em linhas separadas
        bdoc = _BENEF_DOC_RE.search(text)
        bnome = _BENEF_NOME_RE.search(text)
        if bdoc and bnome:
            benef_raw = f"{bdoc.group(1).strip()} - {bnome.group(1).strip()}"
            if DOC_MASK.match(benef_raw):
                doc.beneficiario = Participante.from_raw(benef_raw)

        tdoc = _TRANSP_DOC_RE.search(text)
        tnome = _TRANSP_NOME_RE.search(text)
        if tdoc and tnome:
            transp_raw = f"{tdoc.group(1).strip()} - {tnome.group(1).strip()}"
            if DOC_MASK.match(transp_raw):
                doc.transportador = Participante.from_raw(transp_raw)

        # Totais
        t = _TOTAIS_RE.search(text)
        if t:
            tipo_raw = (t.group("tipo") or "").strip().upper()

            def _normalize_tipo(v: str) -> str:
                if "ARMAZEN" in v:
                    return "ARMAZENAMENTO"
                if not v or v in {"N/A", "-"}:
                    return "DESCONHECIDO"
                return "OUTRO"

            usd = brl = None
            try:
                usd = parse_money_ptbr(t.group("usd"))
                brl = parse_money_ptbr(t.group("brl"))
            except Exception:
                pass

            doc.totais_origem = TotaisOrigem(
                tipo=_normalize_tipo(tipo_raw),
                valor_total_usd=usd,
                valor_total_brl=brl,
            )

        # Via de Transporte / Situação (opcional)
        transp_blk, sit_blk = self._parse_via_situacao(text)
        if transp_blk:
            doc.transporte = transp_blk
        if sit_blk:
            doc.situacao = sit_blk

        # Situação Atual (texto livre — opcional, quando existir neste layout)
        ms = _SIT_ATUAL_RE.search(text)
        if ms:
            bloco = ms.group(1).strip()
            # limpeza básica
            bloco = re.sub(r"javascript:history\.back\(\);\s*", "", bloco)
            doc.situacao_atual = re.sub(r"[ \t]+$", "", bloco, flags=re.MULTILINE)

        return doc
