from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


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
