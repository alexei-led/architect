---
name: tools-archfit
description: >-
  Gather deterministic architecture-policy evidence with archfit 0.9: the check
  status for a change, rule and module facts, dependency answers, and the
  repository report. Use when a repo has .archfit.yaml or the user wants
  architect to combine its review with archfit. Produces hard facts for
  architecture-review to calibrate, not a replacement for independent design
  judgment. NOT for changing the policy, writing exceptions, running doctor --fix,
  or applying fixes.
---

# archfit deterministic evidence

Use archfit as a deterministic policy check. It judges a change against the
repository's `.archfit.yaml` (`version: 1`) and reports the facts; the architect
still judges intent, domain volatility, runtime/deploy context, false positives,
and missing risks.

Install: `brew install coupling-dev/tap/archfit`, `go install
github.com/coupling-dev/archfit/cmd/archfit@v0.9.0`, or the image
`ghcr.io/coupling-dev/archfit`. Source: <https://github.com/coupling-dev/archfit>.

## When to use

Use when a target repo contains `.archfit.yaml`, when `archfit` is available on
`PATH`, or when the user asks to combine architect review with archfit output.
Use it during `architecture-review` before final triage/scoring so hard facts
can reduce sampling bias.

Do not use this skill for:

- `archfit init`, `archfit doctor --fix`, `archfit request`, or any write to
  `.archfit.yaml`, hooks, or exceptions unless the user explicitly asks;
- applying fixes for check errors;
- replacing the architect's independent evidence gathering and Balanced Coupling
  judgment.

## Skill navigation

- Missing or absent policy: return to `architecture-review`; record archfit as
  missing or skipped. Optional archfit absence is a coverage gap, not a blocker.
- Current skill: run deterministic archfit commands, summarize facts, and build
  a calibration matrix.
- Next skill: return to `architecture-review` for independent verification,
  scoring, and report writing; use `methodology-architecture-fitness` for checks
  that should become enforced gates.

## Read-only discipline

Use the existing policy only. Archfit keeps its cache in `.archfit-cache/` of the
target repo (generated tool state; record it, never commit it). Write command
outputs to a temp directory outside the target repo. Do not create or change a
policy, exception, hook, or request without explicit user approval.

## Deterministic command set

Use the local binary if present; otherwise use `archfit` from `PATH`.

```sh
ARCHFIT=archfit
if [ -x ./archfit ]; then ARCHFIT=./archfit; fi
if [ -x ./.bin/archfit ]; then ARCHFIT=./.bin/archfit; fi
```

`check` exits `0` pass, `1` fail, `2` unknown (no verdict), wrong usage, or a tool
error. Treat `1` and `unknown` as evidence, not command failures; `unknown` is not
a pass. `can` exits `0` yes, `1` no, `2` unknown. `rules` and `report` exit `0`
whatever they show.

```sh
# Tool and hook health (read-only without --fix).
$ARCHFIT doctor

# The rules for the files the change touches, one module, or one rule.
$ARCHFIT rules
$ARCHFIT rules <path-or-rule> ...

# The modules by layer and their allowed dependencies.
$ARCHFIT rules --graph

# May <from> depend on <to>? (module, file, directory, import path, or library)
$ARCHFIT can <from> <to>

# Status of the change against its merge base with the target branch.
$ARCHFIT check --format json
$ARCHFIT check --base <base-ref> --format json

# Optional CI annotation artifact (SARIF to stdout).
$ARCHFIT check --format sarif

# Repository-wide state: clean, drift, or expired; unread places; expiring
# exceptions; unchecked rules; balance of each allowed dependency.
$ARCHFIT report --format json
```

`check` compares the change with the target branch's policy; a local policy that
differs from it gives `unknown`. `--policy <file>` previews a candidate policy
without that comparison. Never run `archfit request` for evidence gathering: it
posts a comment or opens an issue.

## Extract these facts

From the JSON (`archfit.result.v1`, `archfit.architecture-state.v2`) or text,
extract and summarize:

