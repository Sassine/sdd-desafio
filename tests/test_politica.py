"""T-005 — política v3 como constantes Decimal (plan.md §4)."""
from decimal import Decimal

from src.motor import politica


def test_politica_expoe_limites_da_v3():
    assert politica.TETOS["alimentacao"] == Decimal("60.00")
    assert politica.TETOS["transporte_urbano"] == Decimal("80.00")
    assert politica.TETOS["hospedagem"] == Decimal("250.00")
    assert politica.PISO_NOTA_FISCAL == Decimal("100.00")

    for valor in (*politica.TETOS.values(), politica.PISO_NOTA_FISCAL, politica.FATOR_VIAGEM):
        assert isinstance(valor, Decimal)
        assert not isinstance(valor, float)
