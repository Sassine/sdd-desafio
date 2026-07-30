"""Fábrica de Despesa com valores default para os testes de regra (DT-006)."""
from datetime import date
from decimal import Decimal

from src.motor.modelo import Despesa


def despesa(
    *,
    id="d-teste",
    data=date(2026, 7, 3),
    categoria="alimentacao",
    descricao="Despesa de teste",
    fornecedor="Fornecedor Teste",
    valor=Decimal("50.00"),
    tem_nota_fiscal=True,
) -> Despesa:
    return Despesa(
        id=id,
        data=data,
        categoria=categoria,
        descricao=descricao,
        fornecedor=fornecedor,
        valor=valor,
        tem_nota_fiscal=tem_nota_fiscal,
    )
