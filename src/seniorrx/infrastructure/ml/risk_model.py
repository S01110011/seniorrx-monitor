"""Modelo de ML supervisionado: probabilidade de evento adverso a medicamento (RAM).

Uso previsto: sinal COMPLEMENTAR ao motor de regras Beers, nao substituto —
o rotulo de treino ("adverse_event") em dados sinteticos e uma proxy
estatistica, nao um desfecho clinico validado. Ver docs/clinical_validation.md
para a estrategia de validacao com dados reais antes de qualquer uso assistencial.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from seniorrx.infrastructure.ml.features import FEATURE_COLUMNS

MODEL_VERSION = "rf-v0.1.0"
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "risk_model.joblib"


class AdverseEventRiskModel:
    """Wrapper fino em torno de um RandomForestClassifier (scikit-learn).

    Mantido simples e interpretavel de proposito: `feature_importances_`
    ja fornece explicabilidade suficiente para o caso de uso educacional.
    Para producao, considerar XGBoost + SHAP (ver docs/architecture.md).
    """

    def __init__(self, model: RandomForestClassifier | None = None, version: str = MODEL_VERSION) -> None:
        self._model = model or RandomForestClassifier(
            n_estimators=300,
            max_depth=6,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
        )
        self.version = version

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> dict[str, Any]:
        x_train, x_test, y_train, y_test = train_test_split(
            features[FEATURE_COLUMNS], labels, test_size=0.2, random_state=42, stratify=labels
        )
        self._model.fit(x_train, y_train)
        y_pred_proba = self._model.predict_proba(x_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred_proba)
        return {"roc_auc": auc, "n_train": len(x_train), "n_test": len(x_test)}

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        proba = self._model.predict_proba(features[FEATURE_COLUMNS])[:, 1]
        return pd.Series(proba, index=features.index)

    def explain(self, features: pd.DataFrame) -> dict[str, float]:
        """Explicabilidade simples via feature_importances_ globais (nao por-instancia)."""
        return dict(
            zip(FEATURE_COLUMNS, self._model.feature_importances_.round(4).tolist(), strict=True)
        )

    def save(self, path: Path = DEFAULT_MODEL_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self._model, "version": self.version}, path)

    @classmethod
    def load(cls, path: Path = DEFAULT_MODEL_PATH) -> AdverseEventRiskModel:
        payload = joblib.load(path)
        return cls(model=payload["model"], version=payload["version"])
