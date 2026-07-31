"""Formata Resultado como documento de saída (spec.md §4).

É a única fronteira onde Decimal vira texto: json.dump nunca recebe um
Decimal cru (DT-001).
"""
import json

from src.motor.modelo import Parecer, Resultado


def _valor(valor) -> str:
    return f"{valor:.2f}"


def _item(parecer: Parecer) -> dict:
    return {
        "id": parecer.despesa.id,
        "data": parecer.despesa.data.isoformat(),
        "categoria": parecer.despesa.categoria,
        "valor_lancado": _valor(parecer.despesa.valor),
        "valor_reembolsavel": _valor(parecer.valor_reembolsavel),
        "valor_glosado": _valor(parecer.valor_glosado),
        "status": parecer.status.value,
        "regras_aplicadas": list(parecer.regras_aplicadas),
        "justificativa": parecer.justificativa,
    }


def para_documento(resultado: Resultado) -> dict:
    solicitacao = resultado.solicitacao
    return {
        "colaborador": solicitacao.colaborador,
        "periodo": {
            "competencia": solicitacao.competencia,
            "inicio": solicitacao.inicio.isoformat(),
            "fim": solicitacao.fim.isoformat(),
        },
        "resumo": {
            "total_lancado": _valor(resultado.total_lancado),
            "total_reembolsavel": _valor(resultado.total_reembolsavel),
            "total_glosado": _valor(resultado.total_glosado),
            "quantidade_por_status": {
                status.value: quantidade
                for status, quantidade in resultado.quantidade_por_status.items()
            },
        },
        "itens": [_item(parecer) for parecer in resultado.pareceres],
    }


def salvar(resultado: Resultado, caminho: str) -> None:
    documento = para_documento(resultado)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(documento, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
