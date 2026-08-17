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
DEFAULT_POLICY = {
    "padrao": {
        "alimentacao": {"limite": Decimal("60.00"), "periodicidade": "dia"},
        "transporte_urbano": {"limite": Decimal("80.00"), "periodicidade": "dia"},
        "hospedagem": {"limite": Decimal("250.00"), "periodicidade": "diaria"},
    },
    "nota_fiscal_obrigatoria_acima_de": Decimal("100.00"),
    "acrescimo_em_viagem_percentual": Decimal("1.50"),
}


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _normalize_category(value: str) -> str:
    return " ".join(value.lower().split())


def _load_policy(policy_path: str | Path | None) -> dict[str, Any]:
    if policy_path is None:
        return DEFAULT_POLICY

    data = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    policy = {
        "padrao": {},
        "centros_custo": {},
        "nota_fiscal_obrigatoria_acima_de": Decimal("100.00"),
        "acrescimo_em_viagem_percentual": Decimal("1.50"),
    }

    padrao = data.get("padrao", {})
    for category, settings in padrao.items():
        policy["padrao"][category] = {
            "limite": _to_decimal(settings.get("limite", LIMITS.get(category, Decimal("0.00")))),
            "periodicidade": settings.get("periodicidade", "dia"),
        }

    policy["centros_custo"] = data.get("centros_custo", {})
    if data.get("nota_fiscal_obrigatoria_acima_de") is not None:
        policy["nota_fiscal_obrigatoria_acima_de"] = _to_decimal(data["nota_fiscal_obrigatoria_acima_de"])
    if data.get("acrescimo_em_viagem_percentual") is not None:
        policy["acrescimo_em_viagem_percentual"] = _to_decimal(data["acrescimo_em_viagem_percentual"])

    return policy


def _load_exchange_rates(cambio_path: str | Path | None) -> dict[str, dict[str, Decimal]]:
    if cambio_path is None:
        return {}

    data = json.loads(Path(cambio_path).read_text(encoding="utf-8"))
    rates: dict[str, dict[str, Decimal]] = {}
    for date, values in data.get("taxas", {}).items():
        rates[date] = {currency: _to_decimal(rate) for currency, rate in values.items()}
    return rates


def _resolve_effective_policy(policy: dict[str, Any], centro_custo: str | None) -> dict[str, dict[str, Any]]:
    effective_policy: dict[str, dict[str, Any]] = {}
    for category, settings in policy.get("padrao", {}).items():
        effective_policy[category] = {
            "limite": settings.get("limite", Decimal("0.00")),
            "periodicidade": settings.get("periodicidade", "dia"),
        }

    center_policy = policy.get("centros_custo", {}).get(centro_custo or "", {})
    for category, settings in center_policy.items():
        effective_policy[category] = {
            "limite": _to_decimal(settings.get("limite", effective_policy.get(category, {}).get("limite", Decimal("0.00")))),
            "periodicidade": settings.get("periodicidade", effective_policy.get(category, {}).get("periodicidade", "dia")),
        }

    return effective_policy


def _resolve_exchange_rate(expense_date: str, rates: dict[str, dict[str, Decimal]], currency: str) -> Decimal | None:
    if currency == "BRL":
        return Decimal("1.00")

    available_dates = sorted(date for date in rates if date <= expense_date)
    if not available_dates:
        return None

    for date in reversed(available_dates):
        rate = rates[date].get(currency)
        if rate is not None:
            return rate

    return None


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


