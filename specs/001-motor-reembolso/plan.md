# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | | | |
| Testes | | | |
| Parsing/validação | | | |
| Aritmética monetária | | | |

<A linha de aritmética monetária não é decoração. Ponto flutuante em dinheiro é
a fonte de bug mais previsível deste projeto.>

## 2. Arquitetura

<Diagrama em blocos ou lista. Quais são as peças, o que cada uma faz, como
conversam. Uma tela, não uma tese.>

```
entrada JSON → <...> → <...> → saída JSON
```

**Fronteiras:** <o que é núcleo de regra de negócio puro e o que é I/O. Onde
essa linha está desenhada determina o quanto o sistema vai resistir a mudança
de requisito.>

## 3. Modelo de dados

<Estruturas internas. Como uma despesa é representada, como um resultado de
avaliação é representado, o que carrega a justificativa.>

## 4. Como a política é representada

<Os limites vivem onde? Constantes no código, arquivo de configuração, tabela?
Esta decisão é a que mais barato ou mais caro vai custar se a política mudar.>

## 5. Decisões técnicas

### DT-001 — <decisão>

**Contexto:** <o que forçou a escolha>
**Decisão:** <o que foi decidido>
**Alternativa descartada:** <e por quê>
**Consequência:** <o que isso torna fácil e o que torna difícil>

### DT-002 — ...

## 6. Estratégia de testes

- **Nível:** <unitário, integração, ponta a ponta — e a proporção entre eles>
- **Cada `RN-NNN` da spec tem teste?** <como você garante isso>
- **Casos de borda da seção 7 da spec:** <cobertos como>
- **Nomenclatura:** <como o nome do teste remete ao requisito — isso é o que
  fecha a rastreabilidade na correção>

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| | | |
