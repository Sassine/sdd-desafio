# Relatório — Desafio SDD

**Aluno:** `Rayanne Oliveira Dutra` · **Repositório:** `https://github.com/rayDutra/sdd-desafio` · **Data:** `01/08/2026`

> Isto não é redação. São **evidências**. Toda afirmação deve vir acompanhada de
> arquivo, hash de commit ou trecho de sessão exportada. Um parágrafo bonito sem
> evidência vale menos que uma frase curta com um hash.
>
> Vale 20 dos 100 pontos, e é a seção que mais separa notas.

---

## Delegação

*O que você fez, o que o Claude fez, e por que dividiu assim.*

**A divisão:**

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Claude (chat) propôs, eu decidi | O JSON de exemplo foi analisado item a item; cada ambiguidade proposta eu confirmava ou ajustava antes de ir para a spec |
| Decidir as ambiguidades | Eu, com justificativa proposta pelo Claude | Nunca aceitei uma decisão sem entender o motivo — algumas (ex: herança de política padrão por categoria, AMB-014) exigiram minha confirmação explícita antes de virar RN |
| Escrever a spec | Claude (chat) redigiu, eu revisei e aprovei linha a linha | O chat nunca editou spec.md diretamente sem eu ver o texto proposto antes |
| Desenhar a arquitetura | Claude (chat) propôs (plan.md, DT-001 a DT-004), eu validei | Decisões técnicas como uso de Decimal, separação parsing/avaliação foram propostas e justificadas antes de codar |
| Implementar | Copilot Chat (VS Code) escreveu o código | Usei o Copilot integrado ao editor para gerar as funções task por task, sempre em TDD |
| Escrever testes | Copilot Chat gerou, Claude (chat) revisou antes do commit | Todo teste passou por uma segunda revisão externa ao ambiente de codificação antes de ser aceito |
| Absorver o envelope | Claude (chat) mapeou o que quebrava, Copilot Chat implementou | A leitura do comunicado do RH e o mapeamento RN-por-RN foi feito no chat, sem código, antes de qualquer prompt de implementação |

**Onde deleguei e me arrependi:**
`<preencher: houve algum momento em que aceitar a sugestão da IA sem
questionar te custou retrabalho? ex: algum teste sintético mal montado,
alguma decisão de arquitetura que teve que ser revertida?>`

**Onde não deleguei e deveria ter delegado:**
`<preencher: alguma tarefa manual repetitiva — ex: copiar/colar arquivos do
envelope, mover despesas-exemplo.json de volta — que poderia ter sido
automatizada?>`
Um caso real: o arquivo `despesas-exemplo.json` foi movido por engano para
dentro de `exemplos/envelope/` durante a organização manual dos arquivos do
envelope, quebrando 30 dos 39 testes até então. Foi um erro de organização
manual de arquivos, não de código — corrigido movendo o arquivo de volta
(commit `chore: corrige localizacao do despesas-exemplo.json`).

**Usei subagentes / skills / MCP / hooks?** Não. Usei dois ambientes
separados — Copilot Chat no VS Code para escrever código task por task, e
Claude (chat, fora do editor) para planejamento de spec, revisão de código
antes de commitar, e diagnóstico de bugs. Nenhum dos dois teve acesso direto
ao outro; toda comunicação entre eles passou por mim copiando/colando código
e resultados de teste.

---

## Descrição

*Como você transformou requisito ambíguo em requisito verificável.*

**Requisito escolhido:** RN-005 — "Colaborador em viagem tem limites
ampliados em 50%" (AMB-004).

**Versão 1 (minha primeira escrita, spec.md commit `a8d3eb6`):**
> ```
> RN-005 — Limites ampliados em viagem
> Regra: A condição de viagem é inferida apenas quando há evidência
> explícita de viagem na descrição ou fornecedor, e essa evidência é
> avaliada para o mesmo dia da despesa.
> ```
> Implementação correspondente: busca por termos ("hotel", "aeroporto",
> "airbnb", "viagem", "traslado") em `descricao + fornecedor` de **qualquer**
> despesa do dia, independente de categoria.

**Versão final (spec.md, após correção):**
> ```
> RN-005 — Limites ampliados em viagem
> Regra: A condição de viagem é inferida de forma heurística apenas
> quando há uma despesa de categoria hospedagem no mesmo dia da despesa
> analisada. Despesas de outras categorias não são usadas como sinal de
> viagem, mesmo quando contêm termos como hotel ou aeroporto.
> ```

**O que estava ambíguo:** a política do RH não define nenhum critério para
"em viagem" — a entrada de dados não tem esse campo. A primeira decisão
(busca de palavras-chave em texto livre) parecia razoável até ser testada.

