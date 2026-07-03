"""Servico de aplicacao: orquestra os motores de regra de dominio e produz
um RiskAssessmentDTO consolidado por paciente.

Este servico e o ponto de entrada usado pela API, pelo dashboard e pelos
jobs batch de ETL — ele nao conhece SQL nem HTTP, apenas objetos de dominio.
"""

from __future__ import annotations

from seniorrx.application.dto import AlertDTO, RiskAssessmentDTO
from seniorrx.domain.entities import (
    Alert,
    AlertType,
    BeersCriterion,
    Patient,
    RiskLevel,
)
from seniorrx.domain.rules.beers_rules import BeersRulesEngine
from seniorrx.domain.rules.interaction_rules import InteractionRulesEngine
from seniorrx.domain.rules.polypharmacy_rules import PolypharmacyRulesEngine

# Thresholds do nivel de risco baseado em regras (heuristica transparente,
# calibravel — ver docs/clinical_validation.md). Complementar (nao substitui)
# a probabilidade do modelo de ML, quando disponivel.
_CRITICAL_ALERT_COUNT = 1     # qualquer alerta CRITICA -> risco CRITICO
_HIGH_ALERT_COUNT = 2         # >=2 alertas ALTA (ou 1 ALTA + polifarmacia) -> risco ALTO
_MODERATE_ALERT_COUNT = 1


class RiskScoringService:
    def __init__(self, beers_criteria: list[BeersCriterion], model_version: str | None = None) -> None:
        self._beers_engine = BeersRulesEngine(beers_criteria)
        self._interaction_engine = InteractionRulesEngine(beers_criteria)
        self._polypharmacy_engine = PolypharmacyRulesEngine()
        self._model_version = model_version

    def assess(self, patient: Patient, ml_probability: float | None = None) -> RiskAssessmentDTO:
        alerts: list[Alert] = [
            *self._beers_engine.evaluate_patient(patient),
            *self._interaction_engine.evaluate_patient(patient),
            *self._polypharmacy_engine.evaluate_patient(patient),
        ]

        pim_count = sum(1 for a in alerts if a.alert_type == AlertType.PIM_BEERS)
        ddi_count = sum(1 for a in alerts if a.alert_type == AlertType.DRUG_DRUG_INTERACTION)
        rule_based_level = self._compute_rule_based_level(alerts)

        return RiskAssessmentDTO(
            patient_id=patient.patient_id,
            active_medication_count=len(patient.active_prescriptions),
            pim_count=pim_count,
            ddi_count=ddi_count,
            comorbidity_count=len(patient.active_comorbidity_codes),
            rule_based_risk_level=rule_based_level.value,
            ml_adverse_event_probability=ml_probability,
            model_version=self._model_version if ml_probability is not None else None,
            alerts=[
                AlertDTO(
                    patient_id=a.patient_id,
                    alert_type=a.alert_type.value,
                    severity=a.severity.value,
                    message=a.message,
                    prescription_id=a.prescription_id,
                    criterion_id=a.criterion_id,
                )
                for a in alerts
            ],
        )

    @staticmethod
    def _compute_rule_based_level(alerts: list[Alert]) -> RiskLevel:
        severities = [a.severity.rank for a in alerts]
        critical_count = sum(1 for s in severities if s == 3)
        high_count = sum(1 for s in severities if s == 2)

        if critical_count >= _CRITICAL_ALERT_COUNT:
            return RiskLevel.CRITICAL
        if high_count >= _HIGH_ALERT_COUNT:
            return RiskLevel.HIGH
        if high_count >= _MODERATE_ALERT_COUNT or len(alerts) >= 2:
            return RiskLevel.MODERATE
        if alerts:
            return RiskLevel.MODERATE
        return RiskLevel.LOW
