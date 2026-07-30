# Desafio Prático — Spec Driven Development

**Duração:** 2 dias · **Modalidade:** individual · **Ferramenta:** Claude Code

---

## Por que este desafio existe

Você já passou por AI Fluency, Claude 101, Claude Code 101, Building with the Claude API e Claude Code in Action. Você sabe fazer o Claude escrever código. Essa parte está resolvida.

O problema que sobra é outro: **quando o software fica maior que uma conversa**, o que segura a qualidade não é a sua habilidade de prompt. É a existência de uma especificação que serve como fonte da verdade — para você, para o agente e para quem vier depois.

Este desafio não mede se o seu código funciona. Mede se o seu **processo** funciona.

> **Leia isto duas vezes:** o produto funcionando vale 10 dos 100 pontos. Um projeto que roda perfeitamente com spec fraca e sem rastreabilidade tira nota baixa. Um projeto com um bug conhecido, spec impecável e trilha de decisões clara tira nota alta. Isso é intencional.

---

## O problema

A empresa reembolsa despesas dos colaboradores. Hoje o processo é manual: alguém do financeiro abre a planilha, confere item por item contra a política e devolve uma lista de aprovações e recusas. Demora e sai errado.

Você vai construir o **motor de cálculo de reembolso**: dado o conjunto de despesas de um colaborador num período, ele decide quanto é reembolsável e justifica cada decisão.

### Interface (esta parte é fixa)

Uma CLI que lê um JSON e escreve um JSON:

```
<seu-comando> calcular --input despesas.json --output resultado.json
```

- **Stack livre.** Python, Node, Go, o que você domina.
- **A entrada** está definida em `exemplos/despesas-exemplo.json`. Respeite esse formato.
- **A saída** é você quem define. O schema de saída faz parte da sua spec — desenhe-o e documente-o.
- **Testes automatizados são obrigatórios.** Sem testes, a rastreabilidade não fecha.

### A política de reembolso (esta parte é o desafio)

O RH mandou isto. É literalmente o que eles mandaram, com a redação deles:

> **Política de Reembolso de Despesas — v3**
>
> 1. Alimentação tem limite de **R$ 60 por dia**.
> 2. Transporte urbano tem limite de **R$ 80 por dia**.
> 3. Hospedagem tem limite de **R$ 250 por diária**.
> 4. Despesas **acima do limite** são reembolsadas parcialmente.
> 5. **Nota fiscal é obrigatória acima de R$ 100.**
> 6. Colaborador **em viagem** tem limites ampliados em 50%.
> 7. Despesas devem ser lançadas **dentro do período de competência**.
> 8. **Duplicatas devem ser tratadas.**
> 9. Categorias fora da política não são reembolsáveis.

Essa política tem, no mínimo, **oito ambiguidades reais**. Algumas exemplos do tipo de pergunta que ela não responde:

- "R$ 60 por dia" — por dia ou por despesa? E se houver dois almoços no mesmo dia?
- "Reembolsadas parcialmente" — paga o limite e corta o excedente, ou recusa o item inteiro?
- "Acima de R$ 100" — e uma despesa de exatamente R$ 100,00?
- "Em viagem" — o que caracteriza estar em viagem? Não há esse campo na entrada.
- "Duplicatas devem ser tratadas" — tratadas como?

**Encontrar e resolver essas ambiguidades é o trabalho.** Não é um obstáculo no caminho do trabalho: é o trabalho.

Você não tem acesso ao RH. Então, para cada ambiguidade, você vai:

1. **Registrar** que ela existe.
2. **Decidir**, explicitamente, qual interpretação adota.
3. **Justificar** a decisão em uma linha.
4. Deixar isso na `spec.md`, onde qualquer pessoa (ou agente) que ler saiba exatamente o que o sistema faz e por quê.

Uma spec que apenas copia a política do RH está reprovada nesse critério. A spec é onde a ambiguidade morre.

---

## O que entregar

Um repositório Git com esta estrutura:

