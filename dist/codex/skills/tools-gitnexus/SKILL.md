---
name: tools-gitnexus
description: >-
  Use GitNexus to mine git history for change-coupling evidence — which files
  change together, change frequency, and the impact of a change over time. Use
  when scoring change_locality or assessing volatility for Balanced Coupling.
  Index staleness is a coverage gap, not evidence. NOT for static call graphs
  (use tools-codegraph) or syntactic pattern search (use tools-ast-grep).
---

# GitNexus

`gitnexus` turns git history into a queryable graph: co-change relationships,
per-file change frequency, and the historical blast radius of a path. It is the
evidence source for "do changes actually stay inside the intended boundary?" and
for the volatility axis of Balanced Coupling.

Evidence dimension: **change**.

## When to use

Use to score `change_locality` (do edits respect module boundaries over history)
and to ground volatility claims — a module that churns and co-changes with a
distant module is a coupling risk only history can show. Build the index during
the system-map step.

## Commands

```sh
gitnexus analyze                 # mine history → build the change graph
gitnexus status                  # index health + commit it covers
gitnexus list                    # entities/files known to the graph
gitnexus query "<expr>"          # query co-change / frequency
gitnexus context <path>          # what co-changes with <path>
gitnexus impact <path>           # historical blast radius of a change
gitnexus detect-changes          # files changed since the indexed commit
gitnexus cypher "<query>"        # raw Cypher for custom graph questions
```

Flow: `analyze`, then `status`, then `context` / `impact` / `cypher` for
co-change evidence.

## Stale-index handling

Run `gitnexus status` (and `detect-changes`) before trusting output. If the
index lags the working tree, co-change data is incomplete:

- Re-run `gitnexus analyze` to refresh.
- If you cannot refresh, the change dimension is `tools_failed` ("stale
  index") — do not score change locality from it.

## Confidence impact

- Fresh co-change/impact data is direct change evidence: `tools_used`, raises
  confidence for `change_locality` and the volatility input to
  `coupling_balance`.
- **Renames split history.** A directory/package rename divides a file's churn
  across old and new paths, halving apparent change. Scope queries to current
  paths or follow renames; otherwise note the undercount and cap confidence.
- Shallow clones and short history windows undercount churn — record the window
  and treat it as a coverage limit.

## Failure and missing-tool handling

- Not installed → change dimension `tools_missing`; fall back to
  `git log --follow`, `git log --pretty --name-only`, and per-file commit counts,
  recording the coarser coverage. Do not assert change locality with no history
  evidence at all.
- `analyze` errors on a shallow/empty repo → record the limit; "no co-change
  found" from a one-commit clone is not evidence of good locality.

## When to stop

Co-change and impact for the modules under review answer the change question
once. Stop after recording them — don't run Cypher variations chasing weak
correlations. If the question shifts to static structure (what calls what,
regardless of history), that is tools-codegraph, not another GitNexus query.

## Hard rules

- Verify freshness with `status` before scoring; a stale index is `tools_failed`.
- Account for renames before reporting churn numbers.
- Do not reimplement git mining in package code — call the CLI.
