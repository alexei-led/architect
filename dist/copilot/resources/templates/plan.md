# Plan: REPLACE-target

Plain Markdown. Useful to humans, coding agents, and task runners. One hotspot,
boundary, module, or flow per plan unless a roadmap is requested. Keep the next
execution horizon to five tasks or fewer before re-review.

When the user confirms a file destination, place generated plans in `docs/plans/`
unless the project configured another plans directory. If this file is stored
elsewhere, run the task runner with this exact path or copy/symlink it into the
configured plans directory.

Task runners execute `### Task N:` or `### Iteration N:` sections. Use checkboxes
only inside those task/iteration sections. Use plain bullets or prose for
context, success criteria, validation commands, file lists, manual checks, and
acceptance criteria.

## Overview

REPLACE: the problem this plan addresses.

## Source artifact

REPLACE: source report/design path or ID. Cite finding IDs, evidence refs, design
decision IDs, contract IDs, risk IDs, or module names used by this plan.

## Success criteria

REPLACE: observable outcomes that mean the plan worked. Tie each to a finding,
score dimension, design decision, contract, module responsibility, or risk.

- REPLACE measurable outcome, e.g. cycle between modules A and B removed.
- REPLACE measurable outcome.

## Validation Commands

- `REPLACE whole-plan command, e.g. make check`
- `REPLACE focused architecture-fitness, test, or lint command`
- `REPLACE if configured: archfit analyze --gate --config .archfit.yaml --base <ref>`

## Implementation Steps

### Task 1: REPLACE safety net

Justification: REPLACE finding/evidence/design/contract/risk ref that motivates
this task.

Files:

- `REPLACE/path.ext` — REPLACE planned change.
- `REPLACE/test_path.ext` — REPLACE safety net.

Preconditions: REPLACE.
Postconditions: REPLACE.

Fitness gate: REPLACE existing gate status, rule/config change, and
before-fail/after-pass expectation, or `None`.

Impact commands:

If GitNexus is unavailable, replace these with fallback commands and note that gap.

- `gitnexus impact REPLACE/path-or-symbol`
- `gitnexus detect-changes`

Verification commands:

- `REPLACE concrete command, e.g. uv run pytest tests/test_boundary.py`
- `REPLACE if configured: archfit analyze --gate --config .archfit.yaml --base <ref>`

Manual checks:

- REPLACE human judgment check, or `None`.

- [ ] REPLACE implement the smallest independently committable safety-net change;
      cite source rationale.
- [ ] REPLACE add or update the characterization test, architecture-fitness
      check, or focused test that protects this change.
- [ ] REPLACE run the verification commands above and record the result.

### Task 2: REPLACE boundary repair

Justification: REPLACE finding/evidence/design/contract/risk ref that motivates
this task.

Files:

- `REPLACE/path.ext` — REPLACE planned change.
- `REPLACE/test_path.ext` — REPLACE focused coverage or fitness check.

Preconditions: REPLACE.
Postconditions: REPLACE.

Fitness gate: REPLACE existing gate status, rule/config change, and
before-fail/after-pass expectation, or `None`.

Impact commands:

If GitNexus is unavailable, replace these with fallback commands and note that gap.

- `gitnexus impact REPLACE/path-or-symbol`
- `gitnexus detect-changes`

Verification commands:

- `REPLACE concrete command, e.g. uv run pytest tests/test_boundary.py`
- `REPLACE if configured: archfit analyze --gate --config .archfit.yaml --base <ref>`

Manual checks:

- REPLACE human judgment check, or `None`.

- [ ] REPLACE implement the smallest independently committable boundary change;
      cite source rationale.
- [ ] REPLACE update the focused verification check for the changed boundary.
- [ ] REPLACE run the verification commands above and record the result.

### Task 3: Final verification and documentation

Justification: REPLACE source refs and acceptance criteria this final task proves.

Files:

- `REPLACE docs/plans/plan-name.md` — REPLACE plan/progress evidence.
- `REPLACE documentation path or "No docs change expected"` — REPLACE docs check.

Preconditions: all prior task verification commands passed.
Postconditions: whole-plan checks pass; docs and re-review scope are clear.

Fitness gate: REPLACE final whole-plan gate status, or `None`.

Impact commands:

If GitNexus is unavailable, replace this with a fallback command and note that gap.

- `gitnexus detect-changes`

Verification commands:

- `REPLACE whole-plan command from Validation Commands, e.g. make check`
- `REPLACE focused architecture-fitness or review-prep command`

Manual checks:

- REPLACE docs/handoff check, or `None`.

- [ ] Run the whole-plan validation commands and record the result.
- [ ] Update or explicitly rule out docs changes.
- [ ] Record the scoped `architecture-review` follow-up: target, acceptance
      signals, and source refs to re-check.

## Acceptance criteria

REPLACE: conditions for the whole plan to be accepted. Prefer characterization
tests, seam creation, boundary repair, and fitness checks before cosmetic
cleanup.

- REPLACE acceptance condition tied to a source finding, decision, contract, or
  risk.
- REPLACE acceptance condition tied to validation command output.
- REPLACE final docs/re-review handoff is recorded.

## Safety notes

REPLACE when risk is high; otherwise state "No elevated risk." Note irreversible
steps, data migrations, or wide-blast-radius changes. The architect does not
apply these changes; an engineer, mutator agent, or task runner executes the
approved plan.

## Re-review

REPLACE: recommend `architecture-review` after implementation, with the scope and
acceptance signals to check.
