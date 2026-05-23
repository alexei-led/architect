---
name: architecture-plan
description: >-
  Turn approved architecture-design artifacts, with supporting review findings
  when present, into an incremental implementation/refactoring plan. Use when
  asked to plan a refactor, sequence remediation, or implement an approved target
  architecture. Produces a phased, verifiable plan that cites source findings,
  evidence, design decisions, contracts, or risks. NOT for applying changes
  (hand off to a mutator agent), designing target architecture (use
  architecture-design), or scoring (use architecture-scorecard).
---

# Architecture plan

Derive an actionable, incremental implementation/refactoring plan from an
approved design, with review findings as supporting context when present. The
architect drafts the plan; it never executes it.

## When to use

Use after an architecture design, when the user wants approved target
architecture implemented. For existing-code remediation, the default chain is
`architecture-review` → `architecture-design` → `architecture-plan`. Plan one
hotspot, boundary, module, or flow per plan unless a roadmap is explicitly
requested.

If there is no approved design artifact, recommend `architecture-design` first.
If there is no review report for existing-code remediation, recommend
`architecture-review` before design unless the user explicitly wants greenfield
target-state design.

## Skill navigation

- Missing findings for an existing system: recommend `architecture-review` first
  unless the user already supplied enough current evidence.
- Missing approved target architecture: recommend `architecture-design` before
  planning.
- Current skill: use `architecture-plan` to sequence small, verifiable changes
  from an approved design, citing review findings as supporting rationale when
  present.
- Next skill after implementation: run `architecture-review` to verify the code
  now matches intended architecture and the plan's acceptance criteria.

## Task list discipline

Maintain a visible task list for the planning flow. Track at least:

1. Approved design artifact confirmed; supporting review report confirmed when
   present.
2. Scope and first execution horizon selected.
3. Safety net ordered before behavior-bearing changes.
4. Executable task sections drafted.
5. Verification and acceptance criteria attached.
6. Handoff and re-review step recorded.

Keep task names outcome-based. Do not expose runtime-specific mechanics in the
plan.

## Destination

When the user asks to write or generate a plan and gives no destination, write it
under `docs/plans/` using a kebab-case slug from the target, for example
`docs/plans/extract-auth-boundary.md`. Create `docs/plans/` if it is missing.
Use a user-specified path only when provided.

## Procedure

1. **Anchor to the source artifacts.** Cite the approved design artifact plus
   decision, contract, risk, or module IDs each task addresses. Include source
   report finding/evidence IDs when the design came from a review. A task with no
   source rationale does not belong in the plan.

2. **Use the plan template.** `src/templates/plan.md` is the skeleton: Overview,
   Source artifact, Success criteria, Validation Commands, Phases with
   executable `### Task N:` sections, Acceptance criteria, Safety notes,
   Re-review. Put checkboxes only inside `### Task N:` or `### Iteration N:`
   sections; context sections must use plain bullets or prose.

3. **Resolve the destination.** For written artifacts, default to
   `docs/plans/<kebab-case-target>.md` unless the user gives another path.

4. **Order for safety.** Prefer characterization tests, seam creation, boundary
   repair, and fitness checks before cosmetic cleanup. Establish a safety net
   before changing behavior-bearing code.

5. **Keep it incremental.** No big-bang rewrites. Each executable task is small
   and independently verifiable. Keep the next execution horizon to five tasks or
   fewer before a re-review.

6. **Make every task verifiable.** Each `### Task N:` section includes a
   concrete check — a test, a fitness check, or a command — that proves it is
   done. Success and acceptance criteria tie back to findings, score dimensions,
   design decisions, integration contracts, or module responsibilities.

7. **Write safety notes.** Flag irreversible steps, data migrations, and
   wide-blast-radius changes. State plainly that the architect does not apply the
   plan; an engineer or mutator agent executes it after approval.

## Failure handling

- Missing approved design, unreadable artifact, or absent finding/evidence/
  decision/contract refs: stop and ask for the missing source or run
  `architecture-design`. Do not invent refs.
- Missing `src/templates/plan.md`: report the missing template and ask before
  using an inline fallback.
- Requested rewrite with no cited finding, design decision, or risk behind it:
  decline that phase and name the missing rationale.

## Output

Return or write a Markdown plan shaped like `src/templates/plan.md`. When
writing the file and no path is provided, use `docs/plans/<kebab-case-target>.md`.
Include:

- `## Source artifact`: approved design path or ID plus decision, contract,
  risk, or module IDs used; include supporting report finding/evidence IDs when
  present.
- `## Success criteria`: measurable outcomes tied to findings, score dimensions,
  design decisions, contracts, or module responsibilities. Use plain bullets, no
  checkboxes.
- `## Validation Commands`: commands to run after task completion.
- `## Phases`: at most five executable `### Task N:` sections. Each task has
  justification, preconditions, checkbox work items, postconditions, and
  verification.
- `## Acceptance criteria`: checks that prove the plan is complete. Use plain
  bullets, no checkboxes.
- `## Safety notes`: blast radius, irreversible steps, rollback notes, and the
  mutator/engineer handoff.

## Hard rules

- Every executable task cites a source finding, evidence ref, design decision,
  contract, risk, or module responsibility.
- Task headers must be `### Task N:` or `### Iteration N:`.
- Checkboxes must appear only under executable task/iteration headings.
- Generated plan files default to `docs/plans/<kebab-case-target>.md` unless the
  user provides a different path.
- Incremental only — no rewrites the source artifact does not justify.
- The plan must end with a re-review recommendation.
- The architect produces the plan and stops. Execution is someone else's job.
