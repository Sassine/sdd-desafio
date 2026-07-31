"""T-013 — RN-008: hospedagem vale uma diária por lançamento; descrição não é interpretada (AMB-007)."""
from datetime import date
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import rn_007_teto_categoria

from tests.fabricas import despesa

CONTEXTO_SEM_VIAGEM = Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_rn_008_hospedagem_conta_como_uma_diaria():
    d = despesa(
        id="d-010",
        data=date(2026, 7, 14),
        categoria="hospedagem",
        descricao="Hotel Rio - 2 diarias",
        valor=Decimal("480.00"),
    )

    parecer = rn_007_teto_categoria(d, CONTEXTO_SEM_VIAGEM)

    assert parecer.valor_reembolsavel == Decimal("250.00")
    assert parecer.status == Status.PARCIAL
    assert "RN-008" in parecer.regras_aplicadas


def test_rn_008_descricao_com_numero_de_noites_diferentes_nao_muda_o_resultado():
    tres_noites = despesa(categoria="hospedagem", descricao="Airbnb 3 noites", valor=Decimal("690.00"))
    sem_descricao_numerica = despesa(categoria="hospedagem", descricao="Hotel qualquer", valor=Decimal("690.00"))

    parecer_a = rn_007_teto_categoria(tres_noites, CONTEXTO_SEM_VIAGEM)
    parecer_b = rn_007_teto_categoria(sem_descricao_numerica, CONTEXTO_SEM_VIAGEM)

    assert parecer_a.valor_reembolsavel == parecer_b.valor_reembolsavel == Decimal("250.00")


def test_rn_008_regra_nao_e_marcada_para_outras_categorias():
    d = despesa(categoria="alimentacao", valor=Decimal("50.00"))
    parecer = rn_007_teto_categoria(d, CONTEXTO_SEM_VIAGEM)
    assert "RN-008" not in parecer.regras_aplicadas
