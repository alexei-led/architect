.DEFAULT_GOAL := help

NODE_VERSION ?= $(shell cat .node-version 2>/dev/null || echo 24)
SKILL_EVAL_ROOT ?= /tmp/architect-skill-eval-root
SKILL_EVAL_WORKSPACE ?= /tmp/architect-skill-eval-workspace
SKILL_EVAL_INCLUDE ?= **
SKILL_EVAL_TARGET ?= gpt-5.4-mini
SKILL_EVAL_JUDGE ?= gpt-5.4-mini
SKILL_EVAL_LOG_FORMAT ?= jsonl
SKILL_EVAL_LOG_FILE ?= $(SKILL_EVAL_WORKSPACE)/events.jsonl
SKILL_EVAL_REPORT ?= $(SKILL_EVAL_WORKSPACE)/summary.md
SKILL_EVAL_HTML_REPORT ?= 1
SKILL_EVAL_BASELINE ?= 1
SKILL_EVAL_CONCURRENCY ?= 4
SKILL_EVAL_STRICT ?= 1
SKILL_EVAL_CLI ?= $(shell if command -v agent-skills-eval >/dev/null 2>&1; then printf 'agent-skills-eval'; elif command -v bunx >/dev/null 2>&1; then printf 'bunx agent-skills-eval'; elif command -v fnm >/dev/null 2>&1; then printf 'fnm exec --using $(NODE_VERSION) -- npx --yes agent-skills-eval'; else printf 'npx --yes agent-skills-eval'; fi)
ifeq ($(FAST),1)
SKILL_EVAL_BASELINE := 0
SKILL_EVAL_HTML_REPORT := 0
SKILL_EVAL_CONCURRENCY := 8
SKILL_EVAL_STRICT := 0
endif

.PHONY: setup build check generated-check npm-packages npm-packages-check package-smoke evals release help

setup: ## Install repo git hooks and dev deps
	git config core.hooksPath scripts/git-hooks
	uv sync

build: ## Compile installable runtime packages from the canonical bundle
	agbun build

check: ## Run CI-safe lint, format, and tests
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest

generated-check: ## Verify generated runtime packages without writing
	agbun check

npm-packages: ## Stage lean npm packages from generated runtime files
	python3 scripts/release/stage_npm_packages.py

npm-packages-check: ## Stage and inspect every npm tarball
	python3 scripts/release/stage_npm_packages.py --check

package-smoke: build npm-packages ## Install or load every generated package with available vendor CLIs
	REQUIRE_VENDOR_CLIS=1 scripts/check-packages

evals: ## Run paid skill evals (use FAST=1 for advisory fast mode)
	@set -u; \
	if [ -f .env ]; then set -a; . ./.env; set +a; fi; \
	test -n "$${OPENAI_API_KEY:-}" || { echo "OPENAI_API_KEY missing"; exit 2; }; \
	uv run python scripts/evals/prepare-skill-evals.py --out $(SKILL_EVAL_ROOT); \
	mkdir -p $(SKILL_EVAL_WORKSPACE); \
	baseline_flag=""; \
	if [ "$(SKILL_EVAL_BASELINE)" != "0" ]; then baseline_flag="--baseline"; fi; \
	report_flag="--no-report"; \
	if [ "$(SKILL_EVAL_HTML_REPORT)" != "0" ]; then report_flag="--report"; fi; \
	$(SKILL_EVAL_CLI) $(SKILL_EVAL_ROOT) \
		--include '$(SKILL_EVAL_INCLUDE)' \
		--workspace $(SKILL_EVAL_WORKSPACE) \
		$$baseline_flag \
		--target $(SKILL_EVAL_TARGET) \
		--judge $(SKILL_EVAL_JUDGE) \
		--base-url https://api.openai.com/v1 \
		--api-key-env OPENAI_API_KEY \
		--concurrency $(SKILL_EVAL_CONCURRENCY) \
		--log-format $(SKILL_EVAL_LOG_FORMAT) \
		--log-file $(SKILL_EVAL_LOG_FILE) \
		--layout iteration \
		--strict \
		$$report_flag; \
	status=$$?; \
	uv run python scripts/evals/summarize-skill-evals.py $(SKILL_EVAL_WORKSPACE) --markdown $(SKILL_EVAL_REPORT) || true; \
	if [ "$(SKILL_EVAL_STRICT)" = "0" ]; then exit 0; fi; \
	exit $$status

release: ## Bump version, update changelog, commit, and tag (usage: make release V=X.Y.Z)
ifndef V
	$(error Usage: make release V=X.Y.Z)
endif
	scripts/release/release-tag v$(V)

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
