# Motor de Cálculo de Reembolso

CLI que lê um JSON de despesas de um colaborador e emite um JSON com o valor
reembolsável e a justificativa de cada item, segundo a Política de Reembolso de
Despesas v3.

> **Status:** especificação fechada (`spec.md` 1.1, `plan.md` 1.0) e as 22 tasks
> da implementação base concluídas — 94 testes verdes. Ver o detalhe em
> [`specs/001-motor-reembolso/tasks.md`](specs/001-motor-reembolso/tasks.md).

---

## Requisitos

- Python 3.11 ou superior
- `pytest` (única dependência, apenas para rodar os testes)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pytest
```

## Como rodar

```bash
python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json
```

O comando lê o arquivo de entrada, aplica a política e escreve o resultado.
Retorna `0` em caso de sucesso. Entrada malformada retorna código diferente de
zero, informa qual campo está errado e **não** escreve o arquivo de saída.

## Como testar

```bash
pytest                  # suíte completa
pytest -k rn_007        # só os testes de uma regra de negócio
pytest -k e2e           # só o teste ponta a ponta sobre o exemplo oficial
```

Cada teste começa pelo ID da regra que exercita (`test_rn_007_...`), então dá
para ir de qualquer regra da spec ao teste que a cobre — e vice-versa. A matriz
completa está no fim do [`tasks.md`](specs/001-motor-reembolso/tasks.md).

## O que o sistema faz

Sobre `exemplos/despesas-exemplo.json`, o total reembolsável é **R$ 703,43**
sobre R$ 1.816,84 lançados. As decisões que produzem esse número não são óbvias
— a política do RH é ambígua em doze pontos, e cada um foi decidido e
justificado na spec:

| Entrada | Resultado | Por quê |
|---|---|---|
| `d-003` R$ 100,00 sem nota | R$ 80,00 | "acima de R$ 100" é estrito; segue para o teto de transporte |
| `d-004` R$ 100,01 sem nota | R$ 0,00 | um centavo acima do piso, sem nota — recusa integral |
| `d-006`/`d-007` R$ 54,90 idênticas | R$ 54,90 e R$ 0,00 | a segunda é duplicata |
| `d-010` R$ 480,00 hospedagem | R$ 375,00 | a data tem hospedagem, logo é viagem: teto de R$ 250 ampliado em 50% |
| `d-011` R$ 33,333 | R$ 33,33 | arredondamento de duas casas na leitura |
| `d-014` `ALIMENTACAO` R$ 61,00 | R$ 60,00 | categoria normalizada; excedente de R$ 1,00 glosado |

## Documentação

| Arquivo | O que responde |
|---|---|
| [`spec.md`](specs/001-motor-reembolso/spec.md) | O **quê** e o **porquê**: regras de negócio, as 12 ambiguidades e as decisões, casos de borda, ordem de aplicação |
| [`plan.md`](specs/001-motor-reembolso/plan.md) | O **como**: stack, arquitetura, modelo de dados, decisões técnicas, estratégia de testes |
| [`tasks.md`](specs/001-motor-reembolso/tasks.md) | Em que **ordem**: T-001 a T-022, com critério de aceite e matriz de cobertura |
| [`DECISIONS.md`](specs/001-motor-reembolso/DECISIONS.md) | O que **mudou** na spec, quando e por quê |
| [`CLAUDE.md`](CLAUDE.md) | Convenções do projeto para o agente |

Se o código e a spec discordarem, a spec está certa e o código é o bug.

## Material do desafio

Este repositório é um fork do desafio de Spec Driven Development. O enunciado
original está em [`DESAFIO.md`](DESAFIO.md), a rubrica em [`RUBRICA.md`](RUBRICA.md)
e os esqueletos de documento em [`template/`](template/).
