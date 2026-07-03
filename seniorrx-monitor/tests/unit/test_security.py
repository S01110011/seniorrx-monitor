"""Testes dos controles de seguranca da API (autenticacao e cabecalhos)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from seniorrx.interface.api import security


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("SENIORRX_API_KEY", raising=False)
    monkeypatch.delenv("SENIORRX_ENV", raising=False)
    yield


def test_dev_without_key_allows_request(monkeypatch):
    monkeypatch.setenv("SENIORRX_ENV", "development")
    # Sem key em dev: autenticacao desabilitada (nao levanta).
    assert security.require_api_key(x_api_key=None) is None


def test_production_without_key_fails_closed(monkeypatch):
    monkeypatch.setenv("SENIORRX_ENV", "production")
    with pytest.raises(HTTPException) as exc:
        security.require_api_key(x_api_key="qualquer")
    assert exc.value.status_code == 503


def test_valid_key_passes(monkeypatch):
    monkeypatch.setenv("SENIORRX_API_KEY", "s3cr3t-key")
    assert security.require_api_key(x_api_key="s3cr3t-key") is None


def test_invalid_key_rejected(monkeypatch):
    monkeypatch.setenv("SENIORRX_API_KEY", "s3cr3t-key")
    with pytest.raises(HTTPException) as exc:
        security.require_api_key(x_api_key="errada")
    assert exc.value.status_code == 401


def test_missing_key_header_rejected_when_configured(monkeypatch):
    monkeypatch.setenv("SENIORRX_API_KEY", "s3cr3t-key")
    with pytest.raises(HTTPException) as exc:
        security.require_api_key(x_api_key=None)
    assert exc.value.status_code == 401


def test_is_production_detection(monkeypatch):
    for value in ("production", "prod", "producao", "PRODUCTION"):
        monkeypatch.setenv("SENIORRX_ENV", value)
        assert security.is_production() is True
    monkeypatch.setenv("SENIORRX_ENV", "development")
    assert security.is_production() is False
