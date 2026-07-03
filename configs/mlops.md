# Estrategia de MLOps

## Versionamento de modelo — MLflow
- Todo treino (`src/seniorrx/infrastructure/ml/train.py`) registra parametros, metricas
  (ROC-AUC) e artefato do modelo em um MLflow Tracking Server (`MLFLOW_TRACKING_URI`).
- Promocao de modelo para "Production" no MLflow Model Registry e um passo manual
  (gate humano), nunca automatico — decisao clinica de risco exige revisao.

## Versionamento de dados — DVC
- `data/raw/` e `data/processed/` sao versionados via [DVC](https://dvc.org/) apontando
  para um remote de armazenamento (S3/GCS/Azure Blob) fora do repositorio git.
- Setup: `dvc init && dvc remote add -d storage <url> && dvc add data/raw`.
- Isso garante reprodutibilidade exata de qual snapshot de dados gerou qual modelo.

## Monitoramento — Evidently AI
- `.github/workflows/model-monitoring.yml` roda semanalmente, gerando um
  `DataDriftPreset` comparando o batch mais recente contra o dataset de treino.
- Alertas de drift significativo devem abrir uma issue automatica (integracao futura,
  ver `docs/roadmap.md` v0.3) e disparar retrain manual revisado por um farmaceutico
  clinico/cientista de dados responsavel.

## Reprodutibilidade
- `docker-compose.yml` fixa versoes de Postgres/Python; `pyproject.toml` fixa
  versoes minimas de dependencias.
- Seeds fixas (`--seed`) em todos os scripts de geracao de dados e split de treino/teste.
- Pipeline completo de bootstrap: `scripts/run_pipeline.sh`.

## Gate de qualidade antes de novo modelo entrar em producao
1. ROC-AUC em holdout >= baseline atual - 0.02 (nao pode regredir significativamente).
2. Revisao humana da tabela `feature_importances_` (nada clinicamente implausivel).
3. Testes unitarios de regras (Beers/DDI/polifarmacia) continuam 100% passando —
   o modelo de ML e sempre complementar as regras determinísticas, nunca as substitui.
