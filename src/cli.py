from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.reembolso import (
    carregar_cambio,
    carregar_politica,
    processar_despesas,
    processar_despesas_v4,
)


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
    parser.add_argument("--politica", required=False, help="Caminho da politica-v4.json (ativa o pipeline v4)")
    parser.add_argument("--cambio", required=False, help="Caminho do cambio.json (ativa o pipeline v4)")
    args = parser.parse_args(argv)

    if bool(args.politica) != bool(args.cambio):
        print(
            "Erro: --politica e --cambio devem ser usados juntos, "
            "ou nenhum dos dois (para usar o pipeline padrao).",
            file=sys.stderr,
        )
        return 1

    with Path(args.input).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if args.politica and args.cambio:
        politica = carregar_politica(args.politica)
        cambio = carregar_cambio(args.cambio)
        resultado = processar_despesas_v4(payload, politica, cambio)
    else:
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