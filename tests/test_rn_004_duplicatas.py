"""T-009 — RN-004: duplicatas — primeira ocorrência paga, demais recusadas (AMB-008)."""
from datetime import date
from decimal import Decimal

from src.motor.modelo import Contexto, Status
from src.motor.regras import criar_rn_004_duplicata

from tests.fabricas import despesa

CONTEXTO = Contexto(competencia="2026-07", datas_em_viagem=frozenset())


def test_rn_004_duplicata_exata_recusa_a_segunda():
    regra = criar_rn_004_duplicata()
    primeira = despesa(
        id="d-006", data=date(2026, 7, 9), fornecedor="Bistro Central",
        descricao="Almoco", valor=Decimal("54.90"),
    )
    segunda = despesa(
        id="d-007", data=date(2026, 7, 9), fornecedor="Bistro Central",
        descricao="Almoco", valor=Decimal("54.90"),
    )

    assert regra(primeira, CONTEXTO) is None

    parecer = regra(segunda, CONTEXTO)
    assert parecer is not None
    assert parecer.valor_reembolsavel == Decimal("0.00")
    assert parecer.status == Status.RECUSADA
    assert "RN-004" in parecer.regras_aplicadas


def test_rn_004_fornecedor_diferente_nao_e_duplicata():
    regra = criar_rn_004_duplicata()
    primeira = despesa(id="d-a", data=date(2026, 7, 9), fornecedor="Loja A", valor=Decimal("54.90"))
    segunda = despesa(id="d-b", data=date(2026, 7, 9), fornecedor="Loja B", valor=Decimal("54.90"))

    assert regra(primeira, CONTEXTO) is None
    assert regra(segunda, CONTEXTO) is None


def test_rn_004_terceira_ocorrencia_tambem_e_recusada():
    regra = criar_rn_004_duplicata()
    chave_comum = dict(data=date(2026, 7, 9), fornecedor="Bistro Central", valor=Decimal("54.90"))

    assert regra(despesa(id="d-1", **chave_comum), CONTEXTO) is None
    assert regra(despesa(id="d-2", **chave_comum), CONTEXTO).status == Status.RECUSADA
    assert regra(despesa(id="d-3", **chave_comum), CONTEXTO).status == Status.RECUSADA


def test_rn_004_cada_calculo_comeca_com_estado_novo():
    primeira_execucao = criar_rn_004_duplicata()
    d = despesa(id="d-1")
    assert primeira_execucao(d, CONTEXTO) is None

    segunda_execucao = criar_rn_004_duplicata()
    assert segunda_execucao(d, CONTEXTO) is None
