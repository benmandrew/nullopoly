.PHONY: run test fmt lint ruff pylint mypy

run:
	python3 main.py

test:
	python3 -m unittest discover tests

fmt:
	python3 -m black --line-length 80 .

fmt-ci:
	python3 -m black --check --line-length 80 .

lint: ruff pylint mypy

ruff:
	python3 -m ruff check .

pylint:
	find . -name ".venv" -prune -o -name "*.py" -print | xargs python3 -m pylint --disable=missing-docstring --score=n --reports=n --output-format=colorized

mypy:
	find . -name ".venv" -prune -o -name "*.py" -print | xargs python3 -m mypy --ignore-missing-imports
