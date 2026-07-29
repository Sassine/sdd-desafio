# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** rascunho · **Última alteração:** 2026-07-29

> Esta especificação descreve o QUE e o PORQUÊ. Ela não define linguagem, biblioteca, estrutura de pasta nem implementação técnica.

---

## 1. Problema

O processo atual de reembolso de despesas é manual, sujeito a erro humano e lento. A empresa precisa de um motor que leia um conjunto de despesas, aplique a política de reembolso e devolva um resultado determinístico, com a decisão de cada item e a justificativa correspondente.

## 2. Objetivo

Criar um motor de cálculo de reembolso que, a partir de um arquivo JSON de entrada, produza um resultado JSON com o valor reembolsável de cada despesa, o valor não reembolsável e o motivo de cada decisão.

## 3. Fora de escopo

- Não será implementado fluxo de aprovação ou aprovação humana.
- Não será implementado persistência de dados ou histórico entre execuções.
- Não será implementado suporte a múltiplos colaboradores em uma mesma execução.
- Não será implementado integração com sistemas externos de ERP, RH ou contabilidade.
- Não será implementado cálculo de imposto ou tributação sobre as despesas.

## 4. Entrada e saída

**Entrada:** conforme o formato de [exemplos/despesas-exemplo.json](../../exemplos/despesas-exemplo.json).

Campos principais da entrada:

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| colaborador | objeto | Dados do colaborador | sim |
| periodo | objeto | Período de competência | sim |
| despesas | array | Lista de despesas a avaliar | sim |

**Saída:** o sistema deve devolver um JSON com a estrutura abaixo.

| Campo | Tipo | Significado |
|---|---|---|
| colaborador | objeto | Dados do colaborador recebidos na entrada |
| periodo | objeto | Período recebido na entrada |
| resumo | objeto | Totais consolidados do processamento |
| despesas | array | Resultado individual de cada despesa |

Exemplo de estrutura de saída:

```json
{
  "colaborador": {
    "id": "c-0417",
    "nome": "Marina Volpi"
  },
  "periodo": {
    "competencia": "2026-07"
  },
  "resumo": {
    "valor_total_despesas": 0,
    "valor_reembolsavel": 0,
    "valor_nao_reembolsavel": 0,
    "quantidade_despesas": 0,
    "quantidade_reembolsadas": 0,
    "quantidade_parcialmente_reembolsadas": 0,
    "quantidade_recusadas": 0,
    "quantidade_ignorar": 0
  },
  "despesas": [
    {
      "id": "d-001",
      "categoria": "alimentacao",
      "status": "parcialmente_reembolsada",
      "valor_original": 72.5,
      "valor_reembolsavel": 60.0,
      "valor_nao_reembolsavel": 12.5,
      "motivo": "limite_diario_excedido",
      "justificativa": "A despesa excedeu o limite diário permitido para a categoria."
    }
  ]
}
```

## 5. Regras de negócio

Cada regra abaixo recebe um identificador e será referenciada pelas tasks.

### RN-001 — Categorias aceitas

**Regra:** Somente as categorias alimentacao, transporte_urbano e hospedagem são elegíveis para reembolso. Outras categorias são não reembolsáveis.
**Origem:** política do RH, item 9.
**Aceite:** uma despesa com categoria coworking deve receber status não reembolsável e motivo categoria_nao_politica.

### RN-002 — Limite diário por categoria

**Regra:** Para alimentação e transporte urbano, o limite diário é de R$ 60,00 e R$ 80,00 respectivamente. O limite é aplicado ao somatório das despesas da mesma categoria no mesmo dia.
**Origem:** política do RH, itens 1 e 2.
**Aceite:** duas despesas de alimentação no mesmo dia somam até R$ 60,00 de reembolso; o excedente é não reembolsável.

### RN-003 — Reembolso parcial

