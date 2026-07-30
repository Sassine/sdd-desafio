"""Uma função pura por regra de negócio, na ordem da spec.md §8 (DT-002).

Cada regra de decisão tem assinatura `(Despesa, Contexto) -> Parecer | None`,
onde `None` significa "não decidi, siga para a próxima". `normalizar_categoria`
é a exceção: é o passo 2 (transformação, não decisão) e devolve uma nova
`Despesa`, não um `Parecer`.
"""
from dataclasses import replace

from src.motor.modelo import Despesa


def normalizar_categoria(despesa: Despesa) -> Despesa:
    """RN-002 — ignora caixa e espaços nas pontas antes de qualquer decisão."""
    categoria_normalizada = despesa.categoria.strip().lower()
    if categoria_normalizada == despesa.categoria:
        return despesa
    return replace(despesa, categoria=categoria_normalizada)
