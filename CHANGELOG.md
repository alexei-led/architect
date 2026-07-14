# Changelog

All notable changes to `architect` are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
major = breaking instruction/report contracts, minor = new skills or tooling,
patch = fixes and documentation updates.

## [Unreleased]

### Fixed

- Scoped Architect's `sandbox_mode` metadata to the Codex package so generated
  Claude, Copilot, Cursor, and Pi agents remain compatible with `agbun` v0.3.0.

## [0.8.1] - 2026-07-14

### Packaging maintenance

- Kept system `agbun` as the local build, generated-artifact drift, package-smoke,
  and release prerequisite while removing it from GitHub CI and release validation.
- Split CI-safe `make check` (Ruff and pytest) from local `make generated-check`
  so GitHub does not invoke or check `agbun`.
- Added isolated native package smoke tests for Claude Code, Codex, Pi, GitHub
  Copilot, Grok Build, and Cursor.
- Added release-safe version propagation, generated-provenance checks, complete skill
  inventory checks, and Grok/Claude compatibility checks.

## [0.8.0] - 2026-07-14

### Distribution

- Migrated generated Claude Code, Codex, Pi, GitHub Copilot, Grok Build, and Cursor
  packages to **Agent Bundler**.
- Added installable GitHub Copilot and Cursor plugin outputs with the Architect role,
  repository marketplace manifests, and generated package READMEs.
- Added a repository-root Pi package that registers generated skills and the Architect
  subagent, including `pi-subagents` as a runtime dependency.
- Kept Grok Build on the Claude-compatible package for role installation; retained
  Codex’s documented manual custom-agent installation.

## [0.7.0] - 2026-06-30

### codebase-memory-mcp tool skill

- Added `tools-codebase-memory` to the architecture plugin: it gathers persistent code-knowledge-graph evidence (architecture overview, type-resolved call edges, cycles, blast radius, module clusters, dead code, and cross-session ADRs) from the `codebase-memory-mcp` MCP server when its `mcp__codebase-memory-mcp__*` tools are installed, and falls back to `tools-codegraph` when the server is absent. Wired it into the `docs/tools.md` evidence ladder and the `architecture-review` evidence step.

### archfit v1.1.0 alignment

- Aligned every archfit invocation to the v1.1.0 CLI: the single `archfit analyze` command replaces `check`/`score`/`scan`/`review`/`diff`, with `--gate` for CI exit codes, `--json`/`--format scorecard`/`--sarif` for output, and `--base <ref>` for deltas (the `--report` flag is gone; `--full`/`--advisory` are now defaults). Updated `tools-archfit`, `architecture-review`, `architecture-plan`, `src/templates/plan.md`, `docs/methodology.md`, and `docs/tools.md`.
- Moved the config/LLM commands in `tools-archfit`'s do-not-use list to their v1.1.0 spellings: `config init`, `config update --apply`, `config enrich {labels,owner,volatility,subdomain}`, `config init --llm`, and `config enrich ... --apply` (renamed from `init`/`update`/`enrich`/`autopilot`/`--pin`); LLM narrative is now `analyze --llm` / `explain`.
- Corrected the archfit output contract in `tools-archfit`: the scorecard now synthesizes a single `coupling_balance` dimension (not seven), finding status values are `new`/`baseline`/`fixed`/`waived`/`expired_waiver` (not `excepted`), `bc/imbalanced_coupling` fields live in each finding's `matched_by`, `symmetric` is a labelable strength, volatility is config + inferred cascade only (no path heuristic), and `cycle`/`blast_radius` are metrics (archfit emits no hub/instability metric).

## [0.6.0] - 2026-06-23

### Balanced Coupling fidelity

