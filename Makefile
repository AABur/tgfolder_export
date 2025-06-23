.PHONY: init dirs clean mypy ruff test test-cov check build version-patch version-minor version-major

FILES_CHECK = .

init: dirs deps

deps:
	uv sync --dev

dirs:
	if [ ! -e var/run ]; then mkdir -p var/run; fi
	if [ ! -e var/log ]; then mkdir -p var/log; fi

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete
	find -name '__pycache__' -delete
	rm -rf *.egg-info
	rm -rf dist/*
	rm -rf .coverage
	rm -rf htmlcov/

mypy:
	uv run mypy $(FILES_CHECK)

ruff:
	uv run ruff check --fix $(FILES_CHECK)
	uv run ruff format --check $(FILES_CHECK)

test:
	uv run pytest

test-cov:
	uv run pytest --cov --cov-report=html --cov-report=term
	@echo "HTML coverage report generated in htmlcov/index.html"

check: ruff mypy test

build:
	uv build

version-patch:
	uv version --bump patch

version-minor:
	uv version --bump minor

version-major:
	uv version --bump major
