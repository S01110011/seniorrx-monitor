# SeniorRx Monitor — Technical Deep Dive

🌐 **English** · [Português](DEEP_DIVE.pt-BR.md)

> A reference document I wrote to explain, end to end, **why** each part of this
> system exists and **how** it works. It serves both as the project's technical
> memory and as a basis for presenting it in interviews.
>
> Disclaimer: research/education project. It does not replace clinical judgement
> and uses synthetic data only.

---

## 1. The problem I set out to solve

Older adults (≥ 65 years) carry the heaviest burden of **polypharmacy** — the
simultaneous use of several medications — and, with it, of **adverse drug
reactions (ADRs)**. Much of that harm is predictable and avoidable, because the
geriatric literature has already catalogued which drugs have an unfavorable
risk–benefit balance in this population. The reference instrument for this is the
**2023 AGS Beers Criteria®**, published by the American Geriatrics Society.

The practical problem is that this check is rarely performed systematically at the
point of prescription. I wanted to build a system that does exactly that: take an
older patient's pharmacotherapeutic profile and return, in an auditable and
explainable way, the **Potentially Inappropriate Medications (PIM)**, the
**dangerous interactions**, the **polypharmacy**, and a consolidated **risk
level** — with every alert traceable to its scientific source.

From the outset I set three non-negotiable principles:

1. **Full transparency.** No "black box": every alert points to the rule and the
   reference that generated it.
2. **Security and privacy by design.** No PII in the data model; everything
   synthetic; secrets kept out of the code.
3. **Scientific honesty.** The system is decision support, not diagnosis, and I
   explicitly mark what is a validated rule versus an exploratory statistical
   signal.

---

## 2. Why clean architecture (and what it gave me)

I organized the code into four concentric layers, with the dependency rule always
pointing inward:

```
interface  →  application  →  domain  ←  infrastructure
(FastAPI/     (use-case      (pure       (SQLAlchemy,
 Streamlit)    services)      clinical    ML model)
                              rules)
```

- **`domain/`** is the heart and imports **nothing** from any framework — no
  SQLAlchemy, no FastAPI, no pandas. It holds immutable `dataclasses` (`Patient`,
  `Prescription`, `BeersCriterion`, `Alert`) and the three rule engines. This lets
  me test 100% of the clinical logic in milliseconds, without standing up a
  database or a server.
- **`application/`** orchestrates the engines and returns DTOs — output objects
  that do not leak the domain's internal enums to the outside world.
- **`infrastructure/`** implements the "how": ORM mapping, repositories that
  translate database rows into domain entities, and the ML model.
- **`interface/`** exposes everything over HTTP (FastAPI) and visualization
  (Streamlit).

The concrete payoff of this separation showed up in practice: when I validated the
system, I could run the 16 rule tests with no external dependency, and later
exercise the whole stack against a real PostgreSQL without touching **a single
line** of clinical logic. If tomorrow I swap Postgres for another database or the
API for gRPC, `domain/` stays intact.

---

## 3. The clinical rule engine (the core of the value)

I split the evaluation into three independent engines, all operating on domain
entities:

### 3.1 `BeersRulesEngine` — PIM
Covers the first two Beers 2023 categories:
- **PIM independent of diagnosis**: drugs to avoid in any older adult
  (benzodiazepines, first-generation antihistamines, glibenclamide, chronic
  NSAIDs, muscle relaxants, etc.). Matching is by **ATC prefix** — so a single
  criterion `N05BA` covers the entire benzodiazepine class.
- **Disease-specific PIM**: drugs that are generally safe but contraindicated in a
  given comorbidity (e.g., NSAIDs in heart failure `I50`). Here I cross the drug's
  ATC code with the patient's active **ICD-10** codes.

One detail I took care of: certain criteria only apply above a **chronic-use
threshold** (PPIs > 8 weeks, metoclopramide > 12 weeks). I modeled this by
comparing `prescription.duration_days` with the threshold, so as not to produce a
false positive on legitimate acute use.

