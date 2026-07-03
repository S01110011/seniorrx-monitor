from __future__ import annotations

import pytest

from seniorrx.infrastructure.db.models import MedicationModel, PatientModel

pytestmark = pytest.mark.integration


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_security_headers_present(client):
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "Content-Security-Policy" in response.headers


def test_list_patients_empty(client):
    response = client.get("/patients")

    assert response.status_code == 200
    assert response.json() == []


def test_get_risk_assessment_for_seeded_patient(client, db_session):
    import uuid

    medication = MedicationModel(
        drug_name="Diazepam", atc_code="N05BA01", drug_class="Benzodiazepinico", route="oral"
    )
    db_session.add(medication)
    db_session.flush()

    patient = PatientModel(
        patient_id=uuid.uuid4(),
        pseudonym="paciente-teste-001",
        birth_year=1945,
        sex="F",
        care_setting="ambulatorial",
    )
    db_session.add(patient)
    db_session.commit()

    response = client.get(f"/patients/{patient.patient_id}/risk-assessment")

    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == str(patient.patient_id)
    assert "rule_based_risk_level" in body
