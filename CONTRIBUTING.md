# Contribuindo com o SeniorRx Monitor

Obrigado por contribuir! Este e um projeto de pesquisa/educacional sobre
seguranca do paciente idoso — contribuicoes de farmaceuticos clinicos,
geriatras, cientistas de dados e engenheiros de software sao bem-vindas.

## Ambiente de desenvolvimento

```bash
python -m venv .venv && source .venv/bin/activate   # ou .venv\Scripts\activate no Windows
make install
cp .env.example .env
docker compose up -d db
python scripts/init_db.py --database-url "$DATABASE_URL"
python scripts/generate_synthetic_data.py
```

## Fluxo de contribuicao

1. Abra uma issue descrevendo o problema/feature antes de comecar (evita retrabalho).
2. Crie um branch a partir de `main`: `git checkout -b feature/nome-curto`.
3. Escreva testes para qualquer mudanca em `src/seniorrx/domain/` ou `application/`.
4. Rode localmente antes do PR:
   ```bash
   make lint
   make typecheck
   make test-unit
   ```
5. Abra o Pull Request preenchendo o template (o que mudou, por que, como testar).

## Convencao de commits

Mensagens curtas, no imperativo, em portugues ou ingles (consistente por PR):

```
feat: adiciona regra de interacao IECA+espironolactona
fix: corrige calculo de duracao de prescricao para PPI cronico
docs: atualiza README com instrucoes de Docker Compose
test: cobre caso de paciente sem eGFR informado
refactor: extrai _atc_matches para modulo compartilhado
```

## Alteracoes em conteudo clinico (criterios Beers/DDI)

Qualquer mudanca em `sql/seed_beers_pim.sql` ou nas regras de dominio que
afete um alerta clinico **exige** citacao da fonte na descricao do PR
(ver template de issue "Novo criterio clinico") e revisao por ao menos
uma pessoa com background clinico/farmaceutico, quando disponivel.

## Padroes de codigo

- Python 3.11+, tipagem completa (`mypy --strict` deve passar).
- `ruff` para lint/format (`make lint`).
- Arquitetura em camadas: `domain/` nao importa de `infrastructure/` ou `interface/`.
- Cobertura de testes minima: 80% (`pytest --cov-fail-under=80`, ja configurado).

## Governanca do repositorio

- A branch `main` e **protegida**: mudancas entram via Pull Request com o CI
  verde (lint, mypy, security-scan, testes e build Docker). Force-push e delecao
  sao bloqueados e o historico e linear.
- `.github/CODEOWNERS` solicita revisao automatica do mantenedor, especialmente
  em conteudo clinico (`sql/`, `domain/`) e seguranca.
- Roadmap organizado em milestones (v0.2, v0.3, v1.0) — ver as issues abertas.

## Codigo de conduta

Este projeto adota o [Contributor Covenant](CODE_OF_CONDUCT.md). Ao participar,
espera-se que voce respeite seus termos. Seja respeitoso e construtivo:
discussoes clinicas podem ser tecnicas e divergentes — mantenha o foco em
evidencia e seguranca do paciente.
