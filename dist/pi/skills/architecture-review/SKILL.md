---
name: architecture-review
description: >-
  Run a repeatable, evidence-based architecture review of an existing codebase.
  Use when asked to assess modularity, coupling, cohesion, dependency direction,
  circular dependencies, blast radius, fragile seams, shallow modules,
  testability, ownership boundaries, architectural drift, structural risk, or fit
  between intended and observed architecture. Drives local search/read/grep,
  code graph, GitNexus/change-history, AST/LSP, language, and operational tool
  evidence; scores with the scorecard and writes cited findings. NOT for
  line-level code review, target architecture design (use architecture-design),
  or implementation sequencing (use architecture-plan after design approval).
---

# Architecture review

The review loop, in order. Do not skip ahead — each step gates the next.

## When to use

Use when a user wants their architecture reviewed, audited, or scored; wants to
understand where modularity, coupling, dependency, blast-radius, or fragility
risk lives; or wants to compare intended and observed architecture. For comparing
two existing reports use `architect-compare-reports`. For a combined "review and
refactor" request, finish the read-only review first, then recommend exactly one
primary next skill: `architecture-design` when remediation needs a target state,
or `architecture-plan` only when an approved target design already exists. A
mutator or engineer applies changes after approval. For target architecture or
requirements-to-design work without review, use `architecture-design` instead.

## Skill navigation

- User asks to define target architecture or work from requirements: use
  `architecture-design` instead of reviewing implementation quality.
- Current skill: use `architecture-review` to compare intended architecture with
  observed implementation. Treat design docs as intent only; actual code,
  runtime config, and tests may have drifted.
- Next skill after a report: choose one primary next step:
  - stop when the user asked for audit/scoring only;
  - `architecture-design` when findings need target boundaries, contracts,
    tests, or fitness checks;
  - `architecture-plan` only when the target design is already approved and the
    user asks for implementation sequencing.
- After implementation, run `architecture-review` again with comparable scope to
  check whether the code now matches intent.

## Task list discipline

Maintain a visible task list for the review flow. Track at least:

1. Context and scope confirmed.
2. Working model validated.
3. System map built.
4. Evidence gathered by dimension.
5. Findings triaged.
6. Scores assigned.
7. Report written and checked.
8. Next skill recommendation made.

Keep task names outcome-based. Do not expose runtime-specific mechanics in the
instructions or report.

## Procedure

1. **Interview if context is missing.** Do not score from a cold start. If you
   lack the intended architecture, quality goals, volatile areas, or scope, run
   the interview first. See `references/interview.md`. Inspect docs, ADRs, and
   manifests before asking — never ask a question the repo already answers. Ask
   only for missing context whose answer would change the architecture
   assessment.
   **Non-interactive runs (CI, autonomous):** when no user is reachable,
   reconstruct intent from docs/ADRs/CLAUDE.md/changelog, label the context
   reconstructed, and cap `analysis_confidence` accordingly. Never invent intent.

2. **Validate the working model.** Before scoring, surface your current
   understanding for correction: system purpose, candidate units, responsibilities,
   major integrations, domain classifications, ownership/deploy assumptions,
   known pain, and doc-vs-code drift risks. Existing architecture docs describe
   intended design, not necessarily current implementation. Ask only for
   corrections that would change the assessment. In non-interactive runs, mark
   this model as reconstructed and record unconfirmed assumptions in
   `missing_evidence`.

3. **Build the system map before judging quality.** Establish what exists:
   languages, package managers, units, deploy units, public interfaces, declared
   modules (manifests/dirs) vs observed modules (graphs/imports/churn), high-risk
   entrypoints, and missing evidence. This populates `system_map` in the report
   frontmatter. Scoring before a map is forbidden. Scoring from directory shape
   alone is explicitly forbidden — a directory tree is not an architecture.

4. **Gather evidence across applicable dimensions.** Use `tools-code-search` for
   local search/read/grep, then the relevant specialized tool skills (ast-grep,
   codegraph, GitNexus, LSP/tree-sitter, language and operational tool skills)
   to cover discovery, structural, semantic, dependency, change, and operational
   evidence. Cite tools and files you used. Record coverage — used, skipped,
   missing, failed — per dimension, even where you find nothing wrong. Summarize
   output; do not paste raw dumps.
   - **Check persistent indexes for staleness first.** Before trusting codegraph
     or GitNexus, confirm the index matches the current commit (e.g.
     `gitnexus status`). A stale index is a coverage gap, not evidence — record
     it as `tools_failed`, do not score from it.
   - **No working tool for an applicable dimension** is recorded as
     `tools_missing` with explicit `confidence_impact`. Do not silently score a
     dimension (e.g. dependency health) from imports alone without flagging the
     gap and capping confidence.
   - **Redirect tool caches** to a writable temp dir when a tool writes a cache
     into the target repo (e.g. `RUFF_CACHE_DIR=$TMPDIR/...`); a sandboxed or
     read-only target will otherwise fail the tool.
   - **Churn across renames:** a directory/package rename splits each file's
     git history across the old and new path, halving apparent churn. Scope churn
     to current paths or use `git log --follow` per file.

