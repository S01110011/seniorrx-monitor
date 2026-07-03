from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from seniorrx.infrastructure.db.database import get_session
from seniorrx.infrastructure.db.repositories import PatientRepository
from seniorrx.interface.api.schemas import PatientSummary

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientSummary])
def list_patients(session: Session = Depends(get_session)) -> list[PatientSummary]:
    patients = PatientRepository(session).list_all_with_clinical_data()
    return [
        PatientSummary(
            patient_id=p.patient_id,
            pseudonym=p.pseudonym,
            age=p.age,
            sex=p.sex.value,
            care_setting=p.care_setting,
        )
        for p in patients
    ]


@router.get("/{patient_id}", response_model=PatientSummary)
def get_patient(patient_id: UUID, session: Session = Depends(get_session)) -> PatientSummary:
    patient = PatientRepository(session).get_with_clinical_data(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente nao encontrado")
    return PatientSummary(
        patient_id=patient.patient_id,
        pseudonym=patient.pseudonym,
        age=patient.age,
        sex=patient.sex.value,
        care_setting=patient.care_setting,
    )
