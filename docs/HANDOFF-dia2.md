# Plano — Absorção do Envelope do Dia 2 (Política v4)

## Contexto

O Dia 1 fechou com a spec 1.1 e as tasks T-001..T-022 implementadas, 94 testes verdes
e o aceite oficial travado em R$ 703,43 sobre `exemplos/despesas-exemplo.json`
(`e025389`). Na manhã do Dia 2 chegou o envelope lacrado (`Day2Envelope/00-ENVELOPE-LACRADO.md`):
o RH publicou a **Política de Reembolso v4**, com três blocos de mudança.

**A. Limites variam por centro de custo e a política sai do código.** Os tetos deixam
de ser constantes e passam a vir de `politica-v4.json`, mantido pelo financeiro e sujeito
a mudar sem aviso. Isso invalida diretamente duas linhas da `spec.md` §3 ("não aplica
política diferente por centro de custo") e a decisão do `plan.md` §4 (constantes em módulo).

**B. Despesas internacionais.** A entrada pode trazer `moeda` (ISO 4217, ausente ⇒ BRL),
convertida pela **taxa da data da despesa** (`cambio.json`) antes de comparar com qualquer
limite. Invalida "não trata moeda diferente de real" da §3.

**C. Fila de aprovação manual (opcional).** Itens com valor reembolsável acima de R$ 500
passam a ter um *estado* de pendência, além do valor.

O resultado esperado não é "o sistema continua passando": é a mudança entrar **pela spec**,
com `DECISIONS.md`, tasks novas e só então código — na ordem que a `RUBRICA.md` §3 avalia
em 20 pontos. Três descobertas da leitura dos dados moldam o plano:

1. `exemplos/despesas-exemplo.json` é do **CC-ENG-PLATAFORMA**, que na v4 tem alimentação
   R$ 75 e **hospedagem R$ 0,00 (não reembolsável)**. O aceite de R$ 703,43 da §9 **quebra
   legitimamente** e passa a R$ 341,93. Essa quebra é o material mais valioso do `DECISIONS.md`.
2. Os dados do envelope têm armadilhas plantadas: `e-004` é **sábado 18/07 sem cotação**;
   `e-006` é **GBP, moeda ausente da tabela**; `f-003` é `representacao` num **CC desconhecido**,
   categoria que o padrão não tem.
3. A arquitetura do Dia 1 absorve quase tudo de graça — `Contexto` (DT-004) e a lista
   declarada de regras (DT-002) foram desenhadas exatamente para isto. O que **resiste** é a
   assinatura `(Despesa, Contexto) -> Parecer | None`, que não comporta um passo que
   *transforma* a despesa e pode *recusar* (a conversão cambial). Ver DT-007 abaixo.

## Decisões de ambiguidade já tomadas (confirmadas com o usuário)

| # | Ambiguidade | Decisão |
|---|---|---|
| 1 | CC presente na tabela mas sem uma categoria | **Herda do padrão** (a tabela do CC é *override*, não substituição). Justificativa: CC-ENG-PLATAFORMA precisou escrever `hospedagem: 0.00` explicitamente — se a omissão já bloqueasse, a linha seria redundante |
| 2 | Data sem cotação publicada (sábado/feriado) | **Última cotação anterior** (PTAX de fechamento). Sem nenhuma anterior ⇒ recusa |
| 3 | Moeda sem cotação na tabela (GBP) | **Recusa o item**, que permanece no resultado com `valor_lancado` 0,00 BRL e `valor_origem`/`moeda` visíveis. Preserva o invariante §9 (soma dos itens = resumo) |
| 4 | Item C (fila de aprovação) | **Entra, como fase final**, executável só depois de A e B verdes; cortável sem deixar a spec inconsistente |

## Estado do repositório neste momento

**Nada foi executado ainda.** Esta sessão produziu só o plano — nenhum arquivo do
projeto foi criado, editado ou movido.

| Item | Estado |
|---|---|
| `HEAD` | `e025389` — igual ao fim do Dia 1 |
| Working tree | limpo, exceto `Day2Envelope/` (ainda **não rastreada**) e este arquivo |
| `Day2Envelope/` | intacta na raiz, com os 5 arquivos — a Fase 0 ainda não rodou |
| `src/`, `tests/` | inalterados; 94 testes verdes na v3 |
| `spec.md` | 1.1 — ainda descreve a política v3 |

Ou seja: a próxima sessão começa na **Fase 0**, do zero.

## Pendência herdada do Dia 1 que este plano não recolheu

O `docs/HANDOFF.md` listava, como pendência 3, a **revisão das 7 sub-decisões de
ambiguidade da v3** (tabela no fim daquele arquivo) — implementadas fielmente, mas
nunca revisadas. Este plano não trata disso. Duas delas encostam na v4 e vale
decidir conscientemente se ficam como estão:

- *"Hospedagem confere viagem à data mesmo quando a própria hospedagem é recusada"* —
  na v4 vira o caso do CC-ENG-PLATAFORMA, cuja hospedagem tem limite 0,00. Já está
  endereçado como AMB-015, mas a origem é essa decisão do Dia 1.
- *"Estorno não consome nem devolve teto de nenhuma outra despesa"* — inalterada pela
  v4, mas passa a conviver com estorno em moeda estrangeira.

Se a conclusão for "seguem válidas", isso também é registro — e é conteúdo de relatório.

---

## Ordem de trabalho (inegociável)

`spec.md` → `DECISIONS.md` → `tasks.md` → código. Nada de código antes dos três documentos.
Commits de documento usam `docs(spec):` / `docs(tasks):` / `docs(plan):`; commits de código
referenciam a task e vêm **sempre em dois**: `test(T-0XX)` antes de `feat(T-0XX)`
(decisão do `docs/HANDOFF.md`, sem exceção a partir de T-023).

---

## Fase 0 — Preparação (1 commit)

Mover os cinco arquivos de `Day2Envelope/` para `exemplos/envelope/` (o envelope pede
explicitamente `exemplos/envelope/` e que sejam commitados como parte da entrega). Remover
a pasta `Day2Envelope/`. O comunicado `00-ENVELOPE-LACRADO.md` vai junto — é a fonte citada
pelo `DECISIONS.md`.

`docs(envelope): incorpora os arquivos do envelope em exemplos/envelope/`

## Fase 1 — Spec (commits `docs(spec):`)

Reescrever `specs/001-motor-reembolso/spec.md` para **1.2**:

**§3 Fora de escopo** — remover "não trata moeda diferente de real" e "não aplica política
diferente por centro de custo" (mantendo cargo/senioridade fora). Reescrever "não consulta
sistema externo": a fonte passa a ser **três documentos de entrada** (despesas, política,
câmbio); o sistema continua sem consultar serviço em tempo de execução.

