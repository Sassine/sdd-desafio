# Handoff — fim do Dia 1, manhã

**Data:** 2026-07-30 · **Próxima sessão:** Dia 1, tarde — implementação

> Este arquivo é fino de propósito. O contexto real do projeto vive na `spec.md`,
> no `plan.md` e no `tasks.md` — se alguma regra de negócio só existir aqui, é
> bug de spec. Aqui ficam só o estado, o que está pendente e por onde retomar.

---

## Estado

| Artefato | Estado | Commit |
|---|---|---|
| `specs/001-motor-reembolso/spec.md` | 1.0 — RN-001..RN-010, 12 ambiguidades decididas, 18 casos de borda, ordem de aplicação | `a85d821` |
| `specs/001-motor-reembolso/plan.md` | 1.0 — Python 3.11+/`Decimal`, DT-001..DT-006 | `7d9c222` |
| `specs/001-motor-reembolso/tasks.md` | T-001..T-022, matriz de cobertura preenchida | `2d36cec` |
| `CLAUDE.md`, `README.md` | preenchidos | `ac6b65d` |
| `specs/001-motor-reembolso/DECISIONS.md` | vazio **de propósito** — spec 1.0 é a linha de base | — |
| `src/`, `tests/` | não existem — a manhã é sem código, por cronograma | — |
| `docs/sessions/` | **pendente** — ver abaixo | — |

Números de referência já verificados contra `exemplos/despesas-exemplo.json`:
**total lançado R$ 1.816,84 · total reembolsável R$ 703,43**. Estão fixados como
critério de aceite na `spec.md` §9 e são o alvo da T-022.

## Pendências que não são código

1. **`/export` da sessão da manhã** para `docs/sessions/01-especificacao.md`.
   Sem `docs/sessions/`, o critério 4 da rúbrica vale zero. É a única pendência
   com custo de nota já incorrido.

2. **Revisão das decisões de ambiguidade.** As 12 foram decididas na opção A.
   Sete sub-decisões não estavam cobertas pela letra e foram tomadas junto —
   estão marcadas abaixo. Elas já vivem na `spec.md`; a pendência é a revisão,
   não o registro.

## Sub-decisões tomadas sem escolha explícita

Todas já registradas na spec. Se alguma for revertida, o caminho é
`spec.md` → entrada no `DECISIONS.md` → tasks afetadas.

| Onde | O que foi decidido |
|---|---|
| RN-009 / AMB-006 | Os 50% de viagem ampliam só os tetos de categoria, não o piso de R$ 100 da nota fiscal |
| RN-009 / AMB-006 | Hospedagem confere viagem à data mesmo quando a própria hospedagem é recusada |
| RN-003 / AMB-009 | Despesa fora da competência é recusada **e permanece** no resultado |
| RN-001 | Idem para categoria fora da política |
| RN-004 / AMB-008 | A chave de duplicata inclui `descricao`; vence a primeira na ordem da entrada |
| RN-005 / AMB-010 | Estorno não consome nem devolve teto de nenhuma outra despesa |
| §10 | Sábado (`d-012`) foi para questões em aberto, não virou ambiguidade |

## Dois pontos que merecem atenção na implementação

- **`d-010` amplia o próprio teto.** É a hospedagem dela que torna 14/07 uma data
  de viagem, então sai por R$ 375,00 e não R$ 250,00. É circular, está justificado
  na RN-009, e é a decisão mais provável de o avaliador questionar.
- **A RN-008 não é exercitada pelo exemplo oficial.** `d-013` morre na checagem de
  nota fiscal (passo 7) antes de chegar ao teto (passo 8), então o caso "3 noites"
  nunca roda. A T-013 precisa de um caso construído à mão, com nota fiscal.

## Por onde retomar

Próxima task: **T-001** (esqueleto do projeto e harness de teste). Depois a
Fase 1 inteira, T-001 a T-005, antes de qualquer regra de negócio.

Ordem de trabalho a cada task, conforme `CLAUDE.md`:

1. Ler a task no `tasks.md` e a RN correspondente na `spec.md`.
2. Escrever o teste do critério de aceite — `test(T-00X)`.
3. Implementar até passar — `feat(T-00X)`.
4. Marcar `[x]` na task e preencher o hash no campo **Commit**.

Se aparecer uma regra de negócio que não está na `spec.md`, **pare** — é bug de
spec, e o conserto é na spec antes do código.
