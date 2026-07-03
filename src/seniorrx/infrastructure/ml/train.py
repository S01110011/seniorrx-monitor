"""Script de treino do modelo de risco, com logging de experimentos via MLflow.

Uso:
    python -m seniorrx.infrastructure.ml.train --data data/processed/training_set.parquet

O rotulo `adverse_event` no dataset de treino synthetic e gerado por
`scripts/generate_synthetic_data.py` a partir de uma funcao de risco
probabilistica (NAO um desfecho clinico real) — ver docs/clinical_validation.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import pandas as pd

from seniorrx.infrastructure.ml.features import FEATURE_COLUMNS
from seniorrx.infrastructure.ml.risk_model import AdverseEventRiskModel


def main() -> None:
    parser = argparse.ArgumentParser(description="Treina o modelo de risco de RAM do SeniorRx Monitor")
    parser.add_argument("--data", type=Path, required=True, help="Parquet/CSV com features + coluna adverse_event")
    parser.add_argument("--mlflow-uri", type=str, default="./mlruns")
    parser.add_argument("--experiment", type=str, default="seniorrx-risk-model")
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.mlflow_uri)
    mlflow.set_experiment(args.experiment)

    df = pd.read_parquet(args.data) if args.data.suffix == ".parquet" else pd.read_csv(args.data)
    labels = df["adverse_event"]

    model = AdverseEventRiskModel()

    with mlflow.start_run():
        metrics = model.fit(df, labels)
        mlflow.log_params({"n_estimators": 300, "max_depth": 6, "features": FEATURE_COLUMNS})
        mlflow.log_metrics(metrics)

        importances = model.explain(df)
        mlflow.log_dict(importances, "feature_importances.json")

        output_path = Path("data/processed/risk_model.joblib")
        model.save(output_path)
        mlflow.log_artifact(str(output_path))

        print(f"ROC-AUC (holdout): {metrics['roc_auc']:.3f}")
        print(f"Importancia das features: {importances}")


if __name__ == "__main__":
    main()