**§4 Entrada e saída** — três blocos novos:
- `despesas[].moeda` (opcional, ISO 4217, ausente ⇒ `BRL`, comparada sem caixa).
- Documento de política: `padrao`, `centros_custo`, `nota_fiscal_obrigatoria_acima_de`,
  `acrescimo_em_viagem_percentual`, `versao`, `vigencia`.
- Documento de câmbio: `taxas` por data e moeda.
- Saída ganha por item `moeda`, `valor_origem`, `taxa_cambio`, `data_taxa`; e um bloco
  `politica` no cabeçalho (`versao`, `vigencia`, `centro_custo_aplicado`,
  `origem_dos_limites: "centro_custo" | "padrao"`) para o leitor auditar qual tabela valeu.
  `valor_lancado`, `valor_reembolsavel`, `valor_glosado` e todos os totais são **sempre BRL**.

**§5 Regras** — três novas e sete emendadas:

| Regra | Mudança |
|---|---|
| **RN-011** (nova) | Conversão cambial: taxa da data; sem cotação na data, a última publicada anterior; sem nenhuma anterior ou moeda ausente da tabela, recusa com o item preservado |
| **RN-012** (nova) | Limites por centro de custo: tabela do CC sobrepõe o padrão categoria a categoria; CC ausente da tabela usa o padrão inteiro; **limite 0,00 ⇒ recusa**, não glosa total |
| **RN-013** (nova, opcional) | Fila de aprovação: valor reembolsável **estritamente acima** de R$ 500,00 ⇒ `pendente_aprovacao`. Estado é ortogonal ao status, não o substitui; estorno nunca fica pendente |
| RN-001 | Categorias cobertas passam a depender do centro de custo (`representacao` só existe no CC-COMERCIAL) |
| RN-004 | Chave de duplicata inclui `moeda`; valores iguais em moedas diferentes não são duplicata |
| RN-006 | Piso de R$ 100,00 vem da política e é comparado ao **valor já convertido em BRL** |
| RN-007 | Teto vem de `RN-012`, não de constante |
| RN-009 | Percentual de acréscimo vem da política (`50` ⇒ fator 1,5). Hospedagem **não reembolsável** (limite 0) **continua caracterizando viagem** — o indício é o pernoite, não o pagamento |
| RN-010 | Estende-se ao valor convertido: arredondamento único de duas casas, meio para cima, logo após a conversão. A taxa não é arredondada |
| RN-008 | Sem mudança (uma diária por lançamento) |

