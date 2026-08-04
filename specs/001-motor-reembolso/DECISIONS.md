# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-003 — Política por centro de custo e fallback padrão · 2026-08-03

**Gatilho:** envelope lacrado com mudança da política de reembolso v4.

**O que mudou na spec:** a spec passou a definir que os limites são determinados pelo centro de custo do colaborador e lidos de uma política externa (`politica-v4.json`); quando o centro não existe, aplica-se a política padrão (RN-010). A regra também passou a tratar a categoria `representacao` para `CC-COMERCIAL` e a não reembolso de `hospedagem` para `CC-ENG-PLATAFORMA` (RN-011).

**Por quê:** a política v4 deixou de ser única para toda a empresa e passou a variar por centro de custo.

**O que isso invalidou:** a hipótese anterior de limites globais e constantes no código; as tarefas que assumiam um único conjunto de limites passaram a precisar de reavaliação.

**Tasks afetadas:** T-012 e T-013 foram criadas para cobrir a nova política externa e as regras especiais por centro de custo.

**Custo:** a mudança afeta a camada de regras de negócio e a futura implementação, mas não exige reescrever o fluxo completo de entrada e saída.

---

## D-004 — Conversão cambial pela data da despesa · 2026-08-03

**Gatilho:** envelope lacrado com a introdução de despesas internacionais e câmbio externo.

**O que mudou na spec:** a spec passou a exigir conversão de despesas em moeda estrangeira para BRL usando a taxa da data da despesa, lida de `cambio.json` (RN-012). Também foi definida a decisão de fallback quando não houver taxa disponível para a data.

**Por quê:** a política v4 passou a tratar despesas internacionais e a conversão precisa ser feita antes da comparação com os limites.

**O que isso invalidou:** a premissa anterior de que todas as despesas estariam em BRL e poderiam ser comparadas diretamente aos limites.

**Tasks afetadas:** T-014 foi criada para cobrir a conversão cambial e o fallback de taxa ausente.

**Custo:** alterou a regra de avaliação monetária e exige expansão da camada de cálculo para aceitar moedas diferentes de BRL.
