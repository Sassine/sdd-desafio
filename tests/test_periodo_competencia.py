from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_despesas, normalizar_despesas, validar_periodo


def _carregar_despesas_exemplo():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"
    return normalizar_despesas(carregar_despesas(fixture))


def test_despesa_fora_do_periodo_eh_marcada_como_ignorada():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-008")

    valido, motivo = validar_periodo(despesa, "2026-07-01", "2026-07-31")

    assert valido is False
    assert motivo == "fora_do_periodo"


def test_despesa_dentro_do_periodo_nao_eh_marcada_como_fora_do_periodo():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-001")

    valido, motivo = validar_periodo(despesa, "2026-07-01", "2026-07-31")

    assert valido is True
    assert motivo is None


def test_datas_de_limite_inclusivo_sao_consideradas_dentro_do_periodo():
    despesa_inicio = type(_carregar_despesas_exemplo()[0])(
        id="synthetic-start",
        data="2026-07-01",
        categoria="alimentacao",
        descricao="Despesa na data inicial",
        fornecedor="Fornecedor",
        valor_original=Decimal("10.00"),
        tem_nota_fiscal=True,
    )
    despesa_fim = type(_carregar_despesas_exemplo()[0])(
        id="synthetic-end",
        data="2026-07-31",
        categoria="alimentacao",
        descricao="Despesa na data final",
        fornecedor="Fornecedor",
        valor_original=Decimal("10.00"),
        tem_nota_fiscal=True,
    )

    valido_inicio, motivo_inicio = validar_periodo(despesa_inicio, "2026-07-01", "2026-07-31")
    valido_fim, motivo_fim = validar_periodo(despesa_fim, "2026-07-01", "2026-07-31")

    assert valido_inicio is True
    assert motivo_inicio is None
    assert valido_fim is True
    assert motivo_fim is None