**§6 Ambiguidades** — acrescentar **AMB-013 a AMB-024**, cada uma com texto original do RH,
tipo, o que não está claro, âncora nos dados do envelope, decisão e justificativa:

| ID | Ambiguidade | Âncora |
|---|---|---|
| AMB-013 | "aplica-se a política padrão": CC ausente vs. categoria ausente dentro de um CC presente | CC-ADM sem `hospedagem`; `f-*` em CC-SUPORTE-N2 |
| AMB-014 | Limite 0,00 é recusa ou glosa total (status `recusada` vs. `parcial` de R$ 0,00)? | CC-ENG-PLATAFORMA `hospedagem: 0.00` · `d-010` |
| AMB-015 | Hospedagem não reembolsável ainda caracteriza viagem? O acréscimo de 50% alcança categorias novas? | `d-010` · `e-007` |
| AMB-016 | `periodicidade: "dia"` reabre AMB-001 (teto por despesa vs. por soma do dia)? **Não** — nada no comunicado mudou a agregação | `e-002`/`e-003` |
| AMB-017 | `vigencia` da política é validada contra a data da despesa? **Não** — a política recebida é a vigente | `vigencia: 2026-07-01` |
| AMB-018 | "a taxa da data da despesa" quando a data não tem cotação | `e-004` (sábado 18/07) |
| AMB-019 | Moeda inteiramente ausente da tabela de câmbio | `e-006` (GBP) |
| AMB-020 | Arredondamento do valor convertido (quantas casas, em que momento) | `e-003` (14,50 × 5,88) |
| AMB-021 | O piso de nota fiscal é comparado em BRL ou na moeda de origem | `e-005` (40 USD = 220,00 BRL sem nota) |
| AMB-022 | Chave de duplicata com moeda | — |
| AMB-023 | Como um item não convertível entra em `total_lancado`, que é em BRL | `e-006` |
| AMB-024 | "passe de R$ 500" é estrito; estado substitui ou acompanha o status; pendente entra no total? | `e-007` (600,00) |

**§7 Casos de borda** — acrescentar linhas: sábado sem cotação · moeda sem cotação ·
limite 0,00 · CC desconhecido · categoria só existente num CC · fronteira R$ 500,00/R$ 500,01 ·
piso de nota fiscal sobre valor convertido.

**§8 Ordem de aplicação** — passa a ter dez passos:

```
1. Arredondamento na leitura            RN-010
2. Normalização da categoria            RN-002       (transformação)
3. Competência                          RN-003
4. Categoria coberta pelo CC            RN-001+012
5. Duplicata (chave com moeda)          RN-004
6. Conversão cambial                    RN-011       (transformação, pode recusar)
7. Estorno                              RN-005
8. Nota fiscal (sobre o valor em BRL)   RN-006
9. Teto do CC, com viagem               RN-007/008/009/012
10. Fila de aprovação (pós-decisão)     RN-013       (opcional; não altera valor)
```

