from __future__ import annotations

from seniorrx.application.services.risk_scoring_service import RiskScoringService
from tests.conftest import MED_DIAZEPAM, MED_GLIBENCLAMIDA, MED_IBUPROFENO, MED_VARFARINA, make_prescription


def test_low_risk_when_no_alerts(beers_criteria, elderly_patient_factory):
    patient = elderly_patient_factory()

    assessment = RiskScoringService(beers_criteria).assess(patient)

    assert assessment.rule_based_risk_level == "BAIXO"
    assert assessment.pim_count == 0
    assert assessment.alerts == []


def test_critical_risk_when_critical_ddi_present(beers_criteria, elderly_patient_factory):
    rx_warfarin = make_prescription(MED_VARFARINA, None)
    rx_ibuprofen = make_prescription(MED_IBUPROFENO, None)
    patient = elderly_patient_factory(prescriptions=(rx_warfarin, rx_ibuprofen))

    assessment = RiskScoringService(beers_criteria).assess(patient)

    assert assessment.rule_based_risk_level == "CRITICO"
    assert assessment.ddi_count == 1


def test_high_risk_with_two_high_severity_pims(beers_criteria, elderly_patient_factory):
    rx_glib = make_prescription(MED_GLIBENCLAMIDA, None)
    rx_diazepam = make_prescription(MED_DIAZEPAM, None)
    patient = elderly_patient_factory(prescriptions=(rx_glib, rx_diazepam))

    assessment = RiskScoringService(beers_criteria).assess(patient)

    assert assessment.pim_count == 2
    assert assessment.rule_based_risk_level == "ALTO"


def test_ml_probability_passthrough(beers_criteria, elderly_patient_factory):
    patient = elderly_patient_factory()

    assessment = RiskScoringService(beers_criteria, model_version="rf-v0.1.0").assess(
        patient, ml_probability=0.42
    )

    assert assessment.ml_adverse_event_probability == 0.42
    assert assessment.model_version == "rf-v0.1.0"
