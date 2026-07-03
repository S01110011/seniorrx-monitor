# Contributing to SeniorRx Monitor

Thank you for contributing! This is a research/education project on older-adult
patient safety — contributions from clinical pharmacists, geriatricians, data
scientists, and software engineers are welcome.

## Development environment

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
make install
make secrets                                          # generate a .env with strong secrets
docker compose up -d db
python scripts/init_db.py --database-url "$DATABASE_URL"
python scripts/generate_synthetic_data.py
```

## Contribution flow

1. Open an issue describing the problem/feature before starting (avoids rework).
2. Create a branch from `main`: `git checkout -b feature/short-name`.
3. Write tests for any change in `src/seniorrx/domain/` or `application/`.
4. Run locally before the PR:
   ```bash
   make lint
   make typecheck
   make test-unit
   ```
5. Open the Pull Request filling in the template (what changed, why, how to test).

## Commit convention

Short, imperative messages in English (Conventional Commits):

```
feat: add ACEi + spironolactone interaction rule
fix: correct prescription-duration calculation for chronic PPI use
docs: update README with Docker Compose instructions
test: cover the case of a patient with no eGFR reported
refactor: extract _atc_matches into a shared module
```

## Changes to clinical content (Beers/DDI criteria)

Any change to `sql/seed_beers_pim.sql` or to the domain rules that affects a
clinical alert **requires** a cited source in the PR description (see the "New
clinical criterion" issue template) and review by at least one person with a
clinical/pharmaceutical background, when available.

## Code standards

- Python 3.11+, full typing (`mypy --strict` must pass).
- `ruff` for lint/format (`make lint`).
- Layered architecture: `domain/` does not import from `infrastructure/` or
  `interface/`.
- Minimum test coverage: 80% (`pytest --cov-fail-under=80`, already configured).

## Repository governance

- The `main` branch is **protected**: changes land via Pull Request with a green
  CI (lint, mypy, security-scan, tests, and Docker build). Force-push and deletion
  are blocked and history is linear.
- `.github/CODEOWNERS` requests automatic maintainer review, especially for
  clinical content (`sql/`, `domain/`) and security.
- The roadmap is organized into milestones (v0.2, v0.3, v1.0) — see the open issues.

## Code of conduct

This project adopts the [Contributor Covenant](CODE_OF_CONDUCT.md). By
participating, you are expected to uphold its terms. Be respectful and
constructive: clinical discussions can be technical and divergent — keep the focus
on evidence and patient safety.
