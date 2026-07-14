---
{"description":"Gather change-coupling and volatility evidence with GitNexus git-history graphs: files that change together, churn hotspots, historical blast radius, and impact over time. Use when scoring change_locality, corroborating Balanced Coupling volatility (domain role sets it; churn only supports it), or checking whether changes stay inside intended module boundaries. Index staleness is a coverage gap, not evidence. NOT for static call/dependency graphs (use tools-codegraph), exact text discovery (use tools-code-search), or syntactic pattern search (use tools-ast-grep).","name":"tools-gitnexus"}
---

# GitNexus

`gitnexus` turns git history into a queryable graph: co-change relationships,
per-file change frequency, and the historical blast radius of a path. It is the
evidence source for "do changes actually stay inside the intended boundary?" and
a corroborating signal for the volatility axis of Balanced Coupling — domain role
sets volatility; churn only supports it, it never sets it.

Evidence dimension: **change**.

## When to use

Use to score `change_locality` (do edits respect module boundaries over history),
to ground volatility claims, and to find fragile seams where distant modules
co-change repeatedly. A module that churns and co-changes with a distant module
is a coupling risk only history can show. Build the index during the system-map
step.

## Commands

Prefer exposed GitNexus runtime tools when available; use the CLI otherwise.
Build or refresh indexes only in an approved writable cache/store.

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

- Re-run `gitnexus analyze` to refresh, only if it can write to an approved
  cache/store.
- If you cannot refresh, the change dimension is `tools_failed` ("stale
  index") — do not score change locality from it.

## Evidence output

Record:

- `dimension`: change.
- `source`: GitNexus status/freshness, query/context/impact command, and history window.
- `facts`: co-change pairs, churn hotspots, historical blast radius, or confirmed absence.
- `limits`: stale index, shallow clone, rename split, short history window, or failed analysis.

## Confidence impact

- Fresh co-change/impact data is direct change evidence: `tools_used`, raises
  confidence for `change_locality`. For `coupling_balance`, it supports churn
  and change-locality claims; domain volatility still comes from the business
  context.
- Renames split history. A directory/package rename divides a file's churn
  across old and new paths, halving apparent change. Scope queries to current
  paths or follow renames; otherwise note the undercount and cap confidence.
- Shallow clones and short history windows undercount churn — record the window
  and treat it as a coverage limit.

## Failure and missing-tool handling

- Not installed → change dimension `tools_missing`; fall back to
  `git log --follow`, `git log --pretty --name-only`, and per-file commit counts,
  recording the coarser coverage. Do not assert change locality with no history
  evidence at all.
- Index creation would mutate the source tree or write to an unapproved location
  → use exposed runtime tools or an approved cache/store; otherwise ask before
  mutating or record `tools_failed`.
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
