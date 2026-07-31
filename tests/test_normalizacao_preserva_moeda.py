from decimal import Decimal

from src.reembolso import Despesa, normalizar_despesas


def test_normalizacao_preserva_campo_moeda():
    despesa = Despesa(
        id="e-teste",
        data="2026-07-14",
        categoria="ALIMENTACAO",
        descricao="teste",
        fornecedor="teste",
        valor_original=Decimal("22.00"),
        tem_nota_fiscal=True,
        moeda="EUR",
    )

    resultado = normalizar_despesas([despesa])

    assert resultado[0].moeda == "EUR"


def test_normalizacao_mantem_moeda_none_quando_ausente():
    despesa = Despesa(
        id="e-teste-2",
        data="2026-07-14",
        categoria="alimentacao",
        descricao="teste",
        fornecedor="teste",
        valor_original=Decimal("10.00"),
        tem_nota_fiscal=True,
    )

    resultado = normalizar_despesas([despesa])

    assert resultado[0].moeda is None