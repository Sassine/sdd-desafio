# COPILOT-INSTRUCTIONS.md

## O projeto

Motor de cálculo de reembolso de despesas corporativas. O fluxo principal é uma CLI em Python que lê um JSON de despesas e gera um JSON com status, valor reembolsável e motivo por item.

## Fonte da verdade

- `specs/001-motor-reembolso/spec.md` define o que o sistema faz.
- `specs/001-motor-reembolso/plan.md` define como a solução é organizada.
- `specs/001-motor-reembolso/tasks.md` define a ordem de execução.
- `specs/001-motor-reembolso/DECISIONS.md` registra mudanças e ambiguidades resolvidas.

Quando código e spec discordarem, a spec está certa e o código é o bug; se a spec estiver errada, corrigimos a spec primeiro e registramos a decisão.

Antes de implementar qualquer coisa, leia a task correspondente em `tasks.md`.
Se o que foi pedido não estiver coberto por uma task, avise antes de implementar.

## Regras de trabalho

- Toda regra de negócio vive na spec, não no chat e não em comentário de código.
- Se uma regra for explicada fora da spec, pare e informe antes de escrever código.
- Mudanças de código devem ter teste. Nenhuma regra de negócio entra sem teste.
- Mudanças de documentação usam prefixos `docs(spec):`, `docs(plan):` ou `docs(tasks):`.

## Stack e comandos

- Linguagem: Python 3
- Rodar: `python src/reembolso.py --input <arquivo> --output <saida>`
- Testes: `python -m pytest -q`
- CLI de exemplo: `python src/reembolso.py --input exemplos/despesas-exemplo.json --output resultado.json`

## Convenções de código

- Preserve a separação entre regras de negócio e I/O.
- Use `Decimal` para valores monetários e arredonde para duas casas decimais.
- Não invente novas regras fora da spec; se algo for ambíguo, registre na spec e nas decisões.

## Fora de escopo

- Não implementar fila de aprovação manual, workflow de gestor ou persistência de estado.
- Não alterar a estrutura do JSON de saída sem ajustar a spec e os testes.