### 3.2 `PolypharmacyRulesEngine`
Applies the literature's consensus thresholds: **≥ 5** active medications =
polypharmacy (moderate severity); **≥ 10** = hyperpolypharmacy (critical,
suggesting structured review / deprescribing).

### 3.3 `InteractionRulesEngine`
Does two things reusing the same criteria table:
- **Drug–drug interactions**, pairwise (`itertools.combinations`), covering
  classic cases: opioid + benzodiazepine, warfarin + NSAID, the *"triple whammy"*
  (ACEi/ARB + diuretic + NSAID), ACEi/ARB + spironolactone.
- **Renal-function adjustment**: when the patient's eGFR falls below a criterion's
  threshold (e.g., metformin in advanced CKD), I raise an adjustment alert.

All engines respect the Beers scope: they only evaluate patients **≥ 65 years**
with **active prescriptions**.

---

## 4. From data to decision: the full flow

```
Prescription/record (synthetic CSV or anonymized source)
        │  scripts/etl_pipeline.py
        ▼
Normalized PostgreSQL (patients, medications, prescriptions, comorbidities)
        │  PatientRepository + BeersCriteriaRepository  (infra → domain)
        ▼
RiskScoringService.assess(patient)
   ├─ BeersRulesEngine        → PIM alerts
   ├─ InteractionRulesEngine  → interactions + renal adjustment
   ├─ PolypharmacyRulesEngine → poly/hyperpolypharmacy
   └─ (optional) ML model     → ADR probability (complementary signal)
        ▼
RiskAssessmentDTO  (risk level + list of explainable alerts)
        ├─→ FastAPI API  (GET /patients/{id}/risk-assessment)
        ├─→ Streamlit dashboard (per-patient visualization)
        └─→ R/Quarto report (aggregated cohort epidemiology)
```

`RiskScoringService` converts the list of alerts into a level
(`BAIXO/MODERADO/ALTO/CRÍTICO` — low/moderate/high/critical) via a transparent
heuristic: any **critical** alert raises the level to critical; two or more
**high** alerts raise it to high; and so on. It is deliberately simple and
auditable — the sophistication lives in the criteria base, not in an opaque
formula.

---

## 5. The data layer

I modeled seven tables in PostgreSQL (`sql/schema.sql`). Deliberate choices:

- **No PII.** `patients` stores only birth year, sex, anthropometric data, and a
  **non-reversible pseudonym** — never a name, national ID, or address. Age is
  derived, not stored.
- **UUID primary keys** (`uuid-ossp` extension), avoiding the volume leakage that
  sequential IDs expose.
- **Standardized coding**: medications by **ATC** (WHO), comorbidities by
  **ICD-10** — which makes rule matching robust and internationalizable.
- **`beers_pim_criteria` as a data-driven table**: adding a new clinical criterion
  means inserting a row with its source, not changing code.
- **`JSONB`** in `risk_scores.explanation` to store semi-structured explainability
  without an extra table.

A real lesson came from here. I had modeled `prescriptions.is_active` as a
**generated column** (`GENERATED ALWAYS AS (end_date IS NULL OR end_date >=
CURRENT_DATE)`). This passed the tests with SQLite, but PostgreSQL **rejected** it
on the real deployment: generated-column expressions must be **immutable**, and
`CURRENT_DATE` is not. I fixed it by moving the "active" computation to the
`v_active_prescriptions` view (evaluated at query time) and to the domain property
`Prescription.is_active`. It was a reminder that only validation against the real
target technology catches this kind of incompatibility.

---

## 6. The Machine Learning component (and its honesty)

I added a `RandomForestClassifier` that estimates the probability of an adverse
event, with feature engineering derived only from domain data (age; counts of
PIM/interactions/comorbidities; eGFR — no PII). I chose Random Forest **on
purpose**: `feature_importances_` provides enough explainability for the context,
and I prefer that to the marginal performance of an opaque model in a clinical
setting. Training logs parameters, ROC-AUC, and the artifact to **MLflow**.

The most important point — and one I make a point of stating explicitly — is that
the **training label is a synthetic proxy**, not an observed clinical outcome. It
exists to demonstrate the end-to-end MLOps *pipeline*, not to claim real
predictive power. In `docs/clinical_validation.md` I describe what would be needed
to validate with real data (a label such as ADR-related readmission within 30
days; AUPRC/calibration/fairness metrics; external validation). The model is
always **complementary** to the deterministic rules, never a substitute.

