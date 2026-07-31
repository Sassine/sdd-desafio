# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>`

**Derivado de:** `spec.md` 1.0 e `plan.md` 1.0. A ordem das tasks da Fase 2 segue
a ordem de aplicação da spec §8.

---

## Fase 1 — Fundação

- [x] **T-001** — Esqueleto do projeto: `src/`, `tests/`, `pyproject.toml` com `pytest` como dependência de desenvolvimento
  - **Atende:** nenhuma RN — habilita as demais
  - **Aceite:** `pytest` coleta e executa ao menos 1 teste, saída verde
  - **Commit:** `284bee9`

- [x] **T-002** — Modelo de dados imutável: `Despesa`, `Solicitacao`, `Contexto`, `Parecer`, `Resultado`, enum `Status`
  - **Atende:** `plan.md` §3
  - **Aceite:** `test_modelo_e_imutavel` — tentar atribuir a um campo de `Despesa` levanta `FrozenInstanceError`; `Resultado.total_reembolsavel` é propriedade calculada, não campo
  - **Commit:** `2ac9a6f`

- [x] **T-003** — Carregador: JSON → `Solicitacao`, com `parse_float=Decimal` e arredondamento único de duas casas meio-para-cima
  - **Atende:** RN-010, AMB-011, `spec.md` §4 (entrada)
  - **Aceite:** `test_rn_010_arredonda_na_leitura` — `33.333` vira exatamente `Decimal("33.33")`, e o valor nunca passa por `float`
  - **Commit:** `56ed38a`

- [x] **T-004** — Validação de entrada: campo obrigatório ausente ou tipo inválido rejeita a execução com mensagem nomeando o campo
  - **Atende:** `spec.md` §9 (último critério), §3 (não adivinha entrada malformada)
  - **Aceite:** `test_entrada_sem_campo_obrigatorio_e_rejeitada` — entrada sem `despesas[].valor` levanta erro citando `valor`, e nenhum resultado parcial é escrito
  - **Commit:** `b17f3c8`

- [x] **T-005** — Módulo de política: tetos por categoria, piso de nota fiscal e fator de viagem como constantes `Decimal`
  - **Atende:** `plan.md` §4
  - **Aceite:** `test_politica_expoe_limites_da_v3` — os quatro valores conferem com a spec §5 (60, 80, 250, 100) e são `Decimal`, não `float`
  - **Commit:** `3ad5782`

## Fase 2 — Regras de negócio

> Uma task por RN, na ordem dos passos da spec §8. Cada uma entra com o seu teste.

- [x] **T-006** — RN-002: normalização da categoria (caixa e espaços nas pontas)
  - **Atende:** RN-002, AMB-012
  - **Aceite:** `test_rn_002_categoria_em_caixa_alta_e_normalizada` — `"ALIMENTACAO"` é tratada como `alimentacao` e a categoria normalizada é a que sai no resultado
  - **Commit:** `3b56b0f`

- [x] **T-007** — RN-003: competência — despesa fora do mês é recusada e permanece no resultado
  - **Atende:** RN-003, AMB-009
  - **Aceite:** `test_rn_003_despesa_fora_da_competencia_e_recusada` — data `2026-04-15` com competência `2026-07` resulta em `0.00`, status `recusada`, presente na lista de itens
  - **Commit:** `8489fed`

- [x] **T-008** — RN-001: categoria fora da política é recusada e permanece no resultado
  - **Atende:** RN-001
  - **Aceite:** `test_rn_001_categoria_fora_da_politica_e_recusada` — `coworking` de R$ 89,00 resulta em `0.00`, status `recusada`
  - **Commit:** `9a3f528`

- [x] **T-009** — RN-004: duplicatas — primeira ocorrência paga, demais recusadas
  - **Atende:** RN-004, AMB-008
  - **Aceite:** `test_rn_004_duplicata_exata_recusa_a_segunda` — duas despesas iguais em data, categoria, fornecedor, descrição e valor resultam em R$ 54,90 e R$ 0,00; e `test_rn_004_fornecedor_diferente_nao_e_duplicata` passa
  - **Commit:** `3b1184f`

