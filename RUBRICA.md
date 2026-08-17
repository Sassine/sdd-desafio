# Rubrica de Avaliação — Desafio SDD

Total: **100 pontos**. Esta rubrica é pública. Leia antes de começar.

Cada critério tem quatro faixas. A nota cai na faixa cujo descritor for verdadeiro — não na faixa que a entrega "quase" alcança.

---

## 1. Qualidade da spec — 25 pontos

Avalia `specs/001-motor-reembolso/spec.md`.

| Faixa | Descritor |
|---|---|
| **23–25** | As oito ambiguidades da política estão identificadas e resolvidas com decisão explícita e justificativa. Nenhuma solução técnica vazou para a spec. Critérios de aceite são verificáveis sem ler código. Escopo negativo declarado ("o que este sistema não faz"). Um desenvolvedor que nunca viu o projeto implementaria a mesma coisa. |
| **17–22** | Maioria das ambiguidades resolvida. Uma ou duas decisões estão implícitas no código em vez de escritas. Um ou dois vazamentos de solução (nome de biblioteca, estrutura de pasta). Critérios de aceite majoritariamente verificáveis. |
| **9–16** | A spec existe e organiza os requisitos, mas ambiguidades centrais ficaram em aberto ou foram resolvidas silenciosamente na implementação. Mistura o quê com o como. Critérios de aceite vagos ("deve funcionar corretamente"). |
| **0–8** | Reescrita da política do RH com formatação melhor. Ou spec gerada pelo agente e aceita sem revisão. Ou a spec descreve o código que já existia. |

**Zera este critério:** a spec não menciona nenhuma ambiguidade.

**Sobre a lista de ambiguidades.** A correção usa uma lista fechada de oito ambiguidades de referência. Ela **não é publicada** — identificá-las é o exercício, e entregar a lista pronta esvaziaria 25 dos 100 pontos.

O que dá para dizer sem estragar o desafio:

- São **no mínimo oito**. Todas estão alcançáveis a partir da política do RH cruzada com `exemplos/despesas-exemplo.json`. Cada item daquele arquivo existe por um motivo.
- Elas se distribuem por **três tipos**: *unidade de aplicação* (a que conjunto uma regra se aplica), *fronteira* (comparações, arredondamento, limites inclusivos ou exclusivos) e *dado ausente* (a política pressupõe informação que a entrada não traz).
- Achar mais de oito é sinal bom e conta a favor dentro da faixa. Achar oito "genéricas" sem decisão registrada não conta.
- **Não existe interpretação certa.** Uma decisão que o avaliador acharia ruim, mas que está escrita e justificada, pontua integralmente. O que não pontua é a ambiguidade resolvida silenciosamente dentro do código.

---

## 2. Rastreabilidade — 25 pontos

Avalia a cadeia `spec.md` → `tasks.md` → `git log` → `tests/`.

| Faixa | Descritor |
|---|---|
| **23–25** | Toda task referencia requisitos da spec. Todo commit referencia uma task. Todo requisito testável tem teste. Dá para pegar qualquer regra de negócio da spec e chegar, sem adivinhar, na linha de código e no teste que a implementam — e vice-versa. |
| **17–22** | A cadeia fecha na maior parte. Alguns commits sem task ou tasks sem requisito. Cobertura de testes boa mas com lacunas nos casos de borda. |
| **9–16** | Tasks existem mas foram escritas depois do código, ou são genéricas demais ("implementar o motor"). Commits em bloco. Testes existem mas testam o caminho feliz. |
| **0–8** | Commits do tipo "wip", "ajustes", "final". Sem testes, ou testes que não exercitam as regras de negócio. `tasks.md` decorativo. |

**Sinais que a correção procura:**
- Histórico de commits com granularidade compatível com as tasks (não 3 commits gigantes, não 200 micro-commits)
- Datas dos commits condizentes com a ordem spec → plan → tasks → código
- Testes nomeados de forma que remetem aos requisitos
- `tasks.md` com tasks marcadas como concluídas ao longo do caminho, não todas de uma vez

---

## 3. Resposta à mudança de requisito — 20 pontos

