---
name: tools-archfit
description: >-
  Gather deterministic architecture-fitness evidence with archfit: full checks,
  scorecards, deltas, SARIF/JSON findings, tool coverage, and agent_tasks. Use
  when a repo has .archfit.yaml or the user wants architect to combine its review
  with archfit. Produces hard facts for architecture-review to calibrate, not a
  replacement for independent design judgment. NOT for running archfit LLM review
  as source-of-truth, changing archfit config, baselining findings, or applying
  fixes.
---

# archfit deterministic evidence

Use archfit as a deterministic measurement and gate engine. It supplies whole-repo
facts; the architect still judges intent, domain volatility, runtime/deploy
context, false positives, and missing risks.

## When to use

Use when a target repo contains `.archfit.yaml` or `archfit.yaml`, when `archfit`
is available on `PATH`, or when the user asks to combine architect review with
archfit output. Use it during `architecture-review` before final triage/scoring
so hard facts can reduce sampling bias.

Do not use this skill for:

- `archfit review` LLM narration as primary evidence;
- `archfit init`, `update --apply`, `baseline`, `enrich --pin`, or config writes
  unless the user explicitly asks for config work;
- applying fixes from `agent_tasks`;
- replacing the architect's independent evidence gathering and Balanced Coupling
  judgment.

## Skill navigation

- Missing or absent config: return to `architecture-review`; record archfit as
  missing or skipped. Optional archfit absence is a coverage gap, not a blocker.
- Current skill: run deterministic archfit commands, summarize facts, and build
  a calibration matrix.
- Next skill: return to `architecture-review` for independent verification,
  scoring, and report writing; use `methodology-architecture-fitness` for checks
  that should become enforced gates.

## Read-only discipline

Prefer existing config only. Write command outputs to a temp directory outside the
target repo. Do not create baselines, labels, generated reports, or config patches
inside the repo without explicit user approval.

If archfit or a child tool writes caches or indexes under the target repo, record
that path as generated tool state. If the output path is inside the scanned root,
warn that reports can contaminate measurements and move future outputs outside
the repo or exclude them.

## Deterministic command set

Use the local binary if present; otherwise use `archfit` from `PATH`.

```sh
ARCHFIT=archfit
if [ -x ./archfit ]; then ARCHFIT=./archfit; fi
if [ -x ./.bin/archfit ]; then ARCHFIT=./.bin/archfit; fi
```

Run only commands that fit the repo and time budget. Treat exit code `1` as gate
findings and `2` as warnings; they are evidence, not command failures. Exit code
`3` or invalid JSON is a tool failure.

```sh
# Tool/config health.
$ARCHFIT doctor

# Full deterministic facts and score synthesis.
$ARCHFIT check --config .archfit.yaml --full --advisory --report --format json
$ARCHFIT check --config .archfit.yaml --full --advisory --report --format scorecard

# Human-readable deterministic audit, when useful.
$ARCHFIT scan --config .archfit.yaml

# Delta facts, only when a meaningful base ref is known.
$ARCHFIT check --config .archfit.yaml --base <base-ref> --advisory --report --format json

# Optional CI annotation artifact.
$ARCHFIT check --config .archfit.yaml --full --format sarif
```

Do not run `archfit review` unless the user specifically wants archfit's LLM
narrative. If you do, label it `advisory_llm`, capture parse/runtime failures,
and never cite it as deterministic evidence.

## Extract these facts

From JSON/scorecard/scan output, extract and summarize:

- `tool_coverage`: missing, failed, skipped, and stale tools; confidence impact.
- `summary` and metric/dimension scores, including confidence and evidence refs.
- `findings`: IDs, severity, status (`new`, `baseline`, `fixed`, `excepted`),
  rule/metric, files, modules, and whether each is gate or advisory.
- `agent_tasks`: machine-readable repair tasks and validation commands.
- dependency facts: cycles, hubs, instability, propagation/blast-radius signals.
- coupling facts: classified edges, strength labels, distance, volatility labels,
  unbalanced-edge advisories, and missing/unclassified edge coverage.
