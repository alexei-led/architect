---
{"description":"Gather persistent code-knowledge-graph evidence from the codebase-memory-mcp MCP server: architecture overview, type-resolved call edges, cycles, blast radius, module clusters, dead code, and cross-session ADR memory. Use when `mcp__codebase-memory-mcp__*` tools are available and you need graph-shaped structure, coupling, or impact evidence without re-reading files. A degraded or stale index is a coverage gap, not evidence. NOT for exact text discovery (use tools-code-search), syntactic patterns (use tools-ast-grep), or git change-coupling/churn (use tools-gitnexus); when this server is absent, fall back to tools-codegraph for the same graph evidence.","name":"tools-codebase-memory"}
---

# codebase-memory-mcp

`codebase-memory-mcp` indexes a repository into a persistent SQLite knowledge
graph (tree-sitter ASTs plus a hybrid LSP layer) and exposes it over MCP. It
answers the same graph-shaped questions as `codegraph` — what calls this, what a
change reaches, where the hubs, cycles, and clusters are — plus cross-session
Architecture Decision Records. Query it instead of re-reading files when the
server is installed.

Evidence dimensions: **dependency**, **semantic**, and **change-impact**.

## When to use

Use when the session exposes `mcp__codebase-memory-mcp__*` tools (verify with
`/mcp`; the server reports as `codebase-memory-mcp`). Index during the
system-map step, then query during evidence gathering for module structure,
call/dependency edges, cycles, blast radius, and Louvain module clusters. Prefer
it over `tools-codegraph` only when its index is present and fresh; otherwise use
whichever graph tool is current.

## Tools

All tools are namespaced `mcp__codebase-memory-mcp__<name>`. The
architecture-relevant set:

- `index_repository` — build or refresh the graph. `repo_path` must be ABSOLUTE.
- `list_projects` — indexed projects with node/edge counts.
- `index_status` — indexing state for a project.
- `get_graph_schema` — node labels, edge types, counts. Run this first.
- `get_architecture` — overview: languages, packages, routes, hotspots,
  clusters, dead code.
- `search_graph` — find symbols by `label` / `name_pattern` / `file_pattern`.
- `trace_path` (alias `trace_call_path`) — callers/callees of a function;
  `direction` in|out|both, `depth` 1-5 (fan-in/out, blast radius).
- `detect_changes` — map the git diff to affected symbols and blast radius.
- `query_graph` — read-only Cypher for cycles, dependency direction, hubs.
- `get_code_snippet` — source for a symbol by qualified name.
- `search_code` — grep-like text search within the index.
- `manage_adr` — read ADRs (`mode: get`); write modes need user approval.

## Workflow

1. `list_projects` — is the target already indexed? If not, `index_repository`
   with the absolute repo path and wait for completion.
2. `get_graph_schema` — learn the available labels/edges before querying.
3. `get_architecture` — overview before deep dive: packages, entry points,
   routes, hotspots, clusters, dead code.
4. `search_graph` then `get_code_snippet` — locate and read specific symbols.
5. `trace_path` — fan-in/out and call paths for boundary/coupling claims.
6. `detect_changes` — blast radius of the working diff before a change.
7. `query_graph` — Cypher for cycles and wrong-way dependencies, e.g.
   `MATCH (f:Function)-[:CALLS]->(g) WHERE ... RETURN ...`.

## Stale-index handling

A background watcher auto-syncs after file/git changes, so the index is usually
current. Still verify before scoring:

- `list_projects` / `index_status` to confirm the project is indexed.
- If `index_repository` returns `status: degraded` (persisted nodes below the
  verify ratio), treat graph metrics as a coverage gap — re-index or record the
  dependency dimension `tools_failed`, and do not score from it.
- Call edges are type-resolved (hybrid LSP) for ~11 languages; other parsed
  languages give syntactic edges only. Record uncovered languages as a coverage
  gap, not as "no dependencies."

## Evidence output

Record:

- `dimension`: dependency, semantic, or change-impact.
- `source`: the tool call (and `project`) plus index freshness.
- `facts`: cycles, hubs, fan-in/out, clusters, affected symbols/paths, dead
  code, or confirmed absence.
- `limits`: degraded/partial index, language coverage, unresolved edges.

## Confidence impact

- Fresh, type-resolved call/cycle/blast-radius facts are direct dependency and
  semantic evidence: `tools_used`, raise confidence for boundary and
  `dependency_graph_health` findings.
- `detect_changes` / `trace_path` blast radius bounds a refactor plan's risk —
  cite it in the plan's safety notes.
- A degraded or partial index caps confidence. Never present graph metrics from
  an index you did not confirm.

## Failure and missing-tool handling

- Server not installed (`mcp__codebase-memory-mcp__*` absent) → take dependency
  evidence from `tools-codegraph` or language dependency tools; record the source
  actually used.
- `trace_path` returns nothing → the exact symbol name is likely wrong; find it
  with `search_graph(name_pattern=".*Partial.*")` first.
- Multi-project session → pass `project` explicitly (from `list_projects`).
- `index_repository` would index a very large tree → it writes only to the
  external cache (`~/.cache/codebase-memory-mcp`, never the repo), but flag huge
  indexes and respect the user's time budget.

## Hard rules

- This is graph evidence, not design judgment — calibrate it like any tool.
- A `degraded`, stale, or unverified index is `tools_failed`, never evidence.
- Read ADRs freely; do not create, update, or delete ADRs, or run
  `ingest_traces`, without explicit user approval.
- Do not treat a missing edge as proof when the language is only syntactically
  parsed.
