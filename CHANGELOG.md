# Changelog

Este projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/) e o
formato de [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Unreleased]

### Seguranca
- Autenticacao de API endurecida: comparacao de key em tempo constante
  (`hmac.compare_digest`) e fail-closed em producao (`SENIORRX_ENV=production`).
- Middleware de cabecalhos de seguranca (CSP, HSTS, nosniff, X-Frame-Options, etc.).
- Rate limiting por IP via `slowapi` (`SENIORRX_RATE_LIMIT`).
- `.dockerignore` impedindo vazamento de `.env`/`.git`/dados nas imagens.
- Job de CI `security-scan`: bandit (SAST), pip-audit (CVEs) e gitleaks (segredos).
- Correcao de schema PostgreSQL (coluna gerada nao-imutavel em `prescriptions`).

### Adicionado
- Estrutura inicial do projeto (arquitetura limpa: domain/application/infrastructure/interface).
- Schema SQL PostgreSQL com tabelas de pacientes, comorbidades, medicamentos,
  criterios Beers 2023, prescricoes, alertas e scores de risco.
- Subconjunto ilustrativo de criterios AGS Beers 2023 (PIM independente de
  diagnostico, condicao especifica, interacao medicamento-medicamento, ajuste renal).
- Motor de regras em Python: `BeersRulesEngine`, `PolypharmacyRulesEngine`, `InteractionRulesEngine`.
- Servico de aplicacao `RiskScoringService` consolidando alertas em nivel de risco.
- API FastAPI (`/patients`, `/patients/{id}/risk-assessment`, `/patients/{id}/prescriptions`).
- Dashboard Streamlit para visualizacao interativa de alertas por paciente.
- Pipeline de dados sinteticos + ETL (`scripts/generate_synthetic_data.py`, `scripts/etl_pipeline.py`).
- Modelo de ML (RandomForest) para probabilidade de evento adverso, com treino via MLflow.
- Suite de testes unitarios e de integracao (pytest), cobertura minima 80%.
- CI/CD via GitHub Actions (lint, typecheck, testes, build Docker) + job semanal de drift (Evidently AI).
- Relatorio reprodutivel em R/Quarto com analise epidemiologica descritiva.
- Documentacao tecnica completa em `docs/`.

## [0.1.0] - a definir no primeiro release
Primeira versao publica (prototipo). Ver `docs/roadmap.md`.
