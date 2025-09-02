from __future__ import annotations

import builtins
import importlib
import sys
from decimal import Decimal


def _import_blocking_formatters(name, globals=None, locals=None, fromlist=(), level=0):
    # Bloqueia especificamente o import do módulo de formatters
    if name == "ws_docflow.cli.formatters":
        raise ImportError("simulated import error for ws_docflow.cli.formatters")
    return _original_import(name, globals, locals, fromlist, level)


def _reload_app_forcing_fallback(monkeypatch):
    """
    Força o app.py a cair no bloco de fallback (sem formatters):
    - intercepta __import__ para levantar ImportError em ws_docflow.cli.formatters
    - remove o módulo app do sys.modules para reimportar 'do zero'
    """
    monkeypatch.setenv("PYTHONHASHSEED", "0")  # determinismo (opcional)

    # intercepta import
    global _original_import
    _original_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", _import_blocking_formatters)

    # garante um import "frio"
    sys.modules.pop("ws_docflow.cli.app", None)

    # agora importa o app.py; como o import de formatters falha,
    # o app define os helpers de fallback (_json_default, to_json_string, etc.)
    app_mod = importlib.import_module("ws_docflow.cli.app")
    return app_mod


def test__json_default_decimal_and_str(monkeypatch):
    app_mod = _reload_app_forcing_fallback(monkeypatch)
    json_default = getattr(app_mod, "_json_default")

    # Decimal -> float
    assert json_default(Decimal("10.5")) == 10.5

    # Objeto genérico -> str()
    class Foo:
        def __str__(self) -> str:
            return "FOO!"

    assert json_default(Foo()) == "FOO!"


def test_to_json_string_uses__json_default(monkeypatch):
    app_mod = _reload_app_forcing_fallback(monkeypatch)
    to_json_string = getattr(app_mod, "to_json_string")

    class Bar:
        def __str__(self) -> str:
            return "BAR-OBJ"

    payload = {
        "totais_origem": {"valor_total_usd": Decimal("1.50")},
        "obj_custom": Bar(),
    }
    out = to_json_string(payload)
    # Decimal vira número (não string)
    assert '"valor_total_usd": 1.5' in out
    # Objeto custom usa str()
    assert '"obj_custom": "BAR-OBJ"' in out


def test__flatten_for_csv_returns_expected_headers_and_row(monkeypatch):
    app_mod = _reload_app_forcing_fallback(monkeypatch)
    flatten = getattr(app_mod, "_flatten_for_csv")

    payload = {
        "origem": {
            "unidade_local": {"codigo": "8765432", "descricao": "PORTO DE SANTOS"},
            "recinto_aduaneiro": {"codigo": "1234567", "descricao": "TECON"},
        },
        "destino": {
            "unidade_local": {"codigo": "7654321", "descricao": "PORTO DE ITAJAÍ"},
            "recinto_aduaneiro": {"codigo": "2345678", "descricao": "PORTONAVE"},
        },
        "beneficiario": {"documento": "11.222.333/0001-44", "nome": "COMPANHIA"},
        "transportador": {"documento": "55.666.777/0001-88", "nome": "NAVIOS"},
        "totais_origem": {
            "tipo": "ARMAZENAMENTO",
            "valor_total_usd": 45200.75,
            "valor_total_brl": 235000.40,
        },
    }

    headers, row = flatten(payload)

    # cabeçalhos chave
    assert "origem_unidade_local_codigo" in headers
    assert "destino_recinto_descricao" in headers
    assert "beneficiario_documento" in headers
    assert "transportador_nome" in headers
    assert "totais_valor_total_usd" in headers

    # valores mapeados
    assert row["origem_unidade_local_codigo"] == "8765432"
    assert row["origem_recinto_descricao"] == "TECON"
    assert row["destino_unidade_local_codigo"] == "7654321"
    assert row["destino_recinto_descricao"] == "PORTONAVE"
    assert row["beneficiario_documento"] == "11.222.333/0001-44"
    assert row["transportador_nome"] == "NAVIOS"
    assert row["totais_tipo"] == "ARMAZENAMENTO"
    assert row["totais_valor_total_usd"] == 45200.75
    assert row["totais_valor_total_brl"] == 235000.40


def test_to_csv_string_outputs_header_and_row(monkeypatch):
    app_mod = _reload_app_forcing_fallback(monkeypatch)
    to_csv_string = getattr(app_mod, "to_csv_string")

    payload = {
        "origem": {"unidade_local": {"codigo": "1111111", "descricao": "PORTO X"}},
        "destino": {"unidade_local": {"codigo": "2222222", "descricao": "PORTO Y"}},
        "beneficiario": {"documento": "00.000.000/0001-00", "nome": "ACME"},
        "transportador": {"documento": "99.999.999/0001-99", "nome": "CARGAS"},
        "totais_origem": {"tipo": "SERVICO", "valor_total_usd": 1.23, "valor_total_brl": 10.0},
    }

    csv_out = to_csv_string(payload)
    header = csv_out.splitlines()[0] if csv_out else ""
    # cabeçalho
    assert "origem_unidade_local_codigo" in header
    assert "beneficiario_documento" in header
    # valores
    assert "1111111" in csv_out
    assert "ACME" in csv_out
    assert "1.23" in csv_out