**Como percebi:** rodando o teste `test_limite_diario_e_viagem` contra o
próprio `despesas-exemplo.json`, a despesa **d-004** ("Corrida hotel",
categoria transporte_urbano — só uma corrida de táxi até um hotel, não uma
hospedagem) disparava a heurística de viagem por conter a palavra "hotel"
na descrição. O teste que eu havia escrito para confirmar "dia sem viagem"
falhava, expondo o problema.

**Commit da mudança:** `feat(T-004): calcula limite diario com viagem
baseada em hospedagem (RN-002, RN-005)` — spec atualizada em commit
separado, registrado como `DEC-010` em decisions.md.

---

## Discernimento

*Onde o Claude errou e você pegou.*

> **Sem um caso concreto e verificável, esta seção vale zero.**

### Caso 1 — Falso positivo na inferência de viagem (RN-005)

**O que ele propôs:** detectar viagem buscando palavras-chave ("hotel",
"aeroporto", "airbnb", "viagem", "traslado") na descrição ou fornecedor de
**qualquer** despesa do dia, sem restringir por categoria.

**Por que estava errado:** o próprio dataset de exemplo continha um caso
que expunha o problema — a despesa d-004 ("Corrida hotel", transporte
urbano) faria o sistema achar erroneamente que o colaborador estava em
viagem, ampliando limites de alimentação/transporte que não deveriam ser
ampliados naquele dia.

**Como eu detectei:** o teste que eu mesmo pedi para cobrir esse caso
(`test_limite_diario_e_viagem`, verificando um dia sem hospedagem) falhava
ao rodar `pytest -v` — o resultado esperado (`60.00`) não batia com o
resultado real (`90.00`, indicando que a viagem foi detectada
incorretamente).

**O que eu fiz:** pedi a correção da heurística para considerar apenas
despesas de categoria `hospedagem` no mesmo dia como evidência válida,
descartando a busca por texto livre em outras categorias. Atualizei
RN-005/AMB-004 na spec e registrei `DEC-010` antes de aceitar o código.

**Onde está a evidência:** `docs/sessions/<nome-do-arquivo-da-sessao-t004>`.

### Caso 2 — Regra de negócio inteira ausente na primeira versão da T-010

**Padrão que eu notei:** a orquestração do pipeline (`processar_despesas`)
tratava explicitamente alimentação e transporte urbano com limite diário,
mas categoria `hospedagem` caía num `else` genérico que concedia reembolso
**integral, sem limite algum** — RN-012 (limite de R$250/diária) nunca
tinha sido escrita na spec nem implementada, apesar de ser um dos 9 itens
originais da política do RH.

**Como eu detectei:** revisão manual do código antes do commit, comparando
a lógica com a lista original de regras do RH — não foi um teste que
pegou, porque nenhum teste da T-010 cobria uma despesa de hospedagem acima
do limite.

**O que eu fiz:** parei antes de commitar, adicionei RN-012 à spec com
`DEC-013`, escrevi um teste que reproduzia o caso (`d-010`, R$480,00) e só
então pedi a correção do código.

**Sinal recorrente:** os erros mais graves que passaram despercebidos
inicialmente foram, em geral, **omissões** (regra inteira faltando,
despesa desaparecendo do resultado), não cálculos errados dentro de uma
regra já escrita. Isso me deixou mais atento a conferir "o resultado tem
o número certo de itens?" além de "os valores estão certos?".

---

## Diligência

*O que você verificou antes de aceitar.*

**Meu procedimento de verificação:** `<preencher honestamente — algo como:
"rodava pytest -v após cada task, lia a saída completa, e para tasks que
tocavam em orquestração (T-010, T-017) também revisava o diff linha por
linha antes de commitar; para tasks isoladas de regra única, confiava mais
no teste passando">`

**Li o diff inteiro em que porcentagem das entregas?** `<preencher com
honestidade — não existe resposta certa, a rubrica valoriza sinceridade
aqui>`

**O que aceitei sem verificar direito, e o que me custou:**
Um caso real e documentado nesta sessão: na integração da T-017
(`processar_despesas_v4`), a lógica que deveria reincorporar despesas com
câmbio indisponível (`despesas_sem_cambio`) ao resultado final foi descrita
verbalmente e nunca colada de fato no arquivo. Isso só foi descoberto
porque um teste novo (via CLI) verificava explicitamente a despesa `e-006`
por id — sem esse teste específico, a despesa teria simplesmente
desaparecido do resultado sem erro nenhum, e o resumo (`quantidade_despesas`)
ficaria inconsistente com a lista de despesas.

**Testes: quem escreveu, e como você sabe que eles testam a coisa certa?**
Os testes foram gerados pelo Copilot Chat junto com o código, na maioria
das tasks. Isso é um risco real — teste escrito pelo mesmo agente que
escreve o código tende a confirmar o comportamento implementado, não o
comportamento correto. Um exemplo concreto: na T-006, um teste chamado
`test_despesa_acima_de_100_com_nota_fiscal_nao_eh_recusada` reaproveitava
o valor de uma despesa (`d-001`, R$72,50) que estava **abaixo** de R$100 —
o teste passava, mas não provava o que o nome prometia. Só foi corrigido
porque o valor foi comparado manualmente contra o nome do teste antes do
commit.

