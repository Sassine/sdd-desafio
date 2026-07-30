"""T-002 — modelo de dados imutável (plan.md §3)."""
from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from src.motor.modelo import Despesa, Parecer, Resultado, Solicitacao, Status


def _despesa(**overrides):
    base = dict(
        id="d-001",
        data=date(2026, 7, 3),
        categoria="alimentacao",
        descricao="Almoco",
        fornecedor="Restaurante Tavola",
        valor=Decimal("60.00"),
        tem_nota_fiscal=True,
    )
    base.update(overrides)
    return Despesa(**base)


def _solicitacao(despesas):
    return Solicitacao(
        colaborador={"id": "c-0417", "nome": "Marina Volpi", "centro_custo": "CC-ENG"},
        competencia="2026-07",
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        despesas=tuple(despesas),
    )


def test_modelo_e_imutavel():
    despesa = _despesa()
    with pytest.raises(FrozenInstanceError):
        despesa.valor = Decimal("1.00")  # type: ignore[misc]


def test_modelo_e_imutavel_para_solicitacao_e_resultado():
    solicitacao = _solicitacao([_despesa()])
    with pytest.raises(FrozenInstanceError):
        solicitacao.competencia = "2026-08"  # type: ignore[misc]

    resultado = Resultado(solicitacao=solicitacao, pareceres=())
    with pytest.raises(FrozenInstanceError):
        resultado.pareceres = ()  # type: ignore[misc]


def test_total_reembolsavel_e_propriedade_calculada_nao_campo():
    assert "total_reembolsavel" not in Resultado.__dataclass_fields__
    assert "total_lancado" not in Resultado.__dataclass_fields__
    assert "total_glosado" not in Resultado.__dataclass_fields__

    despesa_aprovada = _despesa(id="d-001", valor=Decimal("60.00"))
    despesa_parcial = _despesa(id="d-002", valor=Decimal("72.50"))
    parecer_aprovado = Parecer(
        despesa=despesa_aprovada,
        valor_reembolsavel=Decimal("60.00"),
        status=Status.APROVADA,
        regras_aplicadas=("RN-007",),
        justificativa="dentro do teto",
    )
    parecer_parcial = Parecer(
        despesa=despesa_parcial,
        valor_reembolsavel=Decimal("60.00"),
        status=Status.PARCIAL,
        regras_aplicadas=("RN-007",),
        justificativa="acima do teto",
    )
    resultado = Resultado(
        solicitacao=_solicitacao([despesa_aprovada, despesa_parcial]),
        pareceres=(parecer_aprovado, parecer_parcial),
    )

    assert resultado.total_lancado == Decimal("132.50")
    assert resultado.total_reembolsavel == Decimal("120.00")
    assert resultado.total_glosado == Decimal("12.50")
    assert resultado.quantidade_por_status[Status.APROVADA] == 1
    assert resultado.quantidade_por_status[Status.PARCIAL] == 1
    assert resultado.quantidade_por_status[Status.RECUSADA] == 0
    assert resultado.quantidade_por_status[Status.ESTORNO] == 0


def test_valor_glosado_do_parecer_e_derivado_nao_armazenado():
    assert "valor_glosado" not in Parecer.__dataclass_fields__

    despesa = _despesa(valor=Decimal("72.50"))
    parecer = Parecer(
        despesa=despesa,
        valor_reembolsavel=Decimal("60.00"),
        status=Status.PARCIAL,
        regras_aplicadas=("RN-007",),
        justificativa="acima do teto",
    )
    assert parecer.valor_glosado == Decimal("12.50")