**§9 Critérios de aceite** — reescritos para os números da v4 (calculados à mão a partir das
decisões acima; a implementação confirma ou expõe erro meu):

| Arquivo | Centro de custo | Lançado | Reembolsável | Itens-chave |
|---|---|---|---|---|
| `despesas-exemplo.json` | CC-ENG-PLATAFORMA | 1.816,84 | **341,93** | `d-001` 72,50 (teto 75) · `d-010` **0,00** (hospedagem não reembolsável) · `d-014` **61,00** |
| `envelope/despesas-envelope.json` | CC-COMERCIAL | 2.457,52 | **1.343,26** | `e-001` 300,00 · `e-004` 90,00 (taxa de 17/07) · `e-005` 0,00 (220 BRL sem nota) · `e-006` 0,00 (GBP) · `e-007` 600,00 (teto 400 × 1,5) |
| `envelope/...-cc-desconhecido.json` | CC-SUPORTE-N2 → padrão | 623,76 | **433,76** | `f-002` 310,00 (teto 375) · `f-003` **0,00** (`representacao` não existe no padrão) · `f-004` 65,76 (12 USD × 5,48) |

**§10 Em aberto** — acrescentar: vigência não validada · convenção de fim de semana é decisão
nossa, não do RH · item não convertível subestima `total_lancado` · fila de aprovação não
persiste estado entre execuções.

## Fase 2 — DECISIONS.md (1 commit `docs(spec):`)

Três entradas novas, no formato de D-001 (gatilho / o que mudou / por quê / o que invalidou /
tasks afetadas / custo):

- **D-002 — Política v4: limites por centro de custo e política externalizada.** Registra
  explicitamente a quebra do aceite oficial: **R$ 703,43 → R$ 341,93**, com `d-010` de 375,00
  para 0,00. Invalida `spec.md` §3 (duas linhas), `plan.md` §4 e o teste `test_e2e_exemplo_oficial`.
- **D-003 — Despesas internacionais.** Invalida `spec.md` §3, emenda RN-004/006/010 e o schema
  de saída.
- **D-004 — Fila de aprovação manual.** Marcada como opcional; se a Fase 8 não for concluída,
  a entrada é reescrita declarando o item fora de escopo — nunca deixada meio implementada.

## Fase 3 — plan.md e tasks.md (commits `docs(plan):` / `docs(tasks):`)

`plan.md` para **1.1**: reescrever §2 (dois carregadores novos), §3 (campos novos de `Despesa`,
`Contexto` e `Parecer`), §4 (a política deixa de ser constante), §6 (estratégia de testes com
fábricas de política e câmbio) e §7 (riscos reavaliados — o risco "limites variam por perfil"
se materializou e a mitigação prevista funcionou). Duas decisões técnicas novas:

- **DT-007 — Passo do pipeline passa a devolver `Parecer | Despesa | None`.** É o único ponto
  onde a arquitetura do Dia 1 resistiu: a conversão cambial *transforma* e pode *recusar*, e
  a assinatura `(Despesa, Contexto) -> Parecer | None` não comporta as duas coisas.
  `None` = não decidi · `Despesa` = transformei, siga com a nova · `Parecer` = decidi, pare.
  Ganho colateral: RN-002 (hoje fora da lista, chamada à parte na calculadora) passa a ser a
  entrada nº 2 da lista declarada, e a §8 fica inteiramente visível num só lugar.
  *Alternativa descartada:* dois laços separados (regras antes e depois da conversão) — quebraria
  a lista única que DT-002 existe para preservar.
- **DT-008 — Política e câmbio entram no `Contexto`, carregados na fronteira de I/O.**
  `motor/politica.py` e `motor/cambio.py` continuam puros (estruturas + consulta); quem lê
  arquivo é `io/carregador_politica.py` e `io/carregador_cambio.py`. DT-003 sobrevive intacto.
  *Alternativa descartada:* o motor lendo o JSON de política — mataria DT-003 e tornaria todo
  teste de regra um teste de disco.

`tasks.md`: preencher a Fase 5 (hoje vazia) com T-023..T-035, cada uma com "atende", critério
de aceite nomeando o teste, e campo de commit a preencher. Atualizar a matriz de cobertura ao
fim de cada fase.

