---
name: architecture-plan
description: >-
  Turn architecture-report findings into an incremental refactoring plan. Use
  when asked to plan a refactor, sequence remediation, or act on a report's
  findings. Produces a phased, verifiable plan that cites finding and evidence
  IDs. NOT for applying changes (hand off to a mutator agent) or for scoring
  (use architecture-scorecard).
---

# Architecture plan

Derive an actionable, incremental refactoring plan from a report. The architect
drafts the plan; it never executes it.

## When to use

Use after an architecture review, when the user wants the report's findings
turned into a sequence of changes. Plan one hotspot, boundary, or flow per plan
unless a roadmap is explicitly requested.

## Procedure

1. **Anchor to the report.** Cite the source report ID and the finding/evidence
   IDs each phase addresses. A phase with no finding behind it does not belong in
   the plan.

2. **Use the plan template.** `../../templates/plan.md` is the skeleton: Overview,
   Success criteria, Phases (each with justification, preconditions,
   postconditions, tasks, verification), Acceptance criteria, Safety notes.

3. **Order for safety.** Prefer characterization tests, seam creation, boundary
   repair, and fitness checks before cosmetic cleanup. Establish a safety net
   before changing behavior-bearing code.

4. **Keep it incremental.** No big-bang rewrites. Each phase is small and
   independently verifiable. Keep the next execution horizon to five phases or
   fewer before a re-review.

5. **Make every task verifiable.** Each phase ends with a concrete check — a
   test, a fitness check, or a command — that proves it is done. Success and
   acceptance criteria tie back to findings or score dimensions.

6. **Write safety notes.** Flag irreversible steps, data migrations, and
   wide-blast-radius changes. State plainly that the architect does not apply the
   plan; an engineer or mutator agent executes it after approval.

## Hard rules

- Every phase cites a finding or evidence ref.
- Incremental only — no rewrites the evidence does not justify.
- The architect produces the plan and stops. Execution is someone else's job.
