"""Uma função pura por regra de negócio, na ordem da spec.md §8 (DT-002).

Cada regra de decisão tem assinatura `(Despesa, Contexto) -> Parecer | None`,
onde `None` significa "não decidi, siga para a próxima". `normalizar_categoria`
é a exceção: é o passo 2 (transformação, não decisão) e devolve uma nova
`Despesa`, não um `Parecer`.
"""
from collections.abc import Callable
from dataclasses import replace
from decimal import Decimal

from src.motor import politica
from src.motor.modelo import Contexto, Despesa, Parecer, Status

ZERO = Decimal("0.00")


def normalizar_categoria(despesa: Despesa) -> Despesa:
    """RN-002 — ignora caixa e espaços nas pontas antes de qualquer decisão."""
    categoria_normalizada = despesa.categoria.strip().lower()
    if categoria_normalizada == despesa.categoria:
        return despesa
    return replace(despesa, categoria=categoria_normalizada)


def rn_003_competencia(despesa: Despesa, contexto: Contexto) -> Parecer | None:
    """RN-003 — despesa fora do mês de competência é recusada (AMB-009)."""
    if despesa.data.strftime("%Y-%m") == contexto.competencia:
        return None
    return Parecer(
        despesa=despesa,
        valor_reembolsavel=ZERO,
        status=Status.RECUSADA,
        regras_aplicadas=("RN-003",),
        justificativa=(
            f"Despesa fora do periodo de competencia {contexto.competencia}."
        ),
    )


def rn_001_categoria_coberta(despesa: Despesa, contexto: Contexto) -> Parecer | None:
    """RN-001 — categoria fora da política é recusada, mas permanece no resultado."""
    if despesa.categoria in politica.CATEGORIAS_COBERTAS:
        return None
    return Parecer(
        despesa=despesa,
        valor_reembolsavel=ZERO,
        status=Status.RECUSADA,
        regras_aplicadas=("RN-001",),
        justificativa=f"Categoria '{despesa.categoria}' nao e coberta pela politica de reembolso.",
    )


def criar_rn_004_duplicata() -> Callable[[Despesa, Contexto], Parecer | None]:
    """RN-004 — fábrica com estado próprio: a primeira ocorrência da chave
    (data, categoria, fornecedor, descrição, valor) passa; as demais são
    recusadas (AMB-008). Uma instância nova por cálculo, para não vazar
    estado entre execuções (spec.md §3)."""
    vistos: set[tuple] = set()

    def regra(despesa: Despesa, contexto: Contexto) -> Parecer | None:
        chave = (
            despesa.data,
            despesa.categoria,
            despesa.fornecedor,
            despesa.descricao,
            despesa.valor,
        )
        if chave in vistos:
            return Parecer(
                despesa=despesa,
                valor_reembolsavel=ZERO,
                status=Status.RECUSADA,
                regras_aplicadas=("RN-004",),
                justificativa=(
                    "Duplicata de um lancamento anterior identico em data, "
                    "categoria, fornecedor, descricao e valor."
                ),
            )
        vistos.add(chave)
        return None

    return regra


def rn_005_estorno(despesa: Despesa, contexto: Contexto) -> Parecer | None:
    """RN-005 — valor negativo é estorno: abate integral, sem teto e sem nota (AMB-010)."""
    if despesa.valor >= ZERO:
        return None
    return Parecer(
        despesa=despesa,
        valor_reembolsavel=despesa.valor,
        status=Status.ESTORNO,
        regras_aplicadas=("RN-005",),
        justificativa="Estorno: valor negativo abatido integralmente do total, sem teto e sem exigencia de nota fiscal.",
    )
