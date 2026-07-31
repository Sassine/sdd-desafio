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

### RN-012 — Limite diário de hospedagem

**Regra:** Hospedagem tem limite de R$ 250,00 por diária. Sem um campo estruturado de número de diárias na entrada, cada despesa de hospedagem é avaliada como 1 diária (conforme decisão em AMB-010) e o limite de R$ 250,00 é aplicado à despesa individualmente — sem agregação por dia, diferente de alimentação e transporte urbano.
**Origem:** política do RH, item 3.
**Aceite:** uma despesa de hospedagem de R$ 480,00 deve resultar em R$ 250,00 reembolsável e R$ 230,00 não reembolsável.

### RN-013 — Limites lidos de política externa por centro de custo

**Regra:** Os limites de reembolso deixam de ser constantes no código e passam a ser lidos de um arquivo de política externo (politica-v4.json), que define uma tabela "padrão" e tabelas específicas por centro de custo. Quando o centro de custo do colaborador não está na tabela, aplica-se a tabela "padrão" para todas as categorias. Quando o centro de custo está na tabela mas não define uma categoria específica (ex: CC-ADM não define hospedagem nem representacao), aplica-se o limite "padrão" apenas para essa categoria ausente — o restante das categorias definidas no centro de custo continua usando os valores específicos dele.
**Origem:** comunicado do RH, item A.
**Aceite:** um colaborador do CC-ADM com uma despesa de hospedagem deve usar o limite padrão de R$250,00/diária (já que CC-ADM não define hospedagem), mas uma despesa de alimentação do mesmo colaborador usa R$45,00/dia (valor específico do CC-ADM).

### RN-014 — Categoria "representacao"

**Regra:** A categoria representacao passa a ser válida para reembolso, mas apenas nos centros de custo cuja tabela de política a define explicitamente. Em centros de custo sem essa categoria na tabela (inclusive na política padrão), despesas de representacao são recusadas como categoria fora da política (mesmo comportamento de RN-001).
**Origem:** comunicado do RH, item A.
**Aceite:** uma despesa de representacao do CC-COMERCIAL é avaliada contra o limite de R$300,00/dia; a mesma categoria em um centro de custo sem essa entrada é recusada com motivo categoria_nao_politica.

### RN-015 — Hospedagem não reembolsável em centro de custo específico

**Regra:** Quando a tabela de política de um centro de custo define limite 0,00 para uma categoria (caso de CC-ENG-PLATAFORMA e hospedagem), toda despesa dessa categoria nesse centro de custo é recusada integralmente, com motivo próprio — não tratada como "limite muito baixo que gera reembolso parcial de zero".
**Origem:** comunicado do RH, item A ("CC-ENG-PLATAFORMA não reembolsa hospedagem de forma alguma").
**Aceite:** uma despesa de hospedagem de qualquer valor no CC-ENG-PLATAFORMA deve ter status recusada e motivo categoria_nao_reembolsavel_no_centro_custo, não parcialmente_reembolsada com valor zero.

### RN-016 — Conversão de moeda estrangeira

**Regra:** Despesas podem trazer um campo moeda (código ISO 4217). Quando ausente, assume-se BRL. Despesas em moeda estrangeira são convertidas para BRL usando a taxa de câmbio da DATA DA DESPESA (não a taxa do dia da execução do motor), lida de cambio.json, antes de aplicar qualquer limite ou regra de valor (nota fiscal, limite diário, etc.). Os limites da política são sempre expressos em BRL.
**Origem:** comunicado do RH, item B.
**Aceite:** uma despesa de EUR 22,00 na data 2026-07-14 (taxa EUR=5,93) deve ser convertida para R$130,46 antes de ser comparada a qualquer limite.

### RN-017 — Taxa de câmbio ausente na data exata

**Regra:** Quando não há cotação publicada para a data exata da despesa (ex: finais de semana, feriados bancários), utiliza-se a cotação do último dia útil anterior disponível em cambio.json.
**Origem:** interpretação definida por esta spec (o comunicado do RH menciona a lacuna sem resolvê-la — ver AMB-016).
**Aceite:** uma despesa datada em 2026-07-18 (sábado, sem cotação) em EUR deve usar a taxa de 2026-07-17 (EUR=5,96), o último dia útil anterior disponível.

### RN-018 — Câmbio indisponível para a moeda da despesa

**Regra:** Quando não há nenhuma cotação disponível para a moeda da despesa em cambio.json (nem na data exata, nem em dia útil anterior), a despesa é recusada, não avaliada com taxa presumida.
**Origem:** interpretação definida por esta spec (o comunicado do RH não cobre moeda totalmente ausente do arquivo de câmbio, apenas data ausente).
**Aceite:** uma despesa em GBP, moeda não presente em nenhuma entrada de cambio.json, deve ser recusada com motivo cambio_indisponivel.

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
**Regra afetada:** RN-012

### AMB-011 — Precisão decimal do valor da despesa

