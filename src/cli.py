"""CLI: orquestra carregador → motor → serializador (plan.md §2, DESAFIO.md).

`python -m src.cli calcular --input <arquivo> --output <arquivo>`
"""
import argparse
import sys

from src.io.carregador import ErroDeEntrada, carregar
from src.io.serializador import salvar
from src.motor.calculadora import calcular as calcular_reembolso


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="motor-reembolso")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    parser_calcular = subparsers.add_parser("calcular")
    parser_calcular.add_argument("--input", required=True, dest="entrada")
    parser_calcular.add_argument("--output", required=True, dest="saida")

    args = parser.parse_args(argv)
    return _executar_calcular(args.entrada, args.saida)


def _executar_calcular(caminho_entrada: str, caminho_saida: str) -> int:
    try:
        solicitacao = carregar(caminho_entrada)
    except ErroDeEntrada as erro:
        print(f"Entrada invalida: {erro}", file=sys.stderr)
        return 1

    resultado = calcular_reembolso(solicitacao)
    salvar(resultado, caminho_saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
