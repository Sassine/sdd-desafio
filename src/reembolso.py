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
