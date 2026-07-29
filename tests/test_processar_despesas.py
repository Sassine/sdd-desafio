import json
from decimal import Decimal
from pathlib import Path

from src.reembolso import processar_despesas


def _carregar_payload_exemplo():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"
    with fixture.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_resultado_copia_colaborador_e_periodo_da_entrada():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)

    assert resultado["colaborador"] == payload["colaborador"]
    assert resultado["periodo"] == payload["periodo"]


def test_resultado_tem_uma_entrada_por_despesa_e_status_valido():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)

    assert len(resultado["despesas"]) == len(payload["despesas"])

    statuses = {item["status"] for item in resultado["despesas"]}
    assert statuses <= {"reembolsada", "parcialmente_reembolsada", "recusada", "ignorada"}


def test_alguns_statuses_conhecidos_do_json_exemplo():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)
    por_id = {item["id"]: item for item in resultado["despesas"]}

    assert por_id["d-006"]["status"] == "reembolsada"
    assert por_id["d-001"]["status"] == "parcialmente_reembolsada"
    assert por_id["d-005"]["status"] == "recusada"
    assert por_id["d-008"]["status"] == "ignorada"


def test_todas_as_despesas_tem_justificativa_preenchida():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)

    for item in resultado["despesas"]:
        assert isinstance(item["justificativa"], str)
        assert item["justificativa"].strip() != ""


def test_hospedagem_aplica_limite_individual_de_250_reais():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)
    por_id = {item["id"]: item for item in resultado["despesas"]}

    assert por_id["d-010"]["status"] == "parcialmente_reembolsada"
    assert por_id["d-010"]["valor_reembolsavel"] == Decimal("250.00")
    assert por_id["d-010"]["valor_nao_reembolsavel"] == Decimal("230.00")


def test_resumo_bate_com_soma_das_despesas_do_resultado():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)
    despesas = resultado["despesas"]

    valor_total = sum((item["valor_original"] for item in despesas), Decimal("0.00"))
    valor_reembolsavel = sum((item["valor_reembolsavel"] for item in despesas), Decimal("0.00"))
    valor_nao_reembolsavel = sum((item["valor_nao_reembolsavel"] for item in despesas), Decimal("0.00"))

    resumo = resultado["resumo"]
    assert resumo["valor_total_despesas"] == float(valor_total)
    assert resumo["valor_reembolsavel"] == float(valor_reembolsavel)
    assert resumo["valor_nao_reembolsavel"] == float(valor_nao_reembolsavel)
    assert resumo["quantidade_despesas"] == len(despesas)
    assert resumo["quantidade_reembolsadas"] == sum(1 for item in despesas if item["status"] == "reembolsada")
    assert resumo["quantidade_parcialmente_reembolsadas"] == sum(1 for item in despesas if item["status"] == "parcialmente_reembolsada")
    assert resumo["quantidade_recusadas"] == sum(1 for item in despesas if item["status"] == "recusada")
    assert resumo["quantidade_ignorar"] == sum(1 for item in despesas if item["status"] == "ignorada")


def test_duplicata_tem_precedencia_sobre_nota_fiscal_e_limite():
    payload = _carregar_payload_exemplo()

    resultado = processar_despesas(payload)
    por_id = {item["id"]: item for item in resultado["despesas"]}

    assert por_id["d-007"]["status"] == "recusada"
    assert por_id["d-007"]["motivo"] == "duplicata_de_d-006"
