from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ALLOWED_CATEGORIES = {"alimentacao", "transporte_urbano", "hospedagem"}
LIMITS = {
    "alimentacao": Decimal("60.00"),
    "transporte_urbano": Decimal("80.00"),
    "hospedagem": Decimal("250.00"),
}


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _normalize_category(value: str) -> str:
    return " ".join(value.lower().split())


def _is_duplicate(existing: list[dict[str, Any]], candidate: dict[str, Any]) -> bool:
    for item in existing:
        if (
            item["data"] == candidate["data"]
            and item["categoria"] == candidate["categoria"]
            and item["fornecedor"] == candidate["fornecedor"]
            and item["descricao"] == candidate["descricao"]
            and item["valor"] == candidate["valor"]
        ):
            return True
    return False


def evaluate_expenses(payload: dict[str, Any]) -> dict[str, Any]:
    periodo_inicio = payload["periodo"]["inicio"]
    periodo_fim = payload["periodo"]["fim"]
    results: list[dict[str, Any]] = []
    seen: list[dict[str, Any]] = []
    daily_usage: dict[tuple[str, str], Decimal] = {}

    for raw in payload["despesas"]:
        expense = dict(raw)
        expense["categoria"] = _normalize_category(expense["categoria"])
        expense["valor"] = _to_decimal(expense["valor"])

        if expense["valor"] <= 0:
            results.append(
                {
                    "id": expense["id"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["valor_nao_reembolsavel"],
                }
            )
            continue

        if not (periodo_inicio <= expense["data"] <= periodo_fim):
            results.append(
                {
                    "id": expense["id"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["fora_do_periodo"],
                }
            )
            continue

        if expense["categoria"] not in ALLOWED_CATEGORIES:
            results.append(
                {
                    "id": expense["id"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["categoria_nao_politica"],
                }
            )
            continue

        if _is_duplicate(seen, expense):
            results.append(
                {
                    "id": expense["id"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["duplicata"],
                }
            )
            continue

        seen.append(expense)

        if expense["valor"] > Decimal("100.00") and not expense["tem_nota_fiscal"]:
            results.append(
                {
                    "id": expense["id"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["nota_fiscal_obrigatoria"],
                }
            )
            continue

        daily_key = (expense["categoria"], expense["data"])
        used_today = daily_usage.get(daily_key, Decimal("0.00"))
        remaining = LIMITS[expense["categoria"]] - used_today
        reimbursable = min(expense["valor"], remaining)

        if reimbursable < expense["valor"]:
            status = "reembolsado_parcialmente"
        else:
            status = "reembolsado"

        daily_usage[daily_key] = used_today + reimbursable
        results.append(
            {
                "id": expense["id"],
                "categoria": expense["categoria"],
                "valor_original": float(expense["valor"]),
                "valor_reembolsavel": float(reimbursable.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "status": status,
                "motivo": ["limite_diario"],
            }
        )

    total_original = sum(_to_decimal(item["valor_original"]) for item in results if item["status"] != "nao_reembolsavel" or item["motivo"] != ["valor_nao_reembolsavel"])
    total_reembolsavel = sum(_to_decimal(item["valor_reembolsavel"]) for item in results)

    return {
        "colaborador": payload["colaborador"],
        "periodo": payload["periodo"],
        "resumo": {
            "quantidade_itens": len(results),
            "valor_original": float(total_original.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "valor_reembolsavel": float(total_reembolsavel.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        },
        "itens": results,
    }


def write_output_file(result: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def process_input_file(input_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    result = evaluate_expenses(payload)
    write_output_file(result, output_path)
    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    process_input_file(args.input, args.output)


if __name__ == "__main__":
    main()
