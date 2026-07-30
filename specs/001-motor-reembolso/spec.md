# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.1 · **Status:** em desenvolvimento · **Última alteração:** 2026-07-30

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o `plan.md`.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

---

## 1. Problema

A empresa precisa decidir, de forma consistente e rastreável, quanto de cada despesa pode ser reembolsado, com base em uma política ambígua e em um conjunto de despesas que pode incluir valores fora do padrão. O sistema deve transformar essa política em decisões objetivas, justificando cada resultado para que financeiramente não dependa de conferência manual e de interpretação ad hoc.

## 2. Objetivo

Quando o sistema processa um conjunto de despesas, ele deve indicar, para cada item, se a despesa é reembolsável, qual valor pode ser pago e por que, com base em regras explícitas e verificáveis.

## 3. Fora de escopo

- Não realiza pagamento, emissão de boleto, transferência ou integração com contabilidade.
- Não calcula impostos, taxas, juros ou descontos financeiros.
- Não há campo explícito de viagem na entrada; por isso, o sistema considera como em viagem qualquer dia que tenha uma hospedagem associada, inferindo esse status a partir da própria entrada.
- Não reclassifica categorias fora da política; categorias diferentes de alimentação, transporte urbano e hospedagem não são reembolsáveis.
- Não oferece interface interativa; a entrada e a saída ocorrem por arquivo.

## 4. Entrada e saída

**Entrada:** conforme o formato de `exemplos/despesas-exemplo.json`. Os campos obrigatórios são:

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| colaborador.id | texto | Identificador do colaborador | sim |
| colaborador.nome | texto | Nome do colaborador | sim |
| periodo.competencia | texto | Mês de competência no formato `AAAA-MM` | sim |
| periodo.inicio | data | Início do período de competência | sim |
| periodo.fim | data | Fim do período de competência | sim |
| despesas[] | lista | Despesas a avaliar | sim |
| despesas[].id | texto | Identificador da despesa | sim |
| despesas[].data | data | Data da despesa | sim |
| despesas[].categoria | texto | Categoria da despesa | sim |
| despesas[].descricao | texto | Descrição da despesa | sim |
| despesas[].fornecedor | texto | Nome do fornecedor | sim |
| despesas[].valor | número | Valor monetário da despesa | sim |
| despesas[].tem_nota_fiscal | booleano | Indica se há nota fiscal | sim |

**Saída:** a saída deve conter o conjunto de despesas processadas e a decisão de cada uma. O formato mínimo é:

| Campo | Tipo | Significado |
|---|---|---|
| colaborador | objeto | Dados do colaborador recebidos na entrada |
| periodo | objeto | Período recebido na entrada |
| resumo | objeto | Totais gerais de valor original, valor reembolsável e quantidade de itens |
| itens | lista | Uma entrada por despesa, com status, valor reembolsável e motivo |

Exemplo de estrutura de saída para uma despesa simples:

```json
{
  "itens": [
    {
      "id": "d-001",
      "data": "2026-07-03",
      "categoria": "alimentacao",
      "valor_original": 72.5,
      "valor_reembolsavel": 60,
      "status": "reembolsado_parcialmente",
      "motivo": ["limite_diario"]
    }
  ]
}
```

## 5. Regras de negócio

Cada regra recebe um ID (`RN-001`, `RN-002`, ...). As tasks vão referenciar esses IDs.

### RN-001 — Categorias aceitas

**Regra:** Apenas as categorias `alimentacao`, `transporte_urbano` e `hospedagem` são passíveis de reembolso. Qualquer outra categoria é não reembolsável.
**Origem:** política do RH, item 9
**Aceite:** Uma despesa com categoria `coworking` deve receber status `nao_reembolsavel` e motivo `categoria_nao_politica`.

### RN-002 — Competência do lançamento

**Regra:** Uma despesa só pode ser reembolsada se a sua data estiver dentro do período de competência informado, inclusive nas datas de início e fim.
**Origem:** política do RH, item 7
**Aceite:** Uma despesa com data `2026-04-15` para um período de `2026-07-01` a `2026-07-31` deve ser marcada como `nao_reembolsavel` e motivo `fora_do_periodo`.

### RN-003 — Limite diário por categoria

**Regra:** O limite diário aplica-se por categoria e por dia calendário. Se mais de uma despesa da mesma categoria ocorrer no mesmo dia, o limite é compartilhado entre elas.
**Origem:** política do RH, itens 1, 2 e 3
**Aceite:** Duas despesas de alimentação no mesmo dia, de `R$ 40,00` e `R$ 30,00`, devem gerar reembolso de `R$ 40,00` e `R$ 20,00`, respectivamente, se o limite diário for `R$ 60,00`.

