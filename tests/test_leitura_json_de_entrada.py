from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_despesas


def test_leitura_json_de_entrada_passa():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"

    despesas = carregar_despesas(fixture)

    assert len(despesas) == 14
    assert despesas[0].id == "d-001"
    assert despesas[0].data == "2026-07-03"
    assert despesas[0].categoria == "alimentacao"
    assert despesas[0].descricao == "Almoco com cliente"
    assert despesas[0].fornecedor == "Restaurante Tavola"
    assert despesas[0].valor_original == Decimal("72.50")
    assert despesas[0].tem_nota_fiscal is True
    assert despesas[13].categoria == "ALIMENTACAO"
