from decimal import Decimal
from pathlib import Path

from src.reembolso import carregar_cambio, converter_para_brl


REPO_ROOT = Path(__file__).resolve().parents[1]
CAMBIO_PATH = REPO_ROOT / "exemplos" / "envelope" / "cambio.json"


def _carregar_cambio_exemplo():
    return carregar_cambio(CAMBIO_PATH)


def test_conversao_com_taxa_disponivel_na_data_exata():
    cambio = _carregar_cambio_exemplo()

    valor_convertido = converter_para_brl(Decimal("22.00"), "EUR", "2026-07-14", cambio)

    assert valor_convertido == Decimal("130.46")  # 22.00 * 5.93


def test_conversao_com_taxa_ausente_usa_ultimo_dia_util_anterior():
    cambio = _carregar_cambio_exemplo()

    # 2026-07-18 é sábado, sem cotação — deve usar 2026-07-17 (EUR=5.96)
    valor_convertido = converter_para_brl(Decimal("30.00"), "EUR", "2026-07-18", cambio)

    assert valor_convertido == Decimal("178.80")  # 30.00 * 5.96


def test_moeda_brl_nao_e_convertida():
    cambio = _carregar_cambio_exemplo()

    valor_convertido = converter_para_brl(Decimal("95.00"), "BRL", "2026-07-23", cambio)

    assert valor_convertido == Decimal("95.00")


def test_moeda_ausente_e_tratada_como_brl():
    cambio = _carregar_cambio_exemplo()

    valor_convertido = converter_para_brl(Decimal("88.00"), None, "2026-07-27", cambio)

    assert valor_convertido == Decimal("88.00")


def test_conversao_usd_funciona_tambem():
    cambio = _carregar_cambio_exemplo()

    valor_convertido = converter_para_brl(Decimal("40.00"), "USD", "2026-07-20", cambio)

    assert valor_convertido == Decimal("220.00")  # 40.00 * 5.50