```
seu-repo/
├── COPILOT-INSTRUCTIONS.md      # convenções do projeto para o agente
├── README.md                     # como rodar e como testar
├── specs/
│   └── 001-motor-reembolso/
│       ├── spec.md               # o QUÊ e o PORQUÊ
│       ├── plan.md               # o COMO
│       ├── tasks.md              # T-001..T-0NN, com critério de aceite
│       └── DECISIONS.md          # log de mudanças de spec
├── src/
├── tests/
└── docs/
    ├── sessions/                 # exports das suas conversas com o Claude
    └── RELATORIO.md              # o relatório final
```

Use os arquivos em `template/` como ponto de partida — eles já vêm com a estrutura e as perguntas que cada documento precisa responder.

### O que vai em cada documento

**`spec.md` — o quê e o porquê.**
Requisitos funcionais, regras de negócio já desambiguadas, casos de borda, critérios de aceite, e o que está explicitamente **fora** de escopo. Escrito de forma que alguém consiga verificar se o sistema atende, sem ler o código.
Proibido: nome de biblioteca, nome de classe, estrutura de pastas, decisão de linguagem. Se apareceu solução, saiu da spec.

**`plan.md` — o como.**
Stack e por quê. Arquitetura em blocos. Modelo de dados. Decisões técnicas com a alternativa que você descartou e o motivo. Estratégia de testes.

**`tasks.md` — a fatia executável.**
Tarefas `T-001`, `T-002`, ... Cada uma com: o que faz, quais requisitos da spec ela atende, e o critério de aceite (normalmente "o teste X passa"). Uma task deve ser pequena o suficiente para virar um commit.

**`DECISIONS.md` — o log de mudanças de spec.**
Toda vez que a spec mudar, uma entrada: o que mudou, por quê, o que quebrou, quais tasks foram afetadas. Este arquivo é a prova de que você tratou a spec como um artefato vivo e não como um documento cerimonial escrito no começo e abandonado.

**`docs/sessions/` — as suas interações.**
Exporte suas conversas do Claude Code e commite. Um arquivo por sessão, nomeado `NN-descricao-curta.md`.

> Como exportar: dentro do Claude Code, rode `/export` para salvar a conversa atual em arquivo. Faça isso ao final de cada sessão de trabalho — se você fechar o terminal sem exportar, o esforço daquela sessão vira invisível para a correção.

**`docs/RELATORIO.md` — o relatório final.**
Detalhado mais abaixo. É onde metade da sua nota mora.

---

## As três regras do jogo

Estas regras não são burocracia. São o mecanismo que faz o SDD acontecer em vez de ser encenado.

### 1. Nenhum commit sem task

Toda mensagem de commit referencia a task:

```
feat(T-003): aplica limite diário de alimentação com agregação por data
test(T-003): casos de borda de múltiplas despesas no mesmo dia
docs(spec): resolve ambiguidade de reembolso parcial — corta excedente
```

Commits de spec/docs usam `docs(spec)`, `docs(plan)`, `docs(tasks)`.
O `git log` vai ser lido na correção. Ele é a sua trilha de auditoria.

### 2. Explicação no chat que não está na spec é bug de spec

Se você precisou digitar para o Claude uma regra de negócio, uma decisão ou uma restrição que não está escrita na spec — **a spec está incompleta**. Pare, corrija a spec, registre no `DECISIONS.md`, e só então continue.

Esta regra é o coração do desafio. O chat é volátil; a spec é o que fica. Todo conhecimento que só existe no chat é conhecimento que você vai perder.

### 3. Interações exportadas e commitadas

Sem `docs/sessions/`, não há como avaliar seu processo — e processo é o que está sendo avaliado. Exports vazios ou de uma única sessão gigante no último minuto são sinal de que a regra foi cumprida por fora.

---

## Cronograma

| Quando | O quê |
|---|---|
| **Dia 1, manhã** | `spec.md` → `plan.md` → `tasks.md`. Não escreva código ainda. |
| **Dia 1, tarde** | Implementação guiada pelas tasks. Commits rastreáveis. |
| **Dia 2, ~10h** | **Chega o envelope lacrado.** Você recebe uma mudança de requisito que não sabia que vinha. |
| **Dia 2, tarde** | Absorve a mudança, fecha os testes, escreve o `RELATORIO.md`. |
| **Dia 2, 18h** | Entrega: link do repositório. |

