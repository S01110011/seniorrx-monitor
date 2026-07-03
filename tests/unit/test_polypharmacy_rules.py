from __future__ import annotations

from seniorrx.domain.entities import AlertType, Medication
from seniorrx.domain.rules.polypharmacy_rules import PolypharmacyRulesEngine
from tests.conftest import make_prescription


def _make_n_prescriptions(n: int, patient_id):
    return tuple(
        make_prescription(Medication(i, f"Droga{i}", f"X0{i}A", "classe generica"), patient_id)
        for i in range(n)
    )


def test_no_alert_below_threshold(elderly_patient_factory):
    patient = elderly_patient_factory()
    patient = elderly_patient_factory(
        patient_id=patient.patient_id, prescriptions=_make_n_prescriptions(4, patient.patient_id)
    )

    alerts = PolypharmacyRulesEngine().evaluate_patient(patient)

    assert alerts == []


def test_polypharmacy_alert_at_five_medications(elderly_patient_factory):
    patient = elderly_patient_factory()
    patient = elderly_patient_factory(
        patient_id=patient.patient_id, prescriptions=_make_n_prescriptions(5, patient.patient_id)
    )

    alerts = PolypharmacyRulesEngine().evaluate_patient(patient)

    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.POLYPHARMACY


def test_hyper_polypharmacy_alert_at_ten_medications(elderly_patient_factory):
    patient = elderly_patient_factory()
    patient = elderly_patient_factory(
        patient_id=patient.patient_id, prescriptions=_make_n_prescriptions(10, patient.patient_id)
    )

    alerts = PolypharmacyRulesEngine().evaluate_patient(patient)

    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.HYPER_POLYPHARMACY