---

## Fases de código

Cada task = 2 commits (`test(T-0XX)` → `feat(T-0XX)`).

### Fase 5 — Política externa por centro de custo (T-023..T-026)

| Task | O quê | Aceite |
|---|---|---|
| **T-023** | `motor/politica.py` deixa de expor constantes e passa a expor `Politica` e `LimiteCategoria` (`@dataclass(frozen=True)`), com `limite(cc, categoria) -> Decimal \| None` e `categorias_cobertas(cc)`. Merge `{**padrao, **centros_custo[cc]}` | `test_rn_012_cc_desconhecido_usa_padrao`, `test_rn_012_categoria_ausente_no_cc_herda_padrao`, `test_rn_012_cc_sobrepoe_o_padrao` |
| **T-024** | `io/carregador_politica.py`: JSON → `Politica`, `parse_float=Decimal`, validação nomeando o campo ausente (mesmo padrão de `ErroDeEntrada`). `acrescimo_em_viagem_percentual: 50` vira fator `1.5` | `test_carregador_politica_rejeita_campo_ausente`, `test_carregador_politica_converte_percentual_em_fator` |
| **T-025** | `Contexto` ganha `centro_custo`, `politica`. RN-001 e RN-007 passam a consultar a política; **limite 0,00 recusa** (RN-012). RN-009 lê o fator da política | `test_rn_012_limite_zero_recusa`, `test_rn_001_representacao_coberta_apenas_no_cc_comercial`, `test_rn_009_fator_vem_da_politica` |
| **T-026** | CLI `--politica` **opcional**, default `exemplos/envelope/politica-v4.json` resolvido a partir da raiz do pacote (não do CWD). Preserva o contrato fixo `calcular --input X --output Y` do `DESAFIO.md` — os casos ocultos do instrutor rodam sem flag nova | `test_cli_usa_politica_padrao_sem_flag`, `test_cli_aceita_politica_alternativa` |

### Fase 6 — Despesas internacionais (T-027..T-031)

| Task | O quê | Aceite |
|---|---|---|
| **T-027** | `Despesa` ganha `moeda`, `valor_origem`, `taxa_cambio`, `data_taxa`. Carregador lê `moeda` opcional, default `BRL`, normalizada (caixa/espaços) | `test_carregador_moeda_ausente_assume_brl`, `test_carregador_normaliza_codigo_de_moeda` |
| **T-028** | `motor/cambio.py` puro: `TabelaCambio.taxa(moeda, data) -> (Decimal, date) \| None`, retrocedendo para a última data **que tenha aquela moeda**. `io/carregador_cambio.py` + CLI `--cambio` (mesmo padrão da T-026) | `test_rn_011_taxa_da_data_exata`, `test_rn_011_data_sem_cotacao_usa_ultima_anterior`, `test_rn_011_sem_cotacao_anterior_recusa` |
| **T-029** | **DT-007**: passo do pipeline devolve `Parecer \| Despesa \| None`; a calculadora passa a ter uma lista única e RN-002 entra nela. `converter_para_brl` como passo 6 | `test_ordem_conversao_antes_da_nota_fiscal`, `test_pipeline_e_uma_lista_unica` |
| **T-030** | RN-011 completa: converte, arredonda uma vez (RN-010 estendida), preenche `valor_origem`/`taxa_cambio`/`data_taxa`. Moeda sem cotação ⇒ recusa com `valor` 0,00 BRL e origem preservada | `test_rn_011_moeda_sem_cotacao_e_recusada`, `test_rn_011_arredonda_valor_convertido`, `test_rn_011_item_nao_convertivel_nao_polui_total` |
| **T-031** | RN-004 com `moeda` na chave; serializador emite `moeda`/`valor_origem`/`taxa_cambio`/`data_taxa` e o bloco `politica` no cabeçalho | `test_rn_004_moedas_diferentes_nao_sao_duplicata`, `test_serializa_despesa_em_moeda_estrangeira` |

### Fase 7 — Reexecução dos aceites (T-032..T-034) — **ponto de corte seguro**

