"""Pipeline ETL: carrega CSVs de data/raw/ (sinteticos ou de origem anonimizada)
para as tabelas normalizadas do PostgreSQL.

Etapas:
    1. Extract: le patients.csv, comorbidities.csv, prescriptions.csv
    2. Transform: normaliza tipos, valida FKs (drug_name -> medications.medication_id)
    3. Load: insere em lote via SQLAlchemy Core (bulk insert)

Uso:
    python scripts/etl_pipeline.py --input-dir data/raw
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from seniorrx.infrastructure.db.database import SessionLocal
from seniorrx.infrastructure.db.models import (
    ComorbidityModel,
    MedicationModel,
    PatientModel,
    PrescriptionModel,
)


def _load_medication_lookup(session) -> dict[str, int]:
    rows = session.scalars(select(MedicationModel)).all()
    return {row.drug_name: row.medication_id for row in rows}


def load_patients(session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        session.merge(
            PatientModel(
                patient_id=row["patient_id"],
                pseudonym=row["pseudonym"],
                birth_year=int(row["birth_year"]),
                sex=row["sex"],
                weight_kg=row["weight_kg"],
                height_cm=row["height_cm"],
                serum_creatinine_mg_dl=row["serum_creatinine_mg_dl"],
                egfr_ml_min_1_73m2=row["egfr_ml_min_1_73m2"],
                care_setting=row["care_setting"],
            )
        )
    session.commit()


def load_comorbidities(session, df: pd.DataFrame) -> None:
    session.add_all(
        ComorbidityModel(
            patient_id=row["patient_id"],
            icd10_code=row["icd10_code"],
            description=row["description"],
            diagnosed_on=row["diagnosed_on"],
            active=bool(row["active"]),
        )
        for _, row in df.iterrows()
    )
    session.commit()


def load_prescriptions(session, df: pd.DataFrame, medication_lookup: dict[str, int]) -> None:
    skipped = 0
    for _, row in df.iterrows():
        medication_id = medication_lookup.get(row["drug_name"])
        if medication_id is None:
            skipped += 1
            continue
        session.add(
            PrescriptionModel(
                prescription_id=row["prescription_id"],
                patient_id=row["patient_id"],
                medication_id=medication_id,
                prescriber_pseudonym=row["prescriber_pseudonym"],
                dose_value=row["dose_value"],
                dose_unit=row["dose_unit"],
                frequency_per_day=row["frequency_per_day"],
                indication_icd10=row["indication_icd10"] if pd.notna(row["indication_icd10"]) else None,
                start_date=row["start_date"],
                end_date=row["end_date"] if pd.notna(row["end_date"]) else None,
            )
        )
    session.commit()
    if skipped:
        print(f"Aviso: {skipped} prescricoes ignoradas (medicamento nao encontrado no catalogo).")


def main() -> None:
    parser = argparse.ArgumentParser(description="ETL: CSV -> PostgreSQL (SeniorRx Monitor)")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()

    patients_df = pd.read_csv(args.input_dir / "patients.csv")
    comorbidities_df = pd.read_csv(args.input_dir / "comorbidities.csv")
    prescriptions_df = pd.read_csv(args.input_dir / "prescriptions.csv")

    session = SessionLocal()
    try:
        load_patients(session, patients_df)
        load_comorbidities(session, comorbidities_df)
        medication_lookup = _load_medication_lookup(session)
        load_prescriptions(session, prescriptions_df, medication_lookup)
    finally:
        session.close()

    print(
        f"ETL concluido: {len(patients_df)} pacientes, {len(comorbidities_df)} comorbidades, "
        f"{len(prescriptions_df)} prescricoes carregadas."
    )


if __name__ == "__main__":
    main()
