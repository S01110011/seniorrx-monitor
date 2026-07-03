"""Aplicacao FastAPI principal do SeniorRx Monitor.

Executar localmente:
    uvicorn seniorrx.interface.api.main:app --reload --port 8000

Seguranca (ver src/seniorrx/interface/api/security.py e SECURITY.md):
- Autenticacao por API key com comparacao em tempo constante e fail-closed
  em producao (SENIORRX_ENV=production exige SENIORRX_API_KEY);
- Cabecalhos de seguranca defensivos em toda resposta (CSP, HSTS, nosniff...);
- Rate limiting por IP (configuravel via SENIORRX_RATE_LIMIT);
- CORS restrito por ambiente.

Para producao, evoluir a API key para OAuth2/OIDC integrado ao provedor de
identidade institucional (ver docs/architecture.md).
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from seniorrx import __version__
from seniorrx.interface.api.routers import alerts, patients, prescriptions
from seniorrx.interface.api.schemas import HealthOut
from seniorrx.interface.api.security import SecurityHeadersMiddleware, require_api_key

RATE_LIMIT = os.environ.get("SENIORRX_RATE_LIMIT", "120/minute")

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

app = FastAPI(
    title="SeniorRx Monitor API",
    description=(
        "API para deteccao de PIM (AGS Beers 2023), polifarmacia e interacoes "
        "medicamentosas em pacientes idosos. Uso exclusivo para pesquisa/educacao — "
        "nao substitui julgamento clinico."
    ),
    version=__version__,
)

# Rate limiting (slowapi): protege contra abuso/forca-bruta na API key.
app.state.limiter = limiter
# slowapi expõe um handler cuja assinatura o mypy não casa com o tipo esperado
# pelo Starlette (Exception vs RateLimitExceeded); ignore pontual e seguro.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Cabecalhos de seguranca em toda resposta.
app.add_middleware(SecurityHeadersMiddleware)

allowed_origins = os.environ.get("SENIORRX_CORS_ORIGINS", "http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

app.include_router(patients.router, dependencies=[Depends(require_api_key)])
app.include_router(prescriptions.router, dependencies=[Depends(require_api_key)])
app.include_router(alerts.router, dependencies=[Depends(require_api_key)])


@app.get("/health", response_model=HealthOut, tags=["infra"])
def health() -> HealthOut:
    return HealthOut(status="ok", version=__version__)