**Regra:** Quando uma despesa exceder o limite aplicável, o valor até o limite é reembolsável e o excedente é não reembolsável. A despesa não é recusada integralmente; ela entra como parcialmente reembolsada.
**Origem:** política do RH, item 4.
**Aceite:** uma despesa de R$ 100,00 em alimentação no mesmo dia em que já houve R$ 60,00 de reembolso deve resultar em R$ 60,00 reembolsável e R$ 40,00 não reembolsável.

### RN-004 — Nota fiscal obrigatória acima de R$ 100,00

**Regra:** Despesas com valor superior a R$ 100,00 precisam de nota fiscal para serem reembolsáveis. Despesas de exatamente R$ 100,00 não exigem nota fiscal.
**Origem:** política do RH, item 5.
**Aceite:** uma despesa de R$ 100,01 sem nota fiscal deve ser recusada com motivo nota_fiscal_obrigatoria.

### RN-005 — Limites ampliados em viagem

**Regra:** A condição de viagem é inferida de forma heurística apenas quando há uma despesa de categoria hospedagem no mesmo dia da despesa analisada. Quando isso ocorre, os limites de alimentação e transporte urbano do dia passam a ser R$ 90,00 e R$ 120,00, respectivamente. Despesas de outras categorias não são usadas como sinal de viagem.
**Origem:** política do RH, item 6.
**Aceite:** uma despesa de alimentação em um dia com uma despesa de hospedagem deve ter limite de R$ 90,00 em vez de R$ 60,00, enquanto um dia sem hospedagem segue o limite padrão.

### RN-006 — Período de competência

**Regra:** Despesas com data fora do intervalo definido em periodo.inicio e periodo.fim são ignoradas e não entram no cálculo de reembolso.
**Origem:** política do RH, item 7.
**Aceite:** uma despesa em abril para um período de competência de julho deve aparecer com status ignorada e motivo fora_do_periodo.

### RN-007 — Duplicatas

**Regra:** Uma despesa é considerada duplicata quando, após normalização de categoria e valores, ela repete os mesmos atributos principais de outra despesa anterior: data, categoria, fornecedor, descrição e valor. A primeira ocorrência é mantida; as demais são recusadas como duplicatas.
**Origem:** política do RH, item 8.
**Aceite:** duas despesas idênticas no mesmo dia e com o mesmo fornecedor devem resultar em uma reembolsada e outra recusada por duplicata.

### RN-008 — Valores negativos

**Regra:** Valores negativos são tratados como ajustes e não são reembolsados. Eles aparecem no resultado como itens ignorados com motivo ajuste.
**Origem:** interpretação definida por esta spec.
**Aceite:** uma despesa com valor -45,00 deve ser registrada como ignorada e sem valor reembolsável.

### RN-009 — Normalização de categoria e datas

**Regra:** Categorias devem ser tratadas de forma insensível a maiúsculas/minúsculas. Datas devem seguir o formato ISO YYYY-MM-DD.
**Origem:** interpretação definida por esta spec.
**Aceite:** uma despesa com categoria ALIMENTACAO deve ser tratada como alimentacao.

### RN-010 — Justificativa obrigatória

**Regra:** Cada despesa do resultado deve trazer uma justificativa textual curta e compreensível para o usuário final.
**Origem:** necessidade de rastreabilidade operacional.
**Aceite:** toda despesa do resultado deve conter o campo justificativa.

### RN-011 — Precisão de valores monetários

**Regra:** Valores de despesa com mais de duas casas decimais são arredondados para duas casas (ROUND_HALF_UP) durante a normalização, antes de qualquer cálculo de limite ou reembolso.
**Origem:** interpretação definida por esta spec (a política do RH não prevê o caso).
**Aceite:** uma despesa com valor 33.333 deve ser normalizada para 33.33.

---

## 6. Ambiguidades identificadas e decisões

### AMB-001 — Limite diário: por despesa ou por dia?

