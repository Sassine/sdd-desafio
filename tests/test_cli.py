"""T-021 — CLI: `calcular --input <arquivo> --output <arquivo>` (DESAFIO.md)."""
import json

from src.cli import main


def _escrever_entrada_valida(tmp_path):
    dados = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-1",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "Almoco",
                "fornecedor": "Restaurante",
                "valor": 50.00,
                "tem_nota_fiscal": True,
            }
        ],
    }
    caminho = tmp_path / "entrada.json"
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return str(caminho)


def test_cli_calcular_escreve_saida(tmp_path):
    entrada = _escrever_entrada_valida(tmp_path)
    saida = tmp_path / "saida.json"

    codigo = main(["calcular", "--input", entrada, "--output", str(saida)])

    assert codigo == 0
    assert saida.exists()
    documento = json.loads(saida.read_text(encoding="utf-8"))
    assert documento["resumo"]["total_reembolsavel"] == "50.00"


def test_cli_calcular_com_entrada_invalida_retorna_codigo_diferente_de_zero_sem_escrever_saida(tmp_path):
    caminho = tmp_path / "entrada.json"
    caminho.write_text(json.dumps({"colaborador": {}}), encoding="utf-8")
    saida = tmp_path / "saida.json"

    codigo = main(["calcular", "--input", str(caminho), "--output", str(saida)])

    assert codigo != 0
    assert not saida.exists()
