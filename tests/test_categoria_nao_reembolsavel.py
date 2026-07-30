from decimal import Decimal
from pathlib import Path

from src.reembolso import Despesa, carregar_politica, validar_limite_nao_zero


REPO_ROOT = Path(__file__).resolve().parents[1]
POLITICA_PATH = REPO_ROOT / "exemplos" / "envelope" / "politica-v4.json"


def _carregar_politica_exemplo():
    return carregar_politica(POLITICA_PATH)


def _despesa_hospedagem() -> Despesa:
    return Despesa(
        id="e-teste-hospedagem",
        data="2026-07-15",
        categoria="hospedagem",
        descricao="Hotel - 2 diarias",
        fornecedor="Hotel Exemplo",
        valor_original=Decimal("300.00"),
        tem_nota_fiscal=True,
    )


def test_hospedagem_com_limite_zero_e_recusada_integralmente():
    politica = _carregar_politica_exemplo()
    despesa = _despesa_hospedagem()

    valido, motivo = validar_limite_nao_zero(despesa, "CC-ENG-PLATAFORMA", politica)

    assert valido is False
    assert motivo == "categoria_nao_reembolsavel_no_centro_custo"


def test_hospedagem_com_limite_positivo_nao_e_recusada_por_essa_regra():
    politica = _carregar_politica_exemplo()
    despesa = _despesa_hospedagem()

    valido, motivo = validar_limite_nao_zero(despesa, "CC-COMERCIAL", politica)

    assert valido is True
    assert motivo is None


def test_categoria_inexistente_no_centro_custo_nao_e_pega_por_essa_regra():
    # representacao não existe nem no CC-SUPORTE-N2 nem no padrão —
    # isso é categoria_nao_politica (T-014), não limite zero (T-015)
    politica = _carregar_politica_exemplo()
    despesa = Despesa(
        id="e-teste-representacao",
        data="2026-07-15",
        categoria="representacao",
        descricao="teste",
        fornecedor="teste",
        valor_original=Decimal("50.00"),
        tem_nota_fiscal=True,
    )

    valido, motivo = validar_limite_nao_zero(despesa, "CC-SUPORTE-N2", politica)

    assert valido is True  # essa função não recusa ausência, só limite zero
    assert motivo is None