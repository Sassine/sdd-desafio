"""T-007 — RN-003: despesa fora do período de competência (AMB-009)."""
from datetime import date
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import rn_003_competencia

from tests.fabricas import despesa


def _contexto():
    return Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_rn_003_despesa_fora_da_competencia_e_recusada():
    d = despesa(id="d-008", data=date(2026, 4, 15), valor=Decimal("41.00"))

    parecer = rn_003_competencia(d, _contexto())

    assert parecer is not None
    assert parecer.valor_reembolsavel == Decimal("0.00")
    assert parecer.status == Status.RECUSADA
    assert "RN-003" in parecer.regras_aplicadas


def test_rn_003_despesa_dentro_da_competencia_nao_decide():
    d = despesa(id="d-001", data=date(2026, 7, 3))

    assert rn_003_competencia(d, _contexto()) is None


def test_rn_003_limites_do_mes_de_competencia():
    primeiro_dia = despesa(id="d-a", data=date(2026, 7, 1))
    ultimo_dia = despesa(id="d-b", data=date(2026, 7, 31))

    assert rn_003_competencia(primeiro_dia, _contexto()) is None
    assert rn_003_competencia(ultimo_dia, _contexto()) is None


def test_rn_003_um_dia_fora_do_mes_e_recusada():
    dia_seguinte = despesa(id="d-c", data=date(2026, 8, 1))

    parecer = rn_003_competencia(dia_seguinte, _contexto())

    assert parecer.status == Status.RECUSADA
