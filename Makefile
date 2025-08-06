.PHONY: init clean mypy lint test test-cov check

init:
	mkdir -p var
	uv sync --dev

clean:
	find . -name '*.pyc' -delete
	find . -name '*.swp' -delete  
	find . -name '__pycache__' -delete
	rm -rf *.egg-info dist .coverage htmlcov

mypy:
	uv run mypy .

lint:
	uv run ruff check --fix .
	uv run ruff format --check .

test:
	uv run pytest

test-cov:
	uv run pytest --cov --cov-report=html --cov-report=term
	@echo "HTML coverage report: htmlcov/index.html"

check: lint mypy test
