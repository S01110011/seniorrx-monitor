"""Motor de regras: PIM segundo AGS Beers Criteria 2023.

Cobre os dois primeiros tipos de criterio da tabela oficial:
  1. PIM independente de diagnostico (ex.: benzodiazepinicos em qualquer idoso);
  2. PIM especifico por condicao/doenca (ex.: AINE em paciente com IC).

Interacoes medicamento-medicamento e ajuste por funcao renal sao tratados em
`interaction_rules.py`, que reusa esta mesma tabela de criterios (todos vem de
`beers_pim_criteria`) mas com logica de casamento diferente.
"""

from __future__ import annotations

from seniorrx.domain.entities import (
    Alert,
    AlertType,
    BeersCriterion,
    CriteriaType,
    Patient,
    Prescription,
)
from seniorrx.domain.value_objects import (
    METOCLOPRAMIDE_CHRONIC_USE_DAYS,
    PPI_CHRONIC_USE_DAYS,
)

# ATC prefixes cujo criterio so se aplica acima de um limiar de uso continuo.
_CHRONIC_USE_ATC_THRESHOLDS = {
    "A02BC": PPI_CHRONIC_USE_DAYS,          # inibidores de bomba de protons
    "A03FA01": METOCLOPRAMIDE_CHRONIC_USE_DAYS,  # metoclopramida
}


def _atc_matches(atc_code: str, pattern: str | None) -> bool:
    if not pattern:
        return False
    return atc_code.upper().startswith(pattern.upper())


class BeersRulesEngine:
    """Avalia as prescricoes ativas de um paciente contra os criterios Beers 2023."""

    def __init__(self, criteria: list[BeersCriterion]) -> None:
        self._independent_criteria = [
            c for c in criteria if c.criteria_type == CriteriaType.INDEPENDENT_OF_DIAGNOSIS
        ]
        self._disease_specific_criteria = [
            c for c in criteria if c.criteria_type == CriteriaType.DISEASE_SPECIFIC
        ]

    def evaluate_patient(self, patient: Patient) -> list[Alert]:
        if not patient.is_elderly:
            return []

        alerts: list[Alert] = []
        for prescription in patient.active_prescriptions:
            alerts.extend(self._evaluate_prescription(patient, prescription))
        return alerts

    def _evaluate_prescription(self, patient: Patient, prescription: Prescription) -> list[Alert]:
        alerts: list[Alert] = []
        atc = prescription.medication.atc_code

        for criterion in self._independent_criteria:
            if not _atc_matches(atc, criterion.atc_pattern):
                continue
            if not self._chronic_threshold_met(criterion, prescription):
                continue
            alerts.append(self._build_pim_alert(patient, prescription, criterion))

        for criterion in self._disease_specific_criteria:
            if not _atc_matches(atc, criterion.atc_pattern):
                continue
            if criterion.related_condition_icd10 and not self._patient_has_condition(
                patient, criterion.related_condition_icd10
            ):
                continue
            alerts.append(self._build_pim_alert(patient, prescription, criterion))

        return alerts

    @staticmethod
    def _chronic_threshold_met(criterion: BeersCriterion, prescription: Prescription) -> bool:
        threshold_days = _CHRONIC_USE_ATC_THRESHOLDS.get(criterion.atc_pattern or "")
        if threshold_days is None:
            return True
        return prescription.duration_days >= threshold_days

    @staticmethod
    def _patient_has_condition(patient: Patient, icd10_prefix: str) -> bool:
        return any(code.startswith(icd10_prefix) for code in patient.active_comorbidity_codes)

    @staticmethod
    def _build_pim_alert(patient: Patient, prescription: Prescription, criterion: BeersCriterion) -> Alert:
        message = (
            f"PIM (Beers 2023): {prescription.medication.drug_name} — {criterion.drug_or_class}. "
            f"Racional: {criterion.rationale} Recomendacao: {criterion.recommendation}"
        )
        return Alert(
            patient_id=patient.patient_id,
            alert_type=AlertType.PIM_BEERS,
            severity=criterion.severity_default,
            message=message,
            prescription_id=prescription.prescription_id,
            criterion_id=criterion.criterion_id,
        )
