"""T-006 — RN-002: normalização de categoria (AMB-012)."""
from datetime import date
from decimal import Decimal

from src.motor.regras import normalizar_categoria
from src.motor.modelo import Despesa


def _despesa(categoria):
    return Despesa(
        id="d-014",
        data=date(2026, 7, 31),
        categoria=categoria,
        descricao="Jantar de encerramento",
        fornecedor="Restaurante Tavola",
        valor=Decimal("61.00"),
        tem_nota_fiscal=True,
    )


def test_rn_002_categoria_em_caixa_alta_e_normalizada():
    despesa = normalizar_categoria(_despesa("ALIMENTACAO"))
    assert despesa.categoria == "alimentacao"


def test_rn_002_categoria_com_espacos_nas_pontas_e_normalizada():
    despesa = normalizar_categoria(_despesa("  transporte_urbano  "))
    assert despesa.categoria == "transporte_urbano"


def test_rn_002_categoria_ja_normalizada_permanece_igual():
    original = _despesa("hospedagem")
    despesa = normalizar_categoria(original)
    assert despesa.categoria == "hospedagem"


def test_rn_002_normalizacao_preserva_demais_campos():
    despesa = normalizar_categoria(_despesa("ALIMENTACAO"))
    assert despesa.id == "d-014"
    assert despesa.valor == Decimal("61.00")
    assert despesa.tem_nota_fiscal is True
