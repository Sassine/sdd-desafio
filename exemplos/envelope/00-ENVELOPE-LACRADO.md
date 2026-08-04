# 🔒 ENVELOPE LACRADO

**Não distribuir antes do Dia 2, 10h.**
Alunos: se você chegou aqui antes da hora, feche. Ler antes queima o exercício inteiro e você é a única pessoa prejudicada.

---

## Mudança de requisito — Política de Reembolso v4

Bom dia. O RH revisou a política. Vigência imediata, retroativa à competência atual.

> **Comunicado do RH — Política de Reembolso v4**
>
> Após auditoria interna, a política deixa de ser única para toda a empresa.
>
> **A. Limites passam a variar por centro de custo.**
> Os limites não são mais constantes. Cada centro de custo tem a sua tabela, mantida pelo financeiro num arquivo à parte, e ela muda sem aviso. O motor precisa ler a política de fora, não de dentro do código.
>
> A tabela vigente está em `politica-v4.json`.
>
> Observações que o financeiro fez questão de incluir:
> - `CC-COMERCIAL` tem uma categoria nova, `representacao`, que não existia na v3 — limite de R$ 300 por dia.
> - `CC-ENG-PLATAFORMA` não reembolsa `hospedagem` de forma alguma.
> - Alguns centros de custo não têm entrada na tabela. Nesse caso, aplica-se a política padrão.
>
> **B. Despesas internacionais.**
> Colaboradores em viagem internacional lançam despesas em moeda estrangeira. A entrada agora pode trazer um campo `moeda` (ISO 4217). Quando ausente, assume-se `BRL`.
>
> A conversão usa a **taxa da data da despesa**, não a taxa de hoje. As taxas estão em `cambio.json`.
>
> Os limites da política são sempre em BRL. Uma despesa em EUR é convertida antes de ser comparada ao limite.
>
> **C. (Opcional — só se sobrar tempo) Fila de aprovação manual.**
> Itens cujo valor reembolsável passe de R$ 500 não são mais aprovados automaticamente. Eles entram em estado de pendência aguardando aprovação do gestor. O resultado deixa de ser apenas um valor: cada item passa a ter um estado.

---

## O que se espera de você agora

Nada de heroísmo. O que se avalia é o **caminho**, não a velocidade:

1. **Primeiro a spec.** Leia a mudança, identifique o que ela quebra na sua `spec.md`, e atualize a spec — incluindo as ambiguidades novas que este comunicado traz (e traz várias).
2. **Registre no `DECISIONS.md`.** O que mudou, por quê, quais requisitos foram invalidados, quais tasks precisam ser refeitas.
3. **Novas tasks no `tasks.md`.** Numeração continuando de onde parou.
4. **Só então, código.** Commits referenciando as novas tasks, como antes.
5. **Anote enquanto faz.** Quantos arquivos você tocou na mão? O que a sua arquitetura absorveu de graça e o que resistiu? Isso vai para o relatório e é a parte mais valiosa dele.

O item C é opcional de propósito. Se você não chegar nele, não perde ponto. Se você deixar a spec inconsistente para chegar nele, perde.

---

## Ambiguidades que este comunicado também traz

Não estão listadas para você. Estão listadas para deixar claro que **elas existem** — a v4 é tão ambígua quanto a v3 era. Trate-as com o mesmo processo: identificar, decidir, justificar, registrar.

Dica: a frase "aplica-se a política padrão" e a frase "a taxa da data da despesa" cada uma esconde pelo menos uma decisão que você vai precisar tomar sozinho.

---

## Arquivos que acompanham este envelope

Estão todos aqui neste mesmo gist. Baixe os quatro e guarde no seu repositório
(sugestão: `exemplos/envelope/`), commitando junto — eles fazem parte da entrega.

- `politica-v4.json` — tabela de limites por centro de custo
- `cambio.json` — taxas de câmbio por data
- `despesas-envelope.json` — novo conjunto de despesas exercitando as mudanças
- `despesas-envelope-cc-desconhecido.json` — um segundo colaborador, em um centro
  de custo que não está na tabela

> Para baixar tudo de uma vez: o botão **Download ZIP** no canto superior direito
> desta página.
