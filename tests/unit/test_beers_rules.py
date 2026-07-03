from __future__ import annotations

from seniorrx.domain.entities import AlertType, Comorbidity
from seniorrx.domain.rules.beers_rules import BeersRulesEngine
from tests.conftest import MED_DIAZEPAM, MED_GLIBENCLAMIDA, MED_IBUPROFENO, make_prescription


def test_flags_glibenclamida_as_pim_independent_of_diagnosis(beers_criteria, elderly_patient_factory):
    patient = elderly_patient_factory()
    prescription = make_prescription(MED_GLIBENCLAMIDA, patient.patient_id)
    patient = elderly_patient_factory(patient_id=patient.patient_id, prescriptions=(prescription,))

    alerts = BeersRulesEngine(beers_criteria).evaluate_patient(patient)

    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.PIM_BEERS
    assert "Glibenclamida" in alerts[0].message


def test_does_not_flag_patient_under_65(beers_criteria, elderly_patient_factory):
    from datetime import date

    prescription = make_prescription(MED_GLIBENCLAMIDA, None)
    younger_patient = elderly_patient_factory(
        birth_year=date.today().year - 50, prescriptions=(prescription,)
    )

    alerts = BeersRulesEngine(beers_criteria).evaluate_patient(younger_patient)

    assert alerts == []


def test_flags_nsaid_in_patient_with_heart_failure(beers_criteria, elderly_patient_factory):
    prescription = make_prescription(MED_IBUPROFENO, None)
    patient = elderly_patient_factory(
        prescriptions=(prescription,),
        comorbidities=(Comorbidity(icd10_code="I50.0", description="ICC"),),
    )

    alerts = BeersRulesEngine(beers_criteria).evaluate_patient(patient)

    assert len(alerts) == 1
    assert "AINEs em Insuficiencia Cardiaca" in alerts[0].message


def test_does_not_flag_nsaid_without_heart_failure_diagnosis(beers_criteria, elderly_patient_factory):
    prescription = make_prescription(MED_IBUPROFENO, None)
    patient = elderly_patient_factory(prescriptions=(prescription,))

    alerts = BeersRulesEngine(beers_criteria).evaluate_patient(patient)

    assert alerts == []


def test_inactive_prescription_is_not_evaluated(beers_criteria, elderly_patient_factory):
    prescription = make_prescription(MED_DIAZEPAM, None, active=False)
    patient = elderly_patient_factory(prescriptions=(prescription,))

    alerts = BeersRulesEngine(beers_criteria).evaluate_patient(patient)

    assert alerts == []
