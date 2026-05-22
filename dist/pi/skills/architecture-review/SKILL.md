---
name: architecture-review
description: >-
  Run an evidence-based architecture review. Use when asked to review, audit, or
  assess a codebase's architecture, find structural risk, or check how a system's
  structure matches its intent. Interviews for missing context, builds a system
  map, gathers tool evidence, scores against the scorecard rubric, and writes a
  cited report. NOT for applying refactors (hand off a plan) or line-level code
  review.
---

# Architecture review

The review loop, in order. Do not skip ahead — each step gates the next.

## When to use

Use when a user wants their architecture reviewed, audited, or scored, or wants
to understand where structural risk lives. For comparing two existing reports
use `architect-compare-reports`; for turning findings into action use the
architecture-plan skill.

## Procedure

1. **Interview if context is missing.** Do not score from a cold start. If you
   lack the intended architecture, quality goals, volatile areas, or scope, run
   the interview first. See `references/interview.md`. Inspect docs, ADRs, and
   manifests before asking — never ask a question the repo already answers.
   **Non-interactive runs (CI, autonomous):** when no user is reachable,
   reconstruct intent from docs/ADRs/CLAUDE.md/changelog, label the context
   reconstructed, and cap `analysis_confidence` accordingly. Never invent intent.

2. **Build the system map before judging quality.** Establish what exists:
   languages, package managers, units, deploy units, public interfaces, declared
   modules (manifests/dirs) vs observed modules (graphs/imports/churn), high-risk
   entrypoints, and missing evidence. This populates `system_map` in the report
   frontmatter. Scoring before a map is forbidden — a directory tree is not an
   architecture.

3. **Gather evidence across applicable dimensions.** Use the relevant tool
   skills (ast-grep, codegraph, GitNexus, LSP/tree-sitter, language and
   operational tool skills) to cover discovery, structural, semantic, dependency,
   change, and operational evidence. Cite tools and files you used. Record
   coverage — used, skipped, missing, failed — per dimension, even where you find
   nothing wrong. Summarize output; do not paste raw dumps.
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

## Structured questions by runtime

The interview asks the user questions. Branch on the agent's
`structured_questions` capability flag (set in the per-target overlay), not on a
hardcoded tool name:

- A concrete tool name (e.g. `AskUserQuestion` on Claude, `ask_user_question` on
  Pi with cc-thingz): use the structured-question tool.
- `unverified` or unset (e.g. Codex until its runtime is confirmed): fall back to
  plain numbered questions in prose. Do not call an unverified tool.

## Hard rules

- No scoring before a system map.
- No finding without cited evidence.
- No high-quality band on low confidence.
- Read-only on source. Hand a plan to a mutator agent for changes.
