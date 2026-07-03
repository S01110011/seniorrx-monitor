"""Controles de seguranca da API: autenticacao, cabecalhos e configuracao de ambiente.

Isolado do main.py para permitir teste unitario dos mecanismos de seguranca
sem subir toda a aplicacao. Todos os segredos vem de variaveis de ambiente
(ver `.env.example`), nunca hardcoded.
"""

from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Ambientes reconhecidos. Em "production" a API falha fechada (fail-closed):
# se nenhuma API key estiver configurada, a aplicacao recusa toda requisicao
# autenticada em vez de ficar aberta silenciosamente.
_PRODUCTION_ENVS = frozenset({"production", "prod", "producao"})


def get_environment() -> str:
    return os.environ.get("SENIORRX_ENV", "development").strip().lower()


def is_production() -> bool:
    return get_environment() in _PRODUCTION_ENVS


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Valida a API key em tempo constante (mitiga timing attacks).

    - Producao: exige SENIORRX_API_KEY configurada; ausencia e erro 503
      (misconfiguracao) e nunca "porta aberta".
    - Desenvolvimento: se a key nao estiver definida, a autenticacao e
      desabilitada para ergonomia local — comportamento documentado e explicito.
    """
    expected = os.environ.get("SENIORRX_API_KEY")

    if not expected:
        if is_production():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servico mal configurado: SENIORRX_API_KEY obrigatoria em producao.",
            )
        return  # dev: auth desabilitada explicitamente

    provided = x_api_key or ""
    # hmac.compare_digest evita vazamento de informacao por tempo de comparacao.
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalida ou ausente.",
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona cabecalhos de seguranca defensivos a toda resposta.

    HSTS so e enviado quando is_production(), pois exigir HTTPS estrito em
    desenvolvimento (http://localhost) quebraria o fluxo local.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-XSS-Protection", "0")  # desabilita filtro legado (CSP e o correto)
        response.headers.setdefault(
            "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
        )
        response.headers.setdefault("Cache-Control", "no-store")
        if is_production():
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload"
            )
        return response
