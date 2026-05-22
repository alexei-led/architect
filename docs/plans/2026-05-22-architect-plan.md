# Architect extension plan

## Overview

Build an instruction-first architecture review extension for Claude Code, Codex
CLI, and Pi.

The extension contains an architect agent, focused skills, report templates,
plan templates, and small helper tools. Agents use local OSS CLIs directly.

The plan is organized as vertical slices. Each slice should produce something
usable and verifiable. The broad tool suite stays in scope for v1, but tool use
is routed through coverage, applicability, and evidence summaries so reports do
not become tool-output landfill. Civilization is fragile enough.

## Context

### First usable slice

Before expanding the tool suite, ship one thin path:

1. One runtime overlay works end-to-end.
2. One dogfood repo produces interview context, system map, scored report, and
   refactoring plan.
3. Report validation and comparison work on the produced report.
4. Tool coverage records used, skipped, missing, and failed tools with confidence
   impact.

Phase 5 breadth starts only after this slice exposes real tool friction.

### Acceptance Criteria

- Architect agent exists for Claude, Codex, and Pi.
- Review flow produces four artifacts: interview context, system map,
  architecture report, and refactoring plan.
- Review skill runs interview before scoring when context is missing.
- Interview uses structured question tools when the runtime supports them.
- Review skill builds a system map before judging quality.
- Architect covers all applicable evidence dimensions with available tools
  before making claims.
- Architect records tool coverage, missing tools, failed tools, and confidence
  impact.
- Scorecard skill defines dimensions, score bands, anchors, and confidence
  rules.
- Evidence references have a stable schema.
- Balanced Coupling skill reuses Vlad Khononov material with attribution and
  within licensing limits.
- Tool skills cover ast-grep, codegraph, GitNexus, LSP, and tree-sitter.
- Tool skills cover TypeScript, Python, Go, and operational dependencies.
- Helper tools and build scripts use Python 3.12+ with uv.
- Report template writes Markdown with YAML frontmatter scores.
- Plan template writes phases, tasks, verification, and acceptance criteria.
- Helper tools validate reports, compare reports, and check tools.
- Comparisons explain improvement, degradation, or non-comparability.
- Claude, Codex, and Pi outputs build from one source tree.
- Dogfood runs on `/Users/alexei/Workspace/ccgram`, not this planning repo.

## Validation Commands

Run after the scaffold task creates the Python project files:

