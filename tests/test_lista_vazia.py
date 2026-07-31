"""T-018 — lista de despesas vazia produz resultado válido (spec.md §7, última linha)."""
from datetime import date
from decimal import Decimal

from src.motor.calculadora import calcular
from src.motor.modelo import Solicitacao, Status


def test_lista_vazia_produz_resultado_valido():
    solicitacao = Solicitacao(
        colaborador={"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        competencia="2026-07",
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        despesas=(),
    )

    resultado = calcular(solicitacao)

    assert resultado.pareceres == ()
    assert resultado.total_lancado == Decimal("0.00")
    assert resultado.total_reembolsavel == Decimal("0.00")
    assert resultado.total_glosado == Decimal("0.00")
    assert all(quantidade == 0 for quantidade in resultado.quantidade_por_status.values())
    assert set(resultado.quantidade_por_status) == set(Status)
