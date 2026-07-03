"""Constroi o dataset de treino do modelo de ML a partir dos dados sinteticos
carregados no banco: aplica feature engineering + gera rotulo proxy `adverse_event`.

O rotulo NAO representa um desfecho clinico real — e uma variavel latente
sintetica, calibrada para correlacionar com contagem de PIM/polifarmacia/eGFR
baixo, apenas para viabilizar o pipeline de MLOps de ponta a ponta.
Substituir por rotulo clinico real (ex.: reinternacao por RAM em 30 dias)
antes de qualquer uso assistencial — ver docs/clinical_validation.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from seniorrx.infrastructure.db.database import SessionLocal
from seniorrx.infrastructure.db.repositories import BeersCriteriaRepository, PatientRepository
from seniorrx.infrastructure.ml.features import build_feature_frame


def synthesize_label(features, rng: np.random.Generator):
    logit = (
        -3.5
        + 0.35 * features["pim_count"]
        + 0.25 * features["ddi_count"]
        + 0.15 * features["active_medication_count"]
        + 0.8 * features["has_renal_impairment"]
        + 0.02 * (features["age"] - 65)
    )
    probability = 1 / (1 + np.exp(-logit))
    return rng.binomial(1, probability)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/processed/training_set.parquet"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    session = SessionLocal()
    try:
        patients = PatientRepository(session).list_all_with_clinical_data()
        criteria = BeersCriteriaRepository(session).list_all()
    finally:
        session.close()

    features = build_feature_frame(patients, criteria)
    rng = np.random.default_rng(args.seed)
    features["adverse_event"] = synthesize_label(features, rng)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(args.output, index=False)
    print(f"Dataset de treino salvo em {args.output} ({len(features)} pacientes, "
          f"prevalencia do rotulo: {features['adverse_event'].mean():.1%})")


if __name__ == "__main__":
    main()
