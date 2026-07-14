---
{"description":"Gather Go architecture evidence with go list, go mod graph, goda, gopls, staticcheck, govulncheck, and go-callvis. Use when a Go module needs package graphs, import cycles, dependency direction, package-boundary checks, call/reference facts, dead code, vulnerabilities, or call graphs for modularity and coupling review. NOT for TS/JS (use tools-typescript), Python (use tools-python), exact text discovery (use tools-code-search), or generic structural patterns (use tools-ast-grep).","name":"tools-go"}
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
vulnerabilities (govulncheck), call graph (go-callvis). Use the results to judge
package modularity, dependency direction, coupling, and architecture fitness.

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

# Semantic references via the language server
# Use exposed LSP operations from tools-lsp-tree-sitter; do not invent gopls CLI syntax.

# Static analysis: bugs, unused code, suspicious constructs
staticcheck ./...

# Known vulnerabilities in deps + reachable call paths
govulncheck ./...

# Call graph visualization (DOT)
go-callvis -format dot ./...
```

## Evidence output

Record:

- `dimension`: dependency, structural, semantic, or security.
- `source`: Go command, package pattern, build tags/GOOS, and module root.
- `facts`: package edges, cycles, diagnostics, call paths, vulnerabilities, or confirmed clean scope.
- `limits`: non-building packages, missing tools, build tags, generated code, or uncovered GOOS targets.

## Confidence impact

- `go list` / `go mod graph` / goda output is direct dependency evidence:
  `tools_used`, raises `dependency_graph_health` and `boundary_integrity`
  confidence. Cycles from `goda cycle` are concrete findings.
- `govulncheck` is the security/supply-chain dimension; it reports reachable
  vulnerabilities, which is stronger than a raw advisory match — cite the call
  path.
- An existing goda/staticcheck rule gating CI is an enforced fitness check —
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
question needs it or the user asks for it (the images are large and noisy;
summarize, never paste).

## Hard rules

- Distinguish an enforced staticcheck/goda CI gate (raises fitness) from a
  recommended one.
- A non-building package yields `tools_failed`, not a clean result.
- Use the toolchain CLIs; do not reimplement Go dependency analysis in package
  code.
