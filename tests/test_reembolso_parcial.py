from decimal import Decimal
from pathlib import Path

from src.reembolso import (
    calcular_limite_diario,
    calcular_reembolso_parcial,
    carregar_despesas,
    normalizar_despesas,
)


def _carregar_despesas_exemplo():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"
    return normalizar_despesas(carregar_despesas(fixture))


def test_reembolso_parcial_quando_despesa_excede_limite():
    despesas = _carregar_despesas_exemplo()
    despesas_dia_03 = [despesa for despesa in despesas if despesa.data == "2026-07-03"]
    limites = calcular_limite_diario(despesas_dia_03)

    resultado = calcular_reembolso_parcial([next(d for d in despesas if d.id == "d-001")], limites)

    assert resultado[0]["valor_reembolsavel"] == Decimal("60.00")
    assert resultado[0]["valor_nao_reembolsavel"] == Decimal("12.50")


def test_reembolso_parcial_aplica_limite_ao_total_do_dia():
    despesas = _carregar_despesas_exemplo()
    despesas_dia_03 = [despesa for despesa in despesas if despesa.data == "2026-07-03"]
    limites = calcular_limite_diario(despesas_dia_03)

    despesas_alimentacao = [
        next(d for d in despesas if d.id == "d-001"),
        next(d for d in despesas if d.id == "d-002"),
    ]
    resultado = calcular_reembolso_parcial(despesas_alimentacao, limites)

    assert resultado[0]["valor_reembolsavel"] == Decimal("60.00")
    assert resultado[0]["valor_nao_reembolsavel"] == Decimal("12.50")
    assert resultado[1]["valor_reembolsavel"] == Decimal("0.00")
    assert resultado[1]["valor_nao_reembolsavel"] == Decimal("38.00")


def test_reembolso_parcial_quando_despesa_esta_dentro_do_limite():
    despesas = _carregar_despesas_exemplo()
    despesas_dia_09 = [despesa for despesa in despesas if despesa.data == "2026-07-09"]
    limites = calcular_limite_diario(despesas_dia_09)

    resultado = calcular_reembolso_parcial([next(d for d in despesas if d.id == "d-006")], limites)

    assert resultado[0]["valor_reembolsavel"] == Decimal("54.90")
    assert resultado[0]["valor_nao_reembolsavel"] == Decimal("0.00")
