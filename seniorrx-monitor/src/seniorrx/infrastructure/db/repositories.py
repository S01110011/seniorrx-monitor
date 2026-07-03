"""Repositorios: traduzem entre modelos ORM (infra) e entidades de dominio.

Mantem a camada de dominio livre de SQLAlchemy — os servicos de aplicacao
recebem/retornam apenas `seniorrx.domain.entities`.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from seniorrx.domain.entities import (
    BeersCriterion,
    Comorbidity,
    CriteriaType,
    Medication,
    Patient,
    Prescription,
    Severity,
    Sex,
)
from seniorrx.infrastructure.db.models import (
    BeersPimCriterionModel,
    MedicationModel,
    PatientModel,
    PrescriptionModel,
)


class BeersCriteriaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[BeersCriterion]:
        rows = self._session.scalars(select(BeersPimCriterionModel)).all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: BeersPimCriterionModel) -> BeersCriterion:
        return BeersCriterion(
            criterion_id=row.criterion_id,
            criteria_type=CriteriaType(row.criteria_type),
            drug_or_class=row.drug_or_class,
            atc_pattern=row.atc_pattern,
            organ_system=row.organ_system,
            rationale=row.rationale,
            recommendation=row.recommendation,
            related_condition_icd10=row.related_condition_icd10,
            interacting_atc_pattern=row.interacting_atc_pattern,
            egfr_threshold_ml_min=float(row.egfr_threshold_ml_min) if row.egfr_threshold_ml_min else None,
            severity_default=Severity(row.severity_default),
            source_reference=row.source_reference,
        )


class PatientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_with_clinical_data(self, patient_id: UUID) -> Patient | None:
        row = self._session.scalar(
            select(PatientModel)
            .options(
                selectinload(PatientModel.comorbidities),
                selectinload(PatientModel.prescriptions).selectinload(PrescriptionModel.medication),
            )
            .where(PatientModel.patient_id == patient_id)
        )
        return self._to_entity(row) if row else None

    def list_all_with_clinical_data(self) -> list[Patient]:
        rows = self._session.scalars(
            select(PatientModel).options(
                selectinload(PatientModel.comorbidities),
                selectinload(PatientModel.prescriptions).selectinload(PrescriptionModel.medication),
            )
        ).all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: PatientModel) -> Patient:
        return Patient(
            patient_id=row.patient_id,
            pseudonym=row.pseudonym,
            birth_year=row.birth_year,
            sex=Sex(row.sex),
            weight_kg=float(row.weight_kg) if row.weight_kg else None,
            height_cm=float(row.height_cm) if row.height_cm else None,
            serum_creatinine_mg_dl=float(row.serum_creatinine_mg_dl) if row.serum_creatinine_mg_dl else None,
            egfr_ml_min_1_73m2=float(row.egfr_ml_min_1_73m2) if row.egfr_ml_min_1_73m2 else None,
            care_setting=row.care_setting,
            comorbidities=tuple(
                Comorbidity(
                    icd10_code=c.icd10_code,
                    description=c.description,
                    diagnosed_on=c.diagnosed_on,
                    active=c.active,
                )
                for c in row.comorbidities
            ),
            prescriptions=tuple(
                Prescription(
                    prescription_id=p.prescription_id,
                    patient_id=p.patient_id,
                    medication=Medication(
                        medication_id=p.medication.medication_id,
                        drug_name=p.medication.drug_name,
                        atc_code=p.medication.atc_code,
                        drug_class=p.medication.drug_class,
                        route=p.medication.route,
                        is_high_alert=p.medication.is_high_alert,
                    ),
                    dose_value=float(p.dose_value) if p.dose_value else None,
                    dose_unit=p.dose_unit,
                    frequency_per_day=float(p.frequency_per_day) if p.frequency_per_day else None,
                    indication_icd10=p.indication_icd10,
                    start_date=p.start_date,
                    end_date=p.end_date,
                )
                for p in row.prescriptions
            ),
        )


class MedicationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_name(self, drug_name: str) -> MedicationModel | None:
        return self._session.scalar(select(MedicationModel).where(MedicationModel.drug_name == drug_name))
