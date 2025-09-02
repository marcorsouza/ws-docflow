from __future__ import annotations

from decimal import Decimal

from ws_docflow.cli.formatters import _json_default, to_json_string


def test__json_default_decimal_to_float():
    assert _json_default(Decimal("12.34")) == 12.34  # float


class Weird:
    def __str__(self) -> str:
        return "WEIRD"


def test__json_default_falls_back_to_str():
    w = Weird()
    assert _json_default(w) == "WEIRD"


def test_to_json_string_uses__json_default():
    # integração rápida: garante que to_json_string aplica _json_default
    out = to_json_string({"v": Decimal("1.50")})
    assert '"v": 1.5' in out
