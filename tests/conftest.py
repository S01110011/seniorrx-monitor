"""Fixtures compartilhadas: pacientes/medicamentos/criterios de teste,
construidos em memoria (sem tocar o banco) para os testes unitarios de dominio.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest

from seniorrx.domain.entities import (
    BeersCriterion,
    CriteriaType,
    Medication,
    Patient,
    Prescription,
    Severity,
    Sex,
)

MED_GLIBENCLAMIDA = Medication(1, "Glibenclamida", "A10BB01", "Sulfonilureia de longa acao")
MED_DIAZEPAM = Medication(2, "Diazepam", "N05BA01", "Benzodiazepinico (longa acao)")
MED_IBUPROFENO = Medication(3, "Ibuprofeno", "M01AE01", "AINE nao seletivo")
MED_VARFARINA = Medication(4, "Varfarina", "B01AA03", "Anticoagulante")
MED_METFORMINA = Medication(5, "Metformina", "A10BA02", "Biguanida")
MED_TRAMADOL = Medication(6, "Tramadol", "N02AX02", "Opioide")


@pytest.fixture
def beers_criteria() -> list[BeersCriterion]:
    return [
        BeersCriterion(
            criterion_id=1,
            criteria_type=CriteriaType.INDEPENDENT_OF_DIAGNOSIS,
            drug_or_class="Glibenclamida",
            atc_pattern="A10BB01",
            organ_system="Endocrino",
            rationale="Hipoglicemia prolongada.",
            recommendation="Evitar.",
            severity_default=Severity.HIGH,
        ),
        BeersCriterion(
            criterion_id=2,
            criteria_type=CriteriaType.INDEPENDENT_OF_DIAGNOSIS,
            drug_or_class="Benzodiazepinicos",
            atc_pattern="N05BA",
            organ_system="SNC",
            rationale="Risco de queda e delirium.",
            recommendation="Evitar.",
            severity_default=Severity.HIGH,
        ),
        BeersCriterion(
            criterion_id=3,
            criteria_type=CriteriaType.DISEASE_SPECIFIC,
            drug_or_class="AINEs em Insuficiencia Cardiaca",
            atc_pattern="M01A",
            organ_system="Cardiovascular",
            rationale="Retencao hidrica.",
            recommendation="Evitar em IC.",
            related_condition_icd10="I50",
            severity_default=Severity.HIGH,
        ),
        BeersCriterion(
            criterion_id=4,
            criteria_type=CriteriaType.DRUG_DRUG_INTERACTION,
            drug_or_class="Varfarina + AINEs",
            atc_pattern="B01AA03",
            organ_system="Hematologico",
            rationale="Risco de sangramento.",
            recommendation="Evitar combinacao.",
            interacting_atc_pattern="M01A",
            severity_default=Severity.CRITICAL,
        ),
        BeersCriterion(
            criterion_id=5,
            criteria_type=CriteriaType.RENAL_ADJUSTMENT,
            drug_or_class="Metformina em DRC avancada",
            atc_pattern="A10BA02",
            organ_system="Renal",
            rationale="Risco de acidose lactica.",
            recommendation="Suspender/ajustar se eGFR < 30.",
            egfr_threshold_ml_min=30.0,
            severity_default=Severity.HIGH,
        ),
    ]


def make_prescription(medication: Medication, patient_id, start_days_ago: int = 30, active: bool = True) -> Prescription:
    return Prescription(
        prescription_id=uuid.uuid4(),
        patient_id=patient_id,
        medication=medication,
        dose_value=10.0,
        dose_unit="mg",
        frequency_per_day=1.0,
        indication_icd10=None,
        start_date=date.today() - timedelta(days=start_days_ago),
        end_date=None if active else date.today() - timedelta(days=1),
    )


@pytest.fixture
def elderly_patient_factory():
    def _factory(**overrides) -> Patient:
        patient_id = overrides.pop("patient_id", uuid.uuid4())
        defaults = dict(
            patient_id=patient_id,
            pseudonym="test-patient",
            birth_year=date.today().year - 78,
            sex=Sex.FEMALE,
            egfr_ml_min_1_73m2=75.0,
            comorbidities=(),
            prescriptions=(),
        )
        defaults.update(overrides)
        return Patient(**defaults)

    return _factory
