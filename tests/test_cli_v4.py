import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
ENVELOPE_DIR = REPO_ROOT / "exemplos" / "envelope"
DESPESAS_ENVELOPE = ENVELOPE_DIR / "despesas-envelope.json"
POLITICA_PATH = ENVELOPE_DIR / "politica-v4.json"
CAMBIO_PATH = ENVELOPE_DIR / "cambio.json"
EXEMPLO_ANTIGO = REPO_ROOT / "exemplos" / "despesas-exemplo.json"


def test_cli_com_politica_e_cambio_usa_pipeline_v4(tmp_path):
    output_path = tmp_path / "resultado.json"

    resultado = subprocess.run(
        [
            sys.executable, "-m", "src.cli",
            "--input", str(DESPESAS_ENVELOPE),
            "--output", str(output_path),
            "--politica", str(POLITICA_PATH),
            "--cambio", str(CAMBIO_PATH),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    por_id = {item["id"]: item for item in payload["despesas"]}
    # e-001: representacao, R$340, limite CC-COMERCIAL = R$300/dia
    assert por_id["e-001"]["status"] == "parcialmente_reembolsada"
    # e-002: EUR convertido, não deve mais estar em 22.00
    assert por_id["e-002"]["valor_original"] != 22.00
    # e-006: GBP sem cotação -> recusada
    assert por_id["e-006"]["status"] == "recusada"
    assert por_id["e-006"]["motivo"] == "cambio_indisponivel"


def test_cli_sem_politica_e_cambio_usa_pipeline_antigo(tmp_path):
    output_path = tmp_path / "resultado.json"

    resultado = subprocess.run(
        [
            sys.executable, "-m", "src.cli",
            "--input", str(EXEMPLO_ANTIGO),
            "--output", str(output_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    por_id = {item["id"]: item for item in payload["despesas"]}
    # comportamento v3 preservado: d-005 (coworking) recusada
    assert por_id["d-005"]["status"] == "recusada"
    assert por_id["d-005"]["motivo"] == "categoria_nao_politica"


def test_cli_apenas_politica_sem_cambio_falha_com_mensagem_clara(tmp_path):
    output_path = tmp_path / "resultado.json"

    resultado = subprocess.run(
        [
            sys.executable, "-m", "src.cli",
            "--input", str(DESPESAS_ENVELOPE),
            "--output", str(output_path),
            "--politica", str(POLITICA_PATH),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode != 0
    assert "cambio" in resultado.stderr.lower()