from pathlib import Path

from src.reembolso import carregar_despesas, normalizar_despesas, validar_categoria


def test_validacao_categoria_aceita():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"

    despesas = normalizar_despesas(carregar_despesas(fixture))
    despesa_valida = next(despesa for despesa in despesas if despesa.id == "d-001")
    despesa_fora_politica = next(despesa for despesa in despesas if despesa.id == "d-005")

    elegivel, motivo = validar_categoria(despesa_valida)
    assert elegivel is True
    assert motivo is None

    elegivel, motivo = validar_categoria(despesa_fora_politica)
    assert elegivel is False
    assert motivo == "categoria_nao_politica"
