#!/usr/bin/env python3
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

# Make prints safe on Windows terminals without UTF-8
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PKG = os.getenv("COV_PKG", "ws_docflow")  # package under test
COV_XML = Path("coverage.xml")

FAIL_UNDER = float(os.getenv("COV_FAIL_UNDER", "85"))
WARN_UNDER = float(os.getenv("COV_WARN_UNDER", "90"))


def run_tests_with_coverage() -> int:
    cmd = [
        "pytest",
        "-q",
        f"--cov={PKG}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term",
    ]
    print("[coverage-gate] running:", " ".join(cmd))
    return subprocess.call(cmd)


def parse_total_coverage(xml_path: Path) -> float:
    tree = ET.parse(xml_path)
    rate = float(tree.getroot().attrib.get("line-rate", "0"))
    return rate * 100.0


def main() -> int:
    rc = run_tests_with_coverage()
    if rc != 0:
        print("\n[coverage-gate] Pytest falhou (testes vermelhos). Commit BLOQUEADO.")
        return rc or 1

    if not COV_XML.exists():
        print("[coverage-gate] coverage.xml não encontrado. Commit BLOQUEADO.")
        return 1

    total = parse_total_coverage(COV_XML)
    print(f"[coverage-gate] Cobertura total: {total:.2f}%")

    if total < FAIL_UNDER:
        print(
            f"[coverage-gate] Coverage {total:.2f}% < {FAIL_UNDER:.0f}% — commit BLOQUEADO."
        )
        return 1
    elif total < WARN_UNDER:
        print(
            f"[coverage-gate] Coverage {total:.2f}% < {WARN_UNDER:.0f}% — commit liberado com AVISO."
        )
        return 0
    else:
        print(f"[coverage-gate] Coverage OK (≥ {WARN_UNDER:.0f}%).")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
