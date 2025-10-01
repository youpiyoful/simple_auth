# Simple Auth Makefile helpers

.PHONY: env dev up down build logs test unit integration fmt fmt-check clean

env:
	cp -n .env.example .env || true
	@echo "+ .env ready (or already present)"

dev:
	python run_server.py

up:
	docker compose up

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f api || docker compose logs -f

test:
	./run_tests.sh

unit:
	python -m pytest tests/test_simple_auth.py -v

integration:
	python -m pytest tests/test_integration.py -v

fmt:
	isort . && black .

fmt-check:
	isort . --check-only && black . --check

clean:
	rm -rf .pytest_cache htmlcov .coverage __pycache__ */__pycache__

# Pre-commit hooks
.PHONY: hooks-install hooks-run hooks-autofix
hooks-install:
	pre-commit install

hooks-run:
	pre-commit run --all-files

hooks-autofix:
	pre-commit run --all-files || true
