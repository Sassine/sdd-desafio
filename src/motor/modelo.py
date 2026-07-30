"""Estruturas de dados do motor (plan.md §3). Núcleo puro: sem I/O."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum


class Status(Enum):
    APROVADA = "aprovada"
    PARCIAL = "parcial"
    RECUSADA = "recusada"
    ESTORNO = "estorno"


@dataclass(frozen=True)
class Despesa:
    id: str
    data: date
    categoria: str
    descricao: str
    fornecedor: str
    valor: Decimal
    tem_nota_fiscal: bool


@dataclass(frozen=True)
class Solicitacao:
    colaborador: dict
    competencia: str
    inicio: date
    fim: date
    despesas: tuple[Despesa, ...]


@dataclass(frozen=True)
class Contexto:
    competencia: str
    datas_em_viagem: frozenset[date] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Parecer:
    despesa: Despesa
    valor_reembolsavel: Decimal
    status: Status
    regras_aplicadas: tuple[str, ...]
    justificativa: str

    @property
    def valor_glosado(self) -> Decimal:
        return self.despesa.valor - self.valor_reembolsavel


@dataclass(frozen=True)
class Resultado:
    solicitacao: Solicitacao
    pareceres: tuple[Parecer, ...]

    @property
    def total_lancado(self) -> Decimal:
        return sum((p.despesa.valor for p in self.pareceres), Decimal("0.00"))

    @property
    def total_reembolsavel(self) -> Decimal:
        return sum((p.valor_reembolsavel for p in self.pareceres), Decimal("0.00"))

    @property
    def total_glosado(self) -> Decimal:
        return self.total_lancado - self.total_reembolsavel

    @property
    def quantidade_por_status(self) -> dict[Status, int]:
        contagem = {status: 0 for status in Status}
        for parecer in self.pareceres:
            contagem[parecer.status] += 1
        return contagem
