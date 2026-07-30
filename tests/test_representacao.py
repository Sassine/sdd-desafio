from decimal import Decimal
from pathlib import Path

from src.reembolso import Despesa, carregar_politica, validar_categoria_por_politica


REPO_ROOT = Path(__file__).resolve().parents[1]
POLITICA_PATH = REPO_ROOT / "exemplos" / "envelope" / "politica-v4.json"


def _carregar_politica_exemplo():
    return carregar_politica(POLITICA_PATH)


def _despesa(categoria: str) -> Despesa:
    return Despesa(
        id="e-teste",
        data="2026-07-13",
        categoria=categoria,
        descricao="Jantar com prospect",
        fornecedor="Casa Trindade",
        valor_original=Decimal("340.00"),
        tem_nota_fiscal=True,
    )


def test_representacao_e_valida_no_centro_custo_que_a_define():
    politica = _carregar_politica_exemplo()
    despesa = _despesa("representacao")

    valido, motivo = validar_categoria_por_politica(despesa, "CC-COMERCIAL", politica)

    assert valido is True
    assert motivo is None


def test_representacao_e_recusada_no_centro_custo_que_nao_a_define():
    politica = _carregar_politica_exemplo()
    despesa = _despesa("representacao")

    valido, motivo = validar_categoria_por_politica(despesa, "CC-SUPORTE-N2", politica)

    assert valido is False
    assert motivo == "categoria_nao_politica"


def test_categorias_ja_conhecidas_continuam_validas_via_politica():
    politica = _carregar_politica_exemplo()
    despesa = _despesa("alimentacao")

    valido, motivo = validar_categoria_por_politica(despesa, "CC-COMERCIAL", politica)

    assert valido is True
    assert motivo is None


def test_categoria_totalmente_fora_da_politica_continua_recusada():
    politica = _carregar_politica_exemplo()
    despesa = _despesa("coworking")

    valido, motivo = validar_categoria_por_politica(despesa, "CC-COMERCIAL", politica)

    assert valido is False
    assert motivo == "categoria_nao_politica"