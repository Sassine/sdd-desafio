# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>`

---

## Fase 1 — Fundação

- [ ] **T-001** — <o que faz>
  - **Atende:** RN-001
  - **Aceite:** <o teste que precisa passar>
  - **Commit:** `<hash preenchido depois>`

- [ ] **T-002** — <...>
  - **Atende:**
  - **Aceite:**
  - **Commit:**

## Fase 2 — Regras de negócio

- [ ] **T-00N** — <...>
  - **Atende:** RN-00X, AMB-00Y
  - **Aceite:**
  - **Commit:**

## Fase 3 — Casos de borda

- [ ] **T-00N** — <...>

## Fase 4 — Saída e CLI

- [ ] **T-00N** — <...>

---

## Fase 5 — Envelope (criar no Dia 2)

<Novas tasks a partir da mudança de requisito. Numeração continua de onde parou —
não reinicie e não renumere as antigas: a numeração é o eixo da rastreabilidade.>

---

## Cobertura

Preencha ao fechar cada fase. É a sua própria checagem de rastreabilidade — e é
exatamente a matriz que a correção vai montar.

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-00X | `<nome do teste>` |
| RN-002 | | |
| AMB-001 | | |
