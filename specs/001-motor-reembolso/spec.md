# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.1 · **Status:** aprovada · **Última alteração:** 2026-07-30

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o `plan.md`.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

---

## 1. Problema

O financeiro confere manualmente, item por item, cada despesa lançada por um
colaborador contra a política de reembolso. O processo é lento e inconsistente:
duas pessoas conferindo a mesma planilha chegam a valores diferentes, porque a
política admite mais de uma leitura em vários pontos. O custo aparece como
retrabalho, reembolso pago a maior e contestação de colaborador.

## 2. Objetivo

Dado o conjunto de despesas de um colaborador num período, o sistema decide
quanto é reembolsável e emite, para cada despesa, o valor aprovado e a
justificativa da decisão — de forma reproduzível e auditável.

## 3. Fora de escopo

- Não decide aprovação final: o resultado é um parecer de cálculo, não um pagamento.
- Não valida autenticidade de nota fiscal — apenas registra se o colaborador declarou possuí-la.
- Não consulta sistema externo (RH, ERP, folha, câmbio). A única fonte é o documento de entrada.
- Não trata moeda diferente de real.
- Não aplica política diferente por centro de custo, cargo ou senioridade.
- Não faz rateio entre centros de custo.
- Não corrige nem completa dados de entrada malformados: entrada inválida é rejeitada, não adivinhada.
- Não mantém histórico entre execuções. Cada execução considera apenas o período recebido.

## 4. Entrada e saída

**Entrada:** conforme `exemplos/despesas-exemplo.json`.

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | Identificador do colaborador | sim |
| `colaborador.nome` | texto | Nome, para exibição no resultado | sim |
| `colaborador.centro_custo` | texto | Centro de custo, repassado ao resultado | sim |
| `periodo.competencia` | texto `AAAA-MM` | Mês de competência do lançamento | sim |
| `periodo.inicio` | data `AAAA-MM-DD` | Início do período, informativo | sim |
| `periodo.fim` | data `AAAA-MM-DD` | Fim do período, informativo | sim |
| `despesas[].id` | texto | Identificador único da despesa | sim |
| `despesas[].data` | data `AAAA-MM-DD` | Data em que a despesa ocorreu | sim |
| `despesas[].categoria` | texto | Categoria declarada | sim |
| `despesas[].descricao` | texto | Texto livre; **não** é usado em nenhuma decisão de cálculo | sim |
| `despesas[].fornecedor` | texto | Estabelecimento; usado na detecção de duplicata | sim |
| `despesas[].valor` | número | Valor em reais; pode ser negativo (estorno) | sim |
| `despesas[].tem_nota_fiscal` | booleano | Declaração de posse de nota fiscal | sim |

