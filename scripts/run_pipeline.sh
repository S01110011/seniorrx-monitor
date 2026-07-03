#!/usr/bin/env bash
# Pipeline completo de bootstrap: banco -> dados sinteticos -> ETL -> treino do modelo.
# Uso: bash scripts/run_pipeline.sh
set -euo pipefail

: "${DATABASE_URL:=postgresql://seniorrx:seniorrx@localhost:5432/seniorrx}"

echo "==> 1/4 Inicializando schema + criterios Beers 2023"
python scripts/init_db.py --database-url "$DATABASE_URL"

echo "==> 2/4 Gerando dados sinteticos"
python scripts/generate_synthetic_data.py --n-patients 500 --seed 42

echo "==> 3/4 Executando ETL (CSV -> PostgreSQL)"
python scripts/etl_pipeline.py --input-dir data/raw

echo "==> 4/4 Construindo dataset de treino e treinando modelo de risco"
python scripts/build_training_set.py --output data/processed/training_set.parquet
python -m seniorrx.infrastructure.ml.train --data data/processed/training_set.parquet

echo "Pipeline concluido. Suba a API com: uvicorn seniorrx.interface.api.main:app --reload"
