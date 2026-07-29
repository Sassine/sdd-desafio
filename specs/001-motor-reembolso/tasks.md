# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar um commit. O critério de aceite deve ser verificável por teste.

---

## Fase 1 — Fundação

- [ ] **T-001** — Criar a estrutura básica do projeto e o fluxo de leitura do JSON de entrada.
  - **Atende:** RN-009
  - **Aceite:** o teste test_leitura_json_de_entrada_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-002** — Normalizar categorias, datas e valores para um formato interno consistente.
  - **Atende:** RN-009
  - **Aceite:** o teste test_normalizacao_de_categoria_e_data_passa.
  - **Commit:** `<preencher depois>`

## Fase 2 — Regras de negócio

- [ ] **T-003** — Implementar a validação de categorias aceitas e o tratamento de categorias fora da política.
  - **Atende:** RN-001, AMB-007
  - **Aceite:** o teste test_categoria_fora_da_politica_eh_recusada_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-004** — Implementar o cálculo de limite diário para alimentação e transporte urbano, incluindo o contexto de viagem.
  - **Atende:** RN-002, RN-005, AMB-001, AMB-004
  - **Aceite:** o teste test_limite_diario_e_viagem_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-005** — Implementar a lógica de reembolso parcial quando a despesa excede o limite aplicável.
  - **Atende:** RN-003, AMB-002
  - **Aceite:** o teste test_reembolso_parcial_excede_limite_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-006** — Implementar a regra de nota fiscal para valores acima de R$ 100,00.
  - **Atende:** RN-004, AMB-003
  - **Aceite:** o teste test_nota_fiscal_obrigatoria_acima_de_100_passa.
  - **Commit:** `<preencher depois>`

## Fase 3 — Casos de borda

- [ ] **T-007** — Implementar o tratamento de despesas fora do período de competência.
  - **Atende:** RN-006, AMB-006
  - **Aceite:** o teste test_despesas_fora_do_periodo_sao_ignoradas_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-008** — Implementar o tratamento de duplicatas com base na regra definida na spec.
  - **Atende:** RN-007, AMB-005
  - **Aceite:** o teste test_duplicatas_sao_recusadas_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-009** — Implementar o tratamento de valores negativos como ajustes e não reembolsáveis.
  - **Atende:** RN-008, AMB-009
  - **Aceite:** o teste test_valores_negativos_sao_ignorados_passa.
  - **Commit:** `<preencher depois>`

## Fase 4 — Saída e CLI

- [ ] **T-010** — Gerar o JSON de saída com resumo, despesas e justificativas obrigatórias.
  - **Atende:** RN-010, RN-001 a RN-009
  - **Aceite:** o teste test_saida_json_com_resumo_e_justificativas_passa.
  - **Commit:** `<preencher depois>`

- [ ] **T-011** — Criar a CLI para executar o motor com os argumentos --input e --output.
  - **Atende:** objetivo do projeto
  - **Aceite:** o teste test_cli_gera_arquivo_json_passa.
  - **Commit:** `<preencher depois>`

## Fase 5 — Envelope (Dia 2)

- [ ] **T-012** — Ajustar o motor para absorver uma mudança de requisito sem reescrever a lógica principal.
  - **Atende:** evolução da spec
  - **Aceite:** o teste de regressão da mudança de requisito passa.
  - **Commit:** `<preencher depois>`

---

## Cobertura

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-003 | test_categoria_fora_da_politica_eh_recusada |
| RN-002 | T-004 | test_limite_diario_e_viagem |
| RN-003 | T-005 | test_reembolso_parcial_excede_limite |
| RN-004 | T-006 | test_nota_fiscal_obrigatoria_acima_de_100 |
| RN-005 | T-004 | test_limite_diario_e_viagem |
| RN-006 | T-007 | test_despesas_fora_do_periodo_sao_ignoradas |
| RN-007 | T-008 | test_duplicatas_sao_recusadas |
| RN-008 | T-009 | test_valores_negativos_sao_ignorados |
| RN-009 | T-001, T-002 | test_normalizacao_de_categoria_e_data |
| RN-010 | T-010 | test_saida_json_com_resumo_e_justificativas |