**Texto original do RH:** não especifica precisão monetária.
**O que não está claro:** valores com mais de duas casas decimais (ex: 33.333) não têm tratamento definido — a política assume implicitamente que dinheiro tem no máximo 2 casas.
**Decisão:** valores são arredondados para 2 casas decimais usando ROUND_HALF_UP durante a normalização.
**Justificativa:** dinheiro não tem subcentavos na prática; ROUND_HALF_UP é a convenção mais comum e previsível para arredondamento comercial.
**Regra afetada:** RN-011

### AMB-012 — Critério de prioridade quando múltiplas despesas excedem o limite do dia

**Texto original do RH:** não define prioridade entre despesas que excedem o limite diário.
**O que não está claro:** quando duas ou mais despesas do mesmo dia ultrapassam o limite, como decidir qual parte do limite é consumida primeiro?
**Decisão:** a ordem de aparição no array de entrada determina a prioridade de consumo do limite, já que não há campo de horário.
**Justificativa:** isso torna o comportamento determinístico e evita depender de um critério implícito ou não documentado.
**Regra afetada:** RN-003

### AMB-013 — Valor zero é ajuste ou despesa normal?

**Texto original do RH:** não trata de valores zero.
**O que não está claro:** um valor igual a zero deve ser tratado como ajuste, como despesa normal ou como caso indefinido?
**Decisão:** valor zero não é tratado como ajuste; apenas valores negativos acionam RN-008.
**Justificativa:** a regra explícita da spec fala em valores negativos como ajustes, e zero não é negativo.
**Regra afetada:** RN-008

### AMB-014 — Herança de política padrão por categoria ou por centro de custo inteiro?

**Texto original do RH:** "Alguns centros de custo não têm entrada na tabela. Nesse caso, aplica-se a política padrão."
**O que não está claro:** o texto só cobre centro de custo totalmente ausente da tabela. Não diz o que fazer quando o centro de custo ESTÁ na tabela, mas uma categoria específica dele não está definida (caso do CC-ADM, que não define hospedagem nem representacao).
**Decisão:** a herança da política padrão é avaliada por categoria, não por centro de custo inteiro. Um centro de custo presente na tabela usa seus valores específicos onde definidos, e cai no padrão categoria a categoria, onde a tabela dele for omissa.
**Justificativa:** essa é a leitura mais útil operacionalmente — caso contrário, um centro de custo que define só 2 das 4 categorias ficaria sem nenhuma regra para as outras duas, o que pareceria uma falha de dados, não uma decisão de negócio.
**Regra afetada:** RN-013

### AMB-015 — Limite de representação: por despesa ou somado por dia?

**Texto original do RH:** politica-v4.json define representacao com "periodicidade": "dia", igual às demais categorias.
**O que não está claro:** o comunicado não repete explicitamente a mesma pergunta já resolvida em AMB-001 (por despesa vs. soma do dia), mas o campo periodicidade sugere que a mesma lógica se aplica.
**Decisão:** representacao segue a mesma regra de AMB-001 — soma de todas as despesas dessa categoria no mesmo dia é comparada ao limite diário.
**Justificativa:** consistência com o tratamento já dado a alimentação e transporte_urbano, que usam a mesma estrutura periodicidade: dia na política.
**Regra afetada:** RN-014

### AMB-016 — Taxa de câmbio ausente na data exata da despesa

**Texto original do RH:** "A conversão usa a taxa da data da despesa, não a taxa de hoje." O arquivo cambio.json observa que "cotações publicadas apenas em dias úteis bancários."
**O que não está claro:** o comunicado não diz o que fazer quando a data da despesa cai em um dia sem cotação publicada (ex: fim de semana) — e o próprio dataset de teste contém esse caso (despesa e-004, datada em um sábado).
**Decisão:** usar a cotação do último dia útil anterior disponível no arquivo.
**Justificativa:** é a convenção mais comum em conversão cambial para despesas de fim de semana, e evita rejeitar despesas legítimas só por caírem em dia sem pregão.
**Regra afetada:** RN-017

### AMB-017 — Moeda sem nenhuma cotação disponível no arquivo de câmbio

**Texto original do RH:** o comunicado define conversão via cambio.json, mas não prevê o caso de a moeda simplesmente não constar no arquivo.
**O que não está claro:** despesa e-006 do despesas-envelope.json está em GBP, moeda que não aparece em nenhuma data de cambio.json — diferente da lacuna de data (AMB-016), aqui não há nenhuma taxa de referência possível.
**Decisão:** a despesa é recusada com motivo cambio_indisponivel, sem tentar aplicar taxa presumida ou tratar como BRL.
**Justificativa:** aplicar taxa 1:1 ou ignorar a conversão mascararia um problema real de dados; recusar explicitamente é mais seguro e auditável que inventar um câmbio.
**Regra afetada:** RN-018

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Categoria desconhecida | coworking | status não reembolsável | RN-001 |
| Limite diário excedido | alimentação com dois itens no mesmo dia | primeiro valor até o limite; excedente não reembolsável | RN-002, RN-003 |
| Limite de hospedagem | despesa de hospedagem de 480,00 | status parcialmente reembolsada com R$ 250,00 reembolsável e R$ 230,00 não reembolsável | RN-012 |
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
