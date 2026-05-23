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
  line-level code review or applying refactors (use architecture-plan for the
  handoff).
---

# Architecture review

The review loop, in order. Do not skip ahead — each step gates the next.

## When to use

Use when a user wants their architecture reviewed, audited, or scored; wants to
understand where modularity, coupling, dependency, blast-radius, or fragility
risk lives; or wants to compare intended and observed architecture. For comparing
two existing reports use `architect-compare-reports`. For a combined "review and
refactor" request, finish the read-only review first, then use
`architecture-plan` to draft the handoff plan; a mutator or engineer applies
changes after approval.

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

2. **Build the system map before judging quality.** Establish what exists:
   languages, package managers, units, deploy units, public interfaces, declared
   modules (manifests/dirs) vs observed modules (graphs/imports/churn), high-risk
   entrypoints, and missing evidence. This populates `system_map` in the report
   frontmatter. Scoring before a map is forbidden. Scoring from directory shape
   alone is explicitly forbidden — a directory tree is not an architecture.

3. **Gather evidence across applicable dimensions.** Use `tools-code-search` for
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

4. **Triage before scoring.** Sort signal from noise: which observations are
   facts, which are hypotheses, which actually bear on a score. See
   `references/triage.md`.

5. **Score with the scorecard skill.** Use the architecture-scorecard skill for
   every score. Read `../../templates/scorecard.yaml` for dimensions, bands,
   anchors, and rules — it is the source of truth. Each non-meta score needs at
   least one evidence ref. Low confidence caps the quality claim.

6. **Write the report from the template.** Use `../../templates/report.md` as the
   skeleton. Fill frontmatter (interview context, system map, scores, findings,
   evidence, tool coverage) and the prose sections. Findings carry stable IDs.

7. **Hand off requested refactors through architecture-plan.** If the user asks
   for review and immediate refactoring, do not edit source or mix audit with
   implementation. Finish the report, then use the architecture-plan skill for
   warranted changes. The handoff must include finding/evidence IDs, scoped
   modules/files, incremental steps, verification checks, acceptance criteria,
   risk/rollback notes, and an explicit mutator/engineer implementation step.

## Output

A completed review produces an architecture report using `../../templates/report.md`.
The report must include `interview_context`, `system_map`, `scores`, `findings`,
`evidence`, and `tool_coverage`. If refactoring is requested, the only follow-up
artifact is an `architecture-plan` handoff tied to finding/evidence IDs.

## Required response clauses

When asked to describe the review workflow, include these clauses explicitly:

- Inspect docs, ADRs, manifests, and repository structure before asking.
- Ask only for missing context whose answer changes the architecture assessment.
- Build the system map before scoring; never score from directory shape alone.
- Require cited evidence and per-dimension tool coverage before findings or scores.
- Keep the review read-only on source; route implementation to a mutator or
  engineer.

When the user asks to review and refactor, separate the response into review,
scoring/recommendations, and implementation handoff. Use the exact skill name
`architecture-plan` for warranted changes. State that the architect refuses
source edits, and that the handoff includes verification steps and acceptance
criteria for the mutator or engineer.

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

- No scoring before a system map; never score from directory shape alone.
- No finding without cited evidence.
- No high-quality band on low confidence.
- Read-only on source. Route implementation to a mutator or engineer via
  architecture-plan with verification-backed acceptance criteria.
