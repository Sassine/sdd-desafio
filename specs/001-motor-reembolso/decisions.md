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

### DEC-010 — Evidência de viagem baseada em hospedagem

- **Data:** 2026-07-29
- **Resumo da mudança:** Corrigida a regra de inferência de viagem para evitar falsos positivos causados por termos como “hotel” ou “aeroporto” em despesas de outras categorias.
- **Motivo:** o teste de T-004 revelou que despesas comuns de transporte urbano não devem disparar limites ampliados apenas por palavras presentes na descrição ou fornecedor.
- **Impacto na spec / tasks / testes:** afetou RN-005, AMB-004 e o comportamento de calcular_limite_diario.
- **Decisão final:** a evidência de viagem é considerada apenas quando há uma despesa de categoria hospedagem no mesmo dia; despesas de outras categorias não passam a ser interpretadas como sinal de viagem.

### DEC-011 — Critério de prioridade no consumo do limite diário

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido o critério de prioridade para o consumo do limite diário quando múltiplas despesas excedem o limite do dia.
- **Motivo:** a spec descreve reembolso parcial, mas não define como dividir o limite entre despesas do mesmo dia quando há mais de uma ocorrência acima do limite.
- **Impacto na spec / tasks / testes:** afetou RN-003, AMB-012 e T-005.
- **Decisão final:** a ordem de aparição no array de entrada define a prioridade de consumo do limite, já que não há campo de horário.

### DEC-012 — Valor zero como ajuste ou despesa normal

- **Data:** 2026-07-29
- **Resumo da mudança:** Definido que valor zero não é tratado como ajuste.
- **Motivo:** a spec menciona valores negativos como ajustes, mas não prevê explicitamente o caso de zero.
- **Impacto na spec / tasks / testes:** afetou RN-008, AMB-013 e T-009.
- **Decisão final:** valor zero é tratado como despesa normal; apenas valores negativos acionam RN-008.

### DEC-013 — Chegada da política de reembolso v4 (envelope Dia 2)

- **Data:** 2026-07-30
- **Resumo da mudança:** Recebido comunicado do RH com política v4, que
  invalida o modelo de limites constantes usado desde a v1 do sistema.
  Os limites deixam de ser valores fixos no código e passam a ser lidos
  de um arquivo de política externo (politica-v4.json), com tabela por
  centro de custo. Também foram introduzidas: categoria representacao
  (válida apenas em centros de custo específicos), hospedagem não
  reembolsável em CC-ENG-PLATAFORMA, suporte a despesas em moeda
  estrangeira com conversão via cambio.json, e (opcional) fila de
  aprovação manual para valores acima de R$500.
- **Motivo:** mudança de requisito de negócio comunicada formalmente
  pelo RH, com vigência imediata e retroativa à competência atual.
- **Impacto na spec / tasks / testes:** invalida parcialmente RN-001
  (lista fixa de categorias), RN-002 (limites constantes de alimentação/
  transporte), RN-004 (limiar de nota fiscal hardcoded), RN-005 (base do
  cálculo de viagem), RN-012 (limite fixo de hospedagem). Nenhuma dessas
  RNs foi removida — elas são complementadas por RN-013 a RN-017, que
  redefinem a origem dos valores (arquivo externo em vez de constante).
  Novas tasks T-013 em diante serão necessárias para reimplementar a
  leitura de política externa, a categoria representacao, a exclusão de
  hospedagem por centro de custo e a conversão de câmbio.
- **Decisão final:** a spec é atualizada com RN-013 a RN-017 e AMB-014 a
  AMB-016 antes de qualquer alteração de código, seguindo o mesmo
  processo usado desde a v1 (spec → decisions → tasks → código).

### DEC-014 — Herança de política padrão avaliada por categoria

- **Data:** 2026-07-30
- **Resumo da mudança:** Definido que a herança da política padrão
  (para centros de custo ou categorias ausentes da tabela) é avaliada
  categoria a categoria, não pelo centro de custo como um todo.
- **Motivo:** o comunicado do RH só define o comportamento para centro
  de custo totalmente ausente da tabela; não cobre o caso de um centro
  de custo presente que omite uma categoria específica (ex: CC-ADM não
  define hospedagem nem representacao).
- **Impacto na spec / tasks / testes:** afetou RN-013 e AMB-014; task de
  leitura de política externa (a numerar) precisa implementar fallback
  por categoria, não por centro de custo inteiro.
- **Decisão final:** um centro de custo presente na tabela usa seus
  valores específicos onde definidos, e cai no padrão apenas nas
  categorias que sua tabela não define.

### DEC-015 — Limite de representação segue mesma regra de agregação diária

- **Data:** 2026-07-30
- **Resumo da mudança:** Definido que o limite de representacao segue a
  mesma lógica já usada para alimentação e transporte_urbano — soma das
  despesas da categoria no mesmo dia, comparada ao limite diário.
- **Motivo:** o comunicado não repete essa pergunta para a nova
  categoria, mas o campo periodicidade em politica-v4.json usa a mesma
  estrutura das categorias existentes.
- **Impacto na spec / tasks / testes:** afetou RN-014 e AMB-015;
  reaproveita a mesma função de agregação por dia já usada para
  alimentação/transporte (calcular_limite_diario), estendida para
  representacao.
- **Decisão final:** representacao é agregada por dia, com o mesmo
  mecanismo de RN-002/AMB-001.

### DEC-016 — Fallback de câmbio para o último dia útil anterior

- **Data:** 2026-07-30
- **Resumo da mudança:** Definido que, quando a data exata da despesa
  não tem cotação publicada em cambio.json (ex: fim de semana), usa-se
  a cotação do último dia útil anterior disponível no arquivo.
- **Motivo:** o comunicado do RH menciona que cotações só são publicadas
  em dias úteis bancários, mas não resolve o que fazer quando a despesa
  cai fora desses dias — e o dataset de teste (despesa e-004, datada em
  um sábado) exercita exatamente esse caso.
- **Impacto na spec / tasks / testes:** afetou RN-016, RN-017 e AMB-016;
  task de conversão de câmbio precisa implementar busca retroativa da
  cotação mais recente disponível, não apenas lookup direto por data.
- **Decisão final:** busca a cotação mais recente com data <= data da
  despesa, dentro das taxas disponíveis em cambio.json.