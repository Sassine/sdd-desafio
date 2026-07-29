from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.reembolso import processar_despesas


def _serializar_json(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {key: _serializar_json(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_serializar_json(item) for item in obj]
    return obj


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="calcular")
    parser.add_argument("--input", required=True, help="Caminho do arquivo JSON de entrada")
    parser.add_argument("--output", required=True, help="Caminho do arquivo JSON de saída")
    args = parser.parse_args(argv)

    with Path(args.input).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    resultado = processar_despesas(payload)
    resultado_serializado = _serializar_json(resultado)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(resultado_serializado, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