Avalia como o envelope lacrado do dia 2 foi absorvido.

| Faixa | Descritor |
|---|---|
| **18–20** | A mudança entrou pela spec: `spec.md` atualizada, entrada no `DECISIONS.md` com o que quebrou, novas tasks criadas, implementação em seguida. Testes existentes continuam passando ou a quebra está justificada. O diff é cirúrgico — a arquitetura absorveu a mudança em vez de resistir a ela. |
| **13–17** | A mudança foi absorvida e a spec foi atualizada, mas fora de ordem (código primeiro, spec depois) ou o `DECISIONS.md` está superficial. Diff maior que o necessário. |
| **6–12** | Implementou direto no código, spec ficou desatualizada ou foi remendada no fim. Testes antigos quebrados sem tratamento. |
| **0–5** | Não absorveu a mudança, ou refez o sistema do zero, ou a spec agora contradiz o código. |

**Não penaliza:** a mudança não ficar 100% completa em meio dia. Penaliza: ela entrar por fora da spec.

**Bônus (até +3, teto de 20):** o relatório demonstra, com números, quanto da absorção veio de reexecutar tasks a partir da spec atualizada versus edição manual.

---

## 4. Relatório e discernimento — 20 pontos

Avalia `docs/RELATORIO.md` cruzado com `docs/sessions/`.

| Faixa | Descritor |
|---|---|
| **18–20** | Os cinco blocos (4 Ds + envelope) respondidos com evidência: commits citados, trechos de sessão referenciados, antes/depois de requisitos colados. A seção de Discernimento traz um erro concreto do agente, com o que foi proposto, por que estava errado e como foi detectado. Há autocrítica verificável — algo que a pessoa faria diferente, com o motivo. |
| **13–17** | Blocos respondidos, evidência parcial. Discernimento tem um caso real mas superficialmente descrito, ou sem link para a sessão. |
| **6–12** | Relatório narrativo sem evidência. "Foi tranquilo", "o Claude ajudou bastante". Discernimento genérico ("sempre revisei o código"). |
| **0–5** | Ausente, ou visivelmente gerado sem revisão, ou contradiz o que está no repositório. |

**Zera a seção de Discernimento (−8 no critério):** nenhum caso concreto de erro do agente. Não existe projeto de 2 dias em que o modelo acertou tudo; a ausência do caso significa que ninguém estava conferindo.

**Sessões exportadas:** ausência total zera este critério inteiro. Uma sessão única exportada no último minuto limita a faixa a 12.

---

## 5. Produto funciona — 10 pontos

| Faixa | Descritor |
|---|---|
| **9–10** | Roda pelo README sem intervenção. Processa `despesas-exemplo.json` e o conjunto oculto do instrutor. Saída coerente com a spec. Testes passando. |
| **6–8** | Roda, saída coerente, mas exige um ajuste manual não documentado ou falha em algum caso oculto. |
| **3–5** | Roda parcialmente, ou o resultado diverge do que a própria spec define. |
| **0–2** | Não executa. |

Casos ocultos do instrutor exercitam as mesmas oito ambiguidades com valores diferentes. **A saída é conferida contra a spec do próprio aluno**, não contra um gabarito único. Se a spec diz que estorno é ignorado e o código ignora, está certo. Se a spec diz que é ignorado e o código soma, está errado — mesmo que somar fosse a interpretação "melhor".

---

## Penalidades transversais

| Situação | Efeito |
|---|---|
| Regra de negócio que só existe no chat, nunca na spec | −5 por ocorrência, teto −15 |
| `DECISIONS.md` ausente tendo havido mudança de spec | −5 |
| `COPILOT-INSTRUCTIONS.md` ausente | −3 |
| README não permite rodar o projeto | −3 |
| Repositório sem histórico (commit único "initial commit") | −15, e o critério 2 fica limitado a 8 |

---

## O que esta rubrica deliberadamente não premia

- Elegância do código
- Quantidade de features
- Cobertura de testes como número
- Tamanho da spec

Spec longa não é spec boa. O critério é: **uma pessoa que nunca viu o projeto consegue, lendo só a spec, verificar se o sistema está correto?**
