# Migrations

Este projeto usa [Alembic](https://alembic.sqlalchemy.org/) para versionar alteracoes
de schema em ambientes com dados reais (o `sql/schema.sql` serve como baseline
para bootstrap rapido em desenvolvimento/demo).

Fluxo recomendado:

```bash
alembic init sql/migrations         # somente na primeira vez (ja inicializado aqui)
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head
```

Cada migration deve ser:
- **Reversivel** (implementar `downgrade()`);
- **Idempotente** em re-execucao acidental;
- Revisada quanto a impacto de lock em tabelas grandes (`alerts`, `risk_scores`) antes de aplicar em producao.