### RN-004 — Reembolso parcial acima do limite

**Regra:** Se o valor da despesa exceder o limite aplicável, o valor reembolsável é o próprio limite e o excedente não é pago.
**Origem:** política do RH, item 4
**Aceite:** Uma despesa de alimentação de `R$ 80,00` em um dia sem limite restante deve ter valor reembolsável igual a `R$ 60,00` e status `reembolsado_parcialmente`.

### RN-005 — Nota fiscal obrigatória acima de R$ 100,00

**Regra:** Despesas com valor superior a `R$ 100,00` precisam de nota fiscal para serem reembolsáveis. O limite de `R$ 100,00` é inclusivo: um valor exatamente igual a `R$ 100,00` não exige nota fiscal.
**Origem:** política do RH, item 5
**Aceite:** Uma despesa de `R$ 100,01` sem nota fiscal deve ser `nao_reembolsavel` e motivo `nota_fiscal_obrigatoria`.

### RN-006 — Dias em viagem inferidos a partir da hospedagem

**Regra:** A entrada atual não contém um campo explícito de viagem; por isso, o sistema considera como dia de viagem qualquer data em que exista uma despesa de hospedagem associada. Nesses dias, os limites diários passam a ser aumentados em 50%.
**Origem:** política do RH, item 6
**Aceite:** Uma despesa de transporte urbano de `R$ 90,00` em um dia com hospedagem associada deve ter valor reembolsável igual a `R$ 90,00` quando o limite diário passa de `R$ 80,00` para `R$ 120,00`.

### RN-007 — Duplicatas

**Regra:** Quando duas despesas são consideradas duplicadas, a segunda ocorrência é rejeitada como não reembolsável, mesmo que o valor e a categoria sejam aceitáveis.
**Origem:** política do RH, item 8
**Aceite:** Se duas despesas tiverem a mesma data, categoria, fornecedor, descrição e valor, a segunda deve ser marcada como `nao_reembolsavel` e motivo `duplicata`.

### RN-008 — Valores negativos ou zero

**Regra:** Valores menores ou iguais a zero são tratados como estornos ou ajustes e não são reembolsados.
**Origem:** decisão explícita do sistema para o exemplo de entrada
**Aceite:** Uma despesa com valor `-45,00` deve ser ignorada para fins de reembolso e não deve aparecer como reembolso nem como rejeição.

### RN-009 — Normalização de categoria

**Regra:** A comparação de categoria é feita sem diferenciar maiúsculas e minúsculas, após remoção de espaços extras.
**Origem:** decisão explícita do sistema para o exemplo de entrada
**Aceite:** Uma despesa com categoria `ALIMENTACAO` deve ser tratada como `alimentacao`.

---

## 6. Ambiguidades identificadas e decisões

> **Esta seção é o coração da spec e vale a maior parte do critério de qualidade.**
> Uma ambiguidade resolvida no código sem registrar aqui conta como não resolvida.

### AMB-001 — Limite por dia ou por despesa

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia"
**O que não está claro:** a política não informa se o limite é por despesa ou por agrupamento diário.
**Decisão:** O limite é compartilhado entre todas as despesas da mesma categoria no mesmo dia calendário.
**Justificativa:** Isso evita que uma pessoa faça várias despesas pequenas para contornar o limite e mantém a regra alinhada ao conceito de "por dia".
**Regra afetada:** RN-003

### AMB-002 — Reembolso parcial ou recusa total

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente"
**O que não está claro:** a política não define se o excedente é rejeitado ou se o item inteiro é recusado.
**Decisão:** O sistema paga até o limite aplicável e corta o excedente.
**Justificativa:** A política fala em reembolso parcial, não em recusa total do item.
**Regra afetada:** RN-004

### AMB-003 — Nota fiscal acima de R$ 100 ou a partir de R$ 100

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100"
**O que não está claro:** o valor de exatamente `R$ 100,00` entra ou não na regra.
**Decisão:** O critério é estritamente superior a `R$ 100,00`; valores iguais a `R$ 100,00` não exigem nota fiscal.
**Justificativa:** A redação usa "acima de", e o sistema deve respeitar o limite exato sem ampliar a regra.
**Regra afetada:** RN-005

### AMB-004 — O que caracteriza estar em viagem

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%"
**O que não está claro:** a política não declara como identificar viagem.
**Decisão:** Como a entrada não possui um campo explícito de viagem, o sistema considera como em viagem qualquer dia que contenha uma hospedagem associada. Nesse caso, os limites diários do dia são ampliados em 50%.
**Justificativa:** A regra precisa ser determinística e a hospedagem funciona como sinal explícito de deslocamento, sem exigir alteração no formato de entrada.
**Regra afetada:** RN-006

