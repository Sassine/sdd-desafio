"""T-019 — serializador: Decimal como texto de duas casas, status em minúsculas."""
import json
from datetime import date
from decimal import Decimal

from src.io.serializador import para_documento
from src.motor.modelo import Parecer, Resultado, Solicitacao, Status

from tests.fabricas import despesa


def _solicitacao(despesas):
    return Solicitacao(
        colaborador={"id": "c-0417", "nome": "Marina Volpi", "centro_custo": "CC-ENG"},
        competencia="2026-07",
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        despesas=tuple(despesas),
    )


def test_serializa_valores_como_texto_de_duas_casas():
    d = despesa(id="d-001", valor=Decimal("60"))
    parecer = Parecer(
        despesa=d,
        valor_reembolsavel=Decimal("60"),
        status=Status.APROVADA,
        regras_aplicadas=("RN-007",),
        justificativa="Valor dentro do teto.",
    )
    resultado = Resultado(solicitacao=_solicitacao([d]), pareceres=(parecer,))

    documento = para_documento(resultado)
    item = documento["itens"][0]

    assert item["valor_lancado"] == "60.00"
    assert item["valor_reembolsavel"] == "60.00"
    assert item["valor_glosado"] == "0.00"
    assert item["status"] == "aprovada"

    # nenhum Decimal cru chega ao json.dump: se algum tivesse escapado, esta
    # linha levantaria TypeError.
    json.dumps(documento)


def test_serializa_regras_aplicadas_como_lista():
    d = despesa()
    parecer = Parecer(
        despesa=d,
        valor_reembolsavel=d.valor,
        status=Status.APROVADA,
        regras_aplicadas=("RN-007",),
        justificativa="ok",
    )
    resultado = Resultado(solicitacao=_solicitacao([d]), pareceres=(parecer,))

    item = para_documento(resultado)["itens"][0]
    assert item["regras_aplicadas"] == ["RN-007"]


def test_serializa_colaborador_e_periodo_sem_alteracao():
    resultado = Resultado(solicitacao=_solicitacao([despesa()]), pareceres=())
    documento = para_documento(resultado)

    assert documento["colaborador"]["id"] == "c-0417"
    assert documento["periodo"]["competencia"] == "2026-07"
    assert documento["periodo"]["inicio"] == "2026-07-01"
    assert documento["periodo"]["fim"] == "2026-07-31"