def evaluate_expenses(payload: dict[str, Any], policy_path: str | Path | None = None, cambio_path: str | Path | None = None) -> dict[str, Any]:
    periodo_inicio = payload["periodo"]["inicio"]
    periodo_fim = payload["periodo"]["fim"]
    results: list[dict[str, Any]] = []
    seen: list[dict[str, Any]] = []
    daily_usage: dict[tuple[str, str], Decimal] = {}
    policy = _load_policy(policy_path)
    exchange_rates = _load_exchange_rates(cambio_path)
    effective_policy = _resolve_effective_policy(policy, payload.get("colaborador", {}).get("centro_custo"))
    travel_days = {
        raw["data"]
        for raw in payload["despesas"]
        if _normalize_category(str(raw["categoria"])) == "hospedagem"
    }

    for raw in payload["despesas"]:
        expense = dict(raw)
        expense["categoria"] = _normalize_category(expense["categoria"])
        expense["valor"] = _to_decimal(expense["valor"])
        expense["moeda"] = str(expense.get("moeda", "BRL")).upper()

        if expense["valor"] <= 0:
            results.append(
                {
                    "id": expense["id"],
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": 0.0,
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
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["fora_do_periodo"],
                }
            )
            continue

        if expense["categoria"] not in effective_policy:
            results.append(
                {
                    "id": expense["id"],
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["categoria_nao_politica"],
                }
            )
            continue

        center_custo = payload.get("colaborador", {}).get("centro_custo")
        if center_custo == "CC-ENG-PLATAFORMA" and expense["categoria"] == "hospedagem":
            results.append(
                {
                    "id": expense["id"],
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["hospedagem_nao_reembolsavel"],
                }
            )
            continue

        exchange_rate = _resolve_exchange_rate(expense["data"], exchange_rates, expense["moeda"])
        if expense["moeda"] != "BRL" and exchange_rate is None:
            results.append(
                {
                    "id": expense["id"],
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": float(expense["valor"]),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["taxa_cambio_indisponivel"],
                }
            )
            continue

        if expense["moeda"] == "BRL":
            value_brl = expense["valor"]
        else:
            value_brl = expense["valor"] * exchange_rate

        value_brl = value_brl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if _is_duplicate(seen, expense):
            results.append(
                {
                    "id": expense["id"],
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": float(value_brl),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["duplicata"],
                }
            )
            continue

        seen.append(expense)

        if value_brl > policy.get("nota_fiscal_obrigatoria_acima_de", Decimal("100.00")) and not expense["tem_nota_fiscal"]:
            results.append(
                {
                    "id": expense["id"],
                    "data": expense["data"],
                    "categoria": expense["categoria"],
                    "valor_original": float(value_brl),
                    "valor_reembolsavel": 0.0,
                    "status": "nao_reembolsavel",
                    "motivo": ["nota_fiscal_obrigatoria"],
                }
            )
            continue

        daily_key = (expense["categoria"], expense["data"])
        used_today = daily_usage.get(daily_key, Decimal("0.00"))
        base_limit = effective_policy[expense["categoria"]]["limite"]
        multiplier = policy.get("acrescimo_em_viagem_percentual", Decimal("1.50")) if expense["data"] in travel_days else Decimal("1.00")
        effective_limit = base_limit * multiplier
        remaining = effective_limit - used_today
        reimbursable = min(value_brl, remaining)

        if reimbursable < value_brl:
            status = "reembolsado_parcialmente"
        else:
            status = "reembolsado"

        daily_usage[daily_key] = used_today + reimbursable
        results.append(
            {
                "id": expense["id"],
                "data": expense["data"],
                "categoria": expense["categoria"],
                "valor_original": float(value_brl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "valor_reembolsavel": float(reimbursable.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "status": status,
                "motivo": ["limite_diario"],
            }
        )

    total_original = sum(_to_decimal(item["valor_original"]) for item in results if item["status"] != "nao_reembolsavel" or item["motivo"] != ["valor_nao_reembolsavel"])
    total_reembulsavel = sum(_to_decimal(item["valor_reembolsavel"]) for item in results)

    return {
        "colaborador": payload["colaborador"],
        "periodo": payload["periodo"],
        "resumo": {
            "quantidade_itens": len(results),
            "valor_original": float(total_original.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "valor_reembolsavel": float(total_reembulsavel.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        },
        "itens": results,
    }


def write_output_file(result: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def process_input_file(input_path: str | Path, output_path: str | Path, policy_path: str | Path | None = None, cambio_path: str | Path | None = None) -> dict[str, Any]:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    result = evaluate_expenses(payload, policy_path=policy_path, cambio_path=cambio_path)
    write_output_file(result, output_path)
    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--policy")
    parser.add_argument("--cambio")
    args = parser.parse_args()

    process_input_file(args.input, args.output, policy_path=args.policy, cambio_path=args.cambio)


if __name__ == "__main__":
    main()
