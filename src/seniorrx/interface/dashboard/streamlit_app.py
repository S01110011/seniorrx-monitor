"""Dashboard clinico interativo (Streamlit) do SeniorRx Monitor.

Consome a API REST (nao acessa o banco diretamente) para manter uma unica
fonte de verdade das regras de negocio. Executar com:

    streamlit run src/seniorrx/interface/dashboard/streamlit_app.py

Variaveis de ambiente:
    SENIORRX_API_URL   URL base da API (default: http://localhost:8000)
    SENIORRX_API_KEY   API key correspondente a SENIORRX_API_KEY do backend
"""

from __future__ import annotations

import os
from typing import Any, cast

import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("SENIORRX_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("SENIORRX_API_KEY", "")

st.set_page_config(page_title="SeniorRx Monitor", page_icon=":pill:", layout="wide")


def _headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY} if API_KEY else {}


@st.cache_data(ttl=30)  # type: ignore[untyped-decorator]  # streamlit nao publica stubs de tipo
def fetch_patients() -> list[dict[str, Any]]:
    response = requests.get(f"{API_URL}/patients", headers=_headers(), timeout=10)
    response.raise_for_status()
    return cast(list[dict[str, Any]], response.json())


def fetch_risk_assessment(patient_id: str) -> dict[str, Any]:
    response = requests.get(
        f"{API_URL}/patients/{patient_id}/risk-assessment", headers=_headers(), timeout=10
    )
    response.raise_for_status()
    return cast(dict[str, Any], response.json())


SEVERITY_COLOR = {
    "BAIXA": "#2E7D32",
    "MODERADA": "#F9A825",
    "ALTA": "#EF6C00",
    "CRITICA": "#C62828",
}

RISK_COLOR = {
    "BAIXO": "#2E7D32",
    "MODERADO": "#F9A825",
    "ALTO": "#EF6C00",
    "CRITICO": "#C62828",
}


def render_header() -> None:
    st.title("SeniorRx Monitor")
    st.caption(
        "Deteccao de Medicamentos Potencialmente Inapropriados (PIM) em idosos "
        "segundo AGS Beers Criteria(R) 2023 — uso educacional/pesquisa, "
        "**nao substitui julgamento clinico**."
    )


def render_patient_list(patients: list[dict[str, Any]]) -> str | None:
    st.sidebar.header("Pacientes")
    if not patients:
        st.sidebar.info("Nenhum paciente cadastrado. Rode scripts/generate_synthetic_data.py.")
        return None

    df = pd.DataFrame(patients)
    selected_pseudonym = st.sidebar.selectbox("Selecionar paciente (pseudonimo)", df["pseudonym"])
    selected = df[df["pseudonym"] == selected_pseudonym].iloc[0]
    st.sidebar.metric("Idade", f"{selected['age']} anos")
    st.sidebar.metric("Sexo", selected["sex"])
    st.sidebar.metric("Setting", selected["care_setting"])
    return str(selected["patient_id"])


def render_risk_assessment(assessment: dict[str, Any]) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Medicamentos ativos", assessment["active_medication_count"])
    col2.metric("PIM (Beers 2023)", assessment["pim_count"])
    col3.metric("Interacoes medicamentosas", assessment["ddi_count"])
    col4.metric("Comorbidades", assessment["comorbidity_count"])

    risk_level = assessment["rule_based_risk_level"]
    st.markdown(
        f"### Nivel de risco farmacoterapeutico: "
        f"<span style='color:{RISK_COLOR.get(risk_level, '#000')}'>**{risk_level}**</span>",
        unsafe_allow_html=True,
    )

    if assessment.get("ml_adverse_event_probability") is not None:
        st.progress(assessment["ml_adverse_event_probability"])
        st.caption(
            f"Probabilidade estimada de evento adverso (modelo {assessment.get('model_version')}): "
            f"{assessment['ml_adverse_event_probability']:.1%} — sinal complementar, nao diagnostico."
        )

    st.subheader("Alertas clinicos")
    alerts = assessment["alerts"]
    if not alerts:
        st.success("Nenhum alerta de PIM, polifarmacia ou interacao identificado.")
        return

    for alert in sorted(alerts, key=lambda a: ["BAIXA", "MODERADA", "ALTA", "CRITICA"].index(a["severity"]), reverse=True):
        color = SEVERITY_COLOR.get(alert["severity"], "#000")
        st.markdown(
            f"<div style='border-left: 4px solid {color}; padding: 0.5rem 1rem; margin-bottom: 0.5rem;'>"
            f"<b>[{alert['severity']}] {alert['alert_type']}</b><br>{alert['message']}</div>",
            unsafe_allow_html=True,
        )


def main() -> None:
    render_header()
    try:
        patients = fetch_patients()
    except requests.RequestException as exc:
        st.error(f"Nao foi possivel conectar a API ({API_URL}): {exc}")
        return

    patient_id = render_patient_list(patients)
    if patient_id is None:
        return

    try:
        assessment = fetch_risk_assessment(patient_id)
    except requests.RequestException as exc:
        st.error(f"Erro ao calcular avaliacao de risco: {exc}")
        return

    render_risk_assessment(assessment)


if __name__ == "__main__":
    main()
