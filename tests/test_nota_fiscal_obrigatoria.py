from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_despesas, normalizar_despesas, validar_nota_fiscal


def _carregar_despesas_exemplo():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"
    return normalizar_despesas(carregar_despesas(fixture))


def test_despesa_com_100_exato_sem_nota_fiscal_nao_eh_recusada():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-003")

    valido, motivo = validar_nota_fiscal(despesa)

    assert valido is True
    assert motivo is None


def test_despesa_acima_de_100_sem_nota_fiscal_eh_recusada():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-004")

    valido, motivo = validar_nota_fiscal(despesa)

    assert valido is False
    assert motivo == "nota_fiscal_obrigatoria"


def test_despesa_muito_acima_de_100_sem_nota_fiscal_eh_recusada():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-013")

    valido, motivo = validar_nota_fiscal(despesa)

    assert valido is False
    assert motivo == "nota_fiscal_obrigatoria"


def test_despesa_acima_de_100_com_nota_fiscal_nao_eh_recusada():
    despesa = next(
        d
        for d in _carregar_despesas_exemplo()
        if d.id == "d-001"
    )
    despesa_com_nf = type(despesa)(
        id=despesa.id,
        data=despesa.data,
        categoria=despesa.categoria,
        descricao=despesa.descricao,
        fornecedor=despesa.fornecedor,
        valor_original=Decimal("150.00"),
        tem_nota_fiscal=True,
    )

    valido, motivo = validar_nota_fiscal(despesa_com_nf)

    assert valido is True
    assert motivo is None


def test_despesa_abaixo_de_100_sem_nota_fiscal_nao_eh_recusada():
    despesas = _carregar_despesas_exemplo()
    despesa = next(d for d in despesas if d.id == "d-001")

    valido, motivo = validar_nota_fiscal(despesa)

    assert valido is True
    assert motivo is None
