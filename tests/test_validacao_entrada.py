"""T-004 — entrada invalida e rejeitada com mensagem, sem resultado parcial.

Atende spec.md §9 (ultimo criterio) e §3 (nao adivinha entrada malformada).
"""
import json

import pytest

from src.io.carregador import ErroDeEntrada, carregar

ENTRADA_BASE = {
    "colaborador": {"id": "c-1", "nome": "Teste", "centro_custo": "CC"},
    "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
    "despesas": [
        {
            "id": "d-001",
            "data": "2026-07-15",
            "categoria": "alimentacao",
            "descricao": "Cafe da manha",
            "fornecedor": "Hotel Copa Sul",
            "valor": 33.33,
            "tem_nota_fiscal": True,
        }
    ],
}


def _escrever(tmp_path, dados, nome="entrada.json"):
    caminho = tmp_path / nome
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return str(caminho)


def _sem_campo(dados_despesa, campo):
    import copy

    dados = copy.deepcopy(ENTRADA_BASE)
    del dados["despesas"][0][campo]
    return dados


def test_entrada_sem_campo_obrigatorio_e_rejeitada(tmp_path):
    dados = _sem_campo(ENTRADA_BASE, "valor")
    caminho = _escrever(tmp_path, dados)

    with pytest.raises(ErroDeEntrada, match="valor"):
        carregar(caminho)


def test_entrada_sem_campo_obrigatorio_nao_produz_resultado_parcial(tmp_path):
    dados = _sem_campo(ENTRADA_BASE, "valor")
    caminho = _escrever(tmp_path, dados)

    resultado = None
    try:
        resultado = carregar(caminho)
    except ErroDeEntrada:
        pass

    assert resultado is None


@pytest.mark.parametrize(
    "campo",
    ["id", "data", "categoria", "descricao", "fornecedor", "valor", "tem_nota_fiscal"],
)
def test_entrada_sem_cada_campo_obrigatorio_da_despesa_e_rejeitada(tmp_path, campo):
    dados = _sem_campo(ENTRADA_BASE, campo)
    caminho = _escrever(tmp_path, dados)

    with pytest.raises(ErroDeEntrada, match=campo):
        carregar(caminho)


def test_entrada_sem_colaborador_id_e_rejeitada(tmp_path):
    import copy

    dados = copy.deepcopy(ENTRADA_BASE)
    del dados["colaborador"]["id"]
    caminho = _escrever(tmp_path, dados)

    with pytest.raises(ErroDeEntrada, match="colaborador.id"):
        carregar(caminho)


def test_entrada_sem_periodo_competencia_e_rejeitada(tmp_path):
    import copy

    dados = copy.deepcopy(ENTRADA_BASE)
    del dados["periodo"]["competencia"]
    caminho = _escrever(tmp_path, dados)

    with pytest.raises(ErroDeEntrada, match="periodo.competencia"):
        carregar(caminho)


def test_entrada_com_valor_de_tipo_invalido_e_rejeitada(tmp_path):
    import copy

    dados = copy.deepcopy(ENTRADA_BASE)
    dados["despesas"][0]["valor"] = "nao-e-numero"
    caminho = _escrever(tmp_path, dados)

    with pytest.raises(ErroDeEntrada, match="valor"):
        carregar(caminho)


def test_entrada_com_tem_nota_fiscal_de_tipo_invalido_e_rejeitada(tmp_path):
    import copy

    dados = copy.deepcopy(ENTRADA_BASE)
    dados["despesas"][0]["tem_nota_fiscal"] = "sim"
    caminho = _escrever(tmp_path, dados)

    with pytest.raises(ErroDeEntrada, match="tem_nota_fiscal"):
        carregar(caminho)
