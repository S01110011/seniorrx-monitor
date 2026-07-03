# MLOps Strategy

## Model versioning — MLflow
- Every training run (`src/seniorrx/infrastructure/ml/train.py`) logs parameters,
  metrics (ROC-AUC), and the model artifact to an MLflow Tracking Server
  (`MLFLOW_TRACKING_URI`).
- Promoting a model to "Production" in the MLflow Model Registry is a manual step
  (a human gate), never automatic — a clinical risk decision requires review.

## Data versioning — DVC
- `data/raw/` and `data/processed/` are versioned with [DVC](https://dvc.org/),
  pointing to a storage remote (S3/GCS/Azure Blob) outside the git repository.
- Setup: `dvc init && dvc remote add -d storage <url> && dvc add data/raw`.
- This guarantees exact reproducibility of which data snapshot produced which model.

## Monitoring — Evidently AI
- `.github/workflows/model-monitoring.yml` runs weekly, generating a
  `DataDriftPreset` that compares the most recent batch against the training
  dataset.
- Significant drift alerts should open an automatic issue (future integration, see
  `docs/roadmap.md` v0.3) and trigger a manual retrain reviewed by a responsible
  clinical pharmacist / data scientist.

## Reproducibility
- `docker-compose.yml` pins Postgres/Python versions; `pyproject.toml` pins minimum
  dependency versions.
- Fixed seeds (`--seed`) in all data-generation scripts and in the train/test split.
- Full bootstrap pipeline: `scripts/run_pipeline.sh`.

## Quality gate before a new model reaches production
1. Holdout ROC-AUC ≥ current baseline − 0.02 (no significant regression allowed).
2. Human review of the `feature_importances_` table (nothing clinically
   implausible).
3. The rule unit tests (Beers/DDI/polypharmacy) still pass 100% — the ML model is
   always complementary to the deterministic rules, never a replacement for them.
