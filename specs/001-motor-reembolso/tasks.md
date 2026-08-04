# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>`

---

## Fase 1 — Fundação

- [ ] **T-001** — Criar a estrutura mínima de processamento e carregar a entrada JSON
  - **Atende:** RN-001, RN-002, RN-009
  - **Aceite:** O teste `test_carrega_entrada_e_normaliza_categorias` passa.
  - **Commit:** `<hash preenchido depois>`

- [ ] **T-002** — Definir o modelo de saída e montar o resumo inicial do processamento
  - **Atende:** seção 4 da spec
  - **Aceite:** O teste `test_estrutura_de_saida_contem_resumo_e_itens` passa.
  - **Commit:**

## Fase 2 — Regras de negócio

- [ ] **T-003** — Aplicar a regra de categorias aceitas e marcar despesas fora da política
  - **Atende:** RN-001, AMB-007
  - **Aceite:** O teste `test_categoria_fora_da_politica_eh_nao_reembolsavel` passa.
  - **Commit:**

- [ ] **T-004** — Validar o período de competência e rejeitar despesas fora do período
  - **Atende:** RN-002, AMB-005
  - **Aceite:** O teste `test_despesa_fora_do_periodo_eh_recusada` passa.
  - **Commit:**

- [ ] **T-005** — Aplicar a regra de nota fiscal para valores acima de R$ 100,00
  - **Atende:** RN-005, AMB-003
  - **Aceite:** O teste `test_despesa_acima_de_100_sem_nota_fiscal_eh_recusada` passa.
  - **Commit:**

- [ ] **T-006** — Tratar valores negativos e zeros como ajustes não reembolsáveis
  - **Atende:** RN-008, AMB-008
  - **Aceite:** O teste `test_valor_negativo_eh_ignorado` passa.
  - **Commit:**

## Fase 3 — Casos de borda

- [ ] **T-007** — Aplicar limite diário por categoria e compartilhar o limite entre despesas do mesmo dia
  - **Atende:** RN-003, AMB-001
  - **Aceite:** O teste `test_limite_diario_eh_compartilhado_entre_despesas_do_mesmo_dia` passa.
  - **Commit:**

- [ ] **T-008** — Reembolsar parcialmente quando a despesa excede o limite aplicável
  - **Atende:** RN-004, AMB-002
  - **Aceite:** O teste `test_despesa_acima_do_limite_reembolsa_apenas_o_limite` passa.
  - **Commit:**

- [ ] **T-009** — Detectar duplicatas e rejeitar a segunda ocorrência
  - **Atende:** RN-007, AMB-006
  - **Aceite:** O teste `test_duplicata_eh_markada_como_nao_reembolsavel` passa.
  - **Commit:**

## Fase 4 — Saída e CLI

- [ ] **T-010** — Expor a saída final em formato JSON com status, valor reembolsável, data e motivo por item
  - **Atende:** seção 4 da spec, critérios de aceite
  - **Aceite:** O teste `test_saida_json_contem_status_valor_e_motivo` passa.
  - **Commit:**

- [ ] **T-011** — Implementar a CLI para processar `--input` e `--output`
  - **Atende:** interface do desafio
  - **Aceite:** O comando `calcular --input despesas.json --output resultado.json` gera um arquivo de saída válido.
  - **Commit:**

---

## Fase 5 — Envelope (criar no Dia 2)

- [ ] **T-012** — Ajustar a implementação para carregar a política externa por centro de custo
  - **Atende:** RN-010, AMB-010
  - **Aceite:** O teste `test_politica_externa_por_centro_de_custo` passa.
  - **Commit:**

- [ ] **T-013** — Implementar regras especiais por centro de custo para `representacao` e `hospedagem`
  - **Atende:** RN-011, AMB-010
  - **Aceite:** O teste `test_regras_especiais_por_centro_de_custo` passa.
  - **Commit:**

- [ ] **T-014** — Converter despesas em moeda estrangeira usando a taxa da data da despesa
  - **Atende:** RN-012, AMB-011
  - **Aceite:** O teste `test_conversao_em_moeda_estrangeira_pela_data_da_despesa` passa.
  - **Commit:**

---

## Cobertura

Preencha ao fechar cada fase. É a sua própria checagem de rastreabilidade — e é
exatamente a matriz que a correção vai montar.

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-003 | `test_categoria_fora_da_politica_eh_nao_reembolsavel` |
| RN-002 | T-004 | `test_despesa_fora_do_periodo_eh_recusada` |
| RN-003 | T-007 | `test_limite_diario_eh_compartilhado_entre_despesas_do_mesmo_dia` |
| RN-004 | T-008 | `test_despesa_acima_do_limite_reembolsa_apenas_o_limite` |
| RN-005 | T-005 | `test_despesa_acima_de_100_sem_nota_fiscal_eh_recusada` |
| RN-006 | T-011 | `test_dias_com_hospedagem_recebem_limite_aumentado_em_50_porcento` |
| RN-007 | T-009 | `test_duplicata_eh_markada_como_nao_reembolsavel` |
| RN-008 | T-006 | `test_valor_negativo_eh_ignorado` |
| RN-009 | T-001 | `test_carrega_entrada_e_normaliza_categorias` |
| RN-010 | T-012 | `test_politica_externa_por_centro_de_custo` |
| RN-011 | T-013 | `test_regras_especiais_por_centro_de_custo` |
| RN-012 | T-014 | `test_conversao_em_moeda_estrangeira_pela_data_da_despesa` |
| AMB-001 | T-007 | `test_limite_diario_eh_compartilhado_entre_despesas_do_mesmo_dia` |
| AMB-002 | T-008 | `test_despesa_acima_do_limite_reembolsa_apenas_o_limite` |
| AMB-003 | T-005 | `test_despesa_acima_de_100_sem_nota_fiscal_eh_recusada` |
| AMB-005 | T-004 | `test_despesa_fora_do_periodo_eh_recusada` |
| AMB-006 | T-009 | `test_duplicata_eh_markada_como_nao_reembolsavel` |
| AMB-007 | T-003 | `test_categoria_fora_da_politica_eh_nao_reembolsavel` |
