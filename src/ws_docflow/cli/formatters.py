from __future__ import annotations

import csv
import io
import json
from decimal import Decimal
from typing import Any, Iterable

# Preferir generics embutidos (dict/list/tuple) e manter compat 3.10 com __future__.


def _json_default(o: Any) -> Any:
    """Serializador padrão para tipos não JSON nativos (ex.: Decimal)."""
    if isinstance(o, Decimal):
        # Evita "Decimal('...')" no JSON
        return float(o)
    return str(o)


def to_json_string(payload: dict[str, Any]) -> str:
    """Converte o dicionário de domínio em JSON legível (UTF-8, indentado)."""
    return json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)


def flatten_for_csv(payload: dict[str, Any]) -> tuple[Iterable[str], dict[str, Any]]:
    """
    Achata o dicionário do domínio para 1 linha 'wide' (colunas estáveis).

    Retorna:
        fieldnames: ordem estável das colunas
        row: linha única com campos achatados
    """
    origem = payload.get("origem", {}) or {}
    destino = payload.get("destino", {}) or {}
    beneficiario = payload.get("beneficiario", {}) or {}
    transportador = payload.get("transportador", {}) or {}
    totais = payload.get("totais_origem", {}) or {}

    row: dict[str, Any] = {
        # Origem
        "origem_unidade_local_codigo": (origem.get("unidade_local") or {}).get(
            "codigo"
        ),
        "origem_unidade_local_descricao": (origem.get("unidade_local") or {}).get(
            "descricao"
        ),
        "origem_recinto_codigo": (origem.get("recinto_aduaneiro") or {}).get("codigo"),
        "origem_recinto_descricao": (origem.get("recinto_aduaneiro") or {}).get(
            "descricao"
        ),
        # Destino
        "destino_unidade_local_codigo": (destino.get("unidade_local") or {}).get(
            "codigo"
        ),
        "destino_unidade_local_descricao": (destino.get("unidade_local") or {}).get(
            "descricao"
        ),
        "destino_recinto_codigo": (destino.get("recinto_aduaneiro") or {}).get(
            "codigo"
        ),
        "destino_recinto_descricao": (destino.get("recinto_aduaneiro") or {}).get(
            "descricao"
        ),
        # Participantes
        "beneficiario_documento": beneficiario.get("documento"),
        "beneficiario_nome": beneficiario.get("nome"),
        "transportador_documento": transportador.get("documento"),
        "transportador_nome": transportador.get("nome"),
        # Totais
        "totais_tipo": totais.get("tipo"),
        "totais_valor_total_usd": totais.get("valor_total_usd"),
        "totais_valor_total_brl": totais.get("valor_total_brl"),
    }

    fieldnames: list[str] = list(row.keys())
    return fieldnames, row


def to_csv_string(payload: dict[str, Any]) -> str:
    """
    Retorna CSV (com cabeçalho) como string para 1 documento.
    Útil quando a CLI imprime em stdout.
    """
    fieldnames, row = flatten_for_csv(payload)
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(row)
    return buf.getvalue()


def write_csv_file(path: str, rows: Iterable[dict[str, Any]]) -> None:
    """
    Grava CSV em arquivo para múltiplas linhas (batch).
    Se rows estiver vazio, cria arquivo vazio (sem cabeçalho).
    """
    rows_list = list(rows)
    with open(path, "w", encoding="utf-8", newline="") as f:
        if not rows_list:
            # Arquivo vazio é mais explícito do que cabeçalho sem linhas
            return
        fieldnames = list(rows_list[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_list)
