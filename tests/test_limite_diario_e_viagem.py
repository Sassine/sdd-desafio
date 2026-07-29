from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_despesas, calcular_limite_diario, normalizar_despesas


def test_limite_diario_e_viagem():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"

    despesas = normalizar_despesas(carregar_despesas(fixture))

    despesas_dia_03 = [despesa for despesa in despesas if despesa.data == "2026-07-03"]
    limites = calcular_limite_diario(despesas_dia_03)

    assert limites["alimentacao"] == Decimal("60.00")
    assert limites["transporte_urbano"] == Decimal("80.00")

    despesas_dia_14 = [despesa for despesa in despesas if despesa.data == "2026-07-14"]
    limites_viagem = calcular_limite_diario(despesas_dia_14)

    assert limites_viagem["alimentacao"] == Decimal("90.00")
    assert limites_viagem["transporte_urbano"] == Decimal("120.00")

    despesas_dia_06 = [despesa for despesa in despesas if despesa.data == "2026-07-06"]
    limites_sem_viagem = calcular_limite_diario(despesas_dia_06)

    assert limites_sem_viagem["alimentacao"] == Decimal("60.00")
    assert limites_sem_viagem["transporte_urbano"] == Decimal("80.00")
