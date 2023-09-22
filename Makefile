.PHONY: init venv deps dirs clean mypy pylint ruff check build

FILES_CHECK_MYPY = export.py
FILES_CHECK_ALL = $(FILES_CHECK_MYPY)

init: venv deps dirs

venv:
	virtualenv -p python3 .env

deps:
	curl -sS https://bootstrap.pypa.io/get-pip.py | .env/bin/python3 # a fix for manually built python
	.env/bin/python -m pip install -U setuptools # a fix for manually built python
	.env/bin/pip install -r requirements_dev.txt
	

dirs:
	if [ ! -e var/run ]; then mkdir -p var/run; fi
	if [ ! -e var/log ]; then mkdir -p var/log; fi

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete
	find -name '__pycache__' -delete

mypy:
	mypy --strict $(FILES_CHECK_MYPY)

pylint:
	pylint -j0 $(FILES_CHECK_ALL)

ruff:
	ruff $(FILES_CHECK_ALL)

check: ruff mypy pylint

build:
	rm -rf *.egg-info
	rm -rf dist/*
	python -m build --sdist
