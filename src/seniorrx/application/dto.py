"""Data Transfer Objects usados entre a camada de aplicacao e a interface (API/dashboard).

Mantidos separados das entidades de dominio para nao vazar detalhes internos
(ex.: enums de dominio) diretamente para os contratos externos.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AlertDTO:
    patient_id: UUID
    alert_type: str
    severity: str
    message: str
    prescription_id: UUID | None
    criterion_id: int | None


@dataclass(frozen=True)
class RiskAssessmentDTO:
    patient_id: UUID
    active_medication_count: int
    pim_count: int
    ddi_count: int
    comorbidity_count: int
    rule_based_risk_level: str
    ml_adverse_event_probability: float | None
    model_version: str | None
    alerts: list[AlertDTO]
