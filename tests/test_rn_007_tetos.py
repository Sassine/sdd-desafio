"""T-012 — RN-007: teto por despesa (não por dia) e reembolso parcial (AMB-001/002)."""
from datetime import date
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import rn_007_teto_categoria

from tests.fabricas import despesa

CONTEXTO = Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_rn_007_teto_e_por_despesa_nao_por_dia():
    almoco = despesa(id="d-001", data=date(2026, 7, 3), categoria="alimentacao", valor=Decimal("72.50"))
    jantar = despesa(id="d-002", data=date(2026, 7, 3), categoria="alimentacao", valor=Decimal("38.00"))

    parecer_almoco = rn_007_teto_categoria(almoco, CONTEXTO)
    parecer_jantar = rn_007_teto_categoria(jantar, CONTEXTO)

    assert parecer_almoco.valor_reembolsavel == Decimal("60.00")
    assert parecer_almoco.status == Status.PARCIAL
    assert parecer_jantar.valor_reembolsavel == Decimal("38.00")
    assert parecer_jantar.status == Status.APROVADA


def test_rn_007_valor_no_teto_e_aprovado_integralmente():
    d = despesa(categoria="alimentacao", valor=Decimal("60.00"))

    parecer = rn_007_teto_categoria(d, CONTEXTO)

    assert parecer.status == Status.APROVADA
    assert parecer.valor_reembolsavel == Decimal("60.00")
    assert parecer.valor_glosado == Decimal("0.00")


def test_rn_007_um_centavo_acima_do_teto_e_parcial():
    d = despesa(categoria="alimentacao", valor=Decimal("60.01"))

    parecer = rn_007_teto_categoria(d, CONTEXTO)

    assert parecer.status == Status.PARCIAL
    assert parecer.valor_reembolsavel == Decimal("60.00")
    assert parecer.valor_glosado == Decimal("0.01")


def test_rn_007_tetos_por_categoria():
    casos = [
        ("alimentacao", Decimal("60.00")),
        ("transporte_urbano", Decimal("80.00")),
        ("hospedagem", Decimal("250.00")),
    ]
    for categoria, teto in casos:
        d = despesa(categoria=categoria, valor=teto + Decimal("1.00"))
        parecer = rn_007_teto_categoria(d, CONTEXTO)
        assert parecer.valor_reembolsavel == teto
        assert parecer.status == Status.PARCIAL


def test_rn_007_sempre_decide_nunca_devolve_none():
    d = despesa(valor=Decimal("10.00"))
    assert rn_007_teto_categoria(d, CONTEXTO) is not None
