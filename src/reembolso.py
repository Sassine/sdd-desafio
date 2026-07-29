from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


@dataclass(frozen=True)
class Despesa:
    id: str
    data: str
    categoria: str
    descricao: str
    fornecedor: str
    valor_original: Decimal
    tem_nota_fiscal: bool


def carregar_despesas(caminho: str | Path) -> list[Despesa]:
    path = Path(caminho)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    despesas_payload = payload.get("despesas", [])
    despesas: list[Despesa] = []

    for item in despesas_payload:
        despesas.append(
            Despesa(
                id=item["id"],
                data=item["data"],
                categoria=item["categoria"],
                descricao=item["descricao"],
                fornecedor=item["fornecedor"],
                valor_original=Decimal(str(item["valor"])),
                tem_nota_fiscal=bool(item["tem_nota_fiscal"]),
            )
        )

    return despesas


def normalizar_despesas(despesas: list[Despesa]) -> list[Despesa]:
    normalizadas: list[Despesa] = []

    for despesa in despesas:
        valor_normalizado = despesa.valor_original.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        normalizadas.append(
            Despesa(
                id=despesa.id,
                data=despesa.data,
                categoria=despesa.categoria.lower(),
                descricao=despesa.descricao,
                fornecedor=despesa.fornecedor,
                valor_original=valor_normalizado,
                tem_nota_fiscal=despesa.tem_nota_fiscal,
            )
        )

    return normalizadas


def validar_categoria(despesa: Despesa) -> tuple[bool, str | None]:
    categorias_aceitas = {"alimentacao", "transporte_urbano", "hospedagem"}

    if despesa.categoria in categorias_aceitas:
        return True, None

    return False, "categoria_nao_politica"


def validar_nota_fiscal(despesa: Despesa) -> tuple[bool, str | None]:
    if despesa.valor_original > Decimal("100.00") and not despesa.tem_nota_fiscal:
        return False, "nota_fiscal_obrigatoria"

    return True, None


def validar_periodo(despesa: Despesa, periodo_inicio: str, periodo_fim: str) -> tuple[bool, str | None]:
    if periodo_inicio <= despesa.data <= periodo_fim:
        return True, None

    return False, "fora_do_periodo"


def identificar_duplicatas(despesas: list[Despesa]) -> list[dict[str, object]]:
    vistos: dict[tuple[str, str, str, str, Decimal], str] = {}
    resultados: list[dict[str, object]] = []

    for despesa in despesas:
        chave = (
            despesa.data,
            despesa.categoria,
            despesa.fornecedor,
            despesa.descricao,
            despesa.valor_original,
        )

        if chave in vistos:
            motivo = f"duplicata_de_{vistos[chave]}"
            resultados.append({"id": despesa.id, "duplicata": True, "motivo": motivo})
        else:
            vistos[chave] = despesa.id
            resultados.append({"id": despesa.id, "duplicata": False, "motivo": None})

    return resultados


def identificar_ajuste(despesa: Despesa) -> tuple[bool, str | None]:
    if despesa.valor_original < Decimal("0.00"):
        return True, "ajuste"

    return False, None


def calcular_limite_diario(despesas: list[Despesa]) -> dict[str, Decimal]:
    limites = {
        "alimentacao": Decimal("60.00"),
        "transporte_urbano": Decimal("80.00"),
    }

    tem_evidencia_viagem = any(despesa.categoria == "hospedagem" for despesa in despesas)

    if tem_evidencia_viagem:
        limites["alimentacao"] = Decimal("90.00")
        limites["transporte_urbano"] = Decimal("120.00")

    return limites


def calcular_reembolso_parcial(despesas: list[Despesa], limites: dict[str, Decimal]) -> list[dict[str, Decimal]]:
    if not despesas:
        return []

    categoria = despesas[0].categoria
    limite_categoria = limites.get(categoria, Decimal("0.00"))
    saldo_restante = limite_categoria
    resultados: list[dict[str, Decimal]] = []

    for despesa in despesas:
        valor = despesa.valor_original

        if valor <= Decimal("0.00"):
            reembolsavel = Decimal("0.00")
            nao_reembolsavel = Decimal("0.00")
        elif valor <= saldo_restante:
            reembolsavel = valor
            nao_reembolsavel = Decimal("0.00")
            saldo_restante -= valor
        else:
            reembolsavel = saldo_restante
            nao_reembolsavel = valor - saldo_restante
            saldo_restante = Decimal("0.00")

        resultados.append(
            {
                "valor_reembolsavel": reembolsavel,
                "valor_nao_reembolsavel": nao_reembolsavel,
            }
        )

    return resultados


