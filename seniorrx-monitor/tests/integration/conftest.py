"""Fixtures de integracao: sobem contra um PostgreSQL real (local ou container de CI).

Requer TEST_DATABASE_URL apontando para um banco descartavel. Se ausente ou
inacessivel, os testes de integracao sao pulados (nao falham a suite inteira) —
isso permite rodar `pytest -m "not integration"` offline durante o dia a dia.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from seniorrx.infrastructure.db.database import get_session
from seniorrx.infrastructure.db.models import Base
from seniorrx.interface.api.main import app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://seniorrx:seniorrx@localhost:5432/seniorrx_test"
)


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip(f"TEST_DATABASE_URL indisponivel ({TEST_DATABASE_URL}); pulando testes de integracao.")

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture()
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine, future=True)
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
