"""Percorre as despesas e monta o Resultado (spec.md §8, plan.md DT-002).

A ordem da lista abaixo é a ordem dos passos 3 a 8 da spec — mudar a ordem
das regras é reordenar esta lista, não reescrever `if`s aninhados (DT-002).
`rn_007_teto_categoria` nunca devolve `None`, então o laço interno sempre
para nela quando nenhuma regra anterior recusou.
"""
from src.motor.modelo import Parecer, Resultado, Solicitacao
from src.motor.regras import (
    construir_contexto,
    criar_rn_004_duplicata,
    normalizar_categoria,
    rn_001_categoria_coberta,
    rn_003_competencia,
    rn_005_estorno,
    rn_006_nota_fiscal,
    rn_007_teto_categoria,
)


def calcular(solicitacao: Solicitacao) -> Resultado:
    contexto = construir_contexto(solicitacao.despesas, solicitacao.competencia)
    regras_decisao = (
        rn_003_competencia,
        rn_001_categoria_coberta,
        criar_rn_004_duplicata(),
        rn_005_estorno,
        rn_006_nota_fiscal,
        rn_007_teto_categoria,
    )

    pareceres: list[Parecer] = []
    for despesa in solicitacao.despesas:
        despesa_normalizada = normalizar_categoria(despesa)
        for regra in regras_decisao:
            parecer = regra(despesa_normalizada, contexto)
            if parecer is not None:
                pareceres.append(parecer)
                break

    return Resultado(solicitacao=solicitacao, pareceres=tuple(pareceres))
