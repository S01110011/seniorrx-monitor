from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from seniorrx.infrastructure.db.database import get_session
from seniorrx.infrastructure.db.models import PatientModel, PrescriptionModel
from seniorrx.interface.api.schemas import PrescriptionIn

router = APIRouter(prefix="/patients", tags=["prescriptions"])


@router.post("/{patient_id}/prescriptions", status_code=status.HTTP_201_CREATED)
def create_prescription(
    patient_id: UUID, payload: PrescriptionIn, session: Session = Depends(get_session)
) -> dict[str, str]:
    patient_exists = session.get(PatientModel, patient_id)
    if patient_exists is None:
        raise HTTPException(status_code=404, detail="Paciente nao encontrado")

    prescription = PrescriptionModel(
        prescription_id=uuid.uuid4(),
        patient_id=patient_id,
        medication_id=payload.medication_id,
        prescriber_pseudonym=payload.prescriber_pseudonym,
        dose_value=payload.dose_value,
        dose_unit=payload.dose_unit,
        frequency_per_day=payload.frequency_per_day,
        indication_icd10=payload.indication_icd10,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    session.add(prescription)
    session.commit()
    return {"prescription_id": str(prescription.prescription_id)}
