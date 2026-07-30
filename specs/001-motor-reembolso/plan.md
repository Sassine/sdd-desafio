# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python 3.11+ | Domínio maior; `decimal` e `json` na biblioteca padrão cobrem todo o problema | Go — compilaria num binário só, mas o ganho não paga a menor fluência sob prazo de 2 dias |
| Testes | `pytest` | Parametrização (`@pytest.mark.parametrize`) mapeia direto na tabela de casos de borda da spec §7 | `unittest` — verboso demais para uma tabela de 18 casos |
| Parsing/validação | `json` da stdlib + validação manual explícita | Zero dependência; a spec exige rejeitar entrada inválida com mensagem, e um validador escrito à mão diz exatamente qual campo faltou | `pydantic` — resolveria a validação, mas adiciona dependência e esconde a mensagem de erro atrás de um formato que eu não controlo |
| Aritmética monetária | `decimal.Decimal`, com `json.load(parse_float=Decimal)` | Único jeito de `33.333` da entrada nunca virar binário flutuante; RN-010 exige arredondamento controlado (`ROUND_HALF_UP`) | `float` — quebraria a RN-010 de forma silenciosa · centavos em `int` — correto, mas obrigaria a converter na fronteira e a spec fala em reais |
| CLI | `argparse` da stdlib | O contrato é um subcomando e duas flags; não justifica dependência | `typer`/`click` — ergonomia melhor, irrelevante para uma CLI de um comando |

## 2. Arquitetura

```
arquivo JSON de entrada
   ↓  carregador          (I/O)   lê, valida presença de campos, converte para Decimal
   ↓  Solicitacao                 estrutura imutável: colaborador, período, despesas
   ↓  motor                (puro)  determina viagem, aplica os 8 passos da spec §8
   ↓  Resultado                    lista de pareceres + resumo
   ↓  serializador        (I/O)   formata Decimal como texto de 2 casas, escreve JSON
arquivo JSON de saída
```

**Fronteiras.** O `motor` não conhece arquivo, `argparse`, `json` nem caminho de
disco: recebe uma `Solicitacao` e devolve um `Resultado`. Toda a I/O vive no
carregador, no serializador e na CLI. Essa linha é o que permite testar as dez
regras de negócio sem tocar em disco — e é o que decide se a mudança de
requisito do Dia 2 vai ser cirúrgica ou não.

```
src/
  cli.py                  argparse, orquestra carregador → motor → serializador
  io/carregador.py        arquivo → Solicitacao (+ erros de validação)
  io/serializador.py      Resultado → arquivo
  motor/modelo.py         Despesa, Solicitacao, Parecer, Resultado, Status
  motor/politica.py       os limites, isolados (ver §4)
  motor/regras.py         uma função por RN, na ordem da spec §8
  motor/calculadora.py    percorre as despesas, monta o Resultado
tests/
```

## 3. Modelo de dados

Todas as estruturas são `@dataclass(frozen=True)` — nenhuma regra muda uma
despesa no lugar; cada passo devolve um valor novo.

| Estrutura | Campos | Observação |
|---|---|---|
| `Despesa` | `id, data (date), categoria (str normalizada), descricao, fornecedor, valor (Decimal), tem_nota_fiscal (bool)` | `valor` já arredondado na leitura (RN-010) |
| `Solicitacao` | `colaborador (dict), competencia (str), inicio, fim, despesas (tuple[Despesa])` | Imutável; ordem da entrada preservada, que é o que a RN-004 usa para eleger a primeira ocorrência |
| `Contexto` | `competencia, datas_em_viagem (frozenset[date])` | Calculado uma vez antes do laço; encapsula a RN-009 |
| `Parecer` | `despesa, valor_reembolsavel (Decimal), status (Status), regras_aplicadas (tuple[str]), justificativa (str)` | `valor_glosado` é derivado, não armazenado |
| `Status` | enum: `APROVADA, PARCIAL, RECUSADA, ESTORNO` | Serializado em minúsculas |
| `Resultado` | `solicitacao, pareceres (tuple[Parecer])` | Os totais do resumo são propriedades calculadas, nunca campos — não há como divergirem dos itens |

`regras_aplicadas` carrega os IDs `RN-00X` literais. É o que fecha a
rastreabilidade da spec até a saída em execução: dá para pegar um item do JSON
de resultado e chegar na regra que o produziu sem ler código.

## 4. Como a política é representada

Um único módulo `motor/politica.py` com os limites como constantes `Decimal`
nomeadas, mais um mapa `categoria → teto`:

```python
TETOS = {"alimentacao": Decimal("60.00"), "transporte_urbano": Decimal("80.00"), "hospedagem": Decimal("250.00")}
PISO_NOTA_FISCAL = Decimal("100.00")
FATOR_VIAGEM = Decimal("1.5")
```

**Decisão:** constantes em módulo próprio, não arquivo de configuração externo.
Mudar um limite é editar uma linha, e o `git blame` mostra quando e por quê — o
que um YAML de configuração não daria de graça. Se o Dia 2 trouxer limites
variáveis por perfil, este é o módulo que vira tabela; a fronteira já está
desenhada no lugar certo.

## 5. Decisões técnicas

### DT-001 — `Decimal` desde a leitura do arquivo

**Contexto:** `d-011` vale `33.333` no JSON. Lido como `float`, vira
`33.332999999999998` e a RN-010 passa a depender de sorte de arredondamento.
**Decisão:** `json.load(f, parse_float=Decimal)`, e arredondamento único com
`quantize(Decimal("0.01"), ROUND_HALF_UP)` na construção da `Despesa`.
**Alternativa descartada:** converter para `Decimal` depois de já ter passado por
`float` — inútil, a precisão já se perdeu no parse.
**Consequência:** torna impossível o bug mais previsível do projeto; obriga a
converter para `str` na serialização, porque `Decimal` não é serializável por
padrão.

