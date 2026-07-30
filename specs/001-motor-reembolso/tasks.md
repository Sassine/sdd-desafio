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

## Fase 5 — Envelope (Dia 2, Política v4)

> **T-012 — título da fase.** Comunicado do RH em 2026-07-30 trouxe a
> política v4, que substitui limites constantes por uma tabela externa
> por centro de custo (politica-v4.json), adiciona a categoria
> representacao, exclui hospedagem do CC-ENG-PLATAFORMA, e introduz
> despesas em moeda estrangeira convertidas via cambio.json. T-012 não
> tem entrega própria nem critério de aceite — é apenas o marcador de
> abertura desta fase. O trabalho real está quebrado em T-013 a T-018
> abaixo. Ver DEC-013 a DEC-016 em decisions.md e RN-013 a RN-017 /
> AMB-014 a AMB-016 em spec.md.

- [x] **T-013** — Implementar leitura da política externa (politica-v4.json) com fallback por categoria.
  - **Atende:** RN-013, AMB-014
  - **Aceite:** testes em `tests/test_politica_externa.py` (6 casos:
    valor específico do centro de custo, fallback por categoria dentro
    de um centro de custo presente, centro de custo ausente da tabela
    usando padrão inteiro, limite zero retornado como zero e não como
    ausência, categoria não coberta nem no centro de custo nem no
    padrão retorna None, categoria condicional a centro de custo
    específico).
  - **Commit:** `feat(T-013): le politica externa com fallback por categoria (RN-013)`

- [ ] **T-014** — Suportar a categoria "representacao" como categoria válida condicional ao centro de custo.
  - **Atende:** RN-014, AMB-015
  - **Aceite:** despesa e-001 (representacao, CC-COMERCIAL) é aceita e
    avaliada contra limite de R$300/dia, agregado por dia como as
    demais categorias; a mesma categoria em um centro de custo sem
    essa entrada é recusada como categoria_nao_politica.
  - **Commit:** `<preencher depois>`

- [ ] **T-015** — Tratar categoria com limite zero como não reembolsável no centro de custo.
  - **Atende:** RN-015
  - **Aceite:** despesa sintética de hospedagem no CC-ENG-PLATAFORMA
    (nenhuma existe no dataset fornecido) resulta em status recusada,
    motivo categoria_nao_reembolsavel_no_centro_custo — não
    parcialmente_reembolsada com valor zero.
  - **Commit:** `<preencher depois>`

- [ ] **T-016** — Implementar conversão de moeda estrangeira usando taxa da data da despesa, com fallback para último dia útil anterior.
  - **Atende:** RN-016, RN-017, AMB-016
  - **Aceite:** e-002 (EUR 22,00, 2026-07-14, taxa 5,93) converte para
    R$130,46; e-004 (EUR 30,00, 2026-07-18, sábado sem cotação) usa a
    taxa de 2026-07-17 (5,96) por fallback; e-010 (sem campo moeda) é
    tratada como BRL sem conversão.
  - **Commit:** `<preencher depois>`

- [ ] **T-017** — Integrar política externa, representação, exclusão por centro de custo e câmbio no pipeline `processar_despesas`.
  - **Atende:** RN-013 a RN-017 (orquestração)
  - **Aceite:** rodar a CLI com despesas-envelope.json e
    despesas-envelope-cc-desconhecido.json produz resultados
    consistentes com todas as regras acima, mantendo o comportamento
    das RN-001 a RN-012 para os casos que não mudaram (nota fiscal,
    duplicata, período continuam funcionando como antes).
  - **Commit:** `<preencher depois>`

- [ ] **T-018** *(opcional — item C do comunicado)* — Implementar fila de aprovação manual para valor reembolsável acima de R$500.
  - **Atende:** item C do comunicado (opcional — não pontua ausência,
    mas pode prejudicar se deixar a spec inconsistente)
  - **Aceite:** despesa com valor_reembolsavel > R$500 recebe status
    pendente_aprovacao em vez de reembolsada; resumo do JSON de saída
    ganha uma contagem quantidade_pendente_aprovacao.
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
| RN-013 | T-013 | `test_politica_externa.py` (6 casos) |
| RN-014 | T-014 | *(a definir na implementação)* |
| RN-015 | T-015 | *(a definir na implementação)* |
| RN-016 | T-016 | *(a definir na implementação)* |
| RN-017 | T-016 | *(a definir na implementação)* |