# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-001 — Corrige ID de regra trocado no exemplo ilustrativo da §4 · `2026-07-30`

**Gatilho:** ao implementar T-012 (RN-007, teto por categoria) na tarde do Dia 1,
o exemplo de saída da `spec.md` §4 rotulava as duas decisões de teto
(`d-001` parcial, `d-002` aprovada) com `regras_aplicadas: ["RN-006"]`. RN-006
é a regra de nota fiscal (§5); a decisão ali descrita é claramente de teto —
RN-007. É inconsistência interna da spec, não ambiguidade de negócio: o
catálogo de regras (§5) e o exemplo (§4) discordavam entre si dentro do mesmo
arquivo.

**O que mudou na spec:** exemplo de saída em `spec.md` §4 — `regras_aplicadas`
de `d-001` e `d-002` passou de `["RN-006"]` para `["RN-007"]`, coerente com a
definição de RN-007 e com a ordem de aplicação da §8. Versão do documento
avançou de 1.0 para 1.1.

**Por quê:** o número de regra errado no único exemplo de saída da spec teria
sido copiado para o código e para os testes se não fosse corrigido antes —
exatamente o tipo de erro que a rastreabilidade regra→teste deveria expor, não
esconder.

**O que isso invalidou:** nada em código ou teste, pois a implementação de
T-012 ainda não existia. Nenhum critério de aceite da §9 cita `regras_aplicadas`
literalmente, então nenhum outro trecho da spec dependia do valor errado.

**Tasks afetadas:** nenhuma tarefa precisou ser refeita; T-012 (RN-007) foi
implementada já com o ID correto.

**Custo:** 2 arquivos (`spec.md`, este `DECISIONS.md`), sem retrabalho de código.
