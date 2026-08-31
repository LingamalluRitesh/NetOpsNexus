.PHONY: help install dev build test coverage lint format migrate seed docker-up docker-down clean validate

PYTHON ?= python
NPM ?= npm

help:
	@echo "NetOps Nexus - Enterprise Network Intelligence Platform"
	@echo "--------------------------------------------------------"
	@echo "Available commands:"
	@echo "  make install     - Install all backend and frontend dependencies"
	@echo "  make dev         - Run backend and frontend development servers"
	@echo "  make build       - Build frontend and verify backend packaging"
	@echo "  make test        - Run complete pytest suite"
	@echo "  make coverage    - Run pytest with coverage report"
	@echo "  make lint        - Run ruff, mypy, and frontend linting"
	@echo "  make format      - Format backend code with ruff and black"
	@echo "  make migrate     - Initialize database and run migrations"
	@echo "  make seed        - Seed database with realistic lab network topology"
	@echo "  make docker-up   - Launch multi-container Docker environment"
	@echo "  make docker-down - Stop Docker environment"
	@echo "  make clean       - Remove cache, temporary files, and build artifacts"
	@echo "  make validate    - Run project quality validation benchmark suite"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(NPM) install

dev:
	$(PYTHON) scripts/run_dev.py

build:
	$(NPM) run build
	$(PYTHON) -m pip check

test:
	$(PYTHON) -m pytest tests/ -v

coverage:
	$(PYTHON) -m pytest tests/ --cov=backend/app --cov-report=term-missing --cov-report=html

lint:
	$(PYTHON) -m ruff check backend/ tests/
	$(PYTHON) -m mypy backend/app --ignore-missing-imports || true

format:
	$(PYTHON) -m ruff format backend/ tests/

migrate:
	$(PYTHON) -c "import asyncio; from backend.app.database import init_db; asyncio.run(init_db())"

seed:
	$(PYTHON) scripts/seed_database.py

docker-up:
	docker compose -f docker/docker-compose.yml up -d --build

docker-down:
	docker compose -f docker/docker-compose.yml down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist build .pytest_cache htmlcov .coverage coverage.xml 2>/dev/null || true

validate:
	$(PYTHON) scripts/validate_project.py
