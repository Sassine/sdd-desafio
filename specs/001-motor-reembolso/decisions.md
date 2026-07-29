# DECISIONS — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** inicial

> Este arquivo registra mudanças de decisão de negócio e de especificação ao longo do projeto. Toda mudança importante na spec deve entrar aqui com contexto, motivação, impacto e rastreio.

---

## 1. Formato das entradas

Cada entrada deve registrar:

- **Data**
- **Resumo da mudança**
- **Motivo**
- **Impacto na spec / tasks / testes**
- **Decisão final**

---

## 2. Histórico de decisões

### DEC-001 — Definição de reembolso parcial

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida a interpretação de despesas acima do limite como parcialmente reembolsadas, em vez de rejeitadas integralmente.
- **Motivo:** a política menciona explicitamente “reembolsadas parcialmente”, então a interpretação mais coerente era cortar apenas o excedente.
- **Impacto na spec / tasks / testes:** afetou RN-003, AMB-002 e T-005.
- **Decisão final:** o valor até o limite é reembolsável e o excedente é não reembolsável.

### DEC-002 — Regra de nota fiscal acima de R$ 100,00

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida a regra de que valores exatamente iguais a R$ 100,00 não exigem nota fiscal, enquanto valores acima disso exigem.
- **Motivo:** a frase “acima de R$ 100” sugere um limiar estrito.
- **Impacto na spec / tasks / testes:** afetou RN-004, AMB-003 e T-006.
- **Decisão final:** despesas com valor superior a 100,00 sem nota fiscal são recusadas.

### DEC-003 — Interpretação de “em viagem”

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida uma inferência simples e explícita para identificar viagem com base em evidência textual do dia da despesa.
- **Motivo:** a política menciona limites ampliados em viagem, mas a entrada não possui um campo explícito para isso.
- **Impacto na spec / tasks / testes:** afetou RN-005, AMB-004 e T-004.
- **Decisão final:** a condição de viagem é inferida apenas quando há evidência explícita de viagem na descrição ou fornecedor, aplicada para o mesmo dia da despesa.

### DEC-004 — Tratamento de despesas fora do período

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que despesas fora do intervalo de competência são ignoradas, e não reembolsadas.
- **Motivo:** a política pede que as despesas sejam lançadas dentro do período de competência, mas não diz se devem ser recusadas ou ignoradas.
- **Impacto na spec / tasks / testes:** afetou RN-006, AMB-006 e T-007.
- **Decisão final:** despesas fora do período entram no resultado com status ignorada.

### DEC-005 — Tratamento de duplicatas

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que duplicata é a repetição de data, categoria, fornecedor, descrição e valor.
- **Motivo:** a política menciona duplicatas sem especificar o critério de comparação.
- **Impacto na spec / tasks / testes:** afetou RN-007, AMB-005 e T-008.
- **Decisão final:** a primeira ocorrência é mantida e as demais são recusadas como duplicatas.

### DEC-006 — Tratamento de valores negativos

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que valores negativos são considerados ajustes e não geram reembolso.
- **Motivo:** a política não prevê estornos nem ajustes, então a interpretação mais segura é tratá-los como não reembolsáveis.
- **Impacto na spec / tasks / testes:** afetou RN-008, AMB-009 e T-009.
- **Decisão final:** valores negativos são registrados como ignorados.

### DEC-007 — Ordem de execução das regras

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida a ordem de aplicação das regras para garantir consistência.
- **Motivo:** quando múltiplas regras se aplicam à mesma despesa, a ordem altera o resultado.
- **Impacto na spec / tasks / testes:** afetou a seção 8 da spec, o plano técnico e a ordem de desenvolvimento.
- **Decisão final:** a implementação deve seguir a ordem: normalização, período, duplicatas, ajustes, categoria, nota fiscal, limites e saída.

### DEC-008 — Divisão da task original de casos de borda

- **Data:** 2026-07-29
- **Resumo da mudança:** A task original que misturava período, duplicatas e valores negativos foi dividida em três tasks independentes.
- **Motivo:** reduzir a granularidade e manter rastreabilidade 1:1 entre commit e regra de negócio.
- **Impacto na spec / tasks / testes:** afetou o plano de execução e a organização das tasks em T-007, T-008 e T-009.
- **Decisão final:** o tratamento de despesas fora do período ficou em T-007, duplicatas em T-008 e valores negativos em T-009.

### DEC-009 — Precisão de valores monetários

- **Data:** 2026-07-29
- **Resumo da mudança:** Adicionada RN-011/AMB-011 definindo arredondamento 
  para 2 casas decimais (ROUND_HALF_UP) durante a normalização.
- **Motivo:** o JSON de exemplo contém uma despesa com 3 casas decimais 
  (33.333), caso não previsto pela política do RH; a implementação da 
  T-002 já precisava dessa regra para não propagar sujeira de dado.
- **Impacto na spec / tasks / testes:** spec.md ganhou RN-011/AMB-011; 
  tasks.md T-002 atualizada; novo teste de arredondamento em empate.
- **Decisão final:** ROUND_HALF_UP, aplicado em normalizar_despesas.