Sobre o envelope: ele é real, é obrigatório, e vale 20 pontos. Não é pegadinha — é a demonstração empírica de por que você passou a manhã do dia 1 escrevendo documento em vez de código. Quem especificou de verdade absorve a mudança editando a spec e reexecutando as tasks. Quem não especificou vai refazer na mão.

**Recomendação forte:** chegue ao dia 2 com o sistema base funcionando e testado. Você vai querer as mãos livres.

---

## O relatório

`docs/RELATORIO.md`, organizado pelos 4 Ds do AI Fluency. Não é redação — são evidências. Cite arquivos, linhas, commits e trechos das suas sessões exportadas.

**Delegação.** O que você fez e o que o Claude fez. Por que dividiu assim. Onde você delegou e se arrependeu, ou onde não delegou e deveria ter delegado.

**Descrição.** Pegue um requisito ambíguo da política do RH. Cole a sua primeira versão dele na spec e a versão final. O que estava ambíguo, como você percebeu, o que mudou. Se a primeira versão já estava boa, prove com o histórico do arquivo.

**Discernimento.** *Pelo menos um caso concreto em que o Claude errou e você pegou.* Alucinação, requisito interpretado errado, teste que testava a coisa errada, solução desnecessariamente complexa, o que for. Precisa de: o que ele propôs, por que estava errado, como você detectou, o que fez. Com link para o trecho da sessão exportada.
**Sem um caso concreto e verificável, esta seção vale zero.**

**Diligência.** O que você verificou antes de aceitar cada entrega do agente. Rodou os testes? Leu o diff inteiro ou passou o olho? O que você aceitou sem verificar direito, e o que isso te custou depois?

**O envelope.** Quantos arquivos você tocou na mão para absorver a mudança do dia 2? Quanto tempo levou? O que na sua spec original facilitou, e o que atrapalhou? Se você tivesse escrito a spec sabendo da mudança, o que teria feito diferente?

Honestidade vale ponto aqui. Relatório que diz "correu tudo bem, o Claude acertou tudo" é relatório de quem não estava olhando — e é avaliado como tal.

---

## Como você é avaliado

| Critério | Pontos |
|---|---|
| Qualidade da spec — testável, sem solução vazada, ambiguidades resolvidas | 25 |
| Rastreabilidade — spec → tasks → commits → testes | 25 |
| Resposta à mudança de requisito | 20 |
| Relatório — evidência real de discernimento | 20 |
| Produto funciona | 10 |

Detalhamento completo em `RUBRICA.md`. Leia antes de começar — ela é pública de propósito.

---

## Perguntas frequentes

**Posso usar o Claude para escrever a spec?**
Sim, e é esperado que use. Mas a spec é sua: as decisões sobre ambiguidade são suas, e você vai ter que defendê-las no relatório. Spec gerada e aceita sem revisão aparece na correção — ela tem um cheiro característico.

**E se eu não terminar o produto?**
Entregue o que tem. 10 pontos estão em jogo no produto; 90 estão no resto. Um projeto incompleto com spec impecável e trilha limpa vai bem. Não sacrifique a spec para fechar features.

**Posso mudar a spec no meio?**
Deve. Spec que não muda em 2 dias é spec que ninguém consultou. O que se avalia não é estabilidade — é se toda mudança está registrada e justificada no `DECISIONS.md`.

**Quantas ambiguidades eu preciso achar?**
Existem pelo menos oito. Achar mais que oito é sinal bom. Rode o `exemplos/despesas-exemplo.json` mentalmente contra a política antes de escrever qualquer coisa — cada linha daquele arquivo está lá por um motivo.

**Posso usar subagentes, skills, MCP, hooks?**
Sim. E se usar, conte no relatório — como configurou e se valeu a pena. Vale ponto em Delegação.