---

## 7. Security — what I hardened

I treated security as a requirement, not decoration:

- **API authentication** with **constant-time** key comparison
  (`hmac.compare_digest`, against timing attacks) and **fail-closed in
  production**: with `SENIORRX_ENV=production`, a missing key returns 503 instead
  of silently opening the API.
- **Security headers** on every response (CSP, HSTS in production, `nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy`, `Cache-Control: no-store`).
- **Rate limiting** per IP (`slowapi`), mitigating brute force against the key.
- **`.dockerignore`** preventing `.env`, `.git`, and data from entering the
  images; containers run as a **non-root user**.
- **Automated scanning in CI**: `bandit` (SAST), `pip-audit` (CVEs), and
  `gitleaks` (leaked secrets).
- **No secrets in code**: everything via environment variables; `.env` is never
  committed (only `.env.example`).

I left out of scope (and documented) what belongs to the deployment
infrastructure: TLS termination at a reverse proxy, encryption at rest, and a WAF.

---

## 8. Privacy and compliance

The system was designed for **LGPD/GDPR** from the modeling stage: no real patient
data is used; the schema has no PII fields; patients are referenced by UUID and
pseudonym. In `data/README.md` and `SECURITY.md` I documented what would change in
an adaptation to real data (prior anonymization, RBAC, data versioning via DVC on
encrypted storage, an ethics board).

---

## 9. Quality: tests, typing, and CI

- **Tests** (`pytest`): unit tests cover each rule engine and the risk service
  without touching a database; integration exercises the API against PostgreSQL and
  is skipped automatically when the database is unavailable — which keeps the
  development loop fast and offline.
- **Typing**: `mypy --strict` across all of `src/`.
- **Lint/format**: `ruff` with a deliberate rule set.
- **CI** (GitHub Actions): lint, type-check, `security-scan`, tests with a Postgres
  service, and Docker image builds — plus a scheduled *drift* job with
  Evidently AI.
- Minimum coverage set to **80%** (`--cov-fail-under=80`).

---

## 10. How I validated that it really works

I did not settle for "it compiles". Validation was empirical and layered:

1. **Clinical logic**: 16 green unit tests, covering cases known from the
   literature (glibenclamide always a PIM; benzodiazepine + fall history;
   warfarin + NSAID; renal adjustment by eGFR).
2. **API↔database integration**: I exercised the API against a real SQL database,
   confirming that ORM → repositories → risk service → routes work together.
3. **Full stack with Docker**: I ran `docker compose up --build` and validated the
   end-to-end orchestration — healthy Postgres, an `init` service applying the
   schema + the Beers criteria, the API responding, and the dashboard serving. It
   was at this stage that I found and fixed the non-immutable generated-column bug.
4. **Real endpoints**: with 50 synthetic patients loaded via ETL, the API
   correctly classified a patient as **high** risk — 3 PIM (NSAIDs, PPI), 2 "triple
   whammy" interactions, and polypharmacy — and returned **401** without an API key.

---

## 11. Limitations I acknowledge

- The criteria base is an **illustrative subset** of Beers 2023, not the full
  official table (which is AGS property). Adding criteria is trivial and
  documented.
- The ML model uses a **synthetic label**; there is, as yet, no prospective
  clinical validation.
- The R/Quarto report's epidemiological analysis is **descriptive**, not causal.
- API Key authentication is adequate for the current scope; real production would
  call for OAuth2/OIDC.

All of this is mapped in `docs/roadmap.md` (v0.1 → v1.0).

---

## 12. If I had more time

I would prioritize, in this order: (1) a *golden dataset* reviewed by a clinical
pharmacist to measure rule agreement; (2) **HL7 FHIR** integration to ingest real
anonymized records; (3) a real clinical label for the ML model; (4) per-instance
explainability (SHAP) and OAuth2/OIDC. The system was already built to accommodate
these evolutions without rewriting the core.
