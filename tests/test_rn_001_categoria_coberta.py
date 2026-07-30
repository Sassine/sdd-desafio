"""T-008 — RN-001: categoria fora da política é recusada."""
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import rn_001_categoria_coberta

from tests.fabricas import despesa

CONTEXTO = Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_rn_001_categoria_fora_da_politica_e_recusada():
    d = despesa(id="d-005", categoria="coworking", valor=Decimal("89.00"))

    parecer = rn_001_categoria_coberta(d, CONTEXTO)

    assert parecer is not None
    assert parecer.valor_reembolsavel == Decimal("0.00")
    assert parecer.status == Status.RECUSADA
    assert "RN-001" in parecer.regras_aplicadas


def test_rn_001_categorias_cobertas_nao_decidem():
    for categoria in ("alimentacao", "transporte_urbano", "hospedagem"):
        d = despesa(categoria=categoria)
        assert rn_001_categoria_coberta(d, CONTEXTO) is None
