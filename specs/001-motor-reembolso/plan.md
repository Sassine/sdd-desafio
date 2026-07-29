# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Este arquivo descreve o COMO. Ele pode falar de linguagem, biblioteca e arquitetura, mas não pode introduzir nova regra de negócio.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python 3 | É uma boa escolha para CLI simples, testes rápidos e leitura clara das regras de negócio | Descartei Node.js para evitar mais boilerplate em um projeto com regras explícitas e muita lógica de domínio |
| Testes | pytest | Gera testes legíveis e integração simples com CI | Descartei unittest para manter a suíte mais expressiva e enxuta |
| Parsing/validação | json + validação manual | O formato da entrada é simples e não exige um framework pesado | Descartei Pydantic para não adicionar complexidade desnecessária ao escopo |
| Aritmética monetária | decimal.Decimal | Evita problemas de ponto flutuante em valores financeiros | Descartei float por ser inadequado para operações de dinheiro |

## 2. Arquitetura

O fluxo será simples e com fronteira clara entre entrada, regras e saída.

```text
entrada JSON → normalização → avaliação de regras → montagem do JSON de saída
```

**Blocos principais:**

- **Leitura e normalização:** converte entrada em estruturas internas, padroniza categorias e datas, identifica contexto de viagem.
- **Motor de regras:** aplica as regras da spec em uma ordem definida, produzindo um resultado por despesa.
- **Montagem de saída:** consolida os resultados em um JSON final com resumo e justificativas.

**Fronteiras:** a camada de regras de negócio deve ser independente da CLI e do formato de entrada/saída. Isso facilita futuras mudanças na spec sem reescrever todo o sistema.

## 3. Modelo de dados

A estrutura interna pode ser organizada em torno de duas entidades principais:

- **Despesa:** contém id, data, categoria, valor original, nota fiscal, descrição e fornecedor.
- **ResultadoDespesa:** contém a despesa original, status, valor reembolsável, valor não reembolsável, motivo e justificativa.

A execução também terá um contexto que carrega:

- período de competência;
- presença de evidência de viagem;
- limite diário efetivo por categoria;
- lista de despesas já processadas para detectar duplicatas.

> Nota de escopo: a função de leitura de despesas da T-001 retorna apenas a lista de despesas do JSON de entrada. Os dados de colaborador e período serão capturados na T-010, na etapa de montagem da saída, sem expandir o escopo da leitura inicial.

## 4. Como a política é representada

A política será representada como constantes e regras explícitas no código, em um módulo dedicado de regras. Isso reduz o risco de espalhar a lógica por várias funções e facilita mudanças futuras.

A estrutura sugerida é:

- constantes de limite por categoria;
- função para calcular limite efetivo com base em viagem;
- função para aplicar regras de nota fiscal, duplicata, período e categoria.

## 5. Decisões técnicas

### DT-001 — Uso de Decimal para valores monetários

**Contexto:** a política trabalha com dinheiro e o projeto tem risco alto de erro por arredondamento.
**Decisão:** usar Decimal para todos os cálculos financeiros.
**Alternativa descartada:** usar float.
**Consequência:** o código fica mais robusto, embora um pouco mais verboso em alguns pontos.

### DT-002 — Separação entre parsing e avaliação

**Contexto:** a entrada pode mudar de formato no futuro e a lógica de negócio não deve depender diretamente do JSON bruto.
**Decisão:** primeiro converter a entrada para estruturas internas e depois aplicar as regras.
**Alternativa descartada:** aplicar a lógica diretamente sobre o JSON.
**Consequência:** o núcleo de regras fica mais limpo e mais fácil de testar.

### DT-003 — CLI simples sobre módulo de regras

**Contexto:** a interface do desafio é uma CLI, mas o valor real do projeto está na lógica de negócio.
**Decisão:** implementar a CLI como camada fina sobre o motor de regras.
**Alternativa descartada:** acoplar toda a lógica à execução do terminal.
**Consequência:** a lógica pode ser testada de forma independente da interface.

## 6. Estratégia de testes

- **Nível:** testes unitários para cada regra e testes de integração para o fluxo completo da CLI.
- **Cada RN-NNN da spec tem teste?** Sim. Cada regra terá pelo menos um teste associado.
- **Casos de borda da seção 7 da spec:** todos serão cobertos com testes explícitos.
- **Nomenclatura:** os nomes dos testes devem refletir a regra de negócio, por exemplo: test_reembolso_parcial_excede_limite_diario.

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| Inferência de viagem ficar ambígua | média | manter a regra simples e documentada na spec, evitando sofisticar sem necessidade |
| Regras mudarem com frequência | média | manter o motor de regras isolado e com testes cobrindo cada regra |
| Erros de arredondamento | baixa | usar Decimal e testes de casos com centavos |

## 8. Nota de implementação

A ordem de desenvolvimento deve seguir a ordem de execução da seção 8 da spec. Em outras palavras: primeiro normalização, depois período, duplicatas, ajustes, categoria, nota fiscal, limites e, por fim, montagem da saída. Isso evita aplicar uma regra antes de sua dependência e mantém a implementação alinhada com a lógica de negócio declarada.
