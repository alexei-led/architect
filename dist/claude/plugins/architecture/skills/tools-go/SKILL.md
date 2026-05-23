---
name: tools-go
description: >-
  Run Go dependency and quality tools for review evidence — go list, go mod
  graph, goda, gopls, staticcheck, govulncheck, and go-callvis. Use when the
  target is a Go module and you need package graphs, import cycles, dead code,
  vulnerabilities, or call graphs. NOT for TS/JS (use tools-typescript), Python
  (use tools-python), or generic structural search (use tools-ast-grep).
---

# Go tools

Dependency, semantic, and supply-chain evidence for Go modules. The Go toolchain
itself answers most structural questions; goda and go-callvis add graph shape.

Evidence dimensions: **dependency**, **structural**, **semantic** (gopls,
staticcheck), **security** (govulncheck).

## When to use

Use when the system map shows `go.mod`. Pick to the question: package
import/dependency facts (go list, go mod graph), boundary/graph analysis (goda),
semantic refs (gopls), bug/dead-code analysis (staticcheck), known
vulnerabilities (govulncheck), call graph (go-callvis).

## Commands

```sh
# Direct imports of a package (structural)
go list -deps ./... | sort -u
go list -f '{{.ImportPath}} {{.Imports}}' ./...

# Module-level dependency graph
go mod graph

# Package boundary / dependency queries (cycles, allowed-deps)
goda graph "./...:all"
goda cycle ./...

# Semantic references via the language server (see tools-lsp-tree-sitter)
gopls references <file>:<line>:<col>

# Static analysis: bugs, unused code, suspicious constructs
staticcheck ./...

# Known vulnerabilities in deps + reachable call paths
govulncheck ./...

# Call graph visualization (DOT)
go-callvis -format dot ./...
```

## Confidence impact

- `go list` / `go mod graph` / goda output is direct dependency evidence:
  `tools_used`, raises `dependency_graph_health` and `boundary_integrity`
  confidence. Cycles from `goda cycle` are concrete findings.
- `govulncheck` is the security/supply-chain dimension; it reports _reachable_
  vulnerabilities, which is stronger than a raw advisory match — cite the call
  path.
- An **existing** goda/staticcheck rule gating CI is an enforced fitness check —
  count it toward `architecture_fitness`; one you'd recommend is not.
- staticcheck's `U1000` (unused) is reliable for unexported symbols; reflection
  and build tags can hide reachability — confirm before scoring.

## Failure and missing-tool handling

- Tool missing → record the dimension `tools_missing` + install hint
  (`go install honnef.co/go/tools/cmd/staticcheck@latest`, etc.); fall back to
  the built-in `go list` facts and the code graph, recording reduced coverage.
- A package that doesn't build (missing deps, generate step) makes go list /
  staticcheck fail → `tools_failed` (build state), not "clean." Note it and cap
  confidence.
- Build tags / multiple GOOS targets: a single run covers one build
  configuration — record which, and treat other targets as a coverage gap.

## When to stop

`go list` plus goda answers the dependency/boundary question for a module; add
staticcheck for bugs and govulncheck for supply chain. Stop once those are
recorded — don't generate a full go-callvis render unless a specific call-path
question needs it (the images are large and noisy; summarize, never paste).

## Hard rules

- Distinguish an enforced staticcheck/goda CI gate (raises fitness) from a
  recommended one.
- A non-building package yields `tools_failed`, not a clean result.
- Use the toolchain CLIs; do not reimplement Go dependency analysis in package
  code.
