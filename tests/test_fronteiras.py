"""T-017 — fronteiras testadas dos dois lados (plan.md §6, CLAUDE.md).

Reúne num só teste os quatro valores que a spec fixa como limite: testar só
o lado que passa é o jeito mais comum de a suíte ficar verde com a regra
errada.
"""
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import rn_006_nota_fiscal, rn_007_teto_categoria

from tests.fabricas import despesa

CONTEXTO = Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_fronteiras_inclusivas_e_exclusivas():
    no_piso = despesa(valor=Decimal("100.00"), tem_nota_fiscal=False)
    acima_do_piso = despesa(valor=Decimal("100.01"), tem_nota_fiscal=False)
    no_teto = despesa(categoria="alimentacao", valor=Decimal("60.00"))
    acima_do_teto = despesa(categoria="alimentacao", valor=Decimal("60.01"))

    assert rn_006_nota_fiscal(no_piso, CONTEXTO) is None

    parecer_acima_piso = rn_006_nota_fiscal(acima_do_piso, CONTEXTO)
    assert parecer_acima_piso is not None
    assert parecer_acima_piso.status == Status.RECUSADA
    assert parecer_acima_piso.valor_reembolsavel == Decimal("0.00")

    parecer_no_teto = rn_007_teto_categoria(no_teto, CONTEXTO)
    assert parecer_no_teto.status == Status.APROVADA
    assert parecer_no_teto.valor_glosado == Decimal("0.00")

    parecer_acima_teto = rn_007_teto_categoria(acima_do_teto, CONTEXTO)
    assert parecer_acima_teto.status == Status.PARCIAL
    assert parecer_acima_teto.valor_reembolsavel == Decimal("60.00")
    assert parecer_acima_teto.valor_glosado == Decimal("0.01")
