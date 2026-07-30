"""T-003 — carregador: JSON em disco vira Solicitacao com Decimal (RN-010, AMB-011)."""
import json
from decimal import Decimal

from src.io.carregador import carregar


def _escrever_entrada(tmp_path, valor):
    dados = {
        "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
        "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
        "despesas": [
            {
                "id": "d-001",
                "data": "2026-07-15",
                "categoria": "alimentacao",
                "descricao": "Cafe da manha hotel",
                "fornecedor": "Hotel Copa Sul",
                "valor": valor,
                "tem_nota_fiscal": True,
            }
        ],
    }
    caminho = tmp_path / "entrada.json"
    # Escreve com json.dumps padrão: números permanecem literais textuais no
    # arquivo (ex.: 33.333), exatamente como chegariam de um arquivo real.
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return caminho


def test_rn_010_arredonda_na_leitura(tmp_path):
    caminho = _escrever_entrada(tmp_path, 33.333)

    solicitacao = carregar(str(caminho))

    valor = solicitacao.despesas[0].valor
    assert valor == Decimal("33.33")
    assert isinstance(valor, Decimal)


def test_rn_010_conversao_nunca_passa_por_float(tmp_path):
    # 2.675 como float binário vale 2.67499999999999982...; se o valor tivesse
    # passado por float em algum ponto, o arredondamento meio-para-cima erraria
    # para 2.67. Só dá 2.68 se o texto "2.675" foi lido direto como Decimal.
    caminho = _escrever_entrada(tmp_path, 2.675)

    solicitacao = carregar(str(caminho))

    assert solicitacao.despesas[0].valor == Decimal("2.68")


def test_carregador_preenche_periodo_e_colaborador(tmp_path):
    caminho = _escrever_entrada(tmp_path, 10)

    solicitacao = carregar(str(caminho))

    assert solicitacao.competencia == "2026-07"
    assert solicitacao.colaborador["id"] == "c-1"
    assert solicitacao.despesas[0].categoria == "alimentacao"
    assert solicitacao.despesas[0].tem_nota_fiscal is True
