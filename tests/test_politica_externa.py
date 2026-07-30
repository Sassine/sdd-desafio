import json
from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_politica, obter_limite_categoria


REPO_ROOT = Path(__file__).resolve().parents[1]
POLITICA_PATH = REPO_ROOT / "exemplos" / "envelope" / "politica-v4.json"


def _carregar_politica_exemplo():
    return carregar_politica(POLITICA_PATH)


def test_centro_custo_com_valor_especifico_usa_valor_especifico():
    politica = _carregar_politica_exemplo()

    limite = obter_limite_categoria(politica, "CC-COMERCIAL", "alimentacao")

    assert limite == Decimal("90.00")


def test_centro_custo_presente_mas_sem_categoria_cai_no_padrao_dessa_categoria():
    politica = _carregar_politica_exemplo()

    # CC-ADM define alimentacao e transporte_urbano, mas NÃO define hospedagem
    limite_hospedagem = obter_limite_categoria(politica, "CC-ADM", "hospedagem")
    limite_alimentacao = obter_limite_categoria(politica, "CC-ADM", "alimentacao")

    assert limite_hospedagem == Decimal("250.00")  # veio do padrão
    assert limite_alimentacao == Decimal("45.00")  # veio do valor específico do CC-ADM


def test_centro_custo_ausente_da_tabela_usa_padrao_para_todas_categorias():
    politica = _carregar_politica_exemplo()

    limite = obter_limite_categoria(politica, "CC-SUPORTE-N2", "alimentacao")

    assert limite == Decimal("60.00")


def test_limite_zero_e_retornado_como_zero_nao_como_ausencia():
    politica = _carregar_politica_exemplo()

    limite = obter_limite_categoria(politica, "CC-ENG-PLATAFORMA", "hospedagem")

    assert limite == Decimal("0.00")
    assert limite is not None


def test_categoria_nao_coberta_nem_no_centro_custo_nem_no_padrao_retorna_none():
    politica = _carregar_politica_exemplo()

    # CC-ADM não define representacao, e o padrão também não define representacao
    limite = obter_limite_categoria(politica, "CC-ADM", "representacao")

    assert limite is None


def test_categoria_valida_apenas_em_centro_custo_especifico():
    politica = _carregar_politica_exemplo()

    limite_comercial = obter_limite_categoria(politica, "CC-COMERCIAL", "representacao")
    limite_ausente = obter_limite_categoria(politica, "CC-SUPORTE-N2", "representacao")

    assert limite_comercial == Decimal("300.00")
    assert limite_ausente is None  # nem CC-SUPORTE-N2 nem o padrão têm representacao