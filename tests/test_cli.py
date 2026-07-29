import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from src.reembolso import processar_despesas


REPO_ROOT = Path(__file__).resolve().parents[1]
EXEMPLO_PATH = REPO_ROOT / "exemplos" / "despesas-exemplo.json"


def _normalizar_para_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {chave: _normalizar_para_json(valor) for chave, valor in obj.items()}
    if isinstance(obj, list):
        return [_normalizar_para_json(item) for item in obj]
    return obj


def test_cli_gera_arquivo_json_valido(tmp_path):
    output_path = tmp_path / "resultado.json"

    resultado = subprocess.run(
        [sys.executable, "-m", "src.cli", "--input", str(EXEMPLO_PATH), "--output", str(output_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as handle:
        payload_escrito = json.load(handle)

    payload_esperado = _normalizar_para_json(processar_despesas(json.loads(EXEMPLO_PATH.read_text(encoding="utf-8"))))
    assert payload_escrito == payload_esperado


def test_cli_serializa_decimals_como_numeros(tmp_path):
    output_path = tmp_path / "resultado.json"

    resultado = subprocess.run(
        [sys.executable, "-m", "src.cli", "--input", str(EXEMPLO_PATH), "--output", str(output_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr

    with output_path.open("r", encoding="utf-8") as handle:
        payload_escrito = json.load(handle)

    primeira_despesa = payload_escrito["despesas"][0]
    assert isinstance(primeira_despesa["valor_original"], (int, float))
    assert not isinstance(primeira_despesa["valor_original"], str)
    assert primeira_despesa["valor_reembolsavel"] == pytest.approx(60.0)


@pytest.mark.parametrize(
    ("args", "fragmento_esperado"),
    [
        (["--output", "resultado.json"], "the following arguments are required: --input"),
        (["--input", "despesas.json"], "the following arguments are required: --output"),
    ],
)
def test_cli_sem_argumentos_necessarios_falha_com_mensagem_clara(args, fragmento_esperado):
    resultado = subprocess.run(
        [sys.executable, "-m", "src.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode != 0
    assert fragmento_esperado in resultado.stderr.lower()