- `status` (`pass`, `fail`, `waiting`, `unknown`), `summary`, `base`, `head`,
  `engine`, `date`, and the `policy` block (`protected`, `differs`, `target`).
  `protected: false` means the result is a local guide, not change control.
- `errors[]`: `rule`, `path`, `line`, `what`, `why`, `instead`, `from`/`to`
  modules, `next.kind` (`fix`, `command`, `wait`, `restore`), and `from_change`.
- `unknown[]`: cause (`policy`, `base`, `tool`, `import`) and the restore step.
  Each is a coverage gap; the status is not a pass.
- `balance` on coupling errors: `value`, `min`, `strength` (`contract`, `model`,
  `intrusive`), and the target's declared `volatility`; `surface` and `package`
  for a use past the target's public or model part.
- the `repository` object (push runs, and `report`): `state`, `drift[]`,
  `expiring[]`, `unread[]`.
- exceptions: covered rules, `expires` dates, and expired ones.
- doctor tool rows: missing or invalid tools (`ast-grep`, `cargo`, `dotnet`)
  mean unread code and lower confidence.

Absence of errors is evidence only when the relevant code was read (`unknown[]`
and `unread[]` empty). A `pass` on missing or thin evidence is a calibration
concern, not proof of architectural health.

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
- `config_changes`: `.archfit.yaml` policy changes that would make deterministic
  facts more honest, especially module boundaries, public/model surfaces,
  volatility, allowed dependencies, and missing rules. Propose them for an owner
  (`archfit request`); never edit the policy yourself.
- `new_fitness_checks`: executable checks to add after design/repair.
- `labels_to_confirm`: architect-inferred volatility or surface declarations
  (`volatility`, `public`, `model`) that an owner should approve before the
  policy uses them. Archfit reads volatility only from the policy.

## Balanced Coupling handling

Archfit declares no coupling score. It enforces the policy's rules and, for
coupling rules, a balance of strength against the target's declared volatility.
It cannot own the business truth behind those inputs. For every important
coupling claim, apply `methodology-balanced-coupling` and confirm:

- strength: archfit reports `contract`, `model`, or `intrusive` from the target's
  declared surface. Confirm functional or symmetric coupling by reading the
  crossing code; archfit does not see it.
- distance and runtime/deploy topology: fold these in yourself; archfit's module
  graph is code structure.
- volatility: the policy declares it. Confirm each declaration against the
  business domain; an undeclared or wrong value is a config gap to flag, not a
  finding.
- balancing move: use `instead` and `next` as hypotheses and confirm them
  against the relationship record.

Do not pass through archfit's `balance` values or status as the architect score.
Use the errors, the balance inputs, and the coverage fields as evidence, then
score from relationship records and coverage.

Apply coverage-gap calibration consistently:

- `unknown` status, non-empty `unknown[]` or `unread[]`, or missing tools: set
  confidence `low` for the affected dimension and cap the band at `mixed` unless
  you classify the edges yourself with codegraph, `go list`, or
  dependency-cruiser.
- `policy.protected: false` or `policy.differs: true`: the result does not show
  change control; say so.
- When GitNexus covered only part of the changed files, apply the same cap to
  `change_locality`.

## Output

Return a concise evidence summary:

- commands run and artifacts produced;
- exit statuses interpreted as findings/unknowns/failures;
- coverage (`unknown[]`, `unread[]`, doctor tools) and confidence impact;
- top errors and repository drift by severity/risk;
- check and report highlights;
- calibration matrix;
- smallest follow-up checks needed to verify hypotheses.

## Hard rules

- Deterministic archfit facts can seed review; they do not replace independent
  verification or user/domain context.
- No high-quality architecture claim from missing or unread evidence.
- No source, policy, or exception writes without explicit approval.
- No counting an archfit pass as proof of correctness, security, performance, or
  all architecture quality; it only says the policy's rules passed under the
  observed coverage.
