.PHONY: run test fmt lint ruff pylint mypy

run:
	python3 local.py

test:
	@echo "Running unit tests"
	@python3 -m unittest discover tests

fmt:
	@echo "Formatting Python files with black"
	@python3 -m black .

fmt-ci:
	@echo "Checking Python formatting with black"
	@python3 -m black --check .

lint: ruff-fix pylint mypy bandit
	@echo "Lint suite complete"

ruff:
	@echo "Linting Python files with ruff"
	@python3 -m ruff check .

ruff-fix:
	@echo "Fixing lint issues with ruff"
	@python3 -m ruff check . --fix

pylint:
	@echo "Linting Python files with pylint"
	@find . \( -name ".venv" -o -name "venv" \) -prune -o -name "*.py" -print | xargs python3 -m pylint --score=n --reports=n --output-format=colorized

mypy:
	@echo "Type checking Python files with mypy"
	@find . \( -name ".venv" -o -name "venv" \) -prune -o -name "*.py" -print | xargs python3 -m mypy

bandit:
	@echo "Running security checks with bandit"
	@python3 -m bandit -c pyproject.toml --exclude "./.venv,./venv" -r . -q
