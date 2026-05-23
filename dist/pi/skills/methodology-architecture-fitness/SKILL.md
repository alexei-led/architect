---
name: methodology-architecture-fitness
description: >-
  Treat architecture intent as executable checks (fitness functions), not prose.
  Use when scoring the architecture_fitness dimension, recommending how to keep a
  boundary from re-rotting, or turning a finding into an enforceable check.
  Distinguishes checks that already run from checks you only recommend. NOT for
  judging coupling (use methodology-balanced-coupling) or assigning scores (use
  architecture-scorecard).
---

# Architecture fitness

Architecture intent that lives only in a doc is a suggestion. Intent that runs in
CI is enforced. A **fitness function** is an automated check that fails the build
when the system drifts from an intended architectural property — a layering
rule, an allowed-dependency rule, a cycle ban, a bundle-size budget.

This follows the evolutionary architecture idea of fitness functions. For a
review: a documented rule and an enforced rule are not the same, and the score
must reflect which one you actually found.

## When to use

Use while scoring the `architecture_fitness` dimension, when designing checks for
a new architecture, or when a finding's fix is "and keep it from coming back." A
boundary repair without a check to hold it will rot again; the plan should add
the check.

## Skill navigation

- Missing architecture intent: use `architecture-design` to define it or
  `architecture-review` to reconstruct it from docs and code.
- Current skill: use `methodology-architecture-fitness` to distinguish existing
  enforced checks from recommended checks.
- Next skill: use `architecture-scorecard` when scoring a review, include checks
  in `architecture-design`, or sequence missing checks in `architecture-plan`.

## Existing checks vs recommended checks

Keep these strictly separate — conflating them inflates the score.

- **Existing check** — a check that actually runs and can fail the build today.
  Evidence: a CI step, a lint/dep-rule config, a test that asserts an
  architectural property. Cite it. Only existing, enforced checks raise the
  `architecture_fitness` score.
- **Recommended check** — a check you propose because intent is currently
  unenforced. It is a recommendation, not evidence of fitness. It belongs in
  the report's recommendations and the refactoring plan, and does **not** raise
  the score.

A repo with thorough architecture docs and zero enforcement scores low on
fitness, not high. Documentation is intent; fitness is enforcement.

## Verifying a check is real

Before counting a check as existing, confirm all three:

1. It runs automatically — in CI, a pre-commit hook, or the test suite — not only
   when someone remembers to run it.
2. It can **fail** — a check that always passes (or is wired to warn-only)
   enforces nothing. Look for it gating merges.
3. It asserts an **architectural** property — module boundaries, dependency
   direction, cycles, layering, budgets — not just style or formatting.

If you can't confirm a check fails the build on violation, treat it as
recommended, not existing.

## Mapping findings to candidate checks

When intent is unenforced, recommend the cheapest check that would catch the
finding's class:

- Layer or boundary bypassed: dependency-rule lint, e.g. dependency-cruiser,
  import-linter, ESLint boundaries, or a `go list` rule.
- Import cycles: cycle check, e.g. madge `--circular`, import-linter contract,
  `go list`, or staticcheck.
- Direct DB or framework access from domain code: ast-grep absence rule.
- God module or unbounded fan-in: dependency-count or graph-metric threshold in
  CI.
- Public API surface creeping: knip or exported-symbol diff gate.
- Bundle or binary size budget: size-limit or artifact-size assertion.
- Boundary contract drift: contract/schema test.

Recommend checks the team's existing tools can express — don't propose a new
framework when a lint rule does it. Tie each recommendation to the finding ID it
guards so the plan can sequence it.

## How fitness affects the score and plan

- High `architecture_fitness` requires enforced checks, cited as evidence. No
  enforcement → low band regardless of doc quality.
- In a refactoring plan, add the fitness check with the boundary repair, so the
  repaired boundary can't silently re-rot. Order it as a postcondition of the
  phase that fixes the boundary.

## Output

When applying this methodology, report:

- `finding_id`: finding the check protects.
- `existing_check`: current automated check, or `none`.
- `evidence_ref`: CI/config/test evidence for an existing check.
- `enforced`: whether it runs automatically and can fail the build.
- `score_impact`: how it affects `architecture_fitness`.
- `recommended_check`: cheapest missing check, if intent is unenforced.

## Hard rules

- Never score documented-but-unenforced intent as fitness.
- An existing check must be automated, able to fail, and architectural.
- Recommended checks are recommendations — they live in the report/plan, never in
  the evidence for a high fitness score.
