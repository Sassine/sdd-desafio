"""T-020 — resumo: totais e contagem por status batem com os itens (spec.md §4)."""
from datetime import date
from decimal import Decimal

from src.io.serializador import para_documento
from src.motor.calculadora import calcular
from src.motor.modelo import Solicitacao

from tests.fabricas import despesa


def _solicitacao(despesas):
    return Solicitacao(
        colaborador={"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        competencia="2026-07",
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        despesas=tuple(despesas),
    )


def test_soma_dos_itens_bate_com_o_resumo():
    despesas = [
        despesa(id="d-1", categoria="alimentacao", valor=Decimal("72.50")),
        despesa(id="d-2", categoria="coworking", valor=Decimal("89.00")),
        despesa(id="d-3", categoria="transporte_urbano", valor=Decimal("-45.00")),
    ]
    resultado = calcular(_solicitacao(despesas))
    documento = para_documento(resultado)

    soma_itens = sum(Decimal(item["valor_reembolsavel"]) for item in documento["itens"])

    assert f"{soma_itens:.2f}" == documento["resumo"]["total_reembolsavel"]
    assert documento["resumo"]["total_reembolsavel"] == f"{resultado.total_reembolsavel:.2f}"


def test_resumo_total_glosado_e_diferenca_entre_lancado_e_reembolsavel():
    despesas = [despesa(id="d-1", categoria="alimentacao", valor=Decimal("72.50"))]
    resultado = calcular(_solicitacao(despesas))
    documento = para_documento(resultado)

    lancado = Decimal(documento["resumo"]["total_lancado"])
    reembolsavel = Decimal(documento["resumo"]["total_reembolsavel"])
    glosado = Decimal(documento["resumo"]["total_glosado"])

    assert glosado == lancado - reembolsavel


def test_resumo_quantidade_por_status_soma_o_total_de_itens():
    despesas = [
        despesa(id="d-1", categoria="alimentacao", valor=Decimal("50.00")),
        despesa(id="d-2", categoria="coworking", valor=Decimal("89.00")),
        despesa(id="d-3", categoria="transporte_urbano", valor=Decimal("-45.00")),
    ]
    resultado = calcular(_solicitacao(despesas))
    documento = para_documento(resultado)

    assert sum(documento["resumo"]["quantidade_por_status"].values()) == len(documento["itens"])
    assert documento["resumo"]["quantidade_por_status"]["aprovada"] == 1
    assert documento["resumo"]["quantidade_por_status"]["recusada"] == 1
    assert documento["resumo"]["quantidade_por_status"]["estorno"] == 1
    assert documento["resumo"]["quantidade_por_status"]["parcial"] == 0
