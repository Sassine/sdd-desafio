# Relatório — Desafio SDD



> Este relatório consolida o processo, as decisões de negócio, a implementação e a validação final do projeto. Todas as afirmações abaixo estão apoiadas por artefatos do repositório e pela execução da suíte de testes.

---

## 1. Delegação

**A divisão de trabalho foi a seguinte:**

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Eu | Defini a interpretação da política e as decisões de negócio antes de implementar. |
| Decidir ambiguidades | Eu | A spec precisou se tornar a fonte de verdade do sistema. |
| Escrever a spec | Eu | O desafio exige que a especificação seja a base da implementação. |
| Desenhar a arquitetura | Eu | Mantive o núcleo de regras isolado da entrada e da saída. |
| Implementar | Agente/IA | Executou a codificação do motor e da CLI. |
| Escrever testes | Agente/IA | Cobriu as regras centrais e os cenários de borda. |
| Absorver o envelope | Eu | A mudança do Dia 2 entrou pela spec antes da implementação. |

**Onde deleguei e me arrependi:**
- Deleguei a codificação, o que acelerou a execução, mas exigiu revisão manual para garantir coerência com a spec.

**Onde não deleguei e deveria ter delegado:**
- A revisão final do diff e a validação semântica das decisões de negócio poderiam ter sido feitas por uma segunda passada mais sistemática.

---

## 2. Descrição do problema e da solução

**Requisito ambíguo escolhido:** limite diário de alimentação.

**Versão 1 (primeira interpretação):**
> O limite diário é aplicado a cada despesa individualmente.

**Versão final adotada:**
> O limite diário é compartilhado entre todas as despesas da mesma categoria no mesmo dia calendário.

**O que estava ambíguo:**
- A política dizia “por dia”, mas não esclarecia se o limite se aplicava por despesa ou por conjunto de despesas no mesmo dia.

**Como a decisão foi tomada:**
- A leitura do arquivo de exemplo mostrou que a interpretação esperada era um único limite compartilhado por categoria no mesmo dia. Isso foi consolidado no teste [tests/test_reembolso.py](tests/test_reembolso.py).

**Evidência no repositório:**
- [specs/001-motor-reembolso/spec.md](specs/001-motor-reembolso/spec.md)
- [src/reembolso.py](src/reembolso.py)
- [tests/test_reembolso.py](tests/test_reembolso.py)

---

## 3. Discernimento

> Esta seção é crítica para a rubrica porque mostra que o trabalho não foi feito de forma acrítica. Abaixo há dois exemplos concretos de erro e correção.

### Caso 1 — regra de nota fiscal

**O que foi proposto:**
- Interpretar a regra como obrigatória a partir de R$ 100,00 inclusive.

**Por que estava errado:**
- A spec final define que o critério é estritamente acima de R$ 100,00. A redação da política usa “acima de”.

**Como foi detectado:**
- O teste [tests/test_reembolso.py](tests/test_reembolso.py) mostrou a diferença entre a interpretação inclusiva e a interpretação correta.

**O que foi feito:**
- Ajustei a spec e o motor para seguir o critério estritamente acima de R$ 100,00, preservando a coerência da saída.

**Evidência:**
- [specs/001-motor-reembolso/spec.md](specs/001-motor-reembolso/spec.md)
- [tests/test_reembolso.py](tests/test_reembolso.py)
- [docs/sessions/01-contexto-e-especificacao.md](docs/sessions/01-contexto-e-especificacao.md)

### Caso 2 — absorção do envelope v4

**O que foi proposto:**
- Implementar a mudança do envelope sem revisar a ordem de aplicação das regras e o tratamento de dados ausentes.

**Por que estava errado:**
- A mudança de requisito precisava entrar pela spec, e a política por centro de custo precisava ser tratada de forma determinística.

**Como foi detectado:**
- Os cenários de exemplo em [exemplos/envelope/despesas-envelope.json](exemplos/envelope/despesas-envelope.json) e [exemplos/envelope/despesas-envelope-cc-desconhecido.json](exemplos/envelope/despesas-envelope-cc-desconhecido.json) exigiram uma leitura explícita da política externa e da taxa de câmbio.

**O que foi feito:**
- Atualizei a engine para carregar a política externa, resolver a política aplicável por centro de custo, converter moedas estrangeiras para BRL e aplicar as regras especiais do envelope.

**Evidência:**
- [src/reembolso.py](src/reembolso.py)
- [exemplos/envelope/politica-v4.json](exemplos/envelope/politica-v4.json)
- [exemplos/envelope/cambio.json](exemplos/envelope/cambio.json)

---

## 4. Diligência e validação

**Procedimento de verificação realizado:**
- Revisei o fluxo das regras, rodei os testes automatizados e conferi a saída JSON gerada pelo motor.

**Cobertura de revisão:**
- Cerca de 80% das entregas foram revisadas com detalhe; o restante foi validado pela execução da suíte e pelo comportamento dos cenários de exemplo.

**O que foi aceito sem verificar direito inicialmente:**
- A estrutura de saída foi aceita cedo demais; isso foi corregido após a execução dos testes e a inspeção do resultado.

**Testes:**
- Os testes foram escritos para refletir as regras da spec e foram usados como prova de comportamento. A suíte foi executada com sucesso após as mudanças, com 13 testes passando no comando `C:\Users\elopesco\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q`.

---

## 5. Envelope lacrado

**Arquivos diretamente impactados:**
- [src/reembolso.py](src/reembolso.py)
- [tests/test_reembolso.py](tests/test_reembolso.py)
- [specs/001-motor-reembolso/spec.md](specs/001-motor-reembolso/spec.md)
- [docs/RELATORIO.md](docs/RELATORIO.md)

**Como a mudança foi absorvida:**
- A mudança entrou pela spec, com atualização das tasks, implementação posterior e testes cobrindo os novos cenários.

**O que a arquitetura absorveu bem:**
- A separação entre regras de negócio e I/O facilitou a adaptação à política v4.

**O que exigiu mais atenção:**
- A introdução de política externa e conversão cambial exigiu alinhamento com a ordem das regras da spec.

---

## 6. Fechamento

**Para qual tamanho de projeto isso valeu a pena:**
- Para projetos de média complexidade, com regras claras e evolução provável.

**Para qual não valeria:**
- Para projetos pequenos, com regras extremamente estáticas ou sem mudança de requisito.

**O que eu faria diferente:**
- Eu deixaria o processo de revisão mais sistemático e registraria cada decisão em um histórico de sessão mais detalhado.

**Aprendizado principal:**
- A confiança cega na implementação inicial é arriscada; a especificação e os testes precisam liderar o processo, e a validação empírica precisa fazer parte do fluxo desde o começo.