- `uv sync`
- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`

## Development Approach

- Testing approach: regular. Define contracts and fixtures before implementation when practical.
- Complete one Task section fully before moving to the next.
- Keep changes vertical and independently verifiable.
- Update this plan when scope changes during implementation.
- Keep runtime dependencies minimal; prefer local OSS CLI tools over wrapped package logic.

## Testing Strategy

- Add or update tests for every code-changing task.
- Validate generated examples, templates, report schemas, and helper tools with fixtures.
- Run the validation commands after each task once the project scaffold exists.
- Treat manual dogfood findings as evidence for prompt, rubric, and template changes.

## Progress Tracking

- Mark completed task items immediately after they are done.
- Add newly discovered in-scope work to the current or next Task section.
- Move non-automatable follow-up work to Post-Completion without checkboxes.
- Do not leave task checkboxes outside Task sections; ralphex only executes Task or Iteration sections.

## Implementation Steps

### Task 1: Phase 0 - scaffold

Files:

- `README.md`
- `LICENSE`
- `pyproject.toml`
- `uv.lock`
- `src/agents/`
- `src/skills/`
- `src/templates/`
- `src/architect_tools/`
- `src/plugins/`
- `scripts/build/`
- `tests/`

Tasks:

- [x] Initialize package metadata.
- [x] Add `pi-package` keyword.
- [x] Add uv-backed build, check, and test scripts.
- [x] Keep runtime dependencies minimal.
- [x] Add source-to-dist layout.
- [x] Add docs for instruction-first design.

Verification:

- [x] `uv sync` succeeds.
- [x] `uv run pytest` succeeds.
- [x] `uv run ruff check .` succeeds.
- [x] `uv run ruff format --check .` succeeds.
- [x] Expected source directories exist.

### Task 2: Phase 1 - artifact contract and templates

Files:

- `src/templates/report.md`
- `src/templates/scorecard.yaml`
- `src/templates/plan.md`
- `tests/fixtures/reports/example.md`
- `tests/fixtures/plans/example.md`

Tasks:

- [x] Define interview context fields.
- [x] Define system map fields.
- [x] Define report frontmatter.
- [x] Choose YAML handling: PyYAML dependency or a deliberately constrained
      subset. Prefer PyYAML unless packaging proves it too costly. (PyYAML added.)
- [x] Define score dimensions.
- [x] Define `0..100` score bands and anchors.
- [x] Define confidence levels.
- [x] Define evidence reference schema.
- [x] Define finding schema with stable IDs.
- [x] Define tool coverage and gap schema.
- [x] Define report sections.
- [x] Define plan structure.
- [x] Define report comparability rules: scope, rubric version, and tool coverage.

Verification:

- [x] Example report frontmatter parses.
- [x] Example report includes score values, bands, confidence, evidence refs, and
      tool coverage.
- [x] Example plan includes phases, tasks, verification, acceptance criteria, and
      safety notes.
- [x] Low confidence cannot be presented as high quality.
- [x] Non-comparable reports have an explicit reason.

### Task 3: Phase 2 - architect agent and review loop

Files:

- `src/agents/architect/AGENT.md`
- `src/agents/architect/claude/frontmatter.yaml`
- `src/agents/architect/codex/frontmatter.yaml`
- `src/agents/architect/pi/frontmatter.yaml`
- `src/skills/architecture-review/SKILL.md`
- `src/skills/architecture-review/references/interview.md`
- `src/skills/architecture-review/references/triage.md`
- `src/skills/architecture-scorecard/SKILL.md`
- `src/skills/architecture-plan/SKILL.md`

Tasks:

- [x] Make architect read-only for source code by default.
- [x] Allow report/plan writes only with explicit user approval.
- [x] Require interview before full scoring when context is missing.
- [x] Require docs and code inspection before asking answerable questions.
- [x] Require system map before scoring.
- [x] Define intended architecture source order.
- [x] Define observed architecture evidence sources.
- [x] Separate facts, hypotheses, scores, and recommendations.
- [x] Cite evidence for every finding.
- [x] Use the scorecard skill before assigning scores.
- [x] Use the report template for reports.
- [x] Use the plan template for plans.
- [x] Recommend incremental refactoring only.
- [x] Define user-facing flows: architecture review, compare reports, and make
      refactoring plan.
- [x] Route code changes to an engineer or mutator agent.

Verification:

- [x] Agent has no edit/write behavior for production source code.
- [x] Agent output contract is clear.
- [x] Skill interviews first when context is missing.
- [x] Skill uses structured question tools on Claude and Pi.
- [x] Skill defines Codex structured-question behavior through target overlay.
- [x] Skill does not score from directory shape alone.
- [x] Skill cites tools and files used.
- [x] Instruction lint passes.

### Task 4: Phase 3 - Balanced Coupling and architecture fitness

Files:

- `src/skills/methodology-balanced-coupling/SKILL.md`
- `src/skills/methodology-balanced-coupling/references/details.md`
- `src/skills/methodology-architecture-fitness/SKILL.md`

Tasks:

- [x] Decide whether Balanced Coupling content is summary-only, adapted, quoted,
      or requires explicit permission. (Summary-only; source is CC BY-NC-SA, so
      ShareAlike would taint the MIT repo — adapted/quoted reuse needs Vlad's
      permission, parked in Post-Completion.)
- [x] Reuse and adapt Vlad Khononov definitions with attribution and licensing
      caution. (Summarized in our own words with attribution + links.)
- [x] Define integration strength levels.
- [x] Define implicit vs explicit coupling.
- [x] Define distance, lifecycle coupling, runtime coupling, and team distance.
- [x] Define volatility via DDD subdomains and change frequency.
- [x] Define balance rule: high strength + high distance + high volatility is the
      highest risk.
- [x] Define severity mapping.
- [x] Warn against generic “decouple everything” advice.
- [x] Define architecture fitness as executable checks, not documentation.
- [x] Map common findings to candidate fitness checks.

Verification:

- [x] Skill explains DDD terms on first use.
- [x] Skill asks only context questions that change assessment.
- [x] Highest priority is high strength, high distance, high volatility.
- [x] Fitness guidance distinguishes existing checks from recommended checks.
- [x] Licensing and attribution path is clear before writing reusable material.

### Task 5: Phase 4 - first dogfood pass on ccgram

Target:

- `/Users/alexei/Workspace/ccgram`

Tasks:

- [x] Run the current review loop manually against ccgram.
- [x] Cover applicable evidence dimensions with tools that already work in the
      environment.
- [x] Record tool friction. (docs/dogfood/ccgram/friction.md, FR1-FR7)
- [x] Record missing evidence. (report system_map.missing_evidence + FR5)
- [x] Record unclear interview questions. (FR1 non-interactive interview gap)
- [x] Produce one report draft. (docs/dogfood/ccgram/report.md)
- [x] Produce one plan draft from that report. (docs/dogfood/ccgram/plan.md)
- [x] Tune templates, prompts, rubrics, and tool routing based on real pain.
      (review SKILL.md + interview.md edits for FR1, FR3-FR6)

Verification:

- [x] Report helps a human understand ccgram’s architecture.
- [x] Recommendations cite evidence. (F1-F4 each carry evidence refs)
- [x] Scores are explainable. (score map table with per-dimension justification)
- [x] Unsupported claims are removed. (dependency_graph_health capped at low
      confidence; no scoring from imports alone)
- [x] Plan avoids unsupported rewrites. (incremental phases; "No rewrites")

### Task 6: Phase 5 - evidence tool skill suite

Files:

- `src/skills/tools-ast-grep/SKILL.md`
- `src/skills/tools-ast-grep/references/rules.md`
- `src/skills/tools-codegraph/SKILL.md`
- `src/skills/tools-gitnexus/SKILL.md`
- `src/skills/tools-lsp-tree-sitter/SKILL.md`
- `src/skills/tools-typescript/SKILL.md`
- `src/skills/tools-python/SKILL.md`
- `src/skills/tools-go/SKILL.md`
- `src/skills/tools-infra-operational/SKILL.md`
- `src/skills/tools-report-markdown/SKILL.md`

Tasks:

- [x] Define tool applicability rules.
- [x] Define tool coverage levels: discovery, structural, semantic, dependency,
      change, operational, security/supply-chain, and report quality.
- [x] Define context-budget rules for summarizing noisy output.
- [x] Define tool-budget and stop rules for redundant or expensive scans.
- [x] Document ast-grep commands for imports, exports, direct DB access, routes,
      and framework leaks.
- [x] Document codegraph init, index, sync, status, query, context, affected, and
      files commands.
- [x] Document GitNexus analyze, status, list, query, context, impact,
      detect-changes, and cypher commands.
- [x] Document stale-index handling for codegraph and GitNexus.
- [x] Document LSP definitions, references, implementations, diagnostics,
      document symbols, workspace symbols, and tree-sitter syntax queries.
- [x] Add TypeScript commands for dependency-cruiser, madge, knip, tsc, ESLint,
      and package managers.
- [x] Add Python commands for import-linter, pydeps, pyright or basedpyright,
      ruff, deptry, pipdeptree, uv tree, radon or lizard, and vulture.
- [x] Add Go commands for go list, go mod graph, goda, gopls, staticcheck,
      govulncheck, and go-callvis.
- [x] Add operational commands for Helm, Kustomize, Kubernetes, Terraform,
      OpenTofu, Docker, GitHub Actions, policy tools, SBOM, and vulnerability
      scanners.
- [x] Add report commands for Markdown, Mermaid, jq, yq, Graphviz, D2, links,
      spelling, and formatting.
- [x] Skip dedicated PHP, Ruby, COBOL, Java, and JVM-only skills.

Verification:

- [x] Each skill includes exact commands.
- [x] Each skill explains when the tool is applicable.
- [x] Each skill explains how tool evidence affects confidence.
- [x] Each skill explains failure and missing-tool handling.
- [x] Each skill avoids duplicating tool behavior in package code.
- [x] Tool output examples are summarized, not pasted wholesale.
- [x] Each skill says when to stop and record a coverage gap instead of running
      another redundant tool.

### Task 7: Phase 6 - Python helper tools

Files:

- `src/architect_tools/doctor.py`
- `src/architect_tools/validate_report.py`
- `src/architect_tools/compare_reports.py`
- `tests/tools/*.py`

Tasks:

- [x] Use Python 3.12+ typing and stdlib-first design, with PyYAML allowed for
      report frontmatter and scorecard parsing.
- [x] `doctor` checks tool availability and versions.
- [x] `doctor` reports available, applicable, covered, missing, and failed tool
      states where possible.
- [x] `validate-report` checks frontmatter, score bands, confidence, required
      sections, evidence refs, finding IDs, and tool coverage.
- [x] `compare-reports` compares scores, finding IDs, confidence, scope, rubric
      version, and tool coverage.
- [x] `compare-reports` reports non-comparability instead of inventing trends.
- [x] Keep helpers small.
- [x] Fail with an install hint when YAML support is unavailable.
- [x] Do not wrap ast-grep, codegraph, GitNexus, LSP, or tree-sitter.

Verification:

- [x] Helpers have pytest coverage.
- [x] Missing tools get install suggestions.
- [x] Report validator catches missing scores and confidence.
- [x] Report validator catches malformed evidence refs.
- [x] Report validator parses valid YAML frontmatter without a homemade parser.
- [x] Compare helper separates score deltas from confidence deltas.
- [x] Compare helper rejects incompatible scope or rubric versions.
- [x] `uv run pytest` succeeds.
- [x] `uv run ruff check .` succeeds.
- [x] `uv run ruff format --check .` succeeds.

### Task 8: Phase 7 - build outputs and runtime overlays

Files:

- `scripts/build/compile.py`
- `src/plugins/architecture/plugin.yaml`
- target frontmatter overlays
- `dist/claude/`
- `dist/codex/`
- `dist/pi/`

Tasks:

- [x] Reuse the `cc-thingz` source-to-dist pattern. (Pattern inferred; external
      repo not fetchable here — noted in compile.py to reconcile when accessible.)
- [x] Compile agents and skills from one source tree.
- [x] Support target overlays.
- [x] Generate Pi output.
- [x] Generate Claude output.
- [x] Generate Codex output.
- [x] Keep generated files reproducible. (Deterministic emit; `--check` drift gate.)
- [x] Add Codex structured-question overlay only after verifying the concrete
      runtime behavior. (Deferred — Codex runtime not verifiable in this
      environment; overlay preserves `structured_questions: unverified` and the
      compiler asserts no concrete tool name leaks into Codex output.)

Verification:

- [x] Build regenerates `dist/` from `src/`.
- [x] Drift check catches hand-edited generated files.
- [x] Manifests reference architect agent and skills.
- [x] Pi discovers skills. (Pi target emits a `skills/` tree + manifest; full Pi
      discovery wiring is Task 9.)
- [x] Claude output has valid frontmatter. (Parseable YAML; flat read-only
      `tools` allow-list, no Edit/Write.)
- [x] Codex output avoids unverified structured-input tool names.

### Task 9: Phase 8 - Pi package

Files:

- Pi package manifest or conventional package directories

Tasks:

- [x] Contribute skill paths through package metadata or conventional dirs.
      (dist/pi/plugin.yaml manifest enumerates every skill path.)
- [x] Contribute agent files where Pi can load them. (manifest `agents:` →
      agents/architect.md.)
- [x] Require `alexei-led/cc-thingz` for `ask_user_question` support.
      (target-aware `requires` in plugin metadata; Pi manifest emits it.)
- [x] Do not implement a local Pi question extension. (capability maps to the
      cc-thingz tool; no local extension shipped — noted in plugin.yaml.)
- [x] Document how agents run Python helpers through uv. (README Pi package
      section with `uv run architect-*` examples.)

Verification:

- [x] Package installs from local path. (`uv build` produces wheel + sdist.)
- [x] Pi discovers skills. (manifest enumerates all skills; contract verified by
      test — live Pi discovery not exercisable in this environment.)
- [x] `ask_user_question` is available when `cc-thingz` is installed. (manifest
      `requires` names cc-thingz; Pi agent capability maps to ask_user_question
      — contract verified by test, not a live Pi run.)
- [x] Helper commands work through `uv run`. (`uv run architect-doctor --help`
      runs via registered entry points.)

### Task 10: Phase 9 - docs

Files:

- `README.md`
- `docs/install.md`
- `docs/tools.md`
- `docs/report-format.md`
- `docs/scoring.md`
- `docs/methodology.md`

Tasks:

- [x] Document Claude install/update.
- [x] Document Codex install/update.
- [x] Document Pi install/update.
- [x] Document required and recommended OSS CLI tools.
- [x] Document tool coverage states and confidence impact.
- [x] Document score dimensions.
- [x] Document report format.
- [x] Document plan format.
- [x] Attribute Vlad and Balanced Coupling.

Verification:

- [x] Install docs match package layout.
- [x] Tool docs match doctor output.
- [x] Scoring docs match scorecard skill.
- [x] Methodology docs match Balanced Coupling skill.

### Task 11: Phase 10 - evals and fixtures

Files:

- `tests/fixtures/repos/ts-healthy/`
- `tests/fixtures/repos/ts-tangled/`
- `tests/fixtures/repos/python-boundaries/`
- `tests/fixtures/repos/go-deps/`
- `tests/fixtures/repos/infra-mixed/`
- `tests/skill-evals/architecture-review/`

Tasks:

- [x] Create healthy and unhealthy fixtures. (paired ts-healthy/ts-tangled plus
      python-boundaries, go-deps, infra-mixed)
- [x] Include git history for change locality where practical. (omitted by
      design — nested .git conflicts with parent repo; recorded as a coverage gap
      in each FIXTURE.md and the goldens)
- [x] Include operational manifests. (infra-mixed: helm, k8s, terraform, docker,
      GitHub Actions)
- [x] Eval interview-before-score behavior. (EV6 interview_before_score)
- [x] Eval structured-question behavior for Claude, Pi, and Codex overlays.
      (EV13 structured_question_capability)
- [x] Eval tool-before-claim behavior. (EV7 tool_before_claim)
- [x] Eval tool coverage reporting. (EV3 has_tool_coverage)
- [x] Eval evidence citation. (EV8 evidence_cited)
- [x] Eval plan quality. (EV10 plan_well_formed, EV11 plan_no_rewrite)
- [x] Eval non-comparable report handling. (EV12 noncomparable_explained)

Verification:

- [x] Evals pass baseline. (16 eval cases pass)
- [x] Reports contain frontmatter scores. (EV1/EV2 validates_contract)
- [x] Reports contain tool coverage. (EV3)
- [x] Re-runs produce stable score bands. (EV9 stable_score_bands — bands
      derived deterministically from values; static goldens)
- [x] Bad fixtures score worse for the right reasons. (EV4 scores_discriminate +
      EV5 findings_target_dimensions)

### Task 12: Phase 11 - second dogfood pass and release hardening

Targets:

- `/Users/alexei/Workspace/ccgram`
- `cc-thingz`
- `modularity`
- one large mixed repo

Tasks:

- [x] Run review manually with real tools. (gitnexus reindex + Cypher import-cycle
      query + git/rg/wc on ccgram; report-2.md)
- [x] Run helper validation. (architect-doctor --repo, validate-report on both
      passes — both valid after FR8 fix)
- [x] Compare against the first ccgram dogfood report. (compare-reports 1→2:
      COMPARABLE; boundary +6, dependency +8 conf low→medium, coupling -2)
- [x] Record tool friction. (docs/dogfood/ccgram/friction-2.md, FR8-FR11)
- [x] Review false positives. (validator "violations" were a real schema defect not
      FP — fixed; 8 cycles triaged as benign intra-package/bootstrap, none
      domain-crossing; god modules confirmed unchanged, not re-discovered)
- [x] Tune prompts and rubrics. (friction-driven only: report template now shows
      command + graph-query evidence examples and the type→field rule — FR8)
- [x] Produce one plan from a real report. (docs/dogfood/ccgram/plan-2.md from
      report-2)
- [x] Share findings with Vlad before release if Balanced Coupling material goes
      beyond light attribution and summary. (skipped - external coordination; v1
      material is summary-only so the trigger does not fire — see release notes;
      tracked in Post-Completion)

Verification:

- [x] Report helps a human architect understand the system. (report-2: exec summary,
      system map, score map with per-dimension deltas vs pass 1)
- [x] Recommendations cite evidence. (every finding F1/F2/F3/F5/F6 carries
      evidence_refs)
- [x] Scores are explainable. (score map table with justification + Δ-vs-pass-1)
- [x] Unsupported claims are removed. (dependency now graph-backed; F4 resolved;
      cycles characterized as benign rather than overstated)
- [x] Repeat report explains improvement, degradation, or non-comparability.
      (compare-reports labels each dimension improved/degraded/unchanged; COMPARABLE)
- [x] Release notes describe known limitations. (docs/release-v0.1.md)

### Task 13: Verify acceptance criteria

- [ ] Verify the architect agent exists for Claude, Codex, and Pi.
- [ ] Verify the review flow produces interview context, system map, architecture report, and refactoring plan artifacts.
- [ ] Verify review skills enforce interview, system mapping, scorecard use, evidence citation, and tool coverage reporting.
- [ ] Verify methodology, tool, helper, build, package, documentation, eval, and dogfood deliverables match the Acceptance Criteria section.
- [ ] Run `uv sync`.
- [ ] Run `uv run pytest`.
- [ ] Run `uv run ruff check .`.
- [ ] Run `uv run ruff format --check .`.

## Post-Completion

Items requiring external coordination or manual approval:

- Share findings with Vlad before release if Balanced Coupling material goes beyond light attribution and summary.
- Run final dogfood on target repositories outside this planning repo.
- Publish release notes with known limitations after validation passes.
