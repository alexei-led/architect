---
name: tools-codegraph
description: >-
  Use codegraph to build and query a persistent code graph — definitions,
  references, call edges, and what a change affects. Use when gathering
  dependency and semantic evidence at whole-repo scale: cycles, hubs, fan-in/out,
  and blast radius. Index staleness is a coverage gap, not evidence. NOT for
  single-pattern searches (use tools-ast-grep) or git-history change locality
  (use tools-gitnexus).
---

# codegraph

`codegraph` builds a persistent graph of the codebase — symbols, references, and
call edges — that you query without re-parsing each time. It answers
graph-shaped questions ast-grep can't: what depends on this, what does a change
affect, where are the hubs and cycles.

Evidence dimensions: **dependency** and **semantic**.

## When to use

Use to map observed module structure against declared modules, to find import
cycles and high-fan-in hubs, and to size the blast radius of a proposed change.
Build the graph during the system-map step; query it during evidence gathering.

## Commands

```sh
codegraph init                 # set up the graph store in the repo
codegraph index                # full parse → build the graph
codegraph sync                 # incremental update after changes
codegraph status               # index health + commit it was built at
codegraph query "<expr>"       # query symbols / edges
codegraph context <symbol>     # neighbors of a symbol (callers, callees, refs)
codegraph affected <path>      # what a change to <path> reaches (blast radius)
codegraph files <symbol>       # files defining/referencing a symbol
```

Typical flow: `init` once, `index`, then `status` to confirm freshness, then
`query` / `context` / `affected` for evidence.

## Stale-index handling

Always run `codegraph status` before trusting a query. If the index commit does
not match the working tree, the graph describes an old repo:

- Run `codegraph sync` (incremental) or `codegraph index` (full) to refresh.
- If you cannot refresh (read-only target, time budget), the stale graph is
  **not evidence** — record the dependency dimension `tools_failed` with reason
  "stale index," and do not score dependency health from it.

## Confidence impact

- A fresh graph queried for cycles/hubs/affected is direct dependency evidence:
  `tools_used`, raises confidence for `dependency_graph_health` and boundary
  findings.
- `affected` output bounds a refactoring plan's risk — cite it in the plan's
  safety notes.
- A stale or partial index caps confidence. Never present graph metrics from an
  index whose commit you didn't verify.

## Failure and missing-tool handling

- Not installed → dependency dimension `tools_missing`; fall back to language
  dependency tools (tools-python / tools-typescript / tools-go) for cycles and
  graphs, and record the reduced coverage. Do not infer the dependency graph
  from raw imports alone without flagging the gap.
- `index` errors on an unsupported language → record which languages the graph
  covers; treat uncovered languages as a coverage gap, not as "no dependencies."

## When to stop

The graph answers cycles, hubs, and blast radius once. After you've recorded
those for the applicable modules, stop querying — don't fish the graph for
incidental edges that don't bear on a score. If a question is about _change over
time_ (who keeps touching this together), that is tools-gitnexus territory, not
another codegraph query.

## Hard rules

- Verify index freshness with `status` before every scoring use.
- A stale index is `tools_failed`, never evidence.
- Do not wrap codegraph in package code — agents call the CLI directly.
