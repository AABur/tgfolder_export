.PHONY: init dirs clean mypy ruff check build

FILES_CHECK = export.py

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

mypy:
	mypy $(FILES_CHECK)

ruff:
	ruff check --fxi $(FILES_CHECK)
	ruff format --check $(FILES_CHECK)

check: ruff mypy

build:
	uv build
