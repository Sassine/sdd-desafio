"""Limites da política de reembolso v3, isolados (plan.md §4, spec.md §5)."""
from decimal import Decimal

TETOS = {
    "alimentacao": Decimal("60.00"),
    "transporte_urbano": Decimal("80.00"),
    "hospedagem": Decimal("250.00"),
}

PISO_NOTA_FISCAL = Decimal("100.00")

FATOR_VIAGEM = Decimal("1.5")

CATEGORIAS_COBERTAS = frozenset(TETOS)
