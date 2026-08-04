# Motor de Cálculo de Reembolso

## Como executar

1. Instale Python 3.
2. Execute o comando abaixo na raiz do projeto:

```bash
python src/reembolso.py --input exemplos/despesas-exemplo.json --output resultado.json
```

## Como testar

```bash
pytest -q
```

## O que o projeto faz

O sistema lê um arquivo JSON com despesas, avalia cada item conforme a política de reembolso desambiguada na spec e gera um JSON com:

- status do item (`reembolsado`, `reembolsado_parcialmente` ou `nao_reembolsavel`)
- valor original
- valor reembolsável
- motivo da decisão

## Arquivos principais

- `specs/001-motor-reembolso/spec.md`: regras de negócio e ambiguidades resolvidas
- `specs/001-motor-reembolso/tasks.md`: sequência de implementação e testes
- `specs/001-motor-reembolso/plan.md`: decisões técnicas
- `tests/test_reembolso.py`: suíte de testes automatizados
