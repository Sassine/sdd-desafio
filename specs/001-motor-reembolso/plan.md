# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python 3 | Linguagem simples, ampla adoção e boa produtividade para CLI e testes. | Descartei Go e Node por exigir mais boilerplate para a mesma velocidade de implementação neste desafio. |
| Testes | pytest | Framework leve, sintaxe clara e excelente integração com testes unitários. | Descartei unittest por ser mais verboso para o mesmo objetivo. |
| Parsing/validação | json + validação manual | O formato de entrada é simples e não exige uma biblioteca adicional. | Descartei Pydantic para evitar overhead e manter a solução enxuta. |
| Aritmética monetária | Decimal | Evita erros de ponto flutuante em valores financeiros. | Descartei float para não introduzir imprecisão em centavos. |

## 2. Arquitetura

O fluxo será simples, com uma separação clara entre entrada, regras de negócio e saída.

```text
entrada JSON → carregador → motor de regras → estrutura de saída → arquivo JSON
```

**Fronteiras:** o núcleo de regra de negócio será uma função pura que recebe uma despesa e o estado acumulado do dia, retornando a avaliação da despesa. O carregamento e escrita de arquivos ficam fora desse núcleo para manter a lógica de negócio isolada e mais fácil de testar.

## 3. Modelo de dados

As estruturas internas serão pequenas e explícitas:

- `DespesaInput`: representa os dados recebidos na entrada, incluindo categoria, valor, data, nota fiscal e identificador.
- `DespesaResultado`: representa a decisão final da despesa, contendo `id`, `status`, `valor_original`, `valor_reembolsavel`, `motivo` e `categoria`.
- `Resumo`: agrega os totais de valor original, valor reembolsável e quantidade de itens processados.
- `Processamento`: encapsula a lista de resultados e o resumo final.

## 4. Como a política é representada

A política será representada como constantes e um conjunto pequeno de funções no módulo de regras. Isso mantém as regras centralizadas e fáceis de ajustar se o RH mudar a política. A estrutura será suficientemente simples para que uma futura mudança de limite, critério de nota fiscal ou regra de duplicata não exija refatoração completa.

## 5. Decisões técnicas

### DT-001 — Usar um motor de regras explícito

**Contexto:** a política exige várias regras interdependentes e a chance de regressão é alta.
**Decisão:** implementar um fluxo sequencial de avaliação em função dedicada, com decisões explícitas e motivos por item.
**Alternativa descartada:** implementar tudo inline no CLI ou em um único bloco. Isso seria mais curto no início, mas pioraria a manutenção e a testabilidade.
**Consequência:** torna o código mais legível e facilita a introdução de novas regras no futuro.

### DT-002 — Centralizar os limites em constantes

**Contexto:** os limites e os critérios de negócio podem mudar em versões futuras.
**Decisão:** os limites diários e os valores de regra ficam em constantes nomeadas no módulo de regras.
**Alternativa descartada:** espalhar números diretamente no código de avaliação.
**Consequência:** facilita a leitura e reduz o risco de inconsistência.

### DT-003 — Manter a lógica de saída separada da lógica de negócio

**Contexto:** a entrada e a saída são arquivos JSON, mas a avaliação de regras precisa ser testada isoladamente.
**Decisão:** separar a leitura/escrita de arquivos do núcleo de cálculo.
**Alternativa descartada:** acoplar tudo no mesmo fluxo.
**Consequência:** os testes podem validar a regra sem depender de I/O.

## 6. Estratégia de testes

- **Nível:** testes unitários para o núcleo de regras e testes de integração para a CLI.
- **Cada `RN-NNN` da spec tem teste?** Sim. Cada regra terá ao menos um teste direto, e os casos de borda serão cobertos com testes específicos.
- **Casos de borda da seção 7 da spec:** cada caso será representado por um teste, inclusive duplicata, valor negativo, categoria em caixa alta e despesa fora do período.
- **Nomenclatura:** os testes usarão nomes que refletem a regra e o comportamento esperado, por exemplo `test_despesa_acima_de_100_sem_nota_fiscal_eh_recusada`.

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| Erro de arredondamento em valores monetários | Média | Usar `Decimal` em toda a pipeline e evitar operações com float. |
| Regras aplicadas na ordem errada | Média | Definir explicitamente a ordem de aplicação na implementação e testá-la. |
| Nova regra do envelope no Dia 2 | Alta | Manter o núcleo de regras isolado para ajustar com mínimo impacto. |