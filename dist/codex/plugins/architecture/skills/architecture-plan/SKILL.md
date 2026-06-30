---
name: architecture-plan
description: >-
  Turn approved architecture-design artifacts, with supporting review findings
  when present, into an incremental implementation/refactoring plan. Use when
  asked to plan a refactor, sequence remediation, or implement an approved target
  architecture. Produces a task-runner-compatible, verifiable plan that cites
  source findings, evidence, design decisions, contracts, or risks. NOT for
  applying changes (hand off to a mutator agent), designing target architecture
  (use architecture-design), or scoring (use architecture-scorecard).
---

# Architecture plan

Derive an actionable, incremental implementation/refactoring plan from an
approved design, with review findings as supporting context when present. The
artifact is executable by an engineer, mutator agent, or task runner; the
architect writes the plan and stops.

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

Keep task names outcome-based. Do not expose prompt or tool internals in task
names.

## Destination

When the user explicitly asks for a plan file and gives no destination, ask to
confirm the default path under `docs/plans/` using a kebab-case slug from the
target, for example `docs/plans/extract-auth-boundary.md`. Create `docs/plans/`
only after the destination is confirmed. If the user only asks to generate or
create a plan, return it in the conversation unless they confirm a file path.
Use a user-specified path only when provided. If the user-specified path is
outside `docs/plans/`, state that the executor must be invoked with that exact
path or the plan must be copied/symlinked into the configured plans directory.

## Procedure

1. **Anchor to the source artifacts.** Cite the approved design artifact plus
   decision, contract, risk, or module IDs each task addresses. Include source
   report finding/evidence IDs when the design came from a review. A task with no
   source rationale does not belong in the plan.

2. **Use the plan template.** `../../templates/plan.md` is the skeleton: Overview,
   Source artifact, Success criteria, Validation Commands, Implementation Steps
   with executable `### Task N:` sections, Acceptance criteria, Safety notes,
   Re-review. Put checkboxes only inside `### Task N:` or `### Iteration N:`
   sections; context sections must use plain bullets or prose.

3. **Resolve the destination.** For file artifacts, use the user's path. If no
   path is provided, ask to confirm `docs/plans/<kebab-case-target>.md` before
   writing or creating directories. When the path is outside `docs/plans/`,
   include the exact execution path or the copy/symlink instruction in the
   handoff.

4. **Order for safety.** Prefer characterization tests, seam creation, boundary
   repair, and fitness checks before cosmetic cleanup. Establish a safety net
   before changing behavior-bearing code.

5. **Keep it incremental.** No big-bang rewrites. Each executable task is small,
   independently committable, and independently verifiable. Keep the next
   execution horizon to five tasks or fewer before a re-review.

6. **Make every task concrete.** Each `### Task N:` section includes:
   - Justification: source finding, evidence ref, design decision, contract,
     risk, or module responsibility.
   - Files: planned file paths and what changes in each.
   - Preconditions and postconditions.
   - Impact commands: concrete `gitnexus impact <path-or-symbol>` and
     `gitnexus detect-changes` commands when GitNexus is available; otherwise an
     explicit fallback such as `git diff --name-only` and the missing-tool note.
   - Deterministic architecture checks: if archfit is configured, name the
     existing gate status, the rule/config change when needed, and the focused
     `archfit analyze --gate` or `archfit analyze --gate --base <ref>` command.
     For a new gate,
     state the violation should fail before the fix and pass after it. Otherwise
     name the missing config/tool gap.
   - Verification commands: concrete test, lint, type, or fitness commands for
     this task, not only whole-plan commands.
   - Manual checks: plain bullets only, or `None`.
   - Checkbox work items for executable implementation steps only.

7. **Separate manual checks.** Do not turn human review or judgment into
   checkboxes. Put those under `Manual checks:` using plain bullets so task
   runners do not treat them as extra loop iterations.

8. **End with final verification and docs.** The last executable task is a final
   verification/documentation task. It runs whole-plan validation, updates or
   explicitly rules out docs changes, records GitNexus `detect-changes`, and
   records the scoped `architecture-review` follow-up.

9. **Write safety notes.** Flag irreversible steps, data migrations, and
   wide-blast-radius changes. State plainly that an engineer, mutator agent, or
   task runner executes the approved plan after approval.

## Failure handling

- Missing approved design, unreadable artifact, or absent finding/evidence/
  decision/contract refs: stop and ask for the missing source or run
  `architecture-design`. Do not invent refs.
- Missing `../../templates/plan.md`: report the missing template and ask before
  using an inline fallback.
- Requested rewrite with no cited finding, design decision, or risk behind it:
  decline that task and name the missing rationale.
- No concrete file list or verification command can be named for a task: split,
  narrow, or discard the task before writing the plan.

## Output

Return or write a Markdown plan shaped like `../../templates/plan.md`. When
writing a file with no path provided, use the confirmed default path
`docs/plans/<kebab-case-target>.md`. Include:

- `## Source artifact`: approved design path or ID plus decision, contract,
  risk, or module IDs used; include supporting report finding/evidence IDs when
  present.
- `## Success criteria`: measurable outcomes tied to findings, score dimensions,
  design decisions, contracts, or module responsibilities. Use plain bullets, no
  checkboxes.
- `## Validation Commands`: concrete project-wide commands to run for the whole
  plan, including archfit analyze gate commands (`--base` for deltas) when
  configured.
- `## Implementation Steps`: at most five executable `### Task N:` or
  `### Iteration N:` sections. Each task has justification, files,
  preconditions, postconditions, fitness gate, impact commands, verification
  commands, manual checks, and checkbox work items.
- A final `### Task N: Final verification and documentation` section.
- `## Acceptance criteria`: checks that prove the plan is complete. Use plain
  bullets, no checkboxes.
- `## Safety notes`: blast radius, irreversible steps, rollback notes, and the
  engineer/mutator/task-runner handoff.

## Hard rules

- Every executable task cites a source finding, evidence ref, design decision,
  contract, risk, or module responsibility.
- Task headers must be `### Task N:` or `### Iteration N:`; `N` may be an
  integer or a small variant such as `2.5` or `2a`.
- Checkboxes must appear only under executable task/iteration headings.
- Generated plan files use the user-provided path, or a confirmed default path
  under `docs/plans/<kebab-case-target>.md`.
- If a generated plan is outside `docs/plans/`, the handoff must say how to run
  it by exact path or copy/symlink it into the configured plans directory.
- Every task has a file list, fitness-gate status, and concrete per-task
  verification command.
- When archfit is configured, every boundary/coupling task names the archfit
  check or config/rule update that will make the improvement repeatable,
  including before-fail/after-pass expectation for new gates.
- Manual checks use plain bullets only.
- Every plan includes concrete GitNexus impact/detect-changes commands or an
  explicit missing-tool fallback.
- Incremental only — no rewrites the source artifact does not justify.
- The final executable task is verification/documentation/handoff.
- The plan must end with a re-review recommendation.
- The architect produces the plan and stops. Execution is someone else's job.
