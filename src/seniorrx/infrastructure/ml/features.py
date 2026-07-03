"""Engenharia de features para o modelo de risco de evento adverso a medicamento (RAM).

Features derivadas exclusivamente de dados ja modelados no dominio (idade,
contagem de medicamentos/PIM/comorbidades, funcao renal) — sem PII.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from seniorrx.domain.entities import AlertType, BeersCriterion, Patient
from seniorrx.domain.rules.beers_rules import BeersRulesEngine
from seniorrx.domain.rules.interaction_rules import InteractionRulesEngine

FEATURE_COLUMNS = [
    "age",
    "active_medication_count",
    "pim_count",
    "ddi_count",
    "comorbidity_count",
    "egfr_ml_min_1_73m2",
    "has_renal_impairment",
    "is_hyperpolypharmacy",
]


def build_feature_row(patient: Patient, beers_criteria: list[BeersCriterion]) -> dict[str, Any]:
    beers_engine = BeersRulesEngine(beers_criteria)
    interaction_engine = InteractionRulesEngine(beers_criteria)

    pim_alerts = beers_engine.evaluate_patient(patient)
    ddi_alerts = [
        a
        for a in interaction_engine.evaluate_patient(patient)
        if a.alert_type == AlertType.DRUG_DRUG_INTERACTION
    ]

    egfr = patient.egfr_ml_min_1_73m2
    return {
        "patient_id": str(patient.patient_id),
        "age": patient.age,
        "active_medication_count": len(patient.active_prescriptions),
        "pim_count": len(pim_alerts),
        "ddi_count": len(ddi_alerts),
        "comorbidity_count": len(patient.active_comorbidity_codes),
        "egfr_ml_min_1_73m2": egfr if egfr is not None else 90.0,
        "has_renal_impairment": int(egfr is not None and egfr < 60),
        "is_hyperpolypharmacy": int(len(patient.active_prescriptions) >= 10),
    }


def build_feature_frame(patients: list[Patient], beers_criteria: list[BeersCriterion]) -> pd.DataFrame:
    rows = [build_feature_row(p, beers_criteria) for p in patients]
    return pd.DataFrame(rows)