**Texto original do RH:** “Alimentação tem limite de R$ 60 por dia”.
**O que não está claro:** o limite pode ser interpretado como por item individual ou como somatório do dia.
**Decisão:** o sistema aplica o limite ao somatório das despesas da mesma categoria no mesmo dia.
**Justificativa:** isso evita que duas despesas pequenas no mesmo dia consumam o limite de forma injusta e torna a regra previsível.
**Regra afetada:** RN-002, RN-003

### AMB-002 — Reembolso parcial: recusar tudo ou pagar até o limite?

**Texto original do RH:** “Despesas acima do limite são reembolsadas parcialmente”.
**O que não está claro:** a política não diz se o item inteiro é recusado ou se a parte acima do limite é cortada.
**Decisão:** o valor até o limite é reembolsável e o excedente é não reembolsável.
**Justificativa:** a política fala em reembolso parcial, não em rejeição integral.
**Regra afetada:** RN-003

### AMB-003 — Nota fiscal: exatamente R$ 100,00 entra ou não?

**Texto original do RH:** “Nota fiscal é obrigatória acima de R$ 100”.
**O que não está claro:** o limiar é estritamente maior que 100 ou inclui o valor exato de 100.
**Decisão:** valores exatamente iguais a R$ 100,00 não exigem nota fiscal; valores superiores a R$ 100,00 exigem.
**Justificativa:** a redação “acima de” sugere um limiar estrito.
**Regra afetada:** RN-004

### AMB-004 — Como identificar “em viagem” sem campo explícito?

**Texto original do RH:** “Colaborador em viagem tem limites ampliados em 50%”.
**O que não está claro:** não existe campo na entrada para indicar isso diretamente.
**Decisão:** o sistema considera o colaborador em viagem apenas quando há uma despesa de categoria hospedagem no mesmo dia da despesa analisada. Despesas de outras categorias não são usadas como sinal de viagem, mesmo quando contêm termos como hotel ou aeroporto. Se não houver hospedagem no dia, a regra não cria uma condição de viagem.
**Justificativa:** essa abordagem é mais precisa que assumir viagem para todo o período e evita falsos positivos causados por palavras isoladas em outras categorias.
**Regra afetada:** RN-005

### AMB-005 — O que conta como duplicata?

**Texto original do RH:** “Duplicatas devem ser tratadas”.
**O que não está claro:** a política não define se duplicata é apenas valor igual ou também mesmo fornecedor/descrição.
**Decisão:** duplicata é a repetição de data, categoria, fornecedor, descrição e valor.
**Justificativa:** isso evita tratar como duplicata despesas parecidas, mas diferentes.
**Regra afetada:** RN-007

### AMB-006 — Despesas fora do período de competência

**Texto original do RH:** “Despesas devem ser lançadas dentro do período de competência”.
**O que não está claro:** a política não diz se essas despesas devem ser recusadas ou ignoradas.
**Decisão:** despesas fora do período são ignoradas e não entram no cálculo de reembolso.
**Justificativa:** isso preserva a integridade do período e evita confundir lançamento tardio com regra de reembolso.
**Regra afetada:** RN-006

### AMB-007 — Categoria fora da política

**Texto original do RH:** “Categorias fora da política não são reembolsáveis”.
**O que não está claro:** a política não define se uma categoria desconhecida deve ser recusada imediatamente ou avaliada por outra regra.
**Decisão:** categorias fora da política são rejeitadas como não reembolsáveis sem tentar aplicar limites ou nota fiscal.
**Justificativa:** a categoria não é elegível e não há base para calcular reembolso.
**Regra afetada:** RN-001

### AMB-008 — Formato de categoria

**Texto original do RH:** não especifica normalização de categoria.
**O que não está claro:** categorias com letras maiúsculas devem ser tratadas igual a minúsculas?
**Decisão:** categorias são normalizadas para minúsculas antes da avaliação.
**Justificativa:** isso reduz erros de cadastro e torna a regra mais robusta.
**Regra afetada:** RN-009

### AMB-009 — Valores negativos