- Added a graded read to `methodology-balanced-coupling`: the book's numeric balance equation (`BALANCE = max(|strength - distance|, 10 - volatility) + 1`) with its 1–10 scale anchors, alongside the existing binary rule, plus a per-dimension evidence→band rubric (tools first, LLM where no tool can decide) so the inputs are anchored to observable evidence rather than eyeballed.
- Reframed connascence from a tie-breaker to the model's degree axis within each strength level (static connascence grades contract/model; dynamic connascence plus symmetric functional grades functional), and named symmetric functional coupling — a DRY violation with no dependency edge.
- Added inferred volatility (a stable component coupled to a volatile upstream is effectively volatile) and reconciled the severity mapping with the graded BALANCE.
- Updated `docs/methodology.md` and `docs/scoring.md` to match.
- Tightened volatility sourcing across `tools-gitnexus`, `architecture-review`, and the report template so git churn/change-history only corroborates domain-led volatility and never sets it (the book's essential-vs-accidental volatility rule).

### archfit consumption

- Updated `tools-archfit` to consume archfit's book-aligned coupling output: the book balance equation (`balance = max(|strength - distance|, 10 - volatility) + 1`, scorer `bc_score.v3`) with the `bc/imbalanced_coupling` advisory fields (`score_value`, `score_band`, `cheapest_move`, `distance_basis`) and the `classified_edges` distribution (`mean_balance`, `scored`, `abstained`, per-dimension breakdowns), plus the `archfit score` scorecard command.
- Documented the `.archfit-labels.yaml` strength-label artifact (only `status: approved` overrides the SCIP hint; labelable strengths are contract/model/functional/intrusive; `symmetric` is clone-derived) and that heavy LLM-provenance labeling lowers `coupling_balance` confidence.
- Sharpened calibration: archfit's SCIP strength tops out at `functional` without labels, its volatility is config/heuristic (never churn), `runtime_async` never moves distance, and abstained unknown-strength/distance edges cap `coupling_balance` coverage.

## [0.5.0] - 2026-06-20

### archfit integration and evidence calibration

- Added the `tools-archfit` skill: consume archfit's deterministic facts (full/delta JSON, scorecard, tool coverage, findings, SARIF, `agent_tasks`) and return an `archfit_calibration` matrix (confirmed, severity-adjusted, false-positive/noise, missed-by-archfit, config changes, new fitness checks, labels to confirm) instead of passing tool scores through.
- Updated `architecture-review` to run archfit as a deterministic preflight when a repo has `.archfit.yaml` or `archfit` is available, calibrate its facts with independent verification, and record `module_volatility` and `archfit_calibration` in full reports and quick sweeps.
- Registered `tools-archfit` in the architecture plugin and added archfit detection to `architect-doctor`.

### Scoring honesty

- Added coverage-gap calibration: missing, partial, or stale primary evidence for a dimension forces low confidence and caps the band at `mixed` (default midpoint) until re-established, so down-calibration of tool false-greens (for example archfit `coupling_balance` with no classified edges when scip is absent) is reproducible in magnitude, not only direction.
- Forbade green or high-quality scores derived from missing, unclassified, or uncalibrated tool evidence; absence of findings counts only when a current tool covered that class.

### Reusable judgments and deterministic gates

- Added reusable `module_volatility` judgments (domain role, volatility, source, evidence, confidence) to the report contract and required them in reviews.
- Required architecture plans to tie boundary/coupling tasks to deterministic fitness gates with before-fail/after-pass expectations, and to include archfit check/delta validation commands when configured.
- Updated report, design, and plan templates accordingly (`module_volatility`, `archfit_calibration`, design labels to confirm, per-task fitness-gate slot).

### Documentation

- Documented the combined archfit + architect loop and the coverage-gap rule across README, methodology, scoring, report-format, and tools docs, and added the enhancement plan under `docs/plans/`.

## [0.4.0] - 2026-06-19

### Architecture review workflow

- Added a quick-sweep review mode for multi-repo or low-budget comparisons that returns evidence-backed candidates, next checks, and an explicit quality self-check instead of forcing partial scores.
- Tightened review guidance so `coupling_balance` is grounded in per-relationship records: strength, distance, volatility, evidence, severity, and balancing move.
- Clarified that nonzero exits from analysis tools can be confirmed findings rather than tool failures.

### Methodology and documentation

- Aligned README, methodology, scoring, report-format, and tools docs with Balanced Coupling terminology and the current review workflow.
- Documented the distance split used in reviews: code, ownership, runtime, and deploy distance.
- Clarified domain volatility versus implementation/provider volatility and how quick sweeps differ from full reviews.

### Tooling

- Expanded `architect-doctor` coverage for newly supported analysis, operational, and security tools including `tree-sitter`, `basedpyright`, `pipdeptree`, `radon`, `lizard`, `kubeconform`, `kube-linter`, `hadolint`, `actionlint`, `tflint`, `tofu`, `conftest`, `grype`, `tfsec`, and `zizmor`.
- Improved repo applicability detection for Docker, GitHub Actions, recursive Terraform markers, and Kubernetes manifests.
- Updated release automation to bump `src/architect_tools/__init__.py` version during tagged releases.

## [0.3.2] - 2026-06-06

### Skill instructions

- Made plan writing safer: with no confirmed destination, return the plan in the conversation and ask before creating `docs/plans/` or writing a file, instead of writing one automatically.
- Hardened evidence gathering against polluting the target repo: redirect tool caches and local state to a temp dir (`RUFF_CACHE_DIR`, `TF_DATA_DIR`, Terraform `.terraform`) and ask before writing generated tool artifacts; check GitNexus index freshness via an exposed runtime capability or the CLI (`gitnexus status` / `gitnexus detect-changes`).
- Scoped report tooling (`tools-report-markdown`) to the target report or plan instead of repo-wide link/spell/format sweeps, and switched format checks to the repo's detected package runner (`npm exec` / `pnpm exec` / `bunx`) rather than a hardcoded `npx prettier`.

### Documentation cleanup

- Slimmed the README and CONTRIBUTING for a tighter, less repetitive overview.

## [0.3.1] - 2026-05-24

### Plugin marketplace metadata

- Fixed Claude Code marketplace metadata to satisfy the current manifest schema.
- Updated Codex marketplace and plugin metadata for current plugin installation and UI surfaces.

## [0.3.0] - 2026-05-23

### Architecture workflow

- Added conditional next-skill routing for architecture review, design, and plan flows.
- Made architecture plans task-runner executable with implementation steps, per-task file lists, GitNexus impact checks, concrete verification commands, manual checks, and final verification/documentation handoff.
- Added regression tests for the executable plan-template contract.

## [0.2.1] - 2026-05-23

### Architecture design

- Added `architecture-design` for requirements-to-architecture work, including module maps, integration contracts, module test specifications, fitness checks, self-review, and skill-flow handoff.
- Added `src/templates/design.md` for target architecture artifacts.

### Review and reporting

- Added Mermaid guidance for human-facing reports while keeping AI-targeted reports plain text.
- Added skill navigation and outcome-based task-list discipline to design/review/plan flows.
- Strengthened architecture-review with working-model validation, stale-doc suspicion, and human-facing finding narratives.
- Expanded Balanced Coupling guidance with the balance-rule mnemonic, examples, generic-provider volatility, and connascence tie-breakers.
- Extended architecture-plan to sequence work from approved design artifacts as well as review findings.

## [0.2.0] - 2026-05-23

### Architecture-review routing

- Added `tools-code-search` for local `fd`/`rg`/`git grep` discovery and targeted read evidence.
- Tightened architecture-review and tool skill descriptions around modularity, coupling, dependency direction, blast radius, and fragility.
- Added evidence-output contracts to tool skills for repeatable architecture-report evidence collection.

### Runtime packaging

- Included `tools-code-search` in Claude, Codex, and Pi runtime plugin artifacts.
- Clarified tool coverage docs for discovery, generated/vendor scope, and specialized-tool handoff.
- Fixed brittle shell quoting in the code-search import/dependency search example.
- Removed obsolete `.gitkeep` files from populated template directories.

## [0.1.0] - 2026-05-23

### Added

- Initial architecture-review package with a read-only Architect role.
- Review, scorecard, planning, methodology, and tool-focused Agent Skills.
- Report, plan, and scorecard templates with validation helpers.
- Local CI targets, Git hooks, Gitleaks scanning, and GitHub Actions workflows.
