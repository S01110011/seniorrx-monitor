"""Contratos Pydantic da API publica. Nunca expor PII — apenas patient_id (UUID) e pseudonimo."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PatientSummary(BaseModel):
    patient_id: UUID
    pseudonym: str
    age: int
    sex: str
    care_setting: str


class AlertOut(BaseModel):
    alert_type: str
    severity: str
    message: str
    prescription_id: UUID | None = None
    criterion_id: int | None = None


class RiskAssessmentOut(BaseModel):
    patient_id: UUID
    active_medication_count: int
    pim_count: int
    ddi_count: int
    comorbidity_count: int
    rule_based_risk_level: str
    ml_adverse_event_probability: float | None = None
    model_version: str | None = None
    alerts: list[AlertOut]


class PrescriptionIn(BaseModel):
    medication_id: int
    prescriber_pseudonym: str = Field(..., min_length=1, max_length=32)
    dose_value: float | None = None
    dose_unit: str | None = None
    frequency_per_day: float | None = None
    indication_icd10: str | None = None
    start_date: date
    end_date: date | None = None


class HealthOut(BaseModel):
    status: str
    version: str
