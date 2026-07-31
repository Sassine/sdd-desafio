from pathlib import Path

from src.reembolso import carregar_despesas


REPO_ROOT = Path(__file__).resolve().parents[1]
ENVELOPE_PATH = REPO_ROOT / "exemplos" / "envelope" / "despesas-envelope.json"


def test_carregar_despesas_le_campo_moeda_do_json():
    despesas = carregar_despesas(ENVELOPE_PATH)
    por_id = {despesa.id: despesa for despesa in despesas}

    assert por_id["e-002"].moeda == "EUR"
    assert por_id["e-005"].moeda == "USD"


def test_carregar_despesas_despesa_sem_moeda_fica_none():
    despesas = carregar_despesas(ENVELOPE_PATH)
    por_id = {despesa.id: despesa for despesa in despesas}

    # e-010 no despesas-envelope.json não tem campo "moeda"
    assert por_id["e-010"].moeda is None