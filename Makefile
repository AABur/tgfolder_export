.PHONY: help init clean clean-session mypy lint format test test-cov check run-json run-text
.DEFAULT_GOAL := help

# Help command
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

init: ## Initialize project (sync dependencies)
	uv sync --dev

clean: ## Clean temporary files and cache
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.swp' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf *.egg-info dist .coverage htmlcov .ruff_cache .mypy_cache .pytest_cache

clean-session: ## Clear Telegram session files
	rm -rf .tempts/
	@echo "Session files cleared"

mypy: ## Run type checking with mypy
	uv run mypy .

lint: ## Run ruff linter (check only)
	uv run ruff check --fix .
	uv run ruff format --check .

format: ## Auto-format code with ruff
	uv run ruff check --fix .
	uv run ruff format .

test: ## Run pytest tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov --cov-report=html --cov-report=term
	@echo "HTML coverage report: htmlcov/index.html"

check: lint mypy test ## Run all linting, type checking, and tests

run-json: ## Run export in JSON format (default file)
	uv run export.py -j

run-text: ## Run export in text format (default file)
	uv run export.py -t