| Task | O quê | Aceite |
|---|---|---|
| **T-032** | Atualizar `test_e2e_exemplo_oficial` para os valores v4 (**341,93**), com comentário citando D-002 | `test_e2e_exemplo_oficial` verde nos novos números |
| **T-033** | E2E sobre os dois arquivos do envelope | `test_e2e_envelope_cc_comercial` (1.343,26), `test_e2e_envelope_cc_desconhecido` (433,76) |
| **T-034** | Casos de borda novos da §7 no `test_casos_de_borda.py` (os 18 atuais usam `centro_custo: "CC"` ⇒ padrão ⇒ continuam válidos sem alteração de valor) | `test_casos_de_borda` com as linhas novas; contador atualizado |

### Fase 8 — Opcional: fila de aprovação (T-035..T-036)

Só começar com a Fase 7 inteiramente verde. Se o tempo acabar antes, **não iniciar** —
reescrever D-004 e a `spec.md` §3 declarando o item fora de escopo, que é o que o envelope
manda ("se você deixar a spec inconsistente para chegar nele, perde").

| Task | O quê | Aceite |
|---|---|---|
| **T-035** | Enum `Estado` (`aprovacao_automatica` / `pendente_aprovacao`), campo em `Parecer`, `rn_013_fila_aprovacao(parecer, contexto)` como passo pós-decisão | `test_rn_013_acima_de_500_fica_pendente`, `test_rn_013_exatamente_500_nao_fica_pendente`, `test_rn_013_estorno_nunca_fica_pendente` |
| **T-036** | Saída: `itens[].estado`, `resumo.quantidade_por_estado`, `resumo.total_pendente_aprovacao` | `test_resumo_conta_pendencias`, `e-007` sai `pendente_aprovacao` no e2e |

### Fase 9 — Fechamento (commits `docs:`)

- **`README.md`** — v4, novos flags, novos totais, tabela de "o que o sistema faz" refeita.
- **`CLAUDE.md`** — a seção "Fora de escopo" hoje afirma "não trata outra moeda, não diferencia
  política por cargo ou centro de custo". Vira mentira na v4 e precisa acompanhar a spec.
- **`docs/RELATORIO.md`** — onde moram 20 pontos. Preencher os cinco blocos com evidência:
  - *Delegação, Descrição, Discernimento* (pelo menos um erro concreto meu, com trecho de
    sessão), *Diligência*.
  - *O envelope*: arquivos tocados à mão, `git diff e025389 HEAD --stat`, tempo, o que a
    arquitetura absorveu de graça (DT-002/DT-004: `Contexto` recebeu política e câmbio sem
    mudar a assinatura das regras) e **o que resistiu** (DT-007 — a assinatura não comportava
    um passo que transforma e recusa).
  - Pendências herdadas do `HANDOFF.md`: o **desvio de granularidade de commits** da Fase 1-4
    e por que não foi corrigido por reescrita; e o **formato das sessões** (`.jsonl` +
    `docs/sessions/README.md`, alternativa ao `/export`).
- **`docs/sessions/`** — rodar `python docs/sessions/_exportar.py` ao fim da sessão do Dia 2.

---

## Arquivos afetados

**Criados:** `src/motor/cambio.py` · `src/io/carregador_politica.py` ·
`src/io/carregador_cambio.py` · `tests/test_rn_011_cambio.py` ·
`tests/test_rn_012_centro_custo.py` · `tests/test_rn_013_fila_aprovacao.py` ·
`tests/test_carregador_politica.py` · `tests/test_carregador_cambio.py` ·
`tests/test_e2e_envelope.py` · `exemplos/envelope/*` (5 arquivos movidos)

**Modificados:** `specs/001-motor-reembolso/{spec,plan,tasks,DECISIONS}.md` ·
`src/motor/{modelo,politica,regras,calculadora}.py` · `src/io/{carregador,serializador}.py` ·
`src/cli.py` · `tests/fabricas.py` (ganha fábricas de `Politica`, `TabelaCambio` e `Contexto`) ·
`tests/{test_politica,test_casos_de_borda,test_e2e_exemplo_oficial,test_calculadora,test_serializador}.py`
e os `test_rn_00X_*.py` que constroem `Contexto` à mão · `README.md` · `CLAUDE.md` ·
`docs/RELATORIO.md`

