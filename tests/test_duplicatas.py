from pathlib import Path

from src.reembolso import carregar_despesas, identificar_duplicatas, normalizar_despesas


def _carregar_despesas_exemplo():
    fixture = Path(__file__).resolve().parents[1] / "exemplos" / "despesas-exemplo.json"
    return normalizar_despesas(carregar_despesas(fixture))


def test_despesas_duplicadas_sao_marcadas_com_o_id_original():
    despesas = _carregar_despesas_exemplo()
    resultados = identificar_duplicatas(despesas)

    duplicata = next(resultado for resultado in resultados if resultado["id"] == "d-007")
    original = next(resultado for resultado in resultados if resultado["id"] == "d-006")

    assert duplicata["duplicata"] is True
    assert duplicata["motivo"] == "duplicata_de_d-006"
    assert original["duplicata"] is False
    assert original["motivo"] is None


def test_despesas_com_fornecedor_ou_descricao_diferentes_nao_sao_duplicatas():
    despesas = _carregar_despesas_exemplo()
    resultados = identificar_duplicatas(despesas)

    despesa_a = next(resultado for resultado in resultados if resultado["id"] == "d-001")
    despesa_b = next(resultado for resultado in resultados if resultado["id"] == "d-006")

    assert despesa_a["duplicata"] is False
    assert despesa_a["motivo"] is None
    assert despesa_b["duplicata"] is False
    assert despesa_b["motivo"] is None


def test_a_primeira_ocorrencia_nunca_eh_marcada_como_duplicata():
    despesas = _carregar_despesas_exemplo()
    resultados = identificar_duplicatas(despesas)

    primeira = next(resultado for resultado in resultados if resultado["id"] == "d-006")
    segunda = next(resultado for resultado in resultados if resultado["id"] == "d-007")

    assert primeira["duplicata"] is False
    assert primeira["motivo"] is None
    assert segunda["duplicata"] is True
    assert segunda["motivo"] == "duplicata_de_d-006"
