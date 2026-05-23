---
name: architecture-plan
description: >-
  Turn architecture-report findings or approved architecture-design artifacts
  into an incremental implementation/refactoring plan. Use when asked to plan a
  refactor, sequence remediation, implement a target architecture, or act on a
  report's findings. Produces a phased, verifiable plan that cites source
  findings, evidence, design decisions, contracts, or risks. NOT for applying
  changes (hand off to a mutator agent) or for scoring (use
  architecture-scorecard).
---

# Architecture plan

Derive an actionable, incremental implementation/refactoring plan from a report
or approved design. The architect drafts the plan; it never executes it.

## When to use

Use after an architecture review, when the user wants the report's findings
turned into a sequence of changes. Use after an architecture design, when the
user wants approved target architecture implemented. Plan one hotspot, boundary,
module, or flow per plan unless a roadmap is explicitly requested.

If there is no review report and no approved design artifact, run
`architecture-review` for existing-code remediation or `architecture-design` for
requirements-to-design work first.

## Skill navigation

- Missing findings for an existing system: run `architecture-review` first.
- Missing target architecture for new work: run `architecture-design` first.
- Current skill: use `architecture-plan` to sequence small, verifiable changes
  from a report or approved design.
- Next skill after implementation: run `architecture-review` to verify the code
  now matches intended architecture and the plan's acceptance criteria.

## Task list discipline

Maintain a visible task list for the planning flow. Track at least:

1. Source report or design artifact confirmed.
2. Scope and first execution horizon selected.
3. Safety net ordered before behavior-bearing changes.
4. Phases drafted.
5. Verification and acceptance criteria attached.
6. Handoff and re-review step recorded.

Keep task names outcome-based. Do not expose runtime-specific mechanics in the
plan.

## Procedure

1. **Anchor to the source artifact.** Cite the source report ID plus
   finding/evidence IDs, or the approved design artifact plus decision, contract,
   risk, or module IDs each phase addresses. A phase with no source rationale
   does not belong in the plan.

2. **Use the plan template.** `../../templates/plan.md` is the skeleton: Overview,
   Source artifact, Success criteria, Phases (each with justification,
   preconditions, postconditions, tasks, verification), Acceptance criteria,
   Safety notes, Re-review.

3. **Order for safety.** Prefer characterization tests, seam creation, boundary
   repair, and fitness checks before cosmetic cleanup. Establish a safety net
   before changing behavior-bearing code.

4. **Keep it incremental.** No big-bang rewrites. Each phase is small and
   independently verifiable. Keep the next execution horizon to five phases or
   fewer before a re-review.

5. **Make every task verifiable.** Each phase ends with a concrete check — a
   test, a fitness check, or a command — that proves it is done. Success and
   acceptance criteria tie back to findings, score dimensions, design decisions,
   integration contracts, or module responsibilities.

6. **Write safety notes.** Flag irreversible steps, data migrations, and
   wide-blast-radius changes. State plainly that the architect does not apply the
   plan; an engineer or mutator agent executes it after approval.

## Failure handling

- Missing source report/design, unreadable artifact, or absent finding/evidence/
  decision/contract refs: stop and ask for the missing source. Do not invent
  refs.
- Missing `../../templates/plan.md`: report the missing template and ask before
  using an inline fallback.
- Requested rewrite with no cited finding, design decision, or risk behind it:
  decline that phase and name the missing rationale.

## Output

Return a plan shaped like `../../templates/plan.md` with:

- `source_artifact`: report/design path or ID plus finding, evidence, decision,
  contract, risk, or module IDs used.
- `success_criteria`: measurable outcomes tied to findings, score dimensions,
  design decisions, contracts, or module responsibilities.
- `phases`: at most five next phases, each with justification, preconditions,
  tasks, postconditions, and verification.
- `acceptance_criteria`: checks that prove the plan is complete.
- `safety_notes`: blast radius, irreversible steps, rollback notes, and the
  mutator/engineer handoff.

## Hard rules

- Every phase cites a source finding, evidence ref, design decision, contract,
  risk, or module responsibility.
- Incremental only — no rewrites the source artifact does not justify.
- The plan must end with a re-review recommendation.
- The architect produces the plan and stops. Execution is someone else's job.
