# Handoff — fim do Dia 1, tarde

**Data:** 2026-07-30 · **Próxima sessão:** Dia 2, ~10h — envelope lacrado

> Este arquivo é fino de propósito. O contexto real do projeto vive na `spec.md`,
> no `plan.md` e no `tasks.md` — se alguma regra de negócio só existir aqui, é
> bug de spec. Aqui ficam só o estado, o que está pendente e por onde retomar.

---

## Estado

| Artefato | Estado | Commit |
|---|---|---|
| `specs/001-motor-reembolso/spec.md` | 1.1 — corrigido RN-006→RN-007 no exemplo da §4 (D-001); §9 com os 10 critérios marcados `[x]` | `bd1f432` |
| `specs/001-motor-reembolso/tasks.md` | T-001..T-022 concluídas, `[x]`, com hash de commit preenchido em cada uma | ver `git log --grep "T-0"` |
| `specs/001-motor-reembolso/DECISIONS.md` | D-001 registrado (inconsistência RN-006/RN-007 no exemplo da spec) | `bd1f432` |
| `src/` | núcleo completo: `motor/modelo.py`, `motor/politica.py`, `motor/regras.py`, `motor/calculadora.py`, `io/carregador.py`, `io/serializador.py`, `cli.py` | — |
| `tests/` | 94 testes, todos verdes (`pytest -q`) | — |
| `docs/sessions/` | sessão 03 (implementação) exportada em andamento — reexportar ao fechar o terminal para capturar as mensagens finais | — |

Critério de aceite da spec §9 confirmado pelo teste ponta a ponta
(`tests/test_e2e_exemplo_oficial.py`, T-022): sobre
`exemplos/despesas-exemplo.json`, **total lançado R$ 1.816,84 · total
reembolsável R$ 703,43**, com `d-003=80.00`, `d-004=0.00`, `d-006=54.90`,
`d-007=0.00`, `d-010=375.00`, `d-011=33.33`, `d-014=60.00`.

Também confirmado manualmente via CLI real:
`python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json`
(arquivo gerado, não commitado — está no `.gitignore`).

## O que mudou na spec durante a implementação

**D-001** — o exemplo ilustrativo da spec §4 rotulava as duas decisões de teto
(`d-001`, `d-002`) com `regras_aplicadas: ["RN-006"]`, mas RN-006 é a regra de
nota fiscal; a decisão descrita é de teto (RN-007). Corrigido no exemplo antes
de implementar T-012, para não herdar o erro no código. Ver `DECISIONS.md`.
Nenhuma outra mudança de spec foi necessária — as 12 ambiguidades decididas na
manhã se sustentaram sem revisão durante a implementação.

## Pendências que não são código (carregadas do handoff da manhã)

1. **Reexportar a sessão 03 ao fechar este terminal:** `python docs/sessions/_exportar.py`
   (já registrada no `ROTULOS`). A exportação feita durante a sessão não contém
   as mensagens finais — reexportar sobrescreve com o transcript completo.
2. **O `RELATORIO.md` precisa explicar o formato das sessões** (alternativa ao
   `/export`, motivo em `docs/sessions/README.md`) — ainda não escrito, é
   trabalho do Dia 2.
3. **Revisão das decisões de ambiguidade** (as 7 sub-decisões da tabela abaixo,
   carregada do handoff da manhã) — ainda não revisadas, só implementadas
   fielmente ao que a spec já dizia.

| Onde | O que foi decidido |
|---|---|
| RN-009 / AMB-006 | Os 50% de viagem ampliam só os tetos de categoria, não o piso de R$ 100 da nota fiscal |
| RN-009 / AMB-006 | Hospedagem confere viagem à data mesmo quando a própria hospedagem é recusada |
| RN-003 / AMB-009 | Despesa fora da competência é recusada **e permanece** no resultado |
| RN-001 | Idem para categoria fora da política |
| RN-004 / AMB-008 | A chave de duplicata inclui `descricao`; vence a primeira na ordem da entrada |
| RN-005 / AMB-010 | Estorno não consome nem devolve teto de nenhuma outra despesa |
| §10 | Sábado (`d-012`) foi para questões em aberto, não virou ambiguidade |

