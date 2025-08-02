.PHONY: run test fmt lint ruff pylint mypy

run:
	python3 local.py

test:
	python3 -m unittest discover tests

fmt:
	python3 -m black .

fmt-ci:
	python3 -m black --check .

lint: ruff-fix pylint mypy bandit

ruff:
	python3 -m ruff check .

ruff-fix:
	python3 -m ruff check . --fix

pylint:
	find . -name ".venv" -prune -o -name "*.py" -print | xargs python3 -m pylint --score=n --reports=n --output-format=colorized

mypy:
	find . -name ".venv" -prune -o -name "*.py" -print | xargs python3 -m mypy

bandit:
	python3 -m bandit -c pyproject.toml --exclude "./.venv" -r . -q
