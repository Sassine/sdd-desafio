"""T-014 — RN-009: contexto de viagem por data com hospedagem (AMB-006)."""
from datetime import date
from decimal import Decimal

from src.motor.modelo import Status
from src.motor.regras import construir_contexto, rn_006_nota_fiscal, rn_007_teto_categoria

from tests.fabricas import despesa

DATA_VIAGEM = date(2026, 7, 14)


def test_rn_009_data_com_hospedagem_amplia_tetos():
    hospedagem = despesa(id="d-010", data=DATA_VIAGEM, categoria="hospedagem", valor=Decimal("480.00"))
    contexto = construir_contexto((hospedagem,), competencia="2026-07")

    parecer = rn_007_teto_categoria(hospedagem, contexto)

    assert parecer.valor_reembolsavel == Decimal("375.00")
    assert "RN-009" in parecer.regras_aplicadas


def test_rn_009_hospedagem_recusada_ainda_caracteriza_viagem():
    hospedagem_sem_nota = despesa(
        id="d-013", data=DATA_VIAGEM, categoria="hospedagem", valor=Decimal("690.00"), tem_nota_fiscal=False
    )
    almoco_mesma_data = despesa(id="d-x", data=DATA_VIAGEM, categoria="alimentacao", valor=Decimal("85.00"))

    contexto = construir_contexto((hospedagem_sem_nota, almoco_mesma_data), competencia="2026-07")

    assert DATA_VIAGEM in contexto.datas_em_viagem
    # a hospedagem em si seria recusada por falta de nota fiscal (RN-006)...
    assert rn_006_nota_fiscal(hospedagem_sem_nota, contexto).status == Status.RECUSADA
    # ...mas isso nao impede a data de contar como viagem.

    parecer_almoco = rn_007_teto_categoria(almoco_mesma_data, contexto)
    assert parecer_almoco.status == Status.APROVADA
    assert parecer_almoco.valor_reembolsavel == Decimal("85.00")


def test_rn_009_viagem_nao_amplia_piso_da_nota():
    d = despesa(id="d-y", data=DATA_VIAGEM, categoria="alimentacao", valor=Decimal("105.00"), tem_nota_fiscal=False)
    hospedagem = despesa(id="d-010", data=DATA_VIAGEM, categoria="hospedagem", valor=Decimal("480.00"))
    contexto = construir_contexto((hospedagem, d), competencia="2026-07")

    parecer = rn_006_nota_fiscal(d, contexto)

    assert parecer is not None
    assert parecer.status == Status.RECUSADA


def test_rn_009_data_sem_hospedagem_nao_e_viagem():
    almoco = despesa(id="d-z", data=date(2026, 7, 3), categoria="alimentacao", valor=Decimal("72.50"))
    contexto = construir_contexto((almoco,), competencia="2026-07")

    assert contexto.datas_em_viagem == frozenset()

    parecer = rn_007_teto_categoria(almoco, contexto)
    assert parecer.valor_reembolsavel == Decimal("60.00")


def test_rn_009_viagem_e_por_categoria_normalizada():
    hospedagem_caixa_alta = despesa(id="d-w", data=DATA_VIAGEM, categoria="HOSPEDAGEM", valor=Decimal("300.00"))
    contexto = construir_contexto((hospedagem_caixa_alta,), competencia="2026-07")

    assert DATA_VIAGEM in contexto.datas_em_viagem
