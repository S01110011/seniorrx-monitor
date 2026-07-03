"""Gera dados 100% SINTETICOS de pacientes idosos, comorbidades e prescricoes.

NAO usa nenhum dado real de paciente. Distribuicoes (prevalencia de
comorbidades, classes de medicamento mais prescritas) sao inspiradas em
literatura epidemiologica publica (ver docs/references.md) mas os registros
individuais sao gerados por amostragem aleatoria com seed fixa (reprodutibilidade).

Uso:
    python scripts/generate_synthetic_data.py --n-patients 500 --seed 42

Saida:
    data/raw/patients.csv
    data/raw/comorbidities.csv
    data/raw/prescriptions.csv
"""

from __future__ import annotations

import argparse
import hashlib
import uuid
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ICD10_COMORBIDITIES = [
    ("I10", "Hipertensao essencial", 0.65),
    ("E11", "Diabetes mellitus tipo 2", 0.30),
    ("I50", "Insuficiencia cardiaca", 0.12),
    ("N18", "Doenca renal cronica", 0.20),
    ("F03", "Demencia nao especificada", 0.10),
    ("M19", "Osteoartrite", 0.25),
    ("J44", "DPOC", 0.10),
    ("E78", "Dislipidemia", 0.40),
    ("R29.6", "Tendencia a quedas repetidas", 0.08),
]

# (drug_name, weight relativo de prescricao) — usados para amostrar prescricoes
# a partir do catalogo ja inserido via sql/seed_beers_pim.sql
DRUG_WEIGHTS = [
    ("Losartana", 12), ("Enalapril", 8), ("Metformina", 10), ("Gliclazida", 5),
    ("Glibenclamida", 3), ("Omeprazol", 9), ("Sertralina", 5), ("Diazepam", 3),
    ("Clonazepam", 4), ("Lorazepam", 3), ("Zolpidem", 3), ("Difenidramina", 2),
    ("Hidroxizina", 2), ("Ciclobenzaprina", 2), ("Ibuprofeno", 4), ("Naproxeno", 2),
    ("Diclofenaco", 2), ("Digoxina", 3), ("Doxazosina", 2), ("Metoclopramida", 2),
    ("Varfarina", 3), ("Espironolactona", 3), ("Amitriptilina", 2), ("Tramadol", 3),
    ("Nifedipino (acao curta)", 1), ("Haloperidol", 1), ("Risperidona", 2),
]


def _pseudonymize(index: int, seed: int) -> str:
    raw = f"seniorrx-synthetic-{seed}-{index}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def generate_patients(n_patients: int, rng: np.random.Generator, seed: int) -> pd.DataFrame:
    rows = []
    for i in range(n_patients):
        age = int(np.clip(rng.normal(78, 7), 65, 100))
        birth_year = date.today().year - age
        sex = rng.choice(["F", "M"], p=[0.58, 0.42])
        weight = float(np.clip(rng.normal(68 if sex == "F" else 78, 12), 40, 130))
        height = float(np.clip(rng.normal(160 if sex == "F" else 172, 8), 140, 195))
        creatinine = float(np.clip(rng.normal(1.0, 0.35), 0.4, 4.5))
        egfr = float(np.clip(140 - age * 0.8 - (creatinine - 1.0) * 40 + rng.normal(0, 8), 8, 120))
        care_setting = rng.choice(
            ["ambulatorial", "hospitalar", "ilpi", "domiciliar"], p=[0.55, 0.15, 0.15, 0.15]
        )
        rows.append(
            {
                "patient_id": str(uuid.uuid4()),
                "pseudonym": _pseudonymize(i, seed),
                "birth_year": birth_year,
                "sex": sex,
                "weight_kg": round(weight, 1),
                "height_cm": round(height, 1),
                "serum_creatinine_mg_dl": round(creatinine, 2),
                "egfr_ml_min_1_73m2": round(egfr, 1),
                "care_setting": care_setting,
            }
        )
    return pd.DataFrame(rows)


def generate_comorbidities(patients: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for _, patient in patients.iterrows():
        for icd10, description, prevalence in ICD10_COMORBIDITIES:
            if rng.random() < prevalence:
                rows.append(
                    {
                        "patient_id": patient["patient_id"],
                        "icd10_code": icd10,
                        "description": description,
                        "diagnosed_on": (
                            date.today() - timedelta(days=int(rng.integers(30, 4000)))
                        ).isoformat(),
                        "active": True,
                    }
                )
    return pd.DataFrame(rows)


def generate_prescriptions(patients: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    drug_names = [d for d, _ in DRUG_WEIGHTS]
    weights = np.array([w for _, w in DRUG_WEIGHTS], dtype=float)
    weights /= weights.sum()

    rows = []
    for _, patient in patients.iterrows():
        n_meds = int(np.clip(rng.poisson(6), 1, 16))
        chosen = rng.choice(drug_names, size=n_meds, replace=False, p=weights)
        for drug_name in chosen:
            start_date = date.today() - timedelta(days=int(rng.integers(10, 900)))
            is_active = rng.random() < 0.85
            rows.append(
                {
                    "prescription_id": str(uuid.uuid4()),
                    "patient_id": patient["patient_id"],
                    "drug_name": drug_name,
                    "prescriber_pseudonym": hashlib.sha256(
                        f"prescriber-{rng.integers(0, 200)}".encode()
                    ).hexdigest()[:12],
                    "dose_value": round(float(rng.uniform(5, 100)), 1),
                    "dose_unit": "mg",
                    "frequency_per_day": float(rng.choice([1, 1, 2, 2, 3])),
                    "indication_icd10": None,
                    "start_date": start_date.isoformat(),
                    "end_date": None if is_active else (start_date + timedelta(days=int(rng.integers(30, 400)))).isoformat(),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerador de dados sinteticos SeniorRx Monitor")
    parser.add_argument("--n-patients", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    patients = generate_patients(args.n_patients, rng, args.seed)
    comorbidities = generate_comorbidities(patients, rng)
    prescriptions = generate_prescriptions(patients, rng)

    patients.to_csv(args.output_dir / "patients.csv", index=False)
    comorbidities.to_csv(args.output_dir / "comorbidities.csv", index=False)
    prescriptions.to_csv(args.output_dir / "prescriptions.csv", index=False)

    print(f"Gerados: {len(patients)} pacientes, {len(comorbidities)} comorbidades, "
          f"{len(prescriptions)} prescricoes -> {args.output_dir}/")


if __name__ == "__main__":
    main()