## Decisões de implementação que não estão no `plan.md` (vale registrar se alguém perguntar)

- **RN-004 (duplicata) é uma fábrica, não uma função direta.** `criar_rn_004_duplicata()`
  devolve uma função `(Despesa, Contexto) -> Parecer | None` com estado próprio
  via closure (o conjunto de chaves já vistas), porque é a única regra que
  precisa saber sobre despesas anteriores na mesma execução. Uma instância nova
  por chamada de `calcular()` evita estado vazando entre execuções — a
  calculadora monta a lista de regras (incluindo essa fábrica) a cada chamada.
- **`d-010` amplia o próprio teto**, confirmado no `test_casos_de_borda`
  (`RN-008-hospedagem-varias-noites`): uma hospedagem isolada, sozinha na
  entrada, sai por R$ 375,00 (não R$ 250,00) porque ela mesma torna sua data
  uma data de viagem. É a mesma matemática de `d-010` no exemplo oficial. O
  teste unitário de T-013 (`test_rn_008_hospedagem.py`) prova a regra "crua"
  (sem viagem) construindo um `Contexto` manualmente; o teste de casos de
  borda prova o comportamento real de ponta a ponta. Os dois são intencionais
  e não contradizem um ao outro — testam camadas diferentes.

## ⚠️ Pendência importante para o Dia 2 — granularidade dos commits

O `DESAFIO.md` (linhas 131-135) mostra `test(T-003)` e `feat(T-003)` como
**dois commits separados** para a mesma task, e é isso que o handoff da manhã
também instruía. Na implementação da tarde (T-001..T-022), isso **não** foi
seguido: quase toda task fechou num único commit `feat(T-0XX)` com teste e
implementação juntos (exceção: T-013, T-016, T-017, T-018, T-020, que só
acrescentaram teste a código que já existia e por isso já saíram como
`test(T-0XX)` sozinho — nesses a convenção bateu por acidente).

**Decisão:** não reescrever o histórico do Dia 1 para corrigir isso — é
exatamente o cenário do `FAQ.md` ("Meus commits ficaram grandes demais"): não
reescreva para maquiar, registre o que aconteceu e siga a convenção certa daí
em diante. Histórico honesto imperfeito vale mais que histórico reescrito.

**Para o Dia 2 (T-023 em diante): separar sempre `test(T-02X)` e `feat(T-02X)`
em dois commits**, na ordem teste → implementação, como o exemplo do
`DESAFIO.md` mostra. Sem exceção, mesmo quando parecer pequeno demais para
valer dois commits.

**Isto precisa ir para o `RELATORIO.md`** (seção de Rastreabilidade ou
Diligência): citar que a Fase 1-4 desviou da granularidade do exemplo,
por quê não foi corrigida por reescrita, e que a Fase 5 corrige o padrão
daqui em diante.

## Por onde retomar

Sistema base funcionando e testado, pronto para o envelope do Dia 2. Não há
tasks pendentes da Fase 1 a 4; a Fase 5 (`## Fase 5 — Envelope`) em `tasks.md`
está vazia, aguardando a mudança de requisito.

Ordem de trabalho ao absorver o envelope, conforme `CLAUDE.md` e `DESAFIO.md`:

1. Registrar o gatilho e a mudança em `DECISIONS.md` **antes** de tocar em código.
2. Editar `spec.md` (e `plan.md` se a mudança for de arquitetura).
3. Criar as tasks novas em `tasks.md` a partir de T-023 — não renumerar as antigas.
4. Só então código: commit `test(T-02X)` primeiro, commit `feat(T-02X)` depois,
   **sempre separados** (ver pendência de granularidade acima).

Se aparecer uma regra de negócio que não está na `spec.md`, **pare** — é bug de
spec, e o conserto é na spec antes do código.
