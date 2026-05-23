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

.PHONY: setup lint lint-instructions test skill-evals-prepare skill-evals skill-evals-fast skill-evals-summary check pre-commit pre-push help

setup: ## Install repo git hooks and dev deps
	git config core.hooksPath scripts/git-hooks
	uv sync

lint: lint-instructions ## Run linters
	uv run ruff check .
	uv run ruff format --check .

lint-instructions: ## Lint agent and skill instruction files
	uv run pytest tests/test_instructions.py

test: ## Run tests
	uv run pytest

skill-evals-prepare: ## Build temporary Agent Skills eval tree under /tmp
	uv run python scripts/evals/prepare-skill-evals.py --out $(SKILL_EVAL_ROOT)

skill-evals: skill-evals-prepare ## Run paid Agent Skills evals and print fix-focused summary
	@set -u; \
	if [ -f .env ]; then set -a; . ./.env; set +a; fi; \
	test -n "$${OPENAI_API_KEY:-}" || { echo "OPENAI_API_KEY missing"; exit 2; }; \
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

skill-evals-fast: ## Fast paid skill eval loop: no baseline, no HTML, advisory
	$(MAKE) skill-evals SKILL_EVAL_BASELINE=0 SKILL_EVAL_HTML_REPORT=0 SKILL_EVAL_CONCURRENCY=8 SKILL_EVAL_STRICT=0

skill-evals-summary: ## Print summary for latest skill eval workspace
	uv run python scripts/evals/summarize-skill-evals.py $(SKILL_EVAL_WORKSPACE) --markdown $(SKILL_EVAL_REPORT)

check: lint test ## Run local push gate

pre-commit: lint ## Fast commit gate

pre-push: check ## Full push gate

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