- config quality signals: generated or under-specified modules, missing owner,
  deploy unit, subdomain, volatility, public/private boundary, or weak warn-only
  rules.
- delta facts: new, existing/baseline, resolved, severity-changed, and
  touched-by-delta findings where available.
- artifact/cache noise: `.archfit-cache`, `.codegraph`, `.gitnexus`, generated
  reports, package caches, vendored external caches, or output under the target
  root.

Absence of findings is evidence only when the relevant tool coverage is present
and current. A green score on missing/thin evidence is a calibration concern, not
proof of architectural health.

## Architect calibration matrix

Return this matrix to `architecture-review` whenever archfit output was used:

```yaml
archfit_calibration:
  source_commands: []
  artifacts: []
  confirmed: []
  severity_adjusted: []
  false_positive_or_noise: []
  missed_by_archfit: []
  config_changes: []
  new_fitness_checks: []
  labels_to_confirm: []
  confidence_impact: none # none | low | medium | high
```

Classify with independent evidence:

- `confirmed`: architect verified the same issue in code, graph, runtime, deploy,
  or CI evidence.
- `severity_adjusted`: archfit fact is real, but composition-root role,
  ownership/deploy distance, lazy-import policy, generated code, or low domain
  volatility changes severity.
- `false_positive_or_noise`: cache/generated artifact, output contamination,
  tool limitation, or configured role makes the finding not architecture risk.
- `missed_by_archfit`: meaning-level risk not in deterministic facts, such as
  functional coupling without import edges, duplicated business rules, prompt/tool
  contract drift, deploy selector drift, slow/flaky architecture-adjacent tests,
  or supply-chain/runtime topology risk.
- `config_changes`: `.archfit.yaml` improvements that would make deterministic
  facts more honest, especially module ownership, deploy units, public/private
  boundaries, subdomain, volatility, and stronger gates.
- `new_fitness_checks`: executable checks to add after design/repair.
- `labels_to_confirm`: architect-inferred subdomain/volatility/strength labels
  that a human should approve before deterministic gating uses them.

## Balanced Coupling handling

archfit can enumerate candidate relationships and classify many edges, but it
cannot own the business truth. For every important coupling claim, still apply
`methodology-balanced-coupling`:

- classify strength from evidence;
- split distance into code, ownership, runtime, and deploy distance;
- prefer domain volatility from human/docs/domain role, using churn as support;
- treat generic/supporting code with provider-switch or SDK churn as possible
  implementation volatility;
- choose a balancing move: lower strength, lower distance, or accept due to low
  volatility.

Do not pass through archfit's `coupling_balance` score as the architect score.
Use it as evidence input, then score from relationship records and coverage.

Apply coverage-gap calibration consistently so the magnitude is reproducible,
not just the direction:

- When edge classification is absent (`scip absent` / "no classified
  cross-boundary edges"), set `coupling_balance` confidence `low` and cap the
  band at `mixed` (≤ 60, default ~50) unless you classify the edges yourself with
  codegraph, `go list`, or dependency-cruiser.
- When GitNexus covered only part of the changed files, apply the same cap to
  `change_locality`.
- A clean archfit dimension with `confidence: medium` and an `n/a` sub-metric is
  a coverage gap, not a strong result.

## Output

Return a concise evidence summary:

- commands run and artifacts produced;
- exit statuses interpreted as findings/warnings/failures;
- tool coverage and confidence impact;
- top deterministic findings and agent tasks by severity/risk;
- scorecard/delta highlights;
- calibration matrix;
- smallest follow-up checks needed to verify hypotheses.

## Hard rules

- Deterministic archfit facts can seed review; they do not replace independent
  verification or user/domain context.
- No high-quality architecture claim from missing or unclassified evidence.
- No source or config writes without explicit approval.
- No treating `archfit review` LLM narration as source-of-truth.
- No counting an archfit pass as proof of correctness, security, performance, or
  all architecture quality; it only says configured checks and measured metrics
  passed under the observed coverage.
