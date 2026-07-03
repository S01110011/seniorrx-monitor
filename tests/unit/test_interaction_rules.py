from __future__ import annotations

from seniorrx.domain.entities import AlertType
from seniorrx.domain.rules.interaction_rules import InteractionRulesEngine
from tests.conftest import MED_IBUPROFENO, MED_METFORMINA, MED_VARFARINA, make_prescription


def test_flags_warfarin_nsaid_interaction(beers_criteria, elderly_patient_factory):
    rx_warfarin = make_prescription(MED_VARFARINA, None)
    rx_ibuprofen = make_prescription(MED_IBUPROFENO, None)
    patient = elderly_patient_factory(prescriptions=(rx_warfarin, rx_ibuprofen))

    alerts = InteractionRulesEngine(beers_criteria).evaluate_patient(patient)
    ddi_alerts = [a for a in alerts if a.alert_type == AlertType.DRUG_DRUG_INTERACTION]

    assert len(ddi_alerts) == 1
    assert "Varfarina" in ddi_alerts[0].message and "Ibuprofeno" in ddi_alerts[0].message


def test_no_ddi_alert_without_interacting_pair(beers_criteria, elderly_patient_factory):
    rx_metformina = make_prescription(MED_METFORMINA, None)
    patient = elderly_patient_factory(prescriptions=(rx_metformina,))

    alerts = InteractionRulesEngine(beers_criteria).evaluate_patient(patient)

    assert [a for a in alerts if a.alert_type == AlertType.DRUG_DRUG_INTERACTION] == []


def test_flags_renal_adjustment_when_egfr_below_threshold(beers_criteria, elderly_patient_factory):
    rx_metformina = make_prescription(MED_METFORMINA, None)
    patient = elderly_patient_factory(prescriptions=(rx_metformina,), egfr_ml_min_1_73m2=25.0)

    alerts = InteractionRulesEngine(beers_criteria).evaluate_patient(patient)
    renal_alerts = [a for a in alerts if a.alert_type == AlertType.RENAL_ADJUSTMENT]

    assert len(renal_alerts) == 1
    assert "eGFR=25.0" in renal_alerts[0].message


def test_no_renal_alert_when_egfr_above_threshold(beers_criteria, elderly_patient_factory):
    rx_metformina = make_prescription(MED_METFORMINA, None)
    patient = elderly_patient_factory(prescriptions=(rx_metformina,), egfr_ml_min_1_73m2=75.0)

    alerts = InteractionRulesEngine(beers_criteria).evaluate_patient(patient)

    assert [a for a in alerts if a.alert_type == AlertType.RENAL_ADJUSTMENT] == []
