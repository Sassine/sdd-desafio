"""Uma função pura por regra de negócio, na ordem da spec.md §8 (DT-002).

Cada regra de decisão tem assinatura `(Despesa, Contexto) -> Parecer | None`,
onde `None` significa "não decidi, siga para a próxima". `normalizar_categoria`
é a exceção: é o passo 2 (transformação, não decisão) e devolve uma nova
`Despesa`, não um `Parecer`.
"""
from dataclasses import replace
from decimal import Decimal

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
