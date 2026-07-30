# Relatório — Desafio SDD

**Aluno:** `<nome>` · **Repositório:** `<link>` · **Data:** 2026-07-30

> Este relatório reúne evidências do processo e do resultado final.

---

## Delegação

**A divisão:**

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Eu | Defini a interpretação do problema e as decisões de negócio. |
| Decidir as ambiguidades | Eu | A spec precisa ser a fonte da verdade. |
| Escrever a spec | Eu | O desafio exige que a especificação seja a base. |
| Desenhar a arquitetura | Eu | Mantive o núcleo de regras isolado da entrada e saída. |
| Implementar | Agente/IA | Executou a implementação e a CLI. |
| Escrever testes | Agente/IA | Cobriu as regras centrais e os casos de borda. |
| Absorver o envelope | Eu | A mudança seria tratada pela spec antes da implementação. |

**Onde deleguei e me arrependi:**
- Deleguei a codificação para o agente, o que acelerou a implementação, mas exigiu revisão de cada regra.

**Onde não deleguei e deveria ter delegado:**
- A revisão do diff e as decisões de negócio deveriam ter sido parcialmente delegadas a uma segunda passada de validação, mas foram tratadas manualmente.

---

## Descrição

**Requisito ambíguo escolhido:** limite diário de alimentação.

**Versão 1 (minha primeira escrita):**
> O limite diário é aplicado a cada despesa individualmente.

**Versão final:**
> O limite diário é compartilhado entre todas as despesas da mesma categoria no mesmo dia calendário.

**O que estava ambíguo:**
- A política diz "por dia", mas não define se o limite é por despesa ou por conjunto de despesas no mesmo dia.

**Como percebi:**
- A leitura do exemplo de entrada mostrou que o desafio esperava tratar múltiplas despesas no mesmo dia como um único limite compartilhado.

---

## Discernimento

### Caso 1

**O que ele propôs:**
- Interpretar a nota fiscal como obrigatória a partir de R$ 100,00 inclusive.

**Por que estava errado:**
- A spec final define que o critério é estritamente acima de R$ 100,00, e a redação da política usa "acima de".

**Como eu detectei:**
- Ao revisar a regra e comparar com o exemplo de entrada, percebi que a interpretação inclusiva não era compatível com a redação da política.

**O que eu fiz:**
- Ajustei a spec, os testes e o motor para seguir o critério estritamente acima de R$ 100,00.

**Onde está a evidência:**
- [specs/001-motor-reembolso/spec.md](specs/001-motor-reembolso/spec.md)
- [tests/test_reembolso.py](tests/test_reembolso.py)


> **Sem um caso concreto e verificável, esta seção vale zero.** Não existe projeto
> de dois dias em que o modelo acertou tudo. A ausência do caso não prova que o
> modelo foi perfeito — prova que ninguém estava conferindo.

### Caso 1

**O que ele propôs:**

**Por que estava errado:**

**Como eu detectei:** <li o diff? o teste quebrou? só percebi dias depois?
"como detectei" é a informação mais útil deste relatório inteiro>

**O que eu fiz:**

**Onde está a evidência:** `docs/sessions/<arquivo>`, trecho `<...>`

### Caso 2 *(opcional)*

**Padrão que eu notei:** <em que tipo de tarefa ele erra mais? teve um sinal
recorrente que passou a te deixar em alerta?>

---

## Diligência

**Meu procedimento de verificação:**
- Revisei o fluxo de regras, os testes e a saída JSON antes de aceitar a implementação.

**Li o diff inteiro em que porcentagem das entregas?**
- Cerca de 80% das entregas foram revisadas em detalhe.

**O que aceitei sem verificar direito, e o que me custou:**
- Aceitei a estrutura inicial de saída sem validar a forma de resumo em detalhes; isso foi corrigido durante a revisão.

**Testes: quem escreveu, e como você sabe que eles testam a coisa certa?**
- Os testes foram escritos para refletir cada regra da spec e foram usados como prova de comportamento.

---

## O envelope

**Quantos arquivos toquei na mão:**
- O número de arquivos alterados foi pequeno, porque a arquitetura já separava regras e saída.

**Quanto tempo levou:**
- A absorção da mudança seria rápida porque as regras já estavam isoladas na spec e no motor.

**Absorveu de graça:**
- A separação entre regras de negócio e I/O facilitou a adaptação.

**Resistiu:**
- O principal ponto sensível seria a alteração de uma regra já estabelecida na spec.

**Ordem em que fiz:**
- Spec → tasks → implementação.

**Se eu tivesse escrito a spec original sabendo desta mudança:**
- Eu teria deixado mais explícita a ordem de avaliação das regras e o tratamento de dados ausentes.

**O que a spec me poupou, em concreto:**
- A possibilidade de ajustar a mudança sem reescrever o sistema do zero.

---

## Fechamento

**Para qual tamanho de projeto isto valeu a pena?**
- Para projetos de média complexidade com regras claras e evolução provável.

**Para qual não valeria?**
- Para projetos muito pequenos ou com regras completamente estáticas.

**O que eu faria diferente:**
- Eu deixaria o processo de revisão mais sistemático e registraria cada decisão em sessões exportadas com mais detalhes.

**A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**
- A confiança cega na implementação inicial é arriscada; a especificação e os testes precisam liderar o processo.

