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
- **Impacto na spec / tasks / testes:** afetou RN-003, AMB-002 e as tasks de cálculo de limites.
- **Decisão final:** o valor até o limite é reembolsável e o excedente é não reembolsável.

### DEC-002 — Regra de nota fiscal acima de R$ 100,00

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida a regra de que valores exatamente iguais a R$ 100,00 não exigem nota fiscal, enquanto valores acima disso exigem.
- **Motivo:** a frase “acima de R$ 100” sugere um limiar estrito.
- **Impacto na spec / tasks / testes:** afetou RN-004, AMB-003 e a task de validação de nota fiscal.
- **Decisão final:** despesas com valor superior a 100,00 sem nota fiscal são recusadas.

### DEC-003 — Interpretação de “em viagem”

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida uma inferência simples e explícita para identificar viagem com base em evidência textual do dia da despesa.
- **Motivo:** a política menciona limites ampliados em viagem, mas a entrada não possui um campo explícito para isso.
- **Impacto na spec / tasks / testes:** afetou RN-005, AMB-004 e a task de cálculo de limites diários.
- **Decisão final:** a condição de viagem é inferida apenas quando há evidência explícita de viagem na descrição ou fornecedor, aplicada para o mesmo dia da despesa.

### DEC-004 — Tratamento de despesas fora do período

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que despesas fora do intervalo de competência são ignoradas, e não reembolsadas.
- **Motivo:** a política pede que as despesas sejam lançadas dentro do período de competência, mas não diz se devem ser recusadas ou ignoradas.
- **Impacto na spec / tasks / testes:** afetou RN-006, AMB-006 e a task de casos de borda.
- **Decisão final:** despesas fora do período entram no resultado com status ignorada.

### DEC-005 — Tratamento de duplicatas

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que duplicata é a repetição de data, categoria, fornecedor, descrição e valor.
- **Motivo:** a política menciona duplicatas sem especificar o critério de comparação.
- **Impacto na spec / tasks / testes:** afetou RN-007, AMB-005 e a task dedicada a duplicatas.
- **Decisão final:** a primeira ocorrência é mantida e as demais são recusadas como duplicatas.

### DEC-006 — Tratamento de valores negativos

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que valores negativos são considerados ajustes e não geram reembolso.
- **Motivo:** a política não prevê estornos nem ajustes, então a interpretação mais segura é tratá-los como não reembolsáveis.
- **Impacto na spec / tasks / testes:** afetou RN-008, AMB-009 e a task de casos de borda.
- **Decisão final:** valores negativos são registrados como ignorados.

### DEC-007 — Ordem de execução das regras

- **Data:** 2026-07-29
- **Resumo da mudança:** Definida a ordem de aplicação das regras para garantir consistência.
- **Motivo:** quando múltiplas regras se aplicam à mesma despesa, a ordem altera o resultado.
- **Impacto na spec / tasks / testes:** afetou a seção 8 da spec, o plano técnico e a ordem de desenvolvimento.
- **Decisão final:** a implementação deve seguir a ordem: normalização, período, duplicatas, ajustes, categoria, nota fiscal, limites e saída.
