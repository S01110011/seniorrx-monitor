# Security Policy

## Scope

This is a research/education project. Even so, we take security seriously because
the data model (even synthetic) represents health information.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities. Email the project maintainer with:
- a description of the vulnerability and its potential impact;
- steps to reproduce;
- the affected version/commit.

Initial response time: within 5 business days.

## Practices adopted in this repository

- **No PII in the schema**: `patients` has no name, national ID, address, or phone
  — only `pseudonym` (a non-reversible identifier) and minimal demographic data.
- **Secrets out of the code**: every credential comes from environment variables
  (`.env`, never committed — see `.env.example`). CI uses GitHub Secrets. A
  `.dockerignore` prevents `.env`/`.git` from entering the images.
- **Hardened API authentication** (`src/seniorrx/interface/api/security.py`):
  - **constant-time** API-key comparison (`hmac.compare_digest`), mitigating
    timing attacks;
  - **fail-closed in production**: with `SENIORRX_ENV=production`, a missing
    `SENIORRX_API_KEY` returns 503 instead of leaving the API open;
  - for real production, evolve to OAuth2/OIDC at the identity provider.
- **Security headers** on every response (`SecurityHeadersMiddleware`):
  `Content-Security-Policy`, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`,
  and `Strict-Transport-Security` (HSTS) in production.
- **Rate limiting** per IP (`slowapi`, configurable via `SENIORRX_RATE_LIMIT`):
  limits brute force against the API key and resource abuse.
- **HTTPS required in production**: terminate TLS at the reverse proxy/load
  balancer (nginx, Traefik, ALB); never expose the FastAPI API directly over HTTP
  on the internet.
- **Automated scanning in CI** (`.github/workflows/ci.yml`, job `security-scan`):
  - **bandit** (SAST) over `src/`;
  - **pip-audit** for dependency CVEs;
  - **gitleaks** for detecting secrets leaked in history.
- **Dependencies**: `pyproject.toml` pins minimum versions; Dependabot/Renovate is
  recommended for continuous updates.
- **Least privilege in the database**: the application user should have only
  `SELECT/INSERT/UPDATE` on the necessary tables, without `DROP`/`ALTER` in
  production (migrations run with a separate administrative user).
- **Non-root container**: the images run as user `seniorrx` (uid 1000), with no
  root privileges.
- **Logs**: `configs/logging.yaml` documents the prohibition on logging clinical
  payloads as free text — only identifiers and aggregate counters.

These controls are aligned with the **OWASP ASVS** and the **OWASP API Security
Top 10**.

## Out of scope

This project does not implement encryption at rest (delegated to the managed
database provider / encrypted disk) or a WAF — both must be configured in the
deployment infrastructure, outside this repository.
