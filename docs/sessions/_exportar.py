"""Exporta os transcripts do Claude Code para docs/sessions/.

Alternativa ao `/export`, que nao funciona nesta maquina. Ver FAQ.md e o
README.md deste diretorio. Nao faz parte do produto: e utilitario de processo,
nao roda em producao e nao e coberto por task da spec.

Uso, a partir da raiz do repositorio:

    python docs/sessions/_exportar.py
"""
import json
import os
import re
import shutil
import sys
from glob import glob

SLUG = "c--Users-vitor-Documents-sdd-desafio"
ORIGEM = os.path.join(os.path.expanduser("~"), ".claude", "projects", SLUG)
DESTINO = os.path.join("docs", "sessions")

# Rotulo de cada sessao, por prefixo do UUID. Acrescente conforme surgirem.
ROTULOS = {
    "021469dd": "01-abertura-interrompida",
    "b2a2418d": "02-especificacao-spec-plan-tasks",
}

RUIDO = ("system-reminder", "ide_selection", "ide_opened_file", "local-command-caveat")


def blocos(registro):
    conteudo = registro.get("message", {}).get("content")
    if isinstance(conteudo, str):
        return [{"type": "text", "text": conteudo}]
    return conteudo if isinstance(conteudo, list) else []


def limpa(texto):
    for tag in RUIDO:
        texto = re.sub(rf"<{tag}>.*?</{tag}>", "", texto, flags=re.S)
    return texto.strip()


def renderiza(origem, destino, titulo):
    registros = [json.loads(l) for l in open(origem, encoding="utf-8") if l.strip()]
    marcas = [r.get("timestamp") for r in registros if r.get("timestamp")]
    periodo = f"{marcas[0][:16]} a {marcas[-1][11:16]}" if marcas else "?"

    linhas = [
        f"# {titulo}\n",
        f"**Periodo:** {periodo} · **Registros:** {len(registros)}",
        f"**Origem:** `{os.path.basename(origem)}` (copia crua no mesmo diretorio)\n",
        "> Renderizacao legivel do transcript. O `.jsonl` ao lado e a fonte",
        "> inalterada — em caso de divergencia, vale ele.\n",
        "---\n",
    ]

    for registro in registros:
        papel = registro.get("type")
        if papel not in ("user", "assistant"):
            continue
        for bloco in blocos(registro):
            if not isinstance(bloco, dict):
                continue
            tipo = bloco.get("type")

            if tipo == "text":
                texto = limpa(bloco.get("text", ""))
                if texto:
                    quem = "Usuario" if papel == "user" else "Claude"
                    linhas.append(f"### {quem}\n\n{texto}\n")

            elif tipo == "tool_use":
                entrada = json.dumps(bloco.get("input", {}), ensure_ascii=False)
                if len(entrada) > 400:
                    entrada = entrada[:400] + " …(truncado)"
                linhas.append(
                    f"<details><summary>🔧 <code>{bloco.get('name', '?')}</code></summary>\n\n"
                    f"```json\n{entrada}\n```\n</details>\n"
                )

            elif tipo == "tool_result":
                conteudo = bloco.get("content")
                if isinstance(conteudo, str):
                    texto = conteudo
                elif isinstance(conteudo, list):
                    texto = " ".join(
                        p.get("text", "") for p in conteudo if isinstance(p, dict)
                    )
                else:
                    texto = ""
                texto = texto.strip()
                if not texto:
                    continue
                if len(texto) > 600:
                    texto = texto[:600] + "\n…(resultado truncado — ver .jsonl)"
                linhas.append(
                    f"<details><summary>↩️ resultado</summary>\n\n```\n{texto}\n```\n</details>\n"
                )

    open(destino, "w", encoding="utf-8").write("\n".join(linhas))


def main():
    if not os.path.isdir(ORIGEM):
        sys.exit(f"Diretorio de transcripts nao encontrado: {ORIGEM}")
    os.makedirs(DESTINO, exist_ok=True)

    encontrados = sorted(glob(os.path.join(ORIGEM, "*.jsonl")), key=os.path.getmtime)
    if not encontrados:
        sys.exit(f"Nenhum .jsonl em {ORIGEM}")

    for caminho in encontrados:
        prefixo = os.path.basename(caminho)[:8]
        rotulo = ROTULOS.get(prefixo)
        if rotulo is None:
            print(f"[aviso] sessao {prefixo} sem rotulo em ROTULOS — pulada")
            continue
        shutil.copyfile(caminho, os.path.join(DESTINO, rotulo + ".jsonl"))
        renderiza(caminho, os.path.join(DESTINO, rotulo + ".md"), f"Sessao {rotulo}")
        print(f"exportada: {rotulo}")


if __name__ == "__main__":
    main()