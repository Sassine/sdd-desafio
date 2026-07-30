"""Le o arquivo de entrada e produz uma Solicitacao (plan.md secao 2, DT-001).

Entrada invalida e rejeitada, nao adivinhada (spec.md §3, §9) — ErroDeEntrada
nomeia o campo ausente ou de tipo invalido e nenhuma Solicitacao parcial e
devolvida.
"""
import json
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from src.motor.modelo import Despesa, Solicitacao

DUAS_CASAS = Decimal("0.01")

CAMPOS_COLABORADOR = ("id", "nome", "centro_custo")
CAMPOS_PERIODO = ("competencia", "inicio", "fim")
CAMPOS_DESPESA = ("id", "data", "categoria", "descricao", "fornecedor", "valor", "tem_nota_fiscal")


class ErroDeEntrada(Exception):
    """Campo obrigatorio ausente ou de tipo invalido na entrada."""


def carregar(caminho: str) -> Solicitacao:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo, parse_float=Decimal)
    return _para_solicitacao(dados)


def _arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)


def _exigir(dados: dict, chave: str, rotulo: str):
    if not isinstance(dados, dict) or chave not in dados:
        raise ErroDeEntrada(f"Campo obrigatorio ausente: {rotulo}")
    return dados[chave]


def _exigir_data(dados: dict, chave: str, rotulo: str) -> date:
    valor = _exigir(dados, chave, rotulo)
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ErroDeEntrada(f"Campo invalido: {rotulo}") from None


def _para_despesa(dados: dict, indice: int) -> Despesa:
    rotulo_base = f"despesas[{indice}]"
    for campo in CAMPOS_DESPESA:
        _exigir(dados, campo, f"{rotulo_base}.{campo}")

    data = _exigir_data(dados, "data", f"{rotulo_base}.data")

    try:
        valor = _arredondar(Decimal(dados["valor"]))
    except (InvalidOperation, TypeError, ValueError):
        raise ErroDeEntrada(f"Campo invalido: {rotulo_base}.valor") from None

    if not isinstance(dados["tem_nota_fiscal"], bool):
        raise ErroDeEntrada(f"Campo invalido: {rotulo_base}.tem_nota_fiscal")

    return Despesa(
        id=dados["id"],
        data=data,
        categoria=dados["categoria"],
        descricao=dados["descricao"],
        fornecedor=dados["fornecedor"],
        valor=valor,
        tem_nota_fiscal=dados["tem_nota_fiscal"],
    )


def _para_solicitacao(dados: dict) -> Solicitacao:
    colaborador = _exigir(dados, "colaborador", "colaborador")
    periodo = _exigir(dados, "periodo", "periodo")
    despesas_dados = _exigir(dados, "despesas", "despesas")

    for campo in CAMPOS_COLABORADOR:
        _exigir(colaborador, campo, f"colaborador.{campo}")
    for campo in CAMPOS_PERIODO:
        _exigir(periodo, campo, f"periodo.{campo}")

    inicio = _exigir_data(periodo, "inicio", "periodo.inicio")
    fim = _exigir_data(periodo, "fim", "periodo.fim")

    if not isinstance(despesas_dados, list):
        raise ErroDeEntrada("Campo invalido: despesas")

    despesas = tuple(_para_despesa(item, indice) for indice, item in enumerate(despesas_dados))

    return Solicitacao(
        colaborador=colaborador,
        competencia=periodo["competencia"],
        inicio=inicio,
        fim=fim,
        despesas=despesas,
    )