**Reutilizar, não reinventar:** o padrão `ErroDeEntrada` + `_exigir`/`_exigir_data` de
[carregador.py](src/io/carregador.py#L20-L45) nos dois carregadores novos; a fábrica
`despesa()` de [fabricas.py](tests/fabricas.py); o `_valor()` de
[serializador.py](src/io/serializador.py#L11); a fábrica com closure
`criar_rn_004_duplicata()` de [regras.py](src/motor/regras.py#L54) como modelo para qualquer
regra que precise de estado por execução.

---

## Verificação

1. **Suíte completa:** `pytest -q` — verde. Nenhum teste do Dia 1 pode quebrar *em silêncio*;
   os que mudam de valor (só os que dependem do CC do exemplo oficial) mudam por T-032, com
   D-002 citado no código do teste.
2. **Por regra:** `pytest -k rn_011`, `pytest -k rn_012`, `pytest -k rn_013`.
3. **CLI sem flag nova** (o contrato fixo do `DESAFIO.md`, que é como o instrutor roda os
   casos ocultos):
   ```
   python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json
   ```
   Conferir `resumo.total_reembolsavel == "341.93"` e `d-010` em `0.00`.
4. **Os dois arquivos do envelope:**
   ```
   python -m src.cli calcular --input exemplos/envelope/despesas-envelope.json --output r1.json
   python -m src.cli calcular --input exemplos/envelope/despesas-envelope-cc-desconhecido.json --output r2.json
   ```
   Conferir 1.343,26 e 433,76, mais `e-006` recusada por GBP e `f-003` recusada por categoria.
5. **Flags explícitas:** repetir com `--politica` e `--cambio` apontando para os arquivos, e
   confirmar resultado idêntico ao default.
6. **Rastreabilidade:** `git log --grep "T-02"` mostra os pares `test`/`feat`; a matriz de
   cobertura no fim do `tasks.md` fecha RN-011/012/013.
7. **Métrica para o relatório:** `git diff e025389 HEAD --stat`.

## Riscos conhecidos

- **Os números de aceite acima foram calculados à mão.** Se a implementação divergir, a
  primeira hipótese é erro meu no cálculo, não bug — reconferir antes de mexer na spec.
- **Fase 8 é a única cortável.** Fases 5-7 são o núcleo dos 20 pontos do envelope.
- **Cuidado com o default do `--politica`:** resolvido a partir da raiz do pacote. Se resolver
  pelo CWD, a CLI quebra quando rodada de outro diretório e derruba os 10 pontos de "produto funciona".

---

## Anexo — memória de cálculo dos números de aceite

Os três totais da §9 foram calculados **à mão**, item a item, a partir das decisões
desta sessão. Estão aqui abertos para que, se a implementação divergir, dê para
descobrir **onde** sem refazer a conta inteira — e para que a spec não receba um
número que ninguém sabe de onde saiu.

### `exemplos/despesas-exemplo.json` — CC-ENG-PLATAFORMA

Limites: alimentação **75** · transporte **80** · hospedagem **0,00 (bloqueio explícito)**.
Datas em viagem: 14/07 e 22/07 (`d-010`, `d-013`) — nenhuma outra despesa cai nelas,
então a ampliação de 50% não altera nada neste arquivo.

| Item | Lançado | Reembolsável | Por quê |
|---|---|---|---|
| d-001 | 72,50 | **72,50** | teto 75 (era 60 na v3 → deixa de ser parcial) |
| d-002 | 38,00 | 38,00 | dentro do teto |
| d-003 | 100,00 | 80,00 | piso da nota é estrito; teto de transporte 80 |
| d-004 | 100,01 | 0,00 | um centavo acima do piso, sem nota |
| d-005 | 89,00 | 0,00 | `coworking` fora da política |
| d-006 | 54,90 | 54,90 | primeira ocorrência |
| d-007 | 54,90 | 0,00 | duplicata |
| d-008 | 41,00 | 0,00 | fora da competência |
| d-009 | −45,00 | −45,00 | estorno, integral |
| d-010 | 480,00 | **0,00** | hospedagem não reembolsável no CC (era 375,00 na v3) |
| d-011 | 33,33 | 33,33 | arredondado na leitura |
| d-012 | 47,20 | 47,20 | dentro do teto |
| d-013 | 690,00 | 0,00 | sem nota — RN-006 recusa antes do teto |
| d-014 | 61,00 | **61,00** | teto 75 (era 60 na v3 → deixa de ser parcial) |

`72,50 + 38,00 + 80,00 + 54,90 − 45,00 + 33,33 + 47,20 + 61,00` = **341,93**
Lançado **1.816,84** (inalterado) · glosado **1.474,91**

### `exemplos/envelope/despesas-envelope.json` — CC-COMERCIAL

Limites: alimentação **90** · transporte **150** · hospedagem **400** · representação **300**.
Data em viagem: **22/07** (`e-007`, a própria hospedagem).

| Item | Origem | Taxa | BRL | Reembolsável | Por quê |
|---|---|---|---|---|---|
| e-001 | 340,00 BRL | — | 340,00 | 300,00 | teto de representação |
| e-002 | 22,00 EUR | 5,93 (14/07) | 130,46 | 90,00 | teto de alimentação |
| e-003 | 14,50 EUR | 5,88 (15/07) | 85,26 | 85,26 | 85,26 ≤ 100 dispensa nota; dentro do teto |
| e-004 | 30,00 EUR | **5,96 (17/07)** | 178,80 | 90,00 | 18/07 é sábado — cai na última cotação anterior |
| e-005 | 40,00 USD | 5,50 (20/07) | 220,00 | **0,00** | piso da nota comparado **em BRL**: 220 > 100, sem nota |
| e-006 | 55,00 GBP | **ausente** | 0,00 | 0,00 | moeda sem cotação — recusa, origem preservada |
| e-007 | 1.200,00 BRL | — | 1.200,00 | 600,00 | teto 400 × 1,5 (viagem) · **> 500 ⇒ pendente** |
| e-008 | 95,00 BRL | — | 95,00 | 90,00 | teto de alimentação |
| e-009 | 120,00 BRL | — | 120,00 | 0,00 | `coworking` fora da política |
| e-010 | 88,00 (sem `moeda`) | — | 88,00 | 88,00 | ausente ⇒ BRL; dentro do teto |

Lançado **2.457,52** · reembolsável **1.343,26** · glosado **1.114,26**
Único item pendente de aprovação: `e-007` (600,00).

### `exemplos/envelope/despesas-envelope-cc-desconhecido.json` — CC-SUPORTE-N2

CC ausente da tabela ⇒ **padrão inteiro**: 60 / 80 / 250, **sem `representacao`**.
Data em viagem: **17/07** (`f-002`).

| Item | Origem | Taxa | BRL | Reembolsável | Por quê |
|---|---|---|---|---|---|
| f-001 | 58,00 BRL | — | 58,00 | 58,00 | dentro do teto 60 |
| f-002 | 310,00 BRL | — | 310,00 | 310,00 | teto 250 × 1,5 = 375 (ela própria caracteriza a viagem) |
| f-003 | 190,00 BRL | — | 190,00 | **0,00** | `representacao` só existe no CC-COMERCIAL, não no padrão |
| f-004 | 12,00 USD | 5,48 (21/07) | 65,76 | 65,76 | dentro do teto 80 |

Lançado **623,76** · reembolsável **433,76** · glosado **190,00**

### O que estes três arquivos exercitam

`e-004` cobre a decisão de fim de semana · `e-005` prova que o piso de nota é comparado
em BRL · `e-006` cobre moeda sem cotação · `e-007` cobre viagem + fila de aprovação ·
`e-010` cobre `moeda` ausente · `f-003` cobre categoria que só existe num CC ·
`d-010` cobre limite 0,00 · `d-001`/`d-014` provam que o teto veio do CC e não da constante.
