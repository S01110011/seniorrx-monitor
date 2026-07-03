"""Motor de regras: interacoes medicamento-medicamento e ajuste por funcao renal.

Reusa a tabela `beers_pim_criteria` (criteria_type = INTERACAO_MEDICAMENTO_MEDICAMENTO
ou AJUSTE_FUNCAO_RENAL), aplicando casamento par-a-par entre todas as prescricoes
ativas do paciente.
"""

from __future__ import annotations

from itertools import combinations

from seniorrx.domain.entities import (
    Alert,
    AlertType,
    BeersCriterion,
    CriteriaType,
    Patient,
    Prescription,
)


def _atc_matches(atc_code: str, pattern: str | None) -> bool:
    if not pattern:
        return False
    return atc_code.upper().startswith(pattern.upper())


class InteractionRulesEngine:
    def __init__(self, criteria: list[BeersCriterion]) -> None:
        self._ddi_criteria = [
            c for c in criteria if c.criteria_type == CriteriaType.DRUG_DRUG_INTERACTION
        ]
        self._renal_criteria = [
            c for c in criteria if c.criteria_type == CriteriaType.RENAL_ADJUSTMENT
        ]

    def evaluate_patient(self, patient: Patient) -> list[Alert]:
        alerts: list[Alert] = []
        active = patient.active_prescriptions

        for rx_a, rx_b in combinations(active, 2):
            alerts.extend(self._evaluate_pair(patient, rx_a, rx_b))

        if patient.egfr_ml_min_1_73m2 is not None:
            for prescription in active:
                alerts.extend(self._evaluate_renal(patient, prescription))

        return alerts

    def _evaluate_pair(
        self, patient: Patient, rx_a: Prescription, rx_b: Prescription
    ) -> list[Alert]:
        alerts: list[Alert] = []
        for criterion in self._ddi_criteria:
            forward = _atc_matches(rx_a.medication.atc_code, criterion.atc_pattern) and _atc_matches(
                rx_b.medication.atc_code, criterion.interacting_atc_pattern
            )
            backward = _atc_matches(rx_b.medication.atc_code, criterion.atc_pattern) and _atc_matches(
                rx_a.medication.atc_code, criterion.interacting_atc_pattern
            )
            if not (forward or backward):
                continue
            message = (
                f"Interacao medicamentosa (Beers 2023): {rx_a.medication.drug_name} + "
                f"{rx_b.medication.drug_name} — {criterion.drug_or_class}. "
                f"Racional: {criterion.rationale} Recomendacao: {criterion.recommendation}"
            )
            alerts.append(
                Alert(
                    patient_id=patient.patient_id,
                    alert_type=AlertType.DRUG_DRUG_INTERACTION,
                    severity=criterion.severity_default,
                    message=message,
                    prescription_id=rx_a.prescription_id,
                    criterion_id=criterion.criterion_id,
                )
            )
        return alerts

    def _evaluate_renal(self, patient: Patient, prescription: Prescription) -> list[Alert]:
        alerts: list[Alert] = []
        for criterion in self._renal_criteria:
            if not _atc_matches(prescription.medication.atc_code, criterion.atc_pattern):
                continue
            if criterion.egfr_threshold_ml_min is None:
                continue
            if patient.egfr_ml_min_1_73m2 is None or patient.egfr_ml_min_1_73m2 >= criterion.egfr_threshold_ml_min:
                continue
            message = (
                f"Ajuste por funcao renal (Beers 2023): {prescription.medication.drug_name} "
                f"com eGFR={patient.egfr_ml_min_1_73m2} mL/min/1.73m2 "
                f"(limiar: {criterion.egfr_threshold_ml_min}). Recomendacao: {criterion.recommendation}"
            )
            alerts.append(
                Alert(
                    patient_id=patient.patient_id,
                    alert_type=AlertType.RENAL_ADJUSTMENT,
                    severity=criterion.severity_default,
                    message=message,
                    prescription_id=prescription.prescription_id,
                    criterion_id=criterion.criterion_id,
                )
            )
        return alerts
