---
name: tools-ast-grep
description: >-
  Gather structural-pattern architecture evidence with ast-grep syntax-tree
  queries. Use when checking module boundaries, layer violations, forbidden
  imports, direct DB/framework access, route declarations, exported surface area,
  or framework leaks across seams. Yields exact file:line evidence for
  modularity, coupling, and fragility claims. NOT for whole-graph dependency
  analysis (use tools-codegraph), exact text discovery (use tools-code-search),
  or semantic/type resolution (use tools-lsp-tree-sitter).
---

# ast-grep

`ast-grep` matches code by its syntax tree, so a pattern survives reformatting,
whitespace, and comments that defeat `grep`. It is the cheapest way to answer
"does this pattern exist where it shouldn't?" with a precise file:line list.

Evidence dimension: **structural**. Output is a concrete evidence ref per match.

## When to use

Use when a finding hypothesis is a structural code pattern: "domain code imports
the ORM directly," "routes are declared outside the router module," "this
framework type leaks past the boundary," or "a module exports too much surface."
ast-grep confirms presence/absence with line-anchored hits. Use it before
claiming a boundary is bypassed — a claim about a pattern needs the matched
lines.

## Commands

Run from the repo root. `-l` sets language; `-p` is an inline pattern; `--json`
gives machine-readable hits for counting.

```sh
# Imports of a specific package (TS/JS)
ast-grep -l ts -p 'import $$$ from "typeorm"'

# Direct DB access leaking into a layer (scope with a path)
ast-grep -l ts -p 'createConnection($$$)' src/domain

# Exported symbols (surface-area survey)
ast-grep -l ts -p 'export $$$'

# Route declarations outside the router (framework leak)
ast-grep -l ts -p 'app.$METHOD($PATH, $$$)'

# Framework type used past the boundary (Python example)
ast-grep -l python -p 'Request' src/core

# Count hits without dumping every match
ast-grep -l go -p 'sql.Open($$$)' --json | jq length
```

For reusable, named rules (relational metavariable constraints, `inside`,
`not`), put them in a YAML rule file and run `ast-grep scan -r rule.yml`. See
`references/rules.md` for the rule patterns this review relies on.

## Evidence output

Record:

- `dimension`: structural.
- `source`: ast-grep command, language, pattern/rule file, and searched scope.
- `facts`: matched file:line refs or confirmed zero-match scope.
- `limits`: parse errors, unsupported language, regex fallback, or lack of semantic reachability.

## Confidence impact

- A pattern search that runs and returns hits or a clean zero is direct
  structural evidence: `tools_used` for the structural dimension, raises
  confidence for the related finding.
- ast-grep proves syntactic presence, not runtime reachability. A matched
  forbidden import is strong; "no matches" means the pattern is absent, not that
  the boundary is sound by every measure — pair absence claims with the
  dependency graph before scoring boundary integrity high.

## Failure and missing-tool handling

- Not installed → record the structural dimension `tools_missing`, note the
  install hint (`brew install ast-grep` / `cargo install ast-grep`), and fall
  back to `tools-lsp-tree-sitter` syntax queries or a regex `grep` with an
  explicit confidence caveat. Do not silently downgrade to regex without saying
  so.
- A pattern that errors (unsupported language, bad metavariable) is a tool
  failure on that query, not evidence of absence — fix the pattern or record it
  `tools_failed`; never report "no matches" from a query that never parsed.

## When to stop

One precise rule per hypothesis is enough. Once a pattern returns hits (or a
confirmed clean zero on a correct pattern), record the evidence and move on. Do
not enumerate twenty variant patterns hunting for more matches — if the
structural question is answered, stop and record coverage. If a pattern needs
graph-level reachability (who actually calls this), that is a coverage gap for
ast-grep: hand it to tools-codegraph rather than approximating with more
syntax searches.

## Hard rules

- Cite the matched file:line as the evidence ref; never describe a pattern you
  did not run.
- "No matches" is only evidence if the pattern parsed and the language was
  correct.
- Do not reimplement ast-grep matching in package code — call the CLI.