### AMB-005 — O que conta como período de competência

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência"
**O que não está claro:** a política não informa se a comparação é inclusiva ou exclusiva.
**Decisão:** As datas de início e fim fazem parte do período válido.
**Justificativa:** O termo "dentro do período" é normalmente interpretado de forma inclusiva.
**Regra afetada:** RN-002

### AMB-006 — Como tratar duplicatas

**Texto original do RH:** "Duplicatas devem ser tratadas"
**O que não está claro:** a política não define se a segunda entrada é ignorada, recusada ou ajustada.
**Decisão:** A segunda ocorrência é recusada como duplicata.
**Justificativa:** Isso preserva a integridade do processo sem inventar uma regra nova de compensação.
**Regra afetada:** RN-007

### AMB-007 — Categorias fora da política

**Texto original do RH:** "Categorias fora da política não são reembolsáveis"
**O que não está claro:** a política não define como lidar com categorias não previstas.
**Decisão:** Categorias diferentes de alimentação, transporte urbano e hospedagem são recusadas sem reembolso.
**Justificativa:** A política lista as categorias aceitas e o sistema deve ser estrito para evitar reembolso não previsto.
**Regra afetada:** RN-001

### AMB-008 — Como tratar valores negativos

**Texto original do RH:** não há regra explícita para estornos
**O que não está claro:** o exemplo de entrada inclui valores negativos, o que pode significar estorno ou erro.
**Decisão:** Valores negativos ou zero são ignorados para fins de reembolso.
**Justificativa:** Estornos não são despesas de reembolso e não devem ser tratados como gasto ou como rejeição.
**Regra afetada:** RN-008

### AMB-009 — Como tratar categoria em caixa alta

**Texto original do RH:** não há regra explícita para caixa de texto
**O que não está claro:** a entrada pode trazer categorias com letras maiúsculas.
**Decisão:** A comparação de categoria é case-insensitive.
**Justificativa:** Isso torna o sistema mais robusto sem depender de padronização manual da entrada.
**Regra afetada:** RN-009

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Duas despesas de alimentação no mesmo dia | duas despesas de `R$ 40,00` e `R$ 30,00` no mesmo dia | a primeira recebe `R$ 40,00`, a segunda recebe `R$ 20,00` | RN-003 e RN-004 |
| Despesa exatamente em `R$ 100,00` sem nota fiscal | valor `100.00`, `tem_nota_fiscal=false` | é reembolsável, porque a exigência é para valores acima de `100,00` | RN-005 |
| Despesa de `R$ 100,01` sem nota fiscal | valor `100.01`, `tem_nota_fiscal=false` | é recusada como `nao_reembolsavel` | RN-005 |
| Categoria em maiúsculas | `ALIMENTACAO` | é tratada como `alimentacao` | RN-009 |
| Despesa fora do período | data `2026-04-15` com período `2026-07-01` a `2026-07-31` | é recusada | RN-002 |
| Despesa duplicada | mesma data, fornecedor, valor, categoria e descrição | a segunda ocorrência é recusada | RN-007 |
| Valor negativo | `-45.00` | é ignorada para fins de reembolso | RN-008 |
| Categoria fora da política | `coworking` | é recusada | RN-001 |

## 8. Ordem de aplicação das regras

As regras devem ser aplicadas na seguinte ordem para que o resultado seja determinístico:

1. Normalizar categoria e remover espaços extras.
2. Identificar valores menores ou iguais a zero e ignorá-los.
3. Validar se a despesa está dentro do período de competência.
4. Validar se a categoria é aceitada.
5. Detectar duplicatas e rejeitar a segunda ocorrência.
6. Validar a obrigatoriedade de nota fiscal quando o valor for superior a `R$ 100,00`.
7. Identificar se o dia é de viagem a partir da presença de hospedagem associada.
8. Aplicar o limite diário por categoria, ampliado em 50% quando houver viagem, e calcular o valor reembolsável parcial, quando necessário.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Para o exemplo de entrada fornecido, cada despesa recebe um status explícito de `reembolsado`, `reembolsado_parcialmente` ou `nao_reembolsavel`.
- [ ] O valor reembolsável de cada item é consistente com as regras de limite, nota fiscal, competência e duplicata.
- [ ] A saída inclui, para cada item, pelo menos: `id`, `status`, `valor_original`, `valor_reembolsavel` e `motivo`.
- [ ] A implementação respeita a ordem de aplicação das regras descrita nesta spec.
- [ ] A spec é suficiente para que uma pessoa sem ler o código possa verificar se a decisão de cada despesa está correta.

