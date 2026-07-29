from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_despesas, identificar_ajuste, normalizar_despesas


def _carregar_despesas_exemplo():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"
    return normalizar_despesas(carregar_despesas(fixture))


def test_valor_negativo_eh_identificado_como_ajuste():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-009")

    ajuste, motivo = identificar_ajuste(despesa)

    assert ajuste is True
    assert motivo == "ajuste"


def test_valor_positivo_nao_eh_identificado_como_ajuste():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-001")

    ajuste, motivo = identificar_ajuste(despesa)

    assert ajuste is False
    assert motivo is None


def test_valor_zero_nao_eh_identificado_como_ajuste():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas)
    despesa_zero = type(despesa)(
        id="synthetic-zero",
        data=despesa.data,
        categoria=despesa.categoria,
        descricao=despesa.descricao,
        fornecedor=despesa.fornecedor,
        valor_original=Decimal("0.00"),
        tem_nota_fiscal=despesa.tem_nota_fiscal,
    )

    ajuste, motivo = identificar_ajuste(despesa_zero)

    assert ajuste is False
    assert motivo is None
