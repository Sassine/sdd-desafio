import json
from pathlib import Path

from src.reembolso import evaluate_expenses, process_input_file, write_output_file


def load_example() -> dict:
    return json.loads(Path("exemplos/despesas-exemplo.json").read_text(encoding="utf-8"))


def test_carrega_entrada_e_normaliza_categorias():
    payload = load_example()
    result = evaluate_expenses(payload)

    assert result["itens"][0]["categoria"] == "alimentacao"
    assert result["itens"][-1]["categoria"] == "alimentacao"


def test_categoria_fora_da_politica_eh_nao_reembolsavel():
    payload = load_example()
    payload["despesas"].append(
        {
            "id": "d-999",
            "data": "2026-07-20",
            "categoria": "coworking",
            "descricao": "Espaco compartilhado",
            "fornecedor": "HubOffice",
            "valor": 89.0,
            "tem_nota_fiscal": True,
        }
    )

    result = evaluate_expenses(payload)
    item = next(item for item in result["itens"] if item["id"] == "d-999")

    assert item["status"] == "nao_reembolsavel"
    assert "categoria_nao_politica" in item["motivo"]


def test_despesa_fora_do_periodo_eh_recusada():
    payload = load_example()
    payload["despesas"][0]["data"] = "2026-04-15"

    result = evaluate_expenses(payload)
    item = next(item for item in result["itens"] if item["id"] == "d-001")

    assert item["status"] == "nao_reembolsavel"
    assert "fora_do_periodo" in item["motivo"]


def test_despesa_acima_de_100_sem_nota_fiscal_eh_recusada():
    payload = load_example()
    payload["despesas"][0]["valor"] = 100.01
    payload["despesas"][0]["tem_nota_fiscal"] = False

    result = evaluate_expenses(payload)
    item = next(item for item in result["itens"] if item["id"] == "d-001")

    assert item["status"] == "nao_reembolsavel"
    assert "nota_fiscal_obrigatoria" in item["motivo"]


def test_valor_negativo_eh_ignorado():
    payload = load_example()
    payload["despesas"].append(
        {
            "id": "d-888",
            "data": "2026-07-20",
            "categoria": "alimentacao",
            "descricao": "Estorno",
            "fornecedor": "Restaurante",
            "valor": -45.0,
            "tem_nota_fiscal": True,
        }
    )

    result = evaluate_expenses(payload)
    item = next(item for item in result["itens"] if item["id"] == "d-888")

    assert item["status"] == "nao_reembolsavel"
    assert "valor_nao_reembolsavel" in item["motivo"]


def test_limite_diario_eh_compartilhado_entre_despesas_do_mesmo_dia():
    payload = load_example()
    payload["despesas"] = [
        {
            "id": "d-a",
            "data": "2026-07-03",
            "categoria": "alimentacao",
            "descricao": "Primeira",
            "fornecedor": "F1",
            "valor": 40.0,
            "tem_nota_fiscal": True,
        },
        {
            "id": "d-b",
            "data": "2026-07-03",
            "categoria": "alimentacao",
            "descricao": "Segunda",
            "fornecedor": "F2",
            "valor": 30.0,
            "tem_nota_fiscal": True,
        },
    ]

    result = evaluate_expenses(payload)
    by_id = {item["id"]: item for item in result["itens"]}

    assert by_id["d-a"]["valor_reembolsavel"] == 40.0
    assert by_id["d-b"]["valor_reembolsavel"] == 20.0


def test_despesa_acima_do_limite_reembolsa_apenas_o_limite():
    payload = load_example()
    payload["despesas"] = [
        {
            "id": "d-a",
            "data": "2026-07-03",
            "categoria": "alimentacao",
            "descricao": "Despesa grande",
            "fornecedor": "F1",
            "valor": 80.0,
            "tem_nota_fiscal": True,
        }
    ]

    result = evaluate_expenses(payload)
    item = result["itens"][0]

    assert item["status"] == "reembolsado_parcialmente"
    assert item["valor_reembolsavel"] == 60.0


def test_duplicata_eh_markada_como_nao_reembolsavel():
    payload = load_example()
    payload["despesas"] = [
        {
            "id": "d-a",
            "data": "2026-07-03",
            "categoria": "alimentacao",
            "descricao": "Almoco",
            "fornecedor": "Restaurante",
            "valor": 50.0,
            "tem_nota_fiscal": True,
        },
        {
            "id": "d-b",
            "data": "2026-07-03",
            "categoria": "alimentacao",
            "descricao": "Almoco",
            "fornecedor": "Restaurante",
            "valor": 50.0,
            "tem_nota_fiscal": True,
        },
    ]

    result = evaluate_expenses(payload)
    by_id = {item["id"]: item for item in result["itens"]}

    assert by_id["d-a"]["status"] == "reembolsado"
    assert by_id["d-b"]["status"] == "nao_reembolsavel"
    assert "duplicata" in by_id["d-b"]["motivo"]


def test_saida_json_contem_status_valor_e_motivo(tmp_path):
    input_path = tmp_path / "entrada.json"
    output_path = tmp_path / "saida.json"
    input_path.write_text(json.dumps(load_example()), encoding="utf-8")

    process_input_file(input_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))

    assert "itens" in result
    assert "resumo" in result
    assert result["itens"][0]["status"] in {"reembolsado", "reembolsado_parcialmente", "nao_reembolsavel"}
    assert "valor_reembolsavel" in result["itens"][0]
    assert "motivo" in result["itens"][0]
