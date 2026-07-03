"""Configuracao de conexao com o banco (SQLAlchemy 2.x).

A URL de conexao vem exclusivamente de variavel de ambiente (`DATABASE_URL`),
nunca hardcoded — ver `.env.example`. Sem credenciais no codigo-fonte.
"""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_LOCAL_URL = "postgresql+psycopg://seniorrx:seniorrx@localhost:5432/seniorrx"


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_LOCAL_URL)


engine = create_engine(get_database_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator[Session, None, None]:
    """Dependency-injectable session generator (usado pelo FastAPI e scripts)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
