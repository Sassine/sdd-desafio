# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar um commit. O critério de aceite deve ser verificável por teste.

---

## Fase 1 — Fundação

- [x] **T-001** — Criar a estrutura básica do projeto e o fluxo de leitura do JSON de entrada.
  - **Atende:** RN-009
  - **Aceite:** teste em `tests/test_leitura_json_de_entrada.py` (`test_leitura_json_de_entrada_passa`).
  - **Commit:** `feat(T-001): leitura de despesas do JSON sem normalização precoce de categoria`

- [x] **T-002** — Normalizar categorias, datas e valores para um formato interno consistente.
  - **Atende:** RN-009, RN-011
  - **Aceite:** testes em `tests/test_normalizacao_de_categoria_e_data.py` (`test_normalizacao_de_categoria_e_data_passa`, `test_normalizacao_arredonda_half_up_em_caso_de_empate`).
  - **Commit:** `fix(T-002): usa ROUND_HALF_UP explicito conforme RN-011`

## Fase 2 — Regras de negócio

- [x] **T-003** — Implementar a validação de categorias aceitas e o tratamento de categorias fora da política.
  - **Atende:** RN-001, AMB-007
  - **Aceite:** teste em `tests/test_validacao_categoria_aceita.py` (`test_validacao_categoria_aceita`).
  - **Commit:** `feat(T-003): valida categoria aceita conforme RN-001`

- [x] **T-004** — Implementar o cálculo de limite diário para alimentação e transporte urbano, incluindo o contexto de viagem.
  - **Atende:** RN-002, RN-005, AMB-001, AMB-004
  - **Aceite:** teste em `tests/test_limite_diario_e_viagem.py` (`test_limite_diario_e_viagem`).
  - **Commit:** `feat(T-004): calcula limite diario com viagem baseada em hospedagem (RN-002, RN-005)`

- [x] **T-005** — Implementar a lógica de reembolso parcial quando a despesa excede o limite aplicável.
  - **Atende:** RN-003, AMB-002, AMB-012
  - **Aceite:** testes em `tests/test_reembolso_parcial.py` (`test_reembolso_parcial_quando_despesa_excede_limite`, `test_reembolso_parcial_aplica_limite_ao_total_do_dia`, `test_reembolso_parcial_quando_despesa_esta_dentro_do_limite`).
  - **Commit:** `feat(T-005): calcula reembolso parcial com corte de excedente (RN-003)`

- [x] **T-006** — Implementar a regra de nota fiscal para valores acima de R$ 100,00.
  - **Atende:** RN-004, AMB-003
  - **Aceite:** testes em `tests/test_nota_fiscal_obrigatoria.py` (5 casos, incluindo limite exato de R$100 e valor com nota fiscal acima do limite).
  - **Commit:** `feat(T-006): valida nota fiscal obrigatoria acima de R$100 (RN-004)`

## Fase 3 — Casos de borda

- [x] **T-007** — Implementar o tratamento de despesas fora do período de competência.
  - **Atende:** RN-006, AMB-006
  - **Aceite:** testes em `tests/test_periodo_competencia.py` (`test_despesa_fora_do_periodo_eh_marcada_como_ignorada`, `test_despesa_dentro_do_periodo_nao_eh_marcada_como_fora_do_periodo`, `test_datas_de_limite_inclusivo_sao_consideradas_dentro_do_periodo`).
  - **Commit:** `feat(T-007): valida periodo de competencia (RN-006)`

- [x] **T-008** — Implementar o tratamento de duplicatas com base na regra definida na spec.
  - **Atende:** RN-007, AMB-005
  - **Aceite:** testes em `tests/test_duplicatas.py` (`test_despesas_duplicadas_sao_marcadas_com_o_id_original`, `test_despesas_com_fornecedor_ou_descricao_diferentes_nao_sao_duplicatas`, `test_a_primeira_ocorrencia_nunca_eh_marcada_como_duplicata`).
  - **Commit:** `feat(T-008): identifica duplicatas por data/categoria/fornecedor/descricao/valor (RN-007)`

- [x] **T-009** — Implementar o tratamento de valores negativos como ajustes e não reembolsáveis.
  - **Atende:** RN-008, AMB-009, AMB-013
  - **Aceite:** testes em `tests/test_valores_negativos.py` (`test_valor_negativo_eh_identificado_como_ajuste`, `test_valor_positivo_nao_eh_identificado_como_ajuste`, `test_valor_zero_nao_eh_identificado_como_ajuste`).
  - **Commit:** `feat(T-009): identifica valores negativos como ajuste (RN-008)`

## Fase 4 — Saída e CLI

- [x] **T-010** — Gerar o JSON de saída com resumo, despesas e justificativas obrigatórias, orquestrando RN-001 a RN-012 na ordem definida na seção 8 da spec.
  - **Atende:** RN-010, RN-012
  - **Aceite:** testes em `tests/test_processar_despesas.py` (7 casos: colaborador/periodo copiados, status válidos, statuses conhecidos do JSON exemplo, justificativa preenchida, limite de hospedagem, resumo bate com soma, precedência de duplicata sobre nota fiscal/limite).
  - **Commit:** `feat(T-010): orquestra pipeline completo e aplica limite de hospedagem (RN-012)`

- [x] **T-011** — Criar a CLI para executar o motor com os argumentos --input e --output.
  - **Atende:** objetivo do projeto
  - **Aceite:** testes em `tests/test_cli.py` (`test_cli_gera_arquivo_json_valido`, `test_cli_serializa_decimals_como_numeros`, `test_cli_sem_argumentos_necessarios_falha_com_mensagem_clara`).
  - **Commit:** `feat(T-011): implementa CLI calcular --input --output`

## Fase 5 — Envelope (Dia 2)

- [ ] **T-012** — Ajustar o motor para absorver uma mudança de requisito sem reescrever a lógica principal.
  - **Atende:** evolução da spec
  - **Aceite:** o teste de regressão da mudança de requisito passa.
  - **Commit:** `<preencher depois>`

---

## Cobertura

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-003 | `test_validacao_categoria_aceita` |
| RN-002 | T-004 | `test_limite_diario_e_viagem` |
| RN-003 | T-005 | `test_reembolso_parcial_*` (3 casos) |
| RN-004 | T-006 | `test_*_nota_fiscal_*` (5 casos) |
| RN-005 | T-004 | `test_limite_diario_e_viagem` |
| RN-006 | T-007 | `test_*_periodo_*` (3 casos) |
| RN-007 | T-008 | `test_*_duplicata*` (3 casos) |
| RN-008 | T-009 | `test_valor_*_ajuste` (3 casos) |
| RN-009 | T-001, T-002 | `test_leitura_json_de_entrada_passa`, `test_normalizacao_de_categoria_e_data_passa` |
| RN-010 | T-010 | `test_todas_as_despesas_tem_justificativa_preenchida` |
| RN-011 | T-002 | `test_normalizacao_arredonda_half_up_em_caso_de_empate` |
| RN-012 | T-010 | `test_hospedagem_aplica_limite_individual_de_250_reais` |