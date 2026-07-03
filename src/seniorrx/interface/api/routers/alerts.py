from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from seniorrx.application.services.risk_scoring_service import RiskScoringService
from seniorrx.infrastructure.db.database import get_session
from seniorrx.infrastructure.db.repositories import BeersCriteriaRepository, PatientRepository
from seniorrx.interface.api.schemas import AlertOut, RiskAssessmentOut

router = APIRouter(prefix="/patients", tags=["alerts"])


@router.get("/{patient_id}/risk-assessment", response_model=RiskAssessmentOut)
def get_risk_assessment(patient_id: UUID, session: Session = Depends(get_session)) -> RiskAssessmentOut:
    patient = PatientRepository(session).get_with_clinical_data(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente nao encontrado")

    criteria = BeersCriteriaRepository(session).list_all()
    assessment = RiskScoringService(criteria).assess(patient)

    return RiskAssessmentOut(
        patient_id=assessment.patient_id,
        active_medication_count=assessment.active_medication_count,
        pim_count=assessment.pim_count,
        ddi_count=assessment.ddi_count,
        comorbidity_count=assessment.comorbidity_count,
        rule_based_risk_level=assessment.rule_based_risk_level,
        ml_adverse_event_probability=assessment.ml_adverse_event_probability,
        model_version=assessment.model_version,
        alerts=[AlertOut(**vars(a)) for a in assessment.alerts],
    )