- [x] **T-010** — RN-005: estornos — valor negativo abate integral, sem teto e sem nota
  - **Atende:** RN-005, AMB-010
  - **Aceite:** `test_rn_005_estorno_abate_valor_integral` — −R$ 45,00 resulta em −R$ 45,00, status `estorno`; e −R$ 500,00 em alimentação não é limitado pelo teto
  - **Commit:** `e64b46e`

- [x] **T-011** — RN-006: nota fiscal obrigatória acima de R$ 100,00, comparação estrita, recusa integral na ausência
  - **Atende:** RN-006, AMB-003, AMB-004, AMB-005
  - **Aceite:** `test_rn_006_piso_e_exclusivo` — R$ 100,00 sem nota segue para o teto; `test_rn_006_acima_do_piso_sem_nota_e_recusada` — R$ 100,01 sem nota resulta em `0.00`
  - **Commit:** `22ea8fb`

- [x] **T-012** — RN-007: teto por despesa e reembolso parcial com glosa do excedente
  - **Atende:** RN-007, AMB-001, AMB-002
  - **Aceite:** `test_rn_007_teto_e_por_despesa_nao_por_dia` — R$ 72,50 e R$ 38,00 no mesmo dia resultam em R$ 60,00 e R$ 38,00; `test_rn_007_valor_no_teto_e_aprovado_integralmente` — R$ 60,00 sai como `aprovada` sem glosa
  - **Commit:** `2627349`

- [x] **T-013** — RN-008: cada lançamento de hospedagem vale uma diária; descrição não é interpretada
  - **Atende:** RN-008, AMB-007
  - **Aceite:** `test_rn_008_hospedagem_conta_como_uma_diaria` — R$ 480,00 descrita como "2 diarias", fora de viagem, resulta em R$ 250,00
  - **Commit:** `d706158`

- [x] **T-014** — RN-009: `Contexto` de viagem — datas com lançamento de hospedagem ampliam os tetos em 50%
  - **Atende:** RN-009, AMB-006
  - **Aceite:** `test_rn_009_data_com_hospedagem_amplia_tetos` — R$ 480,00 em `2026-07-14` resulta em R$ 375,00; `test_rn_009_hospedagem_recusada_ainda_caracteriza_viagem` passa; `test_rn_009_viagem_nao_amplia_piso_da_nota` passa
  - **Commit:** `8dc368a`

- [x] **T-015** — Calculadora: encadeia as regras na ordem da spec §8, parando na primeira que recusa
  - **Atende:** `spec.md` §8, RN-001 a RN-010
  - **Aceite:** `test_ordem_nota_fiscal_antes_do_teto` — `d-004` (R$ 100,01, transporte, sem nota) resulta em `0.00` e **não** em R$ 80,00, provando que o passo 7 roda antes do 8
  - **Commit:** `4b43e1b`

## Fase 3 — Casos de borda

- [x] **T-016** — Tabela de casos de borda da spec §7 como teste parametrizado, uma linha por caso
  - **Atende:** `spec.md` §7 (18 linhas)
  - **Aceite:** `test_casos_de_borda` — 18 casos passam, cada um identificado pelo ID da regra no parâmetro
  - **Commit:** `pendente`

- [x] **T-017** — Fronteiras testadas dos dois lados: R$ 100,00/R$ 100,01 e R$ 60,00/R$ 60,01
  - **Atende:** RN-006, RN-007, `plan.md` §6
  - **Aceite:** `test_fronteiras_inclusivas_e_exclusivas` — os quatro casos passam com os valores da spec
  - **Commit:** `pendente`

- [x] **T-018** — Lista de despesas vazia produz resultado válido com todos os totais em `0.00`
  - **Atende:** `spec.md` §7 (última linha)
  - **Aceite:** `test_lista_vazia_produz_resultado_valido` — saída bem formada, sem exceção
  - **Commit:** `pendente`

## Fase 4 — Saída e CLI

- [ ] **T-019** — Serializador: `Decimal` como texto de duas casas, `Status` em minúsculas, `valor_glosado` derivado
  - **Atende:** `spec.md` §4 (saída)
  - **Aceite:** `test_serializa_valores_como_texto_de_duas_casas` — `Decimal("60")` sai como `"60.00"`; nenhum `Decimal` cru chega ao `json.dump`
  - **Commit:**

