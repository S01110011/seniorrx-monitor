# Roadmap

## v0.1 — Prototype (current)
- [x] Clean architecture (domain/application/infrastructure/interface).
- [x] PostgreSQL schema + illustrative subset of the 2023 Beers criteria.
- [x] Rule engine: PIM, polypharmacy/hyperpolypharmacy, DDI, renal adjustment.
- [x] FastAPI API + Streamlit dashboard.
- [x] Synthetic data generation + ETL.
- [x] ML model (RandomForest) with a synthetic label + MLflow tracking.
- [x] Test suite (unit + integration), CI on GitHub Actions.
- [x] Reproducible R/Quarto report.
- [x] Complete technical documentation.

## v0.2 — Robustness and clinical coverage
- [ ] Extend `beers_pim_criteria` to the "use with caution" category (not yet
      covered by the rule engine).
- [ ] Support STOPP/START v3 as a second criteria source (cross-comparison of
      alerts).
- [ ] Real OAuth2/OIDC authentication replacing the API-key stub.
- [ ] Asynchronous queue (e.g., Celery/RQ) for batch re-assessment of large cohorts.
- [ ] Per-instance explainability (SHAP) in the ML model, beyond global importance.
- [ ] Internationalization of the alert texts (pt-BR / en-US).

## v0.3 — Scale and observability
- [ ] Multi-patient dashboard with population filters (unit, age band, risk).
- [ ] HL7 FHIR integration (`MedicationRequest` / `Condition` resources) for
      ingestion from real electronic health records (with anonymization).
- [ ] Automatic drift alerts (Evidently) opening an issue via the GitHub API.
- [ ] Full decision auditing (who acknowledged/dismissed each alert, with a
      mandatory justification).
- [ ] Row-Level Security in PostgreSQL for multi-tenancy (multiple institutions).

## v1.0 — Stable release
- [ ] Validation against a golden dataset reviewed by a clinical pharmacist
      (agreement ≥ 95% — see `docs/clinical_validation.md`).
- [ ] Retraining of the ML model with a real clinical label (no longer synthetic).
- [ ] LGPD/GDPR compliance documentation reviewed by a legal specialist.
- [ ] Formal assessment of regulatory classification (SaMD) if intended for real
      assistive use.
- [ ] Publication of a paper/whitepaper describing the methodology and validation
      results.
