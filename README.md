# SeniorRx Monitor

🌐 **English** · [Português](README.pt-BR.md)

**Detection of Potentially Inappropriate Medications (PIM) and polypharmacy in
older adults, based on the 2023 AGS Beers Criteria®.**

[![CI](https://github.com/S01110011/seniorrx-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/S01110011/seniorrx-monitor/actions/workflows/ci.yml)
[![Model Monitoring](https://github.com/S01110011/seniorrx-monitor/actions/workflows/model-monitoring.yml/badge.svg)](https://github.com/S01110011/seniorrx-monitor/actions/workflows/model-monitoring.yml)
![coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-informational)
![security](https://img.shields.io/badge/security-bandit%20%7C%20pip--audit%20%7C%20gitleaks-orange)
![status](https://img.shields.io/badge/status-v0.1%20prototype-yellow)

> **Disclaimer:** research and education project. It uses synthetic data only.
> The alerts it produces **do not replace clinical judgement** and do not
> constitute a regulated medical device. See [`docs/clinical_validation.md`](docs/clinical_validation.md).

## What this project does

Older adults on polypharmacy (the use of multiple medications) face an elevated
risk of adverse drug reactions — many of which are avoidable, because they are
already known and catalogued in the geriatric literature. **SeniorRx Monitor**
implements, as auditable and tested software, an illustrative subset of the
[2023 AGS Beers Criteria®](https://doi.org/10.1111/jgs.18372) to:

- detect **polypharmacy** (≥ 5 medications) and **hyperpolypharmacy** (≥ 10);
- flag **PIM** (Potentially Inappropriate Medications), whether independent of
  diagnosis or conditional on specific comorbidities (for example, NSAIDs in
  heart failure);
- identify high-risk **drug–drug interactions** (for example, opioid +
  benzodiazepine, warfarin + NSAID, the *triple whammy* ACEi/ARB + diuretic + NSAID);
- alert on the need for **renal dose adjustment** (eGFR);
- consolidate everything into an explainable **pharmacotherapeutic risk level**,
  exposed through a REST API and visualized in a clinical dashboard.

See [`docs/beers_criteria.md`](docs/beers_criteria.md) for the key concepts
(polypharmacy, PIM, the Beers methodology) and the note about the illustrative
(non-exhaustive) nature of the implemented criteria set.

## Architecture

Clean architecture in four layers — the clinical rules are 100% decoupled from
the database and the web framework (see [`docs/architecture.md`](docs/architecture.md)):

```
interface/       FastAPI (REST API) + Streamlit (dashboard)
application/     services that orchestrate the rule engines
domain/          entities + rule engines (Beers, polypharmacy, interactions) — pure core
infrastructure/  SQLAlchemy (PostgreSQL) + ML model (scikit-learn/MLflow)
```

## Tech stack

| Layer | Technology | Rationale |
|---|---|---|
| API | FastAPI | Native typing (Pydantic), async performance, automatic OpenAPI |
| Database | PostgreSQL | JSONB, UUID, views, maturity in healthcare |
| ORM | SQLAlchemy 2.x | Clean separation between ORM and domain entities |
| ML | scikit-learn + MLflow | Interpretability first; experiment tracking |
| Dashboard | Streamlit | Rapid prototyping of an interactive clinical UI |
| Reproducible analysis | R + Quarto | Versionable, citable epidemiological reports |
| Local orchestration | Docker Compose | `db` + `api` + `dashboard` with a single command |
| CI/CD | GitHub Actions | Lint, type-checking, tests, image build and drift checks |

## Quickstart

```bash
git clone https://github.com/S01110011/seniorrx-monitor.git
cd seniorrx-monitor

# Generate a .env with STRONG, random secrets (required: compose fails without them)
make secrets          # or: bash scripts/gen_secrets.sh

# Start PostgreSQL + API + dashboard
docker compose up --build

# In another terminal: initialize the schema, generate synthetic data, run the ETL and train the model
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
bash scripts/run_pipeline.sh
```

Access:
- API: http://localhost:8000/docs (Swagger UI)
- Dashboard: http://localhost:8501

### Running without Docker

```bash
pip install -e ".[dev]"
python scripts/init_db.py --database-url "$DATABASE_URL"
python scripts/generate_synthetic_data.py --n-patients 500
python scripts/etl_pipeline.py
uvicorn seniorrx.interface.api.main:app --reload &
streamlit run src/seniorrx/interface/dashboard/streamlit_app.py
```

### Tests

```bash
make lint          # ruff
make typecheck     # mypy --strict
make test-unit     # pytest, no database required
make test          # full pytest (includes integration; requires TEST_DATABASE_URL)
make cov           # HTML coverage report
```

## API usage example

```bash
curl -H "X-API-Key: $SENIORRX_API_KEY" \
  http://localhost:8000/patients/<patient_id>/risk-assessment
```

```json
{
  "patient_id": "3f5a...",
  "active_medication_count": 7,
  "pim_count": 2,
  "ddi_count": 1,
  "comorbidity_count": 3,
  "rule_based_risk_level": "ALTO",
  "alerts": [
    {
      "alert_type": "PIM_BEERS",
      "severity": "ALTA",
      "message": "PIM (Beers 2023): Glibenclamida — sulfonilureia de longa ação. ..."
    }
  ]
}
```

## Folder structure

```
seniorrx-monitor/
├── src/seniorrx/           # source code (domain/application/infrastructure/interface)
├── sql/                    # schema.sql + seed of the 2023 Beers criteria
├── scripts/                # synthetic data generation, ETL, ML training, full pipeline
├── tests/                  # unit/ (no database) + integration/ (requires PostgreSQL)
├── configs/                # settings.yaml, logging.yaml, MLOps notes
├── data/                   # raw/ (synthetic CSVs) and processed/ (features, model) — not versioned
├── docs/                   # architecture, schema, Beers criteria, roadmap, validation, references
├── references/             # detailed summary of the clinical sources of the implemented criteria
├── reports/quarto/         # reproducible epidemiological report (R/Quarto)
├── notebooks/              # exploratory data analysis (Jupyter)
└── .github/                # CI/CD, issue/PR templates
```

A full description of each module is available in [`docs/architecture.md`](docs/architecture.md).

## Documentation

> Most documents under `docs/` are written in Portuguese.

| Document | Contents |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Layered architecture, data flow, technical decisions |
| [`docs/DEEP_DIVE.md`](docs/DEEP_DIVE.md) | In-depth technical analysis of the whole system |
| [`docs/database_schema.md`](docs/database_schema.md) | Detailed relational model |
| [`docs/beers_criteria.md`](docs/beers_criteria.md) | Clinical concepts and note about the implemented subset |
| [`docs/clinical_validation.md`](docs/clinical_validation.md) | Scientific validation strategy (rules and ML) |
| [`docs/references.md`](docs/references.md) | Complete scientific references |
| [`docs/roadmap.md`](docs/roadmap.md) | Milestones from v0.1 to v1.0 |
| [`docs/linkedin_pitch.md`](docs/linkedin_pitch.md) and [`docs/interview_talking_points.md`](docs/interview_talking_points.md) | Presenting the project for a portfolio |
| [`configs/mlops.md`](configs/mlops.md) | MLflow, DVC and Evidently AI strategy |
| [`SECURITY.md`](SECURITY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) | Security and how to contribute |

## Privacy and compliance

No real patient data is used or stored. The schema contains no PII fields (name,
national ID, address); patients are identified by a non-reversible pseudonym.
See [`data/README.md`](data/README.md) and [`SECURITY.md`](SECURITY.md) for the
full policy (referencing Brazil's LGPD and the GDPR).

## License

Code under the [MIT license](LICENSE). The clinical content of the AGS Beers
Criteria® is owned by the American Geriatrics Society — this repository
implements only an illustrative subset, for educational purposes (see
[`docs/beers_criteria.md`](docs/beers_criteria.md)).
