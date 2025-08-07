.PHONY: help init clean mypy lint test test-cov check
.DEFAULT_GOAL := help

# Help command
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

init: ## Initialize project (create directories and sync dependencies)
	mkdir -p var
	uv sync --dev

clean: ## Clean temporary files and cache
	find . -name '*.pyc' -delete
	find . -name '*.swp' -delete  
	find . -name '__pycache__' -delete
	rm -rf *.egg-info dist .coverage htmlcov

mypy: ## Run type checking with mypy
	uv run mypy .

lint: ## Run ruff linter and formatter
	uv run ruff check --fix .
	uv run ruff format --check .

test: ## Run pytest tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov --cov-report=html --cov-report=term
	@echo "HTML coverage report: htmlcov/index.html"

check: lint mypy test ## Run all linting, type checking, and tests