5. **Triage before scoring.** Sort signal from noise: which observations are
   facts, which are hypotheses, which actually bear on a score. See
   `references/triage.md`.

6. **Score with the scorecard skill.** Use the architecture-scorecard skill for
   every score. Read `../../templates/scorecard.yaml` for dimensions, bands,
   anchors, and rules — it is the source of truth. Each non-meta score needs at
   least one evidence ref. Low confidence caps the quality claim.

7. **Write the report from the template.** Use `../../templates/report.md` as the
   skeleton. Fill frontmatter (interview context, system map, scores, findings,
   evidence, tool coverage) and the prose sections. Findings carry stable IDs
   and human-facing narratives: knowledge or boundary leakage, complexity impact,
   cascading-change scenarios, recommendation, and trade-offs.

8. **Recommend the next primary skill.** If the user asks for review and
   immediate refactoring, do not edit source or mix audit with implementation.
   Finish the report, then choose one next skill:
   - `architecture-design` when the target boundaries, contracts, tests, or
     fitness checks are not yet approved;
   - `architecture-plan` when an approved design already exists and the user
     wants executable sequencing;
   - no next skill when the user asked for audit/scoring only.

   If the user asks for the full remediation pipeline, name the sequence:
   `architecture-review` → `architecture-design` → `architecture-plan` →
   implementation by a mutator/engineer → `architecture-review` re-check. The
   final handoff must include finding/evidence IDs, design decision IDs, scoped
   modules/files, incremental steps, verification checks, acceptance criteria,
   risk/rollback notes, and an explicit mutator/engineer implementation step.

## Output

A completed review produces an architecture report using `../../templates/report.md`.
The report must include `interview_context`, `system_map`, `scores`, `findings`,
`evidence`, and `tool_coverage`. Each finding must include a human-facing
narrative explaining the leak or drift, complexity impact, cascading-change
scenarios, recommendation, and trade-offs. If remediation is requested, recommend
exactly one primary next skill unless the user asks for the full pipeline:
`architecture-design` for target-state work, or `architecture-plan` only when an
approved design already exists and implementation sequencing is requested.

## Required response clauses

When asked to describe the review workflow, include these clauses explicitly:

- Inspect docs, ADRs, manifests, and repository structure before asking.
- Treat architecture/design docs as intended architecture, not proof that the
  implementation still matches them.
- Ask only for missing context whose answer changes the architecture assessment.
- Validate the working model before scoring.
- Build the system map before scoring; never score from directory shape alone.
- Require cited evidence and per-dimension tool coverage before findings or scores.
- Keep the review read-only on source; route implementation to a mutator or
  engineer.

When the user asks to review and refactor, separate the response into review,
scoring/recommendations, next-skill recommendation, and implementation handoff.
Use the exact skill name that applies next: `architecture-design` when target
state is missing, or `architecture-plan` when an approved design already exists.
State that the architect refuses source edits, and that the handoff includes
verification steps and acceptance criteria for the mutator or engineer.

## Structured questions by runtime

Use `references/interview.md` for the full interview and fallback rules. In the
main review flow:

- Determine availability only from the active runtime's exposed tool list,
  never from source agent metadata, per-target overlays, repo metadata, or
  generated config.
- Use concrete tool names only when that tool is actually exposed.
- If no structured-question tool is available, ask exactly one plain prose question and wait.
- Ambiguous or deferred answers become `missing_evidence` and lower
  `analysis_confidence`.

## Hard rules

- No scoring before a validated working model and system map; never score from
  directory shape alone.
- No trusting stale architecture docs as implementation truth.
- No finding without cited evidence and a human-facing narrative.
- No high-quality band on low confidence.
- Read-only on source. Recommend exactly one primary next skill: route target
  definition through `architecture-design`, or route approved implementation
  sequencing to a mutator/engineer via `architecture-plan` with
  verification-backed acceptance criteria.
