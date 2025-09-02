# tests/cli/test_formatters_extra.py
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ws_docflow.cli.formatters import (
    to_json_string,
    to_csv_string,
    flatten_for_csv,
    write_csv_file,
)


def test_to_json_string_serializes_decimal():
    payload = {"totais_origem": {"valor_total_usd": Decimal("12.34")}}
    out = to_json_string(payload)
    # deve ter '12.34' como número (sem Decimal('...'))
    assert '"valor_total_usd": 12.34' in out


def test_to_csv_string_and_flatten_headers():
    payload = {
        "origem": {
            "unidade_local": {"codigo": "8765432", "descricao": "PORTO DE SANTOS"}
        },
        "destino": {
            "unidade_local": {"codigo": "7654321", "descricao": "PORTO DE ITAJAÍ"}
        },
        "beneficiario": {"documento": "11.222.333/0001-44", "nome": "COMPANHIA"},
        "transportador": {"documento": "55.666.777/0001-88", "nome": "NAVIOS"},
        "totais_origem": {
            "tipo": "ARMAZENAMENTO",
            "valor_total_usd": 1.23,
            "valor_total_brl": 10.0,
        },
    }

    # headers e linha achatada coerentes
    headers, row = flatten_for_csv(payload)
    assert "origem_unidade_local_codigo" in headers
    assert row["origem_unidade_local_codigo"] == "8765432"

    # string CSV com cabeçalho e a linha
    csv_out = to_csv_string(payload)
    assert "origem_unidade_local_codigo" in csv_out
    assert "8765432" in csv_out
    assert "beneficiario_documento" in csv_out


def test_write_csv_file_empty(tmp_path: Path):
    out = tmp_path / "empty.csv"
    write_csv_file(str(out), [])
    assert out.exists()
    # por convenção do módulo: arquivo vazio quando não há linhas
    assert out.read_text(encoding="utf-8") == ""


def test_write_csv_file_rows(tmp_path: Path):
    out = tmp_path / "rows.csv"
    rows = [
        {"a": 1, "b": "x"},
        {"a": 2, "b": "y"},
    ]
    write_csv_file(str(out), rows)
    content = out.read_text(encoding="utf-8")
    assert "a,b" in content.splitlines()[0]  # cabeçalho
    assert "1,x" in content
    assert "2,y" in content
