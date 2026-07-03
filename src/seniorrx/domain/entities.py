"""Entidades de dominio puras (sem dependencia de framework/ORM/DB).

Mantidas como dataclasses imutaveis para permitir uso identico em
testes, notebooks, API e jobs batch, sem acoplamento a infraestrutura.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any
from uuid import UUID


class Sex(StrEnum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class CriteriaType(StrEnum):
    INDEPENDENT_OF_DIAGNOSIS = "PIM_INDEPENDENTE_DIAGNOSTICO"
    DISEASE_SPECIFIC = "PIM_CONDICAO_ESPECIFICA"
    USE_WITH_CAUTION = "USAR_COM_CAUTELA"
    DRUG_DRUG_INTERACTION = "INTERACAO_MEDICAMENTO_MEDICAMENTO"
    RENAL_ADJUSTMENT = "AJUSTE_FUNCAO_RENAL"


class AlertType(StrEnum):
    PIM_BEERS = "PIM_BEERS"
    POLYPHARMACY = "POLIFARMACIA"
    HYPER_POLYPHARMACY = "HIPERPOLIFARMACIA"
    DRUG_DRUG_INTERACTION = "INTERACAO_MEDICAMENTOSA"
    DISEASE_DRUG_INTERACTION = "INTERACAO_DOENCA_MEDICAMENTO"
    RENAL_ADJUSTMENT = "AJUSTE_RENAL"


class Severity(StrEnum):
    LOW = "BAIXA"
    MODERATE = "MODERADA"
    HIGH = "ALTA"
    CRITICAL = "CRITICA"

    @property
    def rank(self) -> int:
        return {"BAIXA": 0, "MODERADA": 1, "ALTA": 2, "CRITICA": 3}[self.value]


class RiskLevel(StrEnum):
    LOW = "BAIXO"
    MODERATE = "MODERADO"
    HIGH = "ALTO"
    CRITICAL = "CRITICO"


@dataclass(frozen=True)
class Comorbidity:
    icd10_code: str
    description: str
    diagnosed_on: date | None = None
    active: bool = True


@dataclass(frozen=True)
class Medication:
    medication_id: int
    drug_name: str
    atc_code: str
    drug_class: str
    route: str = "oral"
    is_high_alert: bool = False


@dataclass(frozen=True)
class Prescription:
    prescription_id: UUID
    patient_id: UUID
    medication: Medication
    dose_value: float | None
    dose_unit: str | None
    frequency_per_day: float | None
    indication_icd10: str | None
    start_date: date
    end_date: date | None = None

    @property
    def is_active(self) -> bool:
        return self.end_date is None or self.end_date >= date.today()

    @property
    def duration_days(self) -> int:
        end = self.end_date or date.today()
        return (end - self.start_date).days


@dataclass(frozen=True)
class Patient:
    patient_id: UUID
    pseudonym: str
    birth_year: int
    sex: Sex
    weight_kg: float | None = None
    height_cm: float | None = None
    serum_creatinine_mg_dl: float | None = None
    egfr_ml_min_1_73m2: float | None = None
    care_setting: str = "ambulatorial"
    comorbidities: tuple[Comorbidity, ...] = field(default_factory=tuple)
    prescriptions: tuple[Prescription, ...] = field(default_factory=tuple)

    @property
    def age(self) -> int:
        return date.today().year - self.birth_year

    @property
    def is_elderly(self) -> bool:
        """Elegibilidade Beers 2023: pacientes com 65 anos ou mais."""
        return self.age >= 65

    @property
    def active_prescriptions(self) -> tuple[Prescription, ...]:
        return tuple(p for p in self.prescriptions if p.is_active)

    @property
    def active_comorbidity_codes(self) -> frozenset[str]:
        return frozenset(c.icd10_code for c in self.comorbidities if c.active)


@dataclass(frozen=True)
class BeersCriterion:
    criterion_id: int
    criteria_type: CriteriaType
    drug_or_class: str
    atc_pattern: str | None
    organ_system: str | None
    rationale: str
    recommendation: str
    related_condition_icd10: str | None = None
    interacting_atc_pattern: str | None = None
    egfr_threshold_ml_min: float | None = None
    severity_default: Severity = Severity.MODERATE
    source_reference: str = (
        "American Geriatrics Society 2023 Updated AGS Beers Criteria(R). "
        "J Am Geriatr Soc. 2023;71(7):2052-2081."
    )


@dataclass(frozen=True)
class Alert:
    patient_id: UUID
    alert_type: AlertType
    severity: Severity
    message: str
    prescription_id: UUID | None = None
    criterion_id: int | None = None


@dataclass(frozen=True)
class RiskScore:
    patient_id: UUID
    active_medication_count: int
    pim_count: int
    ddi_count: int
    comorbidity_count: int
    rule_based_risk_level: RiskLevel
    ml_adverse_event_probability: float | None = None
    model_version: str | None = None
    explanation: dict[str, Any] | None = None
