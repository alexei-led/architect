.DEFAULT_GOAL := help

.PHONY: setup lint test check pre-commit pre-push help

setup: ## Install repo git hooks and dev deps
	git config core.hooksPath scripts/git-hooks
	uv sync

lint: ## Run linters
	uv run ruff check .
	uv run ruff format --check .

test: ## Run tests
	uv run pytest

check: lint test ## Run local push gate

pre-commit: lint ## Fast commit gate

pre-push: check ## Full push gate

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