**Saída:** documento com o mesmo cabeçalho da entrada, um resumo e um parecer por
despesa. Valores monetários são texto com exatamente duas casas decimais e ponto
como separador, para que o consumidor não precise inferir precisão.

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador`, `periodo` | objeto | Copiados da entrada, sem alteração |
| `resumo.total_lancado` | texto | Soma dos valores lançados, após arredondamento de leitura |
| `resumo.total_reembolsavel` | texto | Soma dos valores reembolsáveis, estornos incluídos |
| `resumo.total_glosado` | texto | `total_lancado` − `total_reembolsavel` |
| `resumo.quantidade_por_status` | objeto | Contagem de itens em cada status |
| `itens[].id`, `.data`, `.categoria` | texto | Identificação da despesa; `categoria` já normalizada |
| `itens[].valor_lancado` | texto | Valor de entrada após arredondamento de leitura |
| `itens[].valor_reembolsavel` | texto | Valor aprovado; negativo em estorno |
| `itens[].valor_glosado` | texto | `valor_lancado` − `valor_reembolsavel` |
| `itens[].status` | texto | `aprovada`, `parcial`, `recusada` ou `estorno` |
| `itens[].regras_aplicadas` | lista de texto | IDs das regras que determinaram o resultado |
| `itens[].justificativa` | texto | Frase legível explicando a decisão |

**Status:** `aprovada` = reembolsada integralmente · `parcial` = reembolsada com
glosa · `recusada` = reembolso zero · `estorno` = valor negativo abatido do total.

Exemplo de saída para uma entrada de duas despesas — um almoço de R$ 72,50 e um
jantar de R$ 38,00, ambos com nota, no mesmo dia:

```json
{
  "colaborador": { "id": "c-0417", "nome": "Marina Volpi", "centro_custo": "CC-ENG-PLATAFORMA" },
  "periodo": { "competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31" },
  "resumo": {
    "total_lancado": "110.50",
    "total_reembolsavel": "98.00",
    "total_glosado": "12.50",
    "quantidade_por_status": { "aprovada": 1, "parcial": 1, "recusada": 0, "estorno": 0 }
  },
  "itens": [
    {
      "id": "d-001",
      "data": "2026-07-03",
      "categoria": "alimentacao",
      "valor_lancado": "72.50",
      "valor_reembolsavel": "60.00",
      "valor_glosado": "12.50",
      "status": "parcial",
      "regras_aplicadas": ["RN-007"],
      "justificativa": "Valor acima do teto de R$ 60,00 para alimentacao. Excedente de R$ 12,50 glosado."
    },
    {
      "id": "d-002",
      "data": "2026-07-03",
      "categoria": "alimentacao",
      "valor_lancado": "38.00",
      "valor_reembolsavel": "38.00",
      "valor_glosado": "0.00",
      "status": "aprovada",
      "regras_aplicadas": ["RN-007"],
      "justificativa": "Valor dentro do teto de R$ 60,00 para alimentacao."
    }
  ]
}
```

## 5. Regras de negócio

### RN-001 — Categorias cobertas pela política

**Regra:** só são reembolsáveis as categorias `alimentacao`, `transporte_urbano`
e `hospedagem`. Qualquer outra é recusada com valor zero e permanece no resultado
com justificativa — não é omitida.
**Origem:** política do RH, item 9
**Aceite:** uma despesa de categoria `coworking` no valor de R$ 89,00 resulta em
reembolsável R$ 0,00, status `recusada`.

### RN-002 — Normalização da categoria

**Regra:** a categoria declarada é comparada com a política ignorando maiúsculas
e minúsculas e espaços nas pontas. A categoria normalizada é a que aparece no
resultado.
**Origem:** política do RH, item 9 (decorrente de AMB-012)
**Aceite:** uma despesa com categoria `"ALIMENTACAO"` é tratada como
`alimentacao` e concorre ao teto de R$ 60,00, não é recusada por categoria.

### RN-003 — Período de competência

**Regra:** só é reembolsável a despesa cuja data pertença ao mês indicado em
`periodo.competencia`. Despesa fora dele é recusada com valor zero e permanece no
resultado com justificativa. Os campos `periodo.inicio` e `periodo.fim` são
informativos e não decidem nada.
**Origem:** política do RH, item 7
**Aceite:** com competência `2026-07`, uma despesa de `2026-04-15` no valor de
R$ 41,00 resulta em reembolsável R$ 0,00, status `recusada`.

### RN-004 — Duplicatas

**Regra:** duas ou mais despesas são duplicatas entre si quando coincidem em
data, categoria normalizada, fornecedor, descrição e valor. A primeira na ordem
de aparição na entrada é processada normalmente; as demais são recusadas com
valor zero.
**Origem:** política do RH, item 8
**Aceite:** duas despesas idênticas de R$ 54,90 em `2026-07-09` no mesmo
fornecedor resultam em R$ 54,90 para a primeira e R$ 0,00 para a segunda.

### RN-005 — Estornos

**Regra:** despesa com valor negativo é um estorno. Ela não passa por exigência
de nota fiscal nem por teto: entra no total pelo seu valor integral, reduzindo o
reembolso. Estorno não consome nem devolve teto de nenhuma outra despesa.
**Origem:** não prevista na política (decorrente de AMB-010)
**Aceite:** uma despesa de −R$ 45,00 resulta em reembolsável −R$ 45,00, status
`estorno`, e reduz o total do período em R$ 45,00.

### RN-006 — Exigência de nota fiscal

**Regra:** despesa com valor **estritamente maior** que R$ 100,00 exige nota
fiscal declarada. Sem ela, a despesa é recusada integralmente. Valor de
exatamente R$ 100,00 não exige nota. O piso de R$ 100,00 é fixo e não é ampliado
por viagem.
**Origem:** política do RH, item 5
**Aceite:** R$ 100,00 sem nota segue para o teto e é reembolsada; R$ 100,01 sem
nota resulta em R$ 0,00, status `recusada`.

### RN-007 — Tetos por categoria e reembolso parcial

**Regra:** cada despesa é comparada individualmente ao teto da sua categoria —
R$ 60,00 para alimentação, R$ 80,00 para transporte urbano, R$ 250,00 para
hospedagem. O teto é por despesa, não pela soma do dia. Despesa acima do teto é
reembolsada pelo valor do teto; o excedente é glosado.
**Origem:** política do RH, itens 1, 2, 3 e 4
**Aceite:** duas despesas de alimentação no mesmo dia, de R$ 72,50 e R$ 38,00,
resultam em R$ 60,00 e R$ 38,00 — total de R$ 98,00 no dia.

### RN-008 — Hospedagem é uma diária por lançamento

**Regra:** cada lançamento de hospedagem vale como uma diária, qualquer que seja
o número de noites mencionado na descrição. O teto incide sobre o valor
lançado inteiro.
**Origem:** política do RH, item 3 (decorrente de AMB-007)
**Aceite:** hospedagem de R$ 480,00 descrita como "2 diarias", fora de viagem,
é reembolsada em R$ 250,00.

### RN-009 — Ampliação por viagem

**Regra:** o colaborador é considerado em viagem numa data quando existe, nessa
mesma data, ao menos um lançamento de categoria `hospedagem` — independentemente
de esse lançamento ter sido aprovado ou recusado. Nas datas em viagem, os tetos
de categoria da RN-007 são ampliados em 50%: R$ 90,00, R$ 120,00 e R$ 375,00.
A ampliação não alcança o piso de nota fiscal da RN-006.
**Origem:** política do RH, item 6 (decorrente de AMB-006)
**Aceite:** hospedagem de R$ 480,00 em `2026-07-14`, data que contém esse próprio
lançamento de hospedagem, é reembolsada em R$ 375,00 e não em R$ 250,00.

### RN-010 — Arredondamento

**Regra:** todo valor de entrada é arredondado para duas casas decimais na
leitura, meio para cima, antes de qualquer comparação. Todos os cálculos e
somas posteriores usam o valor já arredondado, e nenhum arredondamento adicional
ocorre depois.
**Origem:** não prevista na política (decorrente de AMB-011)
**Aceite:** uma despesa lançada como `33.333` é tratada como R$ 33,33 em todas as
comparações, no item e no total.

---

## 6. Ambiguidades identificadas e decisões

> **Esta seção é o coração da spec.** Uma ambiguidade que foi resolvida no código
> sem estar registrada aqui conta como não resolvida.

### AMB-001 — "por dia" é por despesa ou por soma do dia?

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia."
**Tipo:** unidade de aplicação
**O que não está claro:** o teto incide sobre cada despesa isolada ou sobre a soma das despesas da categoria naquela data.
**Âncora no exemplo:** `d-001` (72,50) + `d-002` (38,00) no dia 03/07. Por despesa → 60,00 + 38,00 = 98,00. Por dia → 60,00.
**Decisão:** o teto incide sobre cada despesa individualmente.
**Justificativa:** o teto funciona como limite de razoabilidade por consumo, e o financeiro precisa justificar a glosa item a item para o colaborador — o que a leitura agregada não permite.
**Regra afetada:** RN-007

### AMB-002 — "reembolsadas parcialmente" significa cortar ou recusar?

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**Tipo:** unidade de aplicação
**O que não está claro:** paga-se o teto e descarta-se o excedente, ou o item inteiro é recusado por violar o teto.
**Âncora no exemplo:** `d-014` (61,00 contra teto de 60,00). Cortar → 60,00. Recusar → 0,00.
**Decisão:** paga-se o valor do teto e o excedente é glosado.
**Justificativa:** é a leitura literal de "parcialmente"; recusar o item inteiro puniria o colaborador por um centavo de excesso.
**Regra afetada:** RN-007

### AMB-003 — "acima de R$ 100" inclui os R$ 100?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**Tipo:** fronteira
**O que não está claro:** a comparação é `> 100` ou `>= 100`.
**Âncora no exemplo:** `d-003` vale exatamente 100,00 e `d-004` vale 100,01 — ambas sem nota fiscal. O par existe para forçar esta decisão.
**Decisão:** a comparação é estrita: exatamente R$ 100,00 não exige nota fiscal.
**Justificativa:** "acima de" exclui o próprio valor em português corrente, e a leitura restritiva não pode ser presumida contra o colaborador.
**Regra afetada:** RN-006

### AMB-004 — falta de nota fiscal recusa o item ou limita o valor?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**Tipo:** unidade de aplicação
**O que não está claro:** sem nota, o item é recusado integralmente, ou é reembolsado até o piso de 100 (a parte que não exigiria nota).
**Âncora no exemplo:** `d-013` (690,00, sem nota). Recusa → 0,00. Limite ao piso → 100,00.
**Decisão:** a despesa é recusada integralmente.
**Justificativa:** a nota é o documento que comprova a despesa; sem ela não há o que reembolsar, nem parcialmente — reembolsar até o piso criaria incentivo a omitir nota.
**Regra afetada:** RN-006

### AMB-005 — a exigência de nota olha o valor lançado ou o valor já limitado?

**Texto original do RH:** itens 4 e 5 combinados.
**Tipo:** fronteira / ordem
**O que não está claro:** se o teto diário for aplicado antes, o valor pode cair abaixo de 100 e dispensar a nota; se a nota for exigida antes, o item cai antes de chegar ao teto.
**Âncora no exemplo:** `d-004` (100,01, transporte, sem nota). Teto de 80 primeiro → 80,00, abaixo de 100, nota dispensada. Nota primeiro → item recusado.
**Decisão:** a exigência de nota é avaliada primeiro, sobre o valor lançado.
**Justificativa:** a obrigação de documentar nasce do valor que o colaborador gastou, não do valor que a empresa decidiu pagar.
**Regra afetada:** RN-006 · define a §8

### AMB-006 — o que caracteriza "em viagem"?

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."
**Tipo:** dado ausente
**O que não está claro:** não existe campo de viagem na entrada. Precisa ser inferido, declarado como não suportado, ou exigido como campo novo. Além disso: os 50% ampliam também o piso de 100 da nota fiscal, ou só os tetos por categoria?
**Âncora no exemplo:** nenhuma despesa traz marcação de viagem; `d-010` e `d-013` são hospedagens que poderiam servir de indício.
**Decisão:** viagem é inferida pela existência de lançamento de hospedagem na mesma data, aprovado ou não. A ampliação de 50% alcança apenas os tetos por categoria, não o piso de R$ 100,00 da nota fiscal.
**Justificativa:** hospedagem é o indício mais direto de pernoite fora, e é o único disponível na entrada; o piso da nota é regra de comprovação, não de limite de gasto, e não há razão para afrouxá-lo em viagem.
**Regra afetada:** RN-009

### AMB-007 — "por diária" quando a entrada traz um valor só

**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária."
**Tipo:** dado ausente
**O que não está claro:** a entrada tem uma data e um valor agregado; o número de diárias só aparece no texto livre da descrição, que não é campo estruturado.
**Âncora no exemplo:** `d-010` = 480,00 "2 diarias" (240,00/noite). `d-013` = 690,00 "3 noites" (230,00/noite).
**Decisão:** cada lançamento de hospedagem conta como uma diária; a descrição não é interpretada.
**Justificativa:** derivar número de diárias de texto livre tornaria o resultado dependente da redação do colaborador, o que é o oposto de auditável — a correção certa é o campo passar a existir na entrada.
**Regra afetada:** RN-008 · consequência registrada na §10

### AMB-008 — o que é uma duplicata e o que é "tratar"

**Texto original do RH:** "Duplicatas devem ser tratadas."
**Tipo:** unidade de aplicação
**O que não está claro:** qual combinação de campos caracteriza duplicata, e o que se faz com ela — descartar a segunda, recusar as duas, ou apenas sinalizar.
**Âncora no exemplo:** `d-006` e `d-007` são idênticas em data, categoria, descrição, fornecedor e valor — diferem só no `id`.
**Decisão:** duplicata é a coincidência de data, categoria, fornecedor, descrição e valor; a primeira ocorrência é paga e as demais são recusadas.
**Justificativa:** pagar as duas assume erro do financeiro e recusar as duas pune o colaborador por um lançamento legítimo — pagar a primeira é a única leitura que não escolhe um lado sem evidência.
**Regra afetada:** RN-004 · consequência registrada na §10

### AMB-009 — qual campo define a competência, e o que acontece fora dela

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."
**Tipo:** fronteira / dado ausente
**O que não está claro:** a entrada traz `competencia` e também `inicio`/`fim` — qual governa se divergirem. E o item fora do período é recusado com justificativa ou excluído do resultado.
**Âncora no exemplo:** `d-008` é de 2026-04-15, fora de julho.
**Decisão:** `periodo.competencia` governa; `inicio` e `fim` são informativos. A despesa fora do período é recusada com valor zero e **permanece** no resultado.
**Justificativa:** competência é o conceito contábil que a política cita, e omitir o item do resultado esconderia do colaborador o motivo de não ter sido pago.
**Regra afetada:** RN-003

### AMB-010 — valor negativo (estorno)

**Texto original do RH:** silente.
**Tipo:** dado ausente
**O que não está claro:** a política não prevê valor negativo. Ele abate o total, é ignorado, é rejeitado como entrada inválida, ou reduz o consumo do teto diário.
**Âncora no exemplo:** `d-009` = −45,00, transporte urbano, 11/07.
**Decisão:** o estorno abate o total pelo valor integral, sem passar por teto nem por exigência de nota.
**Justificativa:** o estorno é a devolução de um valor já adiantado; aplicar teto sobre ele reduziria a devolução e faria a empresa reter dinheiro do colaborador.
**Regra afetada:** RN-005

### AMB-011 — arredondamento: quantas casas e em que momento

**Texto original do RH:** silente.
**Tipo:** fronteira
**O que não está claro:** a entrada admite mais de duas casas decimais. Arredonda-se na leitura, a cada regra, ou só no total — e para cima, para baixo ou meio-a-par.
**Âncora no exemplo:** `d-011` = 33,333.
**Decisão:** arredonda-se para duas casas, meio para cima, uma única vez, na leitura.
**Justificativa:** real não tem fração de centavo, e arredondar uma só vez no começo garante que o item e o total nunca discordem entre si.
**Regra afetada:** RN-010

### AMB-012 — categoria com grafia diferente

**Texto original do RH:** "Categorias fora da política não são reembolsáveis."
**Tipo:** fronteira
**O que não está claro:** a comparação de categoria é literal ou normalizada. Se for literal, uma diferença de caixa joga o item para fora da política.
**Âncora no exemplo:** `d-014` vem como `"ALIMENTACAO"`; todas as outras vêm minúsculas. `d-005` (`coworking`) é o caso de categoria genuinamente fora da política.
**Decisão:** a comparação ignora caixa e espaços nas pontas.
**Justificativa:** diferença de maiúscula é ruído de digitação, não intenção de lançar em outra categoria; recusar por isso seria erro de forma travando direito de fundo.
**Regra afetada:** RN-002

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Valor exatamente no piso da nota | R$ 100,00, sem nota | Não exige nota; segue para o teto | RN-006 |
| Um centavo acima do piso | R$ 100,01, sem nota | Recusada, R$ 0,00 | RN-006 |
| Valor exatamente no teto | Alimentação R$ 60,00 | Aprovada integralmente, sem glosa | RN-007 |
| Um centavo acima do teto | Alimentação R$ 60,01 | Parcial, R$ 60,00, glosa de R$ 0,01 | RN-007 |
| Duas despesas mesmo dia e categoria | R$ 72,50 e R$ 38,00 | R$ 60,00 e R$ 38,00; teto não é compartilhado | RN-007 |
| Duplicata exata | Duas de R$ 54,90, tudo igual | Primeira paga, segunda recusada | RN-004 |
| Mesmo valor, fornecedor diferente | R$ 54,90 em dois lugares | Ambas processadas; não é duplicata | RN-004 |
| Fora da competência | Data de abril, competência julho | Recusada, presente no resultado | RN-003 |
| Categoria fora da política | `coworking` R$ 89,00 | Recusada, presente no resultado | RN-001 |
| Categoria em caixa alta | `ALIMENTACAO` | Normalizada, concorre ao teto | RN-002 |
| Estorno | −R$ 45,00 | Abate integral, sem teto e sem nota | RN-005 |
| Estorno acima do teto em módulo | −R$ 500,00 alimentação | Abate R$ 500,00; teto não se aplica | RN-005 |
| Terceira casa decimal | R$ 33,333 | Tratada como R$ 33,33 em tudo | RN-010 |
| Hospedagem de várias noites | R$ 480,00 "2 diarias" | Uma diária; teto sobre o valor todo | RN-008 |
| Hospedagem sem nota acima do piso | R$ 690,00, sem nota | Recusada antes de chegar ao teto | RN-006 |
| Data com hospedagem | Alimentação R$ 85,00 na data | Teto ampliado para R$ 90,00; aprovada | RN-009 |
| Hospedagem recusada na data | Hospedagem sem nota + almoço | A data segue sendo viagem | RN-009 |
| Lista de despesas vazia | `despesas: []` | Resultado válido, todos os totais em `0.00` | — |

## 8. Ordem de aplicação das regras

A ordem muda o resultado — `d-004` é reembolsada ou recusada dependendo dela.
Cada despesa percorre os passos abaixo e **para no primeiro que a recusar**.

1. **Arredondamento na leitura** (RN-010) — todo o resto opera sobre o valor arredondado.
2. **Normalização da categoria** (RN-002).
3. **Competência** (RN-003) — fora do mês, recusa.
4. **Categoria coberta** (RN-001) — fora da política, recusa.
5. **Duplicata** (RN-004) — ocorrência repetida, recusa.
6. **Estorno** (RN-005) — se o valor é negativo, o resultado é o próprio valor e os passos 7 e 8 não se aplicam.
7. **Nota fiscal** (RN-006) — acima de R$ 100,00 sem nota, recusa.
8. **Teto da categoria** (RN-007, RN-008), com a ampliação de viagem (RN-009) quando a data qualifica.

O passo 8 é o único que pode produzir reembolso parcial. Os passos 3 a 7 produzem
apenas aprovação integral ou recusa integral.

A condição de viagem (RN-009) é determinada antes do passo 1, sobre a lista de
despesas como veio na entrada, e não é afetada por recusas ocorridas nos passos 3 a 7.

## 9. Critérios de aceite

O sistema está pronto quando:

- [x] Processa `exemplos/despesas-exemplo.json` e produz total reembolsável de **R$ 703,43** sobre total lançado de **R$ 1.816,84**.
- [x] Cada uma das 14 despesas do exemplo aparece no resultado com status, valor e justificativa.
- [x] `d-003` (R$ 100,00 sem nota) é reembolsada em R$ 80,00 e `d-004` (R$ 100,01 sem nota) em R$ 0,00.
- [x] `d-006` é reembolsada em R$ 54,90 e `d-007`, sua duplicata, em R$ 0,00.
- [x] `d-010` é reembolsada em R$ 375,00, com o teto ampliado por viagem.
- [x] `d-011` aparece como R$ 33,33 e não como R$ 33,333.
- [x] `d-014` é reconhecida como alimentação apesar da caixa alta e reembolsada em R$ 60,00.
- [x] A soma dos `valor_reembolsavel` dos itens é igual a `resumo.total_reembolsavel`.
- [x] Toda regra de RN-001 a RN-010 tem ao menos um caso de teste que a exercita.
- [x] Entrada com campo obrigatório ausente é rejeitada com mensagem, sem produzir resultado parcial.

## 10. O que fica em aberto

- **Viagem é inferida, não declarada.** A regra atual não reconhece viagem sem pernoite, e trata como viagem um dia em que houve hospedagem lançada por outro motivo. A correção certa é um campo explícito na entrada; enquanto ele não existe, a inferência da RN-009 é a decisão provisória.
- **Hospedagem de várias noites é penalizada.** Pela RN-008, `d-013` seria glosada mesmo se tivesse nota, embora R$ 230,00 por noite esteja dentro da política. Isso é consequência aceita de não interpretar texto livre; um campo `diarias` na entrada resolveria.
- **Duplicata legítima é indistinguível de erro.** Dois almoços iguais no mesmo lugar e no mesmo dia existem na vida real, e a RN-004 os recusa. Não há campo na entrada — hora, número de nota — que permita separar os dois casos.
- **Fim de semana não é tratado.** `d-012` é um sábado e a política não diz nada sobre isso. O sistema não distingue dia útil de fim de semana; se o RH quiser distinguir, é regra nova.
- **A política não versiona seus limites.** Os valores de R$ 60, R$ 80, R$ 250 e R$ 100 são da v3. Não há data de vigência na entrada, então uma despesa antiga é avaliada pelos limites atuais.