def processar_despesas(payload: dict[str, object] | str | Path) -> dict[str, object]:
    if isinstance(payload, (str, Path)):
        path = Path(payload)
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

    colaborador = payload.get("colaborador", {})
    periodo = payload.get("periodo", {})
    despesas_payload = payload.get("despesas", [])

    despesas = []
    for item in despesas_payload:
        despesas.append(
            Despesa(
                id=item["id"],
                data=item["data"],
                categoria=item["categoria"],
                descricao=item["descricao"],
                fornecedor=item["fornecedor"],
                valor_original=Decimal(str(item["valor"])),
                tem_nota_fiscal=bool(item["tem_nota_fiscal"]),
            )
        )

    despesas_normalizadas = normalizar_despesas(despesas)
    duplicatas = {
        item["id"]: item
        for item in identificar_duplicatas(despesas_normalizadas)
    }

    periodo_inicio = str(periodo.get("inicio", ""))
    periodo_fim = str(periodo.get("fim", ""))

    limites_por_dia: dict[str, dict[str, Decimal]] = {}
    consumo_por_chave: dict[tuple[str, str], Decimal] = {}

    resultado_despesas: list[dict[str, object]] = []

    for despesa in despesas_normalizadas:
        duplicata_info = duplicatas.get(despesa.id, {})
        is_duplicata = bool(duplicata_info.get("duplicata"))
        motivo_duplicata = duplicata_info.get("motivo")

        if not validar_periodo(despesa, periodo_inicio, periodo_fim)[0]:
            resultado_despesas.append(
                {
                    "id": despesa.id,
                    "categoria": despesa.categoria,
                    "status": "ignorada",
                    "valor_original": despesa.valor_original,
                    "valor_reembolsavel": Decimal("0.00"),
                    "valor_nao_reembolsavel": Decimal("0.00"),
                    "motivo": "fora_do_periodo",
                    "justificativa": "Despesa fora do período de competência.",
                }
            )
            continue

        if is_duplicata:
            resultado_despesas.append(
                {
                    "id": despesa.id,
                    "categoria": despesa.categoria,
                    "status": "recusada",
                    "valor_original": despesa.valor_original,
                    "valor_reembolsavel": Decimal("0.00"),
                    "valor_nao_reembolsavel": Decimal("0.00"),
                    "motivo": motivo_duplicata,
                    "justificativa": f"Despesa duplicada de {motivo_duplicata.split('_')[-1] if motivo_duplicata else 'outra despesa'}.",
                }
            )
            continue

        ajuste, motivo_ajuste = identificar_ajuste(despesa)
        if ajuste:
            resultado_despesas.append(
                {
                    "id": despesa.id,
                    "categoria": despesa.categoria,
                    "status": "ignorada",
                    "valor_original": despesa.valor_original,
                    "valor_reembolsavel": Decimal("0.00"),
                    "valor_nao_reembolsavel": Decimal("0.00"),
                    "motivo": motivo_ajuste,
                    "justificativa": "Despesa identificada como ajuste e não gera reembolso.",
                }
            )
            continue

        categoria_valida, motivo_categoria = validar_categoria(despesa)
        if not categoria_valida:
            resultado_despesas.append(
                {
                    "id": despesa.id,
                    "categoria": despesa.categoria,
                    "status": "recusada",
                    "valor_original": despesa.valor_original,
                    "valor_reembolsavel": Decimal("0.00"),
                    "valor_nao_reembolsavel": Decimal("0.00"),
                    "motivo": motivo_categoria,
                    "justificativa": "Categoria não está na política de reembolso.",
                }
            )
            continue

        nota_valida, motivo_nota = validar_nota_fiscal(despesa)
        if not nota_valida:
            resultado_despesas.append(
                {
                    "id": despesa.id,
                    "categoria": despesa.categoria,
                    "status": "recusada",
                    "valor_original": despesa.valor_original,
                    "valor_reembolsavel": Decimal("0.00"),
                    "valor_nao_reembolsavel": Decimal("0.00"),
                    "motivo": motivo_nota,
                    "justificativa": "Valor superior a R$ 100,00 exige nota fiscal.",
                }
            )
            continue

        if despesa.categoria in {"alimentacao", "transporte_urbano"}:
            if despesa.data not in limites_por_dia:
                despesas_do_dia = [item for item in despesas_normalizadas if item.data == despesa.data]
                limites_por_dia[despesa.data] = calcular_limite_diario(despesas_do_dia)

            limites = limites_por_dia[despesa.data]
            limite = limites.get(despesa.categoria, Decimal("0.00"))
            chave = (despesa.data, despesa.categoria)
            saldo_restante = limite - consumo_por_chave.get(chave, Decimal("0.00"))

            if despesa.valor_original <= Decimal("0.00"):
                reembolsavel = Decimal("0.00")
                nao_reembolsavel = Decimal("0.00")
                status = "reembolsada"
                motivo = None
                justificativa = "Despesa reembolsável conforme a política."
            elif despesa.valor_original <= saldo_restante:
                reembolsavel = despesa.valor_original
                nao_reembolsavel = Decimal("0.00")
                status = "reembolsada"
                motivo = None
                justificativa = "Despesa reembolsável conforme a política."
                consumo_por_chave[chave] = consumo_por_chave.get(chave, Decimal("0.00")) + reembolsavel
            else:
                reembolsavel = saldo_restante
                nao_reembolsavel = despesa.valor_original - saldo_restante
                status = "parcialmente_reembolsada"
                motivo = "limite_diario_excedido"
                justificativa = "A despesa excedeu o limite diário permitido para a categoria."
                consumo_por_chave[chave] = consumo_por_chave.get(chave, Decimal("0.00")) + reembolsavel
        elif despesa.categoria == "hospedagem":
            resultado_limite = calcular_reembolso_parcial(
                [despesa],
                {"hospedagem": Decimal("250.00")},
            )
            resultado = resultado_limite[0]
            reembolsavel = resultado["valor_reembolsavel"]
            nao_reembolsavel = resultado["valor_nao_reembolsavel"]
            status = "reembolsada" if nao_reembolsavel == Decimal("0.00") else "parcialmente_reembolsada"
            motivo = None if status == "reembolsada" else "limite_diario_excedido"
            justificativa = "Despesa reembolsável conforme a política." if status == "reembolsada" else "A despesa excedeu o limite diário permitido para a categoria."
        else:
            reembolsavel = despesa.valor_original
            nao_reembolsavel = Decimal("0.00")
            status = "reembolsada"
            motivo = None
            justificativa = "Despesa reembolsável conforme a política."

        resultado_despesas.append(
            {
                "id": despesa.id,
                "categoria": despesa.categoria,
                "status": status,
                "valor_original": despesa.valor_original,
                "valor_reembolsavel": reembolsavel,
                "valor_nao_reembolsavel": nao_reembolsavel,
                "motivo": motivo,
                "justificativa": justificativa,
            }
        )

    valor_total_despesas = sum((item["valor_original"] for item in resultado_despesas), Decimal("0.00"))
    valor_reembolsavel = sum((item["valor_reembolsavel"] for item in resultado_despesas), Decimal("0.00"))
    valor_nao_reembolsavel = sum((item["valor_nao_reembolsavel"] for item in resultado_despesas), Decimal("0.00"))

    resumo = {
        "valor_total_despesas": float(valor_total_despesas),
        "valor_reembolsavel": float(valor_reembolsavel),
        "valor_nao_reembolsavel": float(valor_nao_reembolsavel),
        "quantidade_despesas": len(resultado_despesas),
        "quantidade_reembolsadas": sum(1 for item in resultado_despesas if item["status"] == "reembolsada"),
        "quantidade_parcialmente_reembolsadas": sum(1 for item in resultado_despesas if item["status"] == "parcialmente_reembolsada"),
        "quantidade_recusadas": sum(1 for item in resultado_despesas if item["status"] == "recusada"),
        "quantidade_ignorar": sum(1 for item in resultado_despesas if item["status"] == "ignorada"),
    }

    return {
        "colaborador": colaborador,
        "periodo": periodo,
        "resumo": resumo,
        "despesas": resultado_despesas,
    }
