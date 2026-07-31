"""T-010 — RN-005: estornos abatem o valor integral, sem teto e sem nota (AMB-010)."""
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import rn_005_estorno

from tests.fabricas import despesa

CONTEXTO = Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_rn_005_estorno_abate_valor_integral():
    d = despesa(id="d-009", categoria="transporte_urbano", valor=Decimal("-45.00"), tem_nota_fiscal=False)

    parecer = rn_005_estorno(d, CONTEXTO)

    assert parecer is not None
    assert parecer.valor_reembolsavel == Decimal("-45.00")
    assert parecer.status == Status.ESTORNO
    assert "RN-005" in parecer.regras_aplicadas


def test_rn_005_estorno_acima_do_teto_em_modulo_nao_e_limitado():
    d = despesa(categoria="alimentacao", valor=Decimal("-500.00"))

    parecer = rn_005_estorno(d, CONTEXTO)

    assert parecer.valor_reembolsavel == Decimal("-500.00")


def test_rn_005_valor_positivo_nao_decide():
    d = despesa(valor=Decimal("50.00"))
    assert rn_005_estorno(d, CONTEXTO) is None


def test_rn_005_valor_zero_nao_e_estorno():
    d = despesa(valor=Decimal("0.00"))
    assert rn_005_estorno(d, CONTEXTO) is None
