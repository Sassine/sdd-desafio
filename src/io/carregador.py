"""Le o arquivo de entrada e produz uma Solicitacao (plan.md secao 2, DT-001)."""
import json
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from src.motor.modelo import Despesa, Solicitacao

DUAS_CASAS = Decimal("0.01")


def carregar(caminho: str) -> Solicitacao:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo, parse_float=Decimal)
    return _para_solicitacao(dados)


def _arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)


def _para_despesa(dados: dict) -> Despesa:
    return Despesa(
        id=dados["id"],
        data=date.fromisoformat(dados["data"]),
        categoria=dados["categoria"],
        descricao=dados["descricao"],
        fornecedor=dados["fornecedor"],
        valor=_arredondar(Decimal(dados["valor"])),
        tem_nota_fiscal=dados["tem_nota_fiscal"],
    )


def _para_solicitacao(dados: dict) -> Solicitacao:
    periodo = dados["periodo"]
    despesas = tuple(_para_despesa(item) for item in dados["despesas"])
    return Solicitacao(
        colaborador=dados["colaborador"],
        competencia=periodo["competencia"],
        inicio=date.fromisoformat(periodo["inicio"]),
        fim=date.fromisoformat(periodo["fim"]),
        despesas=despesas,
    )
