import json
from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_cambio, carregar_politica, processar_despesas_v4


REPO_ROOT = Path(__file__).resolve().parents[1]
ENVELOPE_DIR = REPO_ROOT / "exemplos" / "envelope"
POLITICA_PATH = ENVELOPE_DIR / "politica-v4.json"
CAMBIO_PATH = ENVELOPE_DIR / "cambio.json"


def _payload(nome_arquivo: str) -> dict:
    with (ENVELOPE_DIR / nome_arquivo).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _politica():
    return carregar_politica(POLITICA_PATH)


def _cambio():
    return carregar_cambio(CAMBIO_PATH)


def test_representacao_e_avaliada_contra_limite_do_centro_custo():
    payload = _payload("despesas-envelope.json")  # CC-COMERCIAL

    resultado = processar_despesas_v4(payload, _politica(), _cambio())
    por_id = {item["id"]: item for item in resultado["despesas"]}

    # e-001: representacao, R$340,00, limite CC-COMERCIAL = R$300/dia
    assert por_id["e-001"]["status"] == "parcialmente_reembolsada"
    assert por_id["e-001"]["valor_reembolsavel"] == Decimal("300.00")


def test_despesa_em_eur_e_convertida_antes_de_aplicar_limite():
    payload = _payload("despesas-envelope.json")

    resultado = processar_despesas_v4(payload, _politica(), _cambio())
    por_id = {item["id"]: item for item in resultado["despesas"]}

    # e-002: EUR 22,00 em 2026-07-14 (taxa 5.93) = R$130,46
    assert por_id["e-002"]["valor_original"] == Decimal("130.46")


def test_hospedagem_com_limite_zero_e_recusada_no_centro_custo():
    payload = _payload("despesas-envelope.json")
    payload = dict(payload)
    payload["colaborador"] = dict(payload["colaborador"])
    payload["colaborador"]["centro_custo"] = "CC-ENG-PLATAFORMA"

    resultado = processar_despesas_v4(payload, _politica(), _cambio())
    por_id = {item["id"]: item for item in resultado["despesas"]}

    assert por_id["e-007"]["status"] == "recusada"
    assert por_id["e-007"]["motivo"] == "categoria_nao_reembolsavel_no_centro_custo"


def test_centro_custo_ausente_da_tabela_usa_politica_padrao():
    payload = _payload("despesas-envelope-cc-desconhecido.json")  # CC-SUPORTE-N2

    resultado = processar_despesas_v4(payload, _politica(), _cambio())
    por_id = {item["id"]: item for item in resultado["despesas"]}

    # f-001: alimentacao R$58,00, limite padrão R$60/dia -> reembolsada integral
    assert por_id["f-001"]["status"] == "reembolsada"

    # f-002: hospedagem R$310,00, limite padrão R$250/diária -> parcial
    assert por_id["f-002"]["status"] == "parcialmente_reembolsada"
    assert por_id["f-002"]["valor_reembolsavel"] == Decimal("250.00")

    # f-003: representacao, categoria não existe nem no CC-SUPORTE-N2 nem no padrão
    assert por_id["f-003"]["status"] == "recusada"
    assert por_id["f-003"]["motivo"] == "categoria_nao_politica"


def test_moeda_usd_e_convertida_com_taxa_da_data():
    payload = _payload("despesas-envelope-cc-desconhecido.json")

    resultado = processar_despesas_v4(payload, _politica(), _cambio())
    por_id = {item["id"]: item for item in resultado["despesas"]}

    # f-004: USD 12,00 em 2026-07-21 (taxa 5.48) = R$65,76
    assert por_id["f-004"]["valor_original"] == Decimal("65.76")