### DT-002 — Uma função pura por regra de negócio

**Contexto:** a spec §8 define oito passos com parada no primeiro que recusa.
**Decisão:** cada RN é uma função `(Despesa, Contexto) -> Parecer | None`, onde
`None` significa "não decidi, siga para a próxima". A calculadora percorre a
lista de regras na ordem da spec.
**Alternativa descartada:** um `if/elif` aninhado dentro de uma função grande —
funcionaria, mas a ordem da spec §8 ficaria implícita na indentação em vez de
declarada numa lista legível.
**Consequência:** mudar a ordem das regras vira reordenar uma lista; adicionar
regra vira acrescentar uma função. É a aposta explícita deste plano para o
envelope do Dia 2.

### DT-003 — Núcleo sem I/O

**Contexto:** critério de aceite da spec exige verificar dez regras.
**Decisão:** `motor/` não importa `json`, `argparse`, `pathlib` nem `open`.
**Alternativa descartada:** motor que recebe caminho de arquivo — mais curto de
escrever, mas cada teste de regra viraria um teste de disco.
**Consequência:** os testes de regra rodam em memória; o custo é uma camada de
tradução a mais entre o arquivo e o modelo.

### DT-004 — Viagem calculada uma vez, antes do laço

**Contexto:** a RN-009 diz que a condição de viagem é determinada sobre a
lista de entrada e não é afetada por recusas.
**Decisão:** varrer as despesas uma vez, montar `frozenset` das datas com
hospedagem, guardar no `Contexto`.
**Alternativa descartada:** consultar as outras despesas de dentro da regra de
teto — criaria dependência entre itens no meio do laço e abriria a porta para a
ordem de processamento mudar o resultado.
**Consequência:** o resultado de cada despesa passa a depender só dela e do
`Contexto`, o que é o que torna o motor testável item a item.

### DT-005 — Sem dependência externa em produção

**Contexto:** `pytest` é a única dependência, e só de desenvolvimento.
**Decisão:** stdlib para tudo em `src/`.
**Alternativa descartada:** `pydantic` para validação de entrada.
**Consequência:** `python -m src.cli` roda em qualquer Python 3.11+ sem instalar
nada; em troca, a validação de entrada é código escrito à mão que precisa de
teste próprio.

### DT-006 — Nome de teste carrega o ID da regra

**Contexto:** o critério de rastreabilidade da rúbrica pede chegar da spec ao
teste sem adivinhar.
**Decisão:** arquivos `tests/test_rn_007_tetos.py`, funções
`test_rn_007_despesa_acima_do_teto_e_reembolsada_pelo_teto`.
**Alternativa descartada:** nomes descritivos sem o ID — legíveis, mas exigiriam
um índice à parte para amarrar na spec.
**Consequência:** `pytest -k rn_007` roda exatamente os testes de uma regra, e a
matriz de cobertura do `tasks.md` se preenche por leitura direta.

## 6. Estratégia de testes

- **Nível.** Maioria unitária sobre o motor puro (uma função de regra por vez);
  um punhado de testes de integração no carregador e no serializador; **um** teste
  ponta a ponta que roda a CLI sobre `exemplos/despesas-exemplo.json` e confere o
  total de R$ 703,43 da spec §9.
- **Cada `RN-NNN` tem teste?** Sim, por construção: a task de cada RN só fecha com
  o teste de nome correspondente passando, e a tabela de cobertura no fim do
  `tasks.md` é preenchida ao encerrar cada fase.
- **Casos de borda da spec §7.** A tabela de 18 linhas vira um
  `@pytest.mark.parametrize` em `tests/test_casos_de_borda.py`, uma linha por
  caso, com o ID da regra no `id` do parâmetro.
- **Fronteiras têm teste dos dois lados.** Onde a spec fixa um limite, existem
  dois casos: R$ 100,00 e R$ 100,01; R$ 60,00 e R$ 60,01. Testar só o lado que
  passa é o jeito mais comum de a suíte ficar verde com a regra errada.
- **Nomenclatura.** `test_rn_00X_<comportamento>` — ver DT-006.

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| O envelope do Dia 2 muda a unidade de aplicação do teto (AMB-001, de "por despesa" para "por dia") | Alta | É a mudança que mais dói: a RN-007 deixa de ser função de uma despesa só. Mitigação já embutida no `Contexto` (DT-004) — o agregado por data entra lá, e a assinatura das regras não muda |
| O envelope introduz campo novo na entrada (`em_viagem`, `diarias`) | Alta | Já previsto na spec §10 como o conserto certo; o carregador ganha campo opcional e a RN-009/RN-008 troca a inferência pelo campo |
| Limites passam a variar por perfil ou por data de vigência | Média | `politica.py` vira tabela indexada; a fronteira já está isolada (§4) |
| `Decimal` vazando para o `json.dump` e estourando `TypeError` | Média | Serializador converte explicitamente; teste ponta a ponta pega |
| Testes escritos depois do código, quebrando a ordem da rastreabilidade | Média | Cada task do `tasks.md` tem o teste como critério de aceite, e o commit `test(T-00X)` vem antes ou junto do `feat(T-00X)` |
| Spec e código divergirem em silêncio ao absorver o envelope | Baixa | `DECISIONS.md` obrigatório antes de tocar em código; o teste ponta a ponta trava o total da spec §9 e falha se o comportamento mudar sem a spec mudar junto |
