from decimal import Decimal
from pathlib import Path

from src.reembolso import Despesa, carregar_despesas, normalizar_despesas


def test_normalizacao_de_categoria_e_data_passa():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"

    despesas = carregar_despesas(fixture)
    despesas_normalizadas = normalizar_despesas(despesas)

    assert despesas_normalizadas[13].categoria == "alimentacao"
    assert despesas_normalizadas[10].valor_original == Decimal("33.33")
    assert despesas_normalizadas[0].data == "2026-07-03"
    assert despesas_normalizadas[0].categoria == "alimentacao"
    assert despesas_normalizadas[0].valor_original == Decimal("72.50")
    assert despesas[13].categoria == "ALIMENTACAO"


def test_normalizacao_arredonda_half_up_em_caso_de_empate():
    despesas = [
        Despesa(
            id="d-empate",
            data="2026-07-01",
            categoria="ALIMENTACAO",
            descricao="Despesa de teste",
            fornecedor="Fornecedor",
            valor_original=Decimal("72.505"),
            tem_nota_fiscal=True,
        )
    ]

    despesas_normalizadas = normalizar_despesas(despesas)

    assert despesas_normalizadas[0].valor_original == Decimal("72.51")
    assert despesas_normalizadas[0].categoria == "alimentacao"