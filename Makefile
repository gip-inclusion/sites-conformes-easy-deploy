.DEFAULT_GOAL := help
.PHONY: help install lint format test check

help: ## Show this help
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

venv: ## Install dependencies, including dev tools
	uv sync

lint: ## Check code style and quality with ruff
	uv run ruff check .
	uv run ruff format --check .

format: ## Fix what ruff can fix and format the code
	uv run ruff check --fix .
	uv run ruff format .

test: ## Run the test suite, reusing the test database (ARGS=--create-db to rebuild it)
	uv run pytest $(ARGS)

check: lint test ## Run lint and tests