- [ ] **T-020** — Resumo: totais lançado, reembolsável e glosado, mais contagem por status
  - **Atende:** `spec.md` §4, §9 (penúltimo critério)
  - **Aceite:** `test_soma_dos_itens_bate_com_o_resumo` — a soma dos `valor_reembolsavel` dos itens é idêntica a `resumo.total_reembolsavel`
  - **Commit:**

- [ ] **T-021** — CLI: `calcular --input <arquivo> --output <arquivo>`
  - **Atende:** contrato fixo do `DESAFIO.md`
  - **Aceite:** `test_cli_calcular_escreve_saida` — o comando cria o arquivo de saída e retorna código 0; entrada inválida retorna código diferente de 0 sem criar o arquivo
  - **Commit:**

- [ ] **T-022** — Teste ponta a ponta sobre `exemplos/despesas-exemplo.json`
  - **Atende:** `spec.md` §9 (critérios 1 a 8)
  - **Aceite:** `test_e2e_exemplo_oficial` — total reembolsável `703.43` sobre total lançado `1816.84`, com os valores por item que a spec §9 fixa para `d-003`, `d-004`, `d-006`, `d-007`, `d-010`, `d-011` e `d-014`
  - **Commit:**

---

## Fase 5 — Envelope (criar no Dia 2)

<Novas tasks a partir da mudança de requisito. Numeração continua de T-023 —
não reinicie e não renumere as antigas: a numeração é o eixo da rastreabilidade.>

---

## Cobertura

Preencha ao fechar cada fase. É a sua própria checagem de rastreabilidade — e é
exatamente a matriz que a correção vai montar.

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-008 | `test_rn_001_categoria_fora_da_politica_e_recusada` |
| RN-002 | T-006 | `test_rn_002_categoria_em_caixa_alta_e_normalizada` |
| RN-003 | T-007 | `test_rn_003_despesa_fora_da_competencia_e_recusada` |
| RN-004 | T-009 | `test_rn_004_duplicata_exata_recusa_a_segunda` |
| RN-005 | T-010 | `test_rn_005_estorno_abate_valor_integral` |
| RN-006 | T-011 | `test_rn_006_piso_e_exclusivo` |
| RN-007 | T-012 | `test_rn_007_teto_e_por_despesa_nao_por_dia` |
| RN-008 | T-013 | `test_rn_008_hospedagem_conta_como_uma_diaria` |
| RN-009 | T-014 | `test_rn_009_data_com_hospedagem_amplia_tetos` |
| RN-010 | T-003 | `test_rn_010_arredonda_na_leitura` |
| AMB-001 | T-012 | `test_rn_007_teto_e_por_despesa_nao_por_dia` |
| AMB-002 | T-012 | `test_rn_007_valor_no_teto_e_aprovado_integralmente` |
| AMB-003 | T-011 | `test_rn_006_piso_e_exclusivo` |
| AMB-004 | T-011 | `test_rn_006_acima_do_piso_sem_nota_e_recusada` |
| AMB-005 | T-015 | `test_ordem_nota_fiscal_antes_do_teto` |
| AMB-006 | T-014 | `test_rn_009_viagem_nao_amplia_piso_da_nota` |
| AMB-007 | T-013 | `test_rn_008_hospedagem_conta_como_uma_diaria` |
| AMB-008 | T-009 | `test_rn_004_fornecedor_diferente_nao_e_duplicata` |
| AMB-009 | T-007 | `test_rn_003_despesa_fora_da_competencia_e_recusada` |
| AMB-010 | T-010 | `test_rn_005_estorno_abate_valor_integral` |
| AMB-011 | T-003 | `test_rn_010_arredonda_na_leitura` |
| AMB-012 | T-006 | `test_rn_002_categoria_em_caixa_alta_e_normalizada` |
| Ordem §8 | T-015 | `test_ordem_nota_fiscal_antes_do_teto` |
| §7 bordas | T-016, T-017, T-018 | `test_casos_de_borda`, `test_fronteiras_inclusivas_e_exclusivas` |
| §9 aceite | T-022 | `test_e2e_exemplo_oficial` |
