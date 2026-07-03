# Architecture

## 1. Overview and clinical context

**SeniorRx Monitor** is a platform that analyzes the pharmacotherapeutic profile
of older patients (≥ 65 years) to identify:

1. **Polypharmacy / hyperpolypharmacy** (≥ 5 / ≥ 10 concurrent chronic medications);
2. **Potentially Inappropriate Medications (PIM)** per the
   [2023 Updated AGS Beers Criteria®](https://doi.org/10.1111/jgs.18372);
3. high-risk **drug–drug interactions** (e.g., opioid + benzodiazepine);
4. **disease–drug interactions** (e.g., NSAID in heart failure);
5. the need for **renal-function dose adjustment** (eGFR).

The output is a per-patient **pharmacotherapeutic risk level** with explainable
alerts (rationale + recommendation + source), consumed through a REST API and
visualized in a clinical dashboard.

> For research and education only. It does not replace clinical judgement and does
> not constitute a regulated medical device.

## 2. Layered architecture (Clean / Hexagonal)

```
┌──────────────────────────────────────────────────────────────────┐
│ INTERFACE (interface/)                                            │
│   - api/          FastAPI: HTTP routes, Pydantic schemas, auth     │
│   - dashboard/    Streamlit: visualization, consumes the API       │
├──────────────────────────────────────────────────────────────────┤
│ APPLICATION (application/)                                         │
│   - services/     orchestrates the domain rule engines            │
│   - dto.py        output contracts (do not leak internal entities) │
├──────────────────────────────────────────────────────────────────┤
│ DOMAIN (domain/)          <-- CORE, no framework dependency        │
│   - entities.py    Patient, Prescription, BeersCriterion, Alert...  │
│   - value_objects.py  clinical thresholds (polypharmacy, eGFR, ...) │
│   - rules/         BeersRulesEngine, PolypharmacyRulesEngine,       │
│                     InteractionRulesEngine                          │
├──────────────────────────────────────────────────────────────────┤
│ INFRASTRUCTURE (infrastructure/)                                    │
│   - db/           SQLAlchemy models + repositories (ORM<->domain)   │
│   - ml/           feature engineering, RandomForest, MLflow training│
└──────────────────────────────────────────────────────────────────┘
```

**Dependency rule**: import arrows always point inward
(`interface → application → domain`; `infrastructure` implements the interfaces
consumed by `application`, but `domain` never imports SQLAlchemy, FastAPI, or
Streamlit). This lets us test 100% of the clinical logic (`domain/`) without a
database or HTTP — see `tests/unit/`. The design follows Robert C. Martin's
**Clean Architecture** and the **Ports & Adapters (Hexagonal)** pattern.

## 3. Data flow (prescription input → report)

```
[1] Electronic prescription / record         [2] ETL (scripts/etl_pipeline.py)
    (synthetic CSV or source system)      ─────────────▶  normalized PostgreSQL
                                                            (patients, medications,
                                                             prescriptions, comorbidities)
                                                                    │
                                                                    ▼
[3] PatientRepository loads Patient (domain)         BeersCriteriaRepository
    with active prescriptions/comorbidities      loads BeersCriterion[] (domain)
                                                                    │
                                                                    ▼
[4] RiskScoringService.assess(patient)
      ├─ BeersRulesEngine        -> PIM alerts
      ├─ InteractionRulesEngine  -> DDI / renal-adjustment alerts
      ├─ PolypharmacyRulesEngine -> poly/hyperpolypharmacy alerts
      └─ (optional) AdverseEventRiskModel.predict_proba -> complementary ML signal
                                                                    │
                                                                    ▼
[5] RiskAssessmentDTO (risk level + list of explainable alerts)
                                                                    │
                            ┌───────────────────────────────────────┤
                            ▼                                       ▼
[6a] FastAPI API                                     [6b] R/Quarto report
     GET /patients/{id}/risk-assessment                    (aggregated cohort
     (JSON, consumed by external systems)                   epidemiological analysis)
                            │
                            ▼
[7] Streamlit dashboard — interactive per-patient view for the clinical pharmacist
```

## 4. Interoperability and coding standards

- **WHO ATC/DDD** for medication classification and **WHO ICD-10** for diagnoses —
  making rule matching robust and internationally portable.
- **HL7 FHIR** (`MedicationRequest`, `Condition`) is the planned interface for
  ingesting real, anonymized electronic health records (see `docs/roadmap.md`).
- **FAIR data principles** guide the schema (documented, standardized, versioned).

## 5. MLOps components

- **MLflow**: experiment tracking and model registry (`configs/mlops.md`).
- **DVC** (optional): versioning of `data/raw` / `data/processed` outside git.
- **Evidently AI**: weekly drift detection via GitHub Actions
  (`.github/workflows/model-monitoring.yml`).
- **Docker Compose**: `db` (Postgres) + `api` (FastAPI) + `dashboard` (Streamlit).

Predictive-model development is intended to follow **TRIPOD+AI** reporting and
**PROBAST** risk-of-bias appraisal (see `docs/clinical_validation.md`).

## 6. Security (summary — see `SECURITY.md`)

- No PII in the schema (pseudonyms, not names/national IDs).
- Secrets via `.env` / GitHub Secrets, never hardcoded.
- Constant-time API-key check with fail-closed in production → to be replaced by
  OAuth2/OIDC.
- HTTPS terminated at a reverse proxy; the API is never exposed over plain HTTP.

Security controls are aligned with the **OWASP ASVS** and **OWASP API Security
Top 10**; software quality attributes map to **ISO/IEC 25010**
(maintainability, security, reliability), and configuration follows the
**Twelve-Factor App** methodology.

## 7. Notable architectural decisions

| Decision | Alternative considered | Rationale |
|---|---|---|
| Clinical rules in pure Python (`domain/`), no SQL embedded in the logic | Rules 100% in SQL (views/stored procedures) | Fast unit testability with no database dependency; SQL used only for persistence/query |
| Dashboard consumes the API (no direct database access) | Streamlit reading the database directly | Single source of truth for business rules; avoids duplicating risk logic in the dashboard |
| Simple RandomForest instead of XGBoost/deep learning | More complex models | Interpretability prioritized over marginal performance in an educational clinical context |
| Synthetic training label explicitly marked as a proxy | Claiming a "real" label | Scientific honesty — see `docs/clinical_validation.md` |
