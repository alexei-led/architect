---
{"description":"Gather resolved semantic evidence with LSP and syntax fallback with tree-sitter. Use when architecture findings need actual definitions, references, callers, implementations, diagnostics, or symbols rather than text matches — especially for coupling and boundary claims. Use tree-sitter when no language server is available or the question is purely syntactic. NOT for exact text discovery (use tools-code-search), repo-scale dependency graphs (use tools-codegraph), or git history (use tools-gitnexus).","name":"tools-lsp-tree-sitter"}
---

# LSP and tree-sitter

A language server resolves symbols the way the compiler does: it knows the real
definition, every reference, the implementations of an interface, and the
diagnostics the toolchain reports. tree-sitter parses syntax without resolution
— fast, language-agnostic, but it cannot tell you what a name resolves to. Reach
for LSP when you need semantic truth; fall back to tree-sitter when no server is
configured.

Evidence dimensions: **semantic** (LSP) and **structural** (tree-sitter).

## When to use

Use LSP to confirm a real call/reference relationship before claiming coupling,
to find every implementation of a boundary interface, to verify callers/callees
at a seam, and to surface compiler diagnostics. Use tree-sitter syntax queries
when LSP is unavailable or when the question is purely syntactic (find all
functions, all type declarations) and a server would be overkill.

## Commands

LSP access depends on the runtime's LSP integration; use only exposed runtime
operations, and do not invent tool names. Operations to request:

```text
definition <file>:<line>:<col>     # where a symbol is defined
references <file>:<line>:<col>     # every use of a symbol
implementations <symbol>           # implementors of an interface/abstract type
diagnostics <file|workspace>       # compiler/linter diagnostics
documentSymbols <file>             # outline of one file
workspaceSymbols <query>           # find a symbol across the project
```

tree-sitter syntax queries (no resolution, pattern over the parse tree):

```sh
# Function definitions (Python grammar)
tree-sitter query func.scm src/**/*.py

# Inline: capture all class declarations
tree-sitter parse src/foo.py            # inspect the tree to write a query
```

A `.scm` query file holds the capture patterns; run it across the target files.

## Evidence output

Record:

- `dimension`: semantic for LSP, structural for tree-sitter.
- `source`: operation, file:line:col or query file, and project/build context.
- `facts`: definitions, references, implementations, diagnostics, symbols, or syntax matches.
- `limits`: missing server, non-building project, partial workspace, or syntax-only fallback.

## Confidence impact

- An LSP `references`/`implementations` result is the strongest structural-
  semantic evidence available — it reflects real resolution. `tools_used`,
  raises confidence for boundary and coupling findings ("X is referenced only
  from Y" is a resolved fact, not a guess).
- tree-sitter answers syntactic questions only; a tree-sitter match is the same
  strength as an ast-grep match (presence, not reachability). Don't claim "no
  callers" from tree-sitter — that needs LSP references or the codegraph.

## Failure and missing-tool handling

- No language server for the language → semantic dimension `tools_missing`; fall
  back to tree-sitter (syntactic) plus tools-codegraph (graph) and record the
  reduced semantic coverage. A claim that needs resolution but has only syntactic
  evidence must be flagged as a hypothesis, not a fact.
- LSP returns nothing because the project doesn't build (missing deps, broken
  config) → that's `tools_failed`, not "no references." Note the build state and
  cap confidence.

## When to stop

Resolve the specific relationship the finding rests on, then stop. Don't pull
references for every symbol in the module — only the ones a score depends on.
When you need aggregate graph shape (all cycles, all hubs) rather than one
symbol's neighborhood, switch to tools-codegraph instead of fanning out LSP
queries.

## Hard rules

- A "no callers / no references" claim requires LSP resolution or the code
  graph — never assert it from syntax alone.
- LSP emptiness from a non-building project is `tools_failed`, not evidence.
- Do not embed a parser in package code — use the runtime's LSP/tree-sitter
  integration.