**Texto original do RH:** não trata de estornos ou ajustes.
**O que não está claro:** um valor negativo deve ser reembolsado ou tratado como erro?
**Decisão:** valores negativos são tratados como ajustes e não geram reembolso.
**Justificativa:** um estorno não representa uma despesa nova e não deve ser reembolsado.
**Regra afetada:** RN-008

### AMB-010 — Hospedagem: como calcular o limite por diária?

**Texto original do RH:** “Hospedagem tem limite de R$ 250 por diária”.
**O que não está claro:** a entrada traz um valor total, mas não informa diretamente a quantidade de noites.
**Decisão:** a quantidade de diárias é inferida quando a descrição menciona explicitamente “diarias” ou “noites”; se não houver indicação, considera-se 1 diária. O limite é aplicado à quantidade de diárias inferida para a despesa, e não a todo o período ou a outros dias.
**Justificativa:** isso deixa a regra operacional sem exigir um novo campo de entrada e limita o efeito do cálculo ao contexto da despesa.
**Regra afetada:** RN-005, RN-002

### AMB-011 — Precisão decimal do valor da despesa

**Texto original do RH:** não especifica precisão monetária.
**O que não está claro:** valores com mais de duas casas decimais (ex: 33.333) não têm tratamento definido — a política assume implicitamente que dinheiro tem no máximo 2 casas.
**Decisão:** valores são arredondados para 2 casas decimais usando ROUND_HALF_UP durante a normalização.
**Justificativa:** dinheiro não tem subcentavos na prática; ROUND_HALF_UP é a convenção mais comum e previsível para arredondamento comercial.
**Regra afetada:** RN-011

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Categoria desconhecida | coworking | status não reembolsável | RN-001 |
| Limite diário excedido | alimentação com dois itens no mesmo dia | primeiro valor até o limite; excedente não reembolsável | RN-002, RN-003 |
| Valor acima de 100 sem nota fiscal | 100,01 sem nota | status recusada | RN-004 |
| Valor exatamente 100 sem nota fiscal | 100,00 sem nota | reembolsável se não houver outro impedimento | RN-004 |
| Despesa fora do período | data em abril | status ignorada | RN-006 |
| Duplicata | mesma data, categoria, fornecedor, descrição e valor | segunda ocorrência recusada | RN-007 |
| Estorno | valor negativo | status ignorada | RN-008 |
| Categoria em maiúsculas | ALIMENTACAO | tratada como alimentacao | RN-009 |

## 8. Ordem de aplicação das regras

A ordem abaixo define o resultado quando mais de uma regra se aplica à mesma despesa:

1. Normalização de categoria e data.
2. Verificação de período de competência.
3. Identificação de duplicatas.
4. Tratamento de valores negativos como ajustes.
5. Validação de categoria aceita.
6. Aplicação de regra de nota fiscal quando o valor for superior a R$ 100,00.
7. Cálculo do limite diário, considerando viagem quando houver evidência explícita para o mesmo dia da despesa.
8. Geração da justificativa final.

> Nota de implementação: a ordem de desenvolvimento deve seguir esta ordem de execução. Implementar a saída ou o cálculo de limites antes de validar o período ou a categoria pode gerar resultados inconsistentes e dificultar a rastreabilidade entre spec e código.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] O JSON de saída é produzido a partir do JSON de entrada sem intervenção manual.
- [ ] Cada despesa recebe um status claro: reembolsada, parcialmente reembolsada, recusada ou ignorada.
- [ ] O valor reembolsável e o valor não reembolsável são calculados de forma consistente com as regras acima.
- [ ] As ambiguidades documentadas nesta spec são respeitadas sem depender do chat para interpretação.
- [ ] O output inclui justificativa para cada despesa.

## 10. O que fica em aberto

Não há lacunas críticas para a execução inicial deste projeto. A única dependência restante é a possibilidade de evoluir a inferência de viagem caso a política mude no futuro.
