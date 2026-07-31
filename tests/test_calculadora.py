"""T-015 — calculadora encadeia as regras na ordem da spec.md §8."""
from datetime import date
from decimal import Decimal

from src.motor.calculadora import calcular
from src.motor.modelo import Solicitacao, Status

from tests.fabricas import despesa


def _solicitacao(despesas, competencia="2026-07"):
    return Solicitacao(
        colaborador={"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        competencia=competencia,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        despesas=tuple(despesas),
    )


def test_ordem_nota_fiscal_antes_do_teto():
    d = despesa(id="d-004", categoria="transporte_urbano", valor=Decimal("100.01"), tem_nota_fiscal=False)
    resultado = calcular(_solicitacao([d]))

    parecer = resultado.pareceres[0]
    assert parecer.valor_reembolsavel == Decimal("0.00")
    assert parecer.status == Status.RECUSADA
    assert "RN-006" in parecer.regras_aplicadas


def test_calculadora_produz_um_parecer_por_despesa_na_mesma_ordem():
    d1 = despesa(id="d-1", valor=Decimal("10.00"))
    d2 = despesa(id="d-2", valor=Decimal("20.00"))
    resultado = calcular(_solicitacao([d1, d2]))

    assert [p.despesa.id for p in resultado.pareceres] == ["d-1", "d-2"]


def test_calculadora_normaliza_categoria_antes_de_decidir():
    d = despesa(id="d-014", categoria="ALIMENTACAO", valor=Decimal("61.00"))
    resultado = calcular(_solicitacao([d]))

    parecer = resultado.pareceres[0]
    assert parecer.despesa.categoria == "alimentacao"
    assert parecer.valor_reembolsavel == Decimal("60.00")


def test_calculadora_aplica_duplicata_entre_despesas_da_mesma_solicitacao():
    primeira = despesa(id="d-006", data=date(2026, 7, 9), fornecedor="Bistro Central", valor=Decimal("54.90"))
    segunda = despesa(id="d-007", data=date(2026, 7, 9), fornecedor="Bistro Central", valor=Decimal("54.90"))
    resultado = calcular(_solicitacao([primeira, segunda]))

    assert resultado.pareceres[0].valor_reembolsavel == Decimal("54.90")
    assert resultado.pareceres[1].valor_reembolsavel == Decimal("0.00")
    assert resultado.pareceres[1].status == Status.RECUSADA


def test_calculadora_amplia_teto_em_data_de_viagem():
    hospedagem = despesa(id="d-010", data=date(2026, 7, 14), categoria="hospedagem", valor=Decimal("480.00"))
    resultado = calcular(_solicitacao([hospedagem]))

    assert resultado.pareceres[0].valor_reembolsavel == Decimal("375.00")


def test_calculadora_estorno_nao_e_afetado_por_teto():
    estorno = despesa(id="d-009", categoria="transporte_urbano", valor=Decimal("-500.00"))
    resultado = calcular(_solicitacao([estorno]))

    assert resultado.pareceres[0].valor_reembolsavel == Decimal("-500.00")
    assert resultado.pareceres[0].status == Status.ESTORNO
