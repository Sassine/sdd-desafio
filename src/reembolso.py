from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


@dataclass(frozen=True)
class Despesa:
    id: str
    data: str
    categoria: str
    descricao: str
    fornecedor: str
    valor_original: Decimal
    tem_nota_fiscal: bool


def carregar_despesas(caminho: str | Path) -> list[Despesa]:
    path = Path(caminho)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    despesas_payload = payload.get("despesas", [])
    despesas: list[Despesa] = []

    for item in despesas_payload:
        despesas.append(
            Despesa(
                id=item["id"],
                data=item["data"],
                categoria=item["categoria"],
                descricao=item["descricao"],
                fornecedor=item["fornecedor"],
                valor_original=Decimal(str(item["valor"])),
                tem_nota_fiscal=bool(item["tem_nota_fiscal"]),
            )
        )

    return despesas


def normalizar_despesas(despesas: list[Despesa]) -> list[Despesa]:
    normalizadas: list[Despesa] = []

    for despesa in despesas:
        valor_normalizado = despesa.valor_original.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        normalizadas.append(
            Despesa(
                id=despesa.id,
                data=despesa.data,
                categoria=despesa.categoria.lower(),
                descricao=despesa.descricao,
                fornecedor=despesa.fornecedor,
                valor_original=valor_normalizado,
                tem_nota_fiscal=despesa.tem_nota_fiscal,
            )
        )

    return normalizadas


def validar_categoria(despesa: Despesa) -> tuple[bool, str | None]:
    categorias_aceitas = {"alimentacao", "transporte_urbano", "hospedagem"}

    if despesa.categoria in categorias_aceitas:
        return True, None

    return False, "categoria_nao_politica"


def calcular_limite_diario(despesas: list[Despesa]) -> dict[str, Decimal]:
    limites = {
        "alimentacao": Decimal("60.00"),
        "transporte_urbano": Decimal("80.00"),
    }

    tem_evidencia_viagem = any(despesa.categoria == "hospedagem" for despesa in despesas)

    if tem_evidencia_viagem:
        limites["alimentacao"] = Decimal("90.00")
        limites["transporte_urbano"] = Decimal("120.00")

    return limites


def calcular_reembolso_parcial(despesas: list[Despesa], limites: dict[str, Decimal]) -> list[dict[str, Decimal]]:
    if not despesas:
        return []

    categoria = despesas[0].categoria
    limite_categoria = limites.get(categoria, Decimal("0.00"))
    saldo_restante = limite_categoria
    resultados: list[dict[str, Decimal]] = []

    for despesa in despesas:
        valor = despesa.valor_original

        if valor <= Decimal("0.00"):
            reembolsavel = Decimal("0.00")
            nao_reembolsavel = Decimal("0.00")
        elif valor <= saldo_restante:
            reembolsavel = valor
            nao_reembolsavel = Decimal("0.00")
            saldo_restante -= valor
        else:
            reembolsavel = saldo_restante
            nao_reembolsavel = valor - saldo_restante
            saldo_restante = Decimal("0.00")

        resultados.append(
            {
                "valor_reembolsavel": reembolsavel,
                "valor_nao_reembolsavel": nao_reembolsavel,
            }
        )

    return resultados
