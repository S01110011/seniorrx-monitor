.PHONY: install secrets lint typecheck security test test-unit cov run-api run-dashboard up down

install:
	pip install -e ".[dev]"

secrets:
	bash scripts/gen_secrets.sh

security:
	bandit -r src -ll
	pip-audit || true

lint:
	ruff check src tests scripts

typecheck:
	mypy src

test:
	pytest

test-unit:
	pytest -m "not integration"

cov:
	pytest --cov=seniorrx --cov-report=html && echo "Relatorio em htmlcov/index.html"

run-api:
	uvicorn seniorrx.interface.api.main:app --reload --port 8000

run-dashboard:
	streamlit run src/seniorrx/interface/dashboard/streamlit_app.py

up:
	docker compose up --build

down:
	docker compose down -v
