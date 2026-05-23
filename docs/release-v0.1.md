# architect v0.1.0 — release notes

Instruction-first architecture-review extension for Claude Code, Codex CLI, and Pi.
An architect agent plus focused skills, report/plan templates, and small Python
helper tools produce evidence-backed architecture reviews. Agents drive local OSS
CLIs directly; the package wraps none of them.

## What it does

- One plain architect role prompt in `src/agents/architect/AGENT.md`, composed
  with runtime tool envelopes and the architecture skills. Runtime wrappers for
  Claude, Codex, or Pi are install-time adapter config, not generated source.
- Review flow produces four artifacts: interview context, system map, scored
  architecture report (Markdown + YAML frontmatter), and an incremental refactoring
  plan.
- Scoring is evidence-gated: dimensions, 0–100 bands, confidence levels, and a rule
  that low confidence cannot be presented as high quality.
- Helper tools (`architect-doctor`, `architect-validate-report`,
  `architect-compare-reports`) check tooling, validate the report contract, and
  compare reports with explicit comparability rules.

## Supported review targets

Validated with instruction lint, prompt-level skill eval definitions, helper
smoke tests, and two dogfood passes against `ccgram` (see
`docs/dogfood/ccgram/`). Languages with first-class tool skills: TypeScript,
Python, Go, plus operational/infra manifests. PHP, Ruby, Java/JVM, and COBOL
have no dedicated tool skill in v1.

## Known limitations

- **OSS CLIs are not bundled.** The extension calls tools that must already be on
  PATH (ast-grep, gitnexus, codegraph, pyright, import-linter, dependency-cruiser,
  govulncheck, helm/terraform, etc.). `architect-doctor` reports which are present,
  applicable, missing, or failing. A dimension with no working tool is recorded as a
  coverage gap with a confidence penalty — never silently scored.
- **doctor checks the running environment, not the target's declared tooling.** A
  tool a target repo declares in its own config (e.g. `deptry` in ccgram's
  `pyproject.toml`) still shows MISSING if it is not installed where the agent runs.
  This is correct for "can I run it now" but should not be read as "the project lacks
  tooling".
- **No live interview in autonomous/CI runs.** With no interactive user the architect
  reconstructs intent from docs (CLAUDE.md, ADRs, design notes) and labels it
  reconstructed, capping confidence. A live interview yields higher confidence.
- **Structured-question tools are runtime-dependent.** Use `AskUserQuestion`,
  `ask_user_question`, or any similar tool when the active runtime exposes it.
  Without one, the review skill asks one plain question and records lower
  confidence when parsing is ambiguous.
- **Report contract is strict.** Evidence entries require a type-dependent field
  (`file→ref`, `command→command`, `graph-query→query`); `architect-validate-report`
  fails on the wrong field. The report template shows all shapes.
- **Persistent indexes can be stale.** gitnexus/codegraph indexes must be checked for
  freshness before their output is trusted; a stale index is recorded as a coverage
  gap, not a reading.
- **Helpers locate the default scorecard relative to the source tree.** The
  packaged default `scorecard.yaml` resolves when the helpers run from an
  editable/source checkout (`uv run …`, the documented path). A non-editable
  wheel install does not bundle `templates/`, so pass `--scorecard <path>`
  explicitly in that case.
- **Dogfood passes are autonomous, not a substitute for human review.** The two
  ccgram passes demonstrate the loop and the helper tools end-to-end; they do not
  replace an architect's judgment on a production system.

## Attribution and licensing

The Balanced Coupling methodology skill summarizes, in our own words and with
attribution, concepts from Vlad Khononov's work on coupling (integration strength,
distance, volatility, and the balance rule). The source material is licensed
CC BY-NC-SA; to avoid ShareAlike tainting this MIT-licensed repo, the skill is
**summary-only** — no adapted or quoted reuse ships in v1. Any reuse beyond light
attribution and summary requires Vlad's explicit permission and must be coordinated
before release. See `docs/methodology.md` and
`src/skills/methodology-balanced-coupling/`.

## Dogfood evidence

`docs/dogfood/ccgram/` contains both passes:

- pass 1: `report.md`, `plan.md`, `friction.md` (FR1–FR7)
- pass 2: `report-2.md`, `plan-2.md`, `friction-2.md` (FR8–FR11)

Pass 2 closed the pass-1 dependency-evidence gap (gitnexus reindex + import-cycle
query), advanced the read-layer migration finding (30 → 10 direct refs), resolved F4,
and surfaced F6 (8 intra-package import cycles). `architect-compare-reports` reports
the change as COMPARABLE with per-dimension score and confidence deltas.