---

## O envelope

*A mudança de requisito do Dia 2.*

**Quantos arquivos toquei na mão:** `<preencher — pelo menos spec.md,
plan.md, decisions.md, tasks.md, reembolso.py, cli.py, e ~8 arquivos de
teste novos (test_politica_externa.py, test_representacao.py,
test_categoria_nao_reembolsavel.py, test_conversao_cambio.py,
test_processar_despesas_v4.py, test_cli_v4.py, test_leitura_preserva_moeda.py,
test_normalizacao_preserva_moeda.py) — conte exatamente pelo git diff>`

**Quanto tempo levou:** `<preencher>`

**Diff de absorção:** `<n> arquivos, +<n>/-<n> linhas` — rodar
`git diff <hash-antes-do-envelope> HEAD --stat` para o número exato.

**Absorveu de graça:** a separação entre parsing e avaliação de regras
(DT-002 do plan.md, decidida desde o Dia 1) permitiu criar
`processar_despesas_v4` como função nova, reaproveitando `normalizar_despesas`,
`identificar_duplicatas`, `validar_periodo`, `identificar_ajuste` e
`calcular_reembolso_parcial` sem alterar nenhuma delas. A função antiga
`processar_despesas` (v3) permaneceu intacta, o que preservou os 33 testes
do Dia 1 sem nenhuma regressão.

**Resistiu:** o modelo de dados `Despesa` (dataclass frozen) não tinha
campo `moeda` — teve que ser adicionado, e isso expôs que **duas** funções
já existentes (`carregar_despesas` e `normalizar_despesas`) reconstroem o
objeto `Despesa` internamente e silenciosamente descartavam qualquer campo
novo que não fosse explicitamente repassado no construtor. Isso não
apareceu como erro — apareceu como despesas em EUR/USD sendo processadas
como se fossem BRL, sem nenhum aviso. Precisou de dois testes dedicados
(`test_leitura_preserva_moeda.py`, `test_normalizacao_preserva_moeda.py`)
para expor e travar essa lacuna.

**Ordem em que fiz:** spec (RN-013 a RN-018, AMB-014 a AMB-017) →
decisions.md (DEC-013 a DEC-017) → tasks.md (T-013 a T-018) → código,
task por task, na mesma ordem do tasks.md. Os timestamps dos commits
confirmam essa ordem — nenhum commit de código antecede o commit de spec
correspondente à mesma regra.

**Se eu tivesse escrito a spec original sabendo desta mudança:**
`<preencher — ex: teria desenhado o modelo de dados com um campo genérico
de "metadados extras" desde o início, ou uma função de fábrica única para
Despesa em vez de reconstrução manual espalhada em 3 lugares diferentes>`

**O que a spec me poupou, em concreto:** a ordem de aplicação das regras
(seção 8 da spec, decidida no Dia 1) já definia que duplicata e período
são avaliados antes de valor — isso significou que, ao integrar a política
v4, não precisei redecidir a precedência entre as regras antigas e novas;
só precisei inserir os dois novos passos (conversão de câmbio antes de
tudo, validação de limite-zero após categoria) no ponto certo de uma
sequência que já existia.

---

## Fechamento

**Para qual tamanho de projeto isto valeu a pena?**
Este processo valeu mais para projetos pequenos ou médios, com regras de negócio ainda em definição ou com bastante ambiguidade. Nesse contexto, a spec funciona como um amortecedor: ela evita que cada mudança de interpretação vire retrabalho e ajuda a manter a implementação alinhada ao que foi decidido.

**Para qual não valeria?**
Ele seria menos útil em projetos grandes, muito consolidados ou com regras altamente estáveis, onde a mudança de escopo é rara e a vantagem principal do SDD — transformar ambiguidades em decisões explícitas — perde parte do impacto.

**O que eu faria diferente:**
Eu começaria com testes ainda mais específicos desde as primeiras tasks, sobretudo para os campos que podem ser silenciosamente descartados ou mal interpretados, como moeda e campos extras no modelo de dados. Também escreveria a spec com mais foco em fronteiras de regra e casos de borda, porque isso reduziria muito o risco de erros escondidos na implementação.

**A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**
Percebi que a IA é muito útil para acelerar a execução, mas também pode criar uma falsa sensação de segurança quando a resposta parece certa demais. Isso me mostrou que preciso revisar com mais rigor os pontos em que a ferramenta “completa” o raciocínio por mim, especialmente em regras de negócio e decisões que não podem ficar implícitas.