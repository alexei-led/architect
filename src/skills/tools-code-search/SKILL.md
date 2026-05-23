---
name: tools-code-search
description: >-
  Gather local codebase evidence with fd, rg, git grep, git log, and targeted
  file reading. Use when starting an architecture review, building the system
  map, finding entrypoints, locating module boundaries, tracing exact text or
  config keys, or collecting file:line evidence for modularity, coupling,
  dependency, blast-radius, or fragility claims. Use before heavier AST, graph,
  LSP, language, or history tools. NOT for final architecture assessment (use
  architecture-review) or semantic/type resolution (use tools-lsp-tree-sitter or
  tools-codegraph).
---

# Code search and targeted reading

Local search is the first evidence pass. It discovers where the architecture is
implemented before heavier tools spend time proving graph or semantic facts.

Evidence dimensions: **discovery** and lightweight **structural** context.

## When to use

Use during the system-map step and whenever a finding needs scoped file:line
support before graph, AST, LSP, or language-tool confirmation. Good questions:

- Where are the entrypoints, deploy units, public interfaces, and package roots?
- Which files mention a domain concept, config key, route, queue, or dependency?
- Which modules import a boundary package or framework type?
- What docs, ADRs, manifests, or ownership files describe intended structure?
- Which exact files should the review read next?

This skill supports `architecture-review`; it does not assign architecture scores
or make findings by itself.

## Commands

Run from the repo root. Prefer `fd` for paths and `rg` for text. Use the
runtime's file-read tool for targeted reads after search narrows the scope.

```sh
# High-signal structure and intent files
fd '(^README|CONTEXT|ARCHITECTURE|adr|decisions|ownership|CODEOWNERS|package.json|pyproject.toml|go.mod|Chart.yaml|kustomization.yaml|Dockerfile|\.github)' .

# Files by language / package marker
fd 'package.json|tsconfig.json|pyproject.toml|requirements.txt|go.mod|main.tf|Chart.yaml|kustomization.yaml'

# Exact concepts, routes, config keys, or dependency names
rg -n --hidden --glob '!{.git,node_modules,dist,build,vendor}/**' 'Order|Payment|Auth|Session|Repository|Controller|Handler|typeorm|sqlalchemy|kafka|redis'

# Import/dependency hints before AST or graph tools
rg -n --glob '!{.git,node_modules,dist,build,vendor}/**' "from ['\"]|import |require\(|package "

# Git-tracked scope, useful for generated/vendor exclusion
git ls-files

# Change hints when GitNexus is missing or stale
git log --name-only --pretty=format: -- <path> | sort | uniq -c | sort -nr | head
```

Prefer `git grep -n <pattern>` when the review should ignore untracked/generated
files and only search the versioned source.

## Evidence output

Record:

- `dimension`: discovery or structural context.
- `source`: exact command, pattern, and searched scope.
- `facts`: file:line refs and the code/doc fact each ref proves.
- `limits`: excluded paths, missing tools, generated/vendor noise, or partial checkout.
- `next_tool`: specialized follow-up if the claim needs AST, graph, LSP, language, or history proof.

## Confidence impact

- A scoped `rg`/`git grep` hit with a targeted file read is direct discovery or
  structural evidence. Cite the command and file:line.
- A clean exact-text search is evidence only for that literal pattern in the
  searched scope. It does not prove absence of a concept, dependency, caller, or
  boundary leak.
- Directory shape and file names are weak evidence of intended modules. Use them
  to plan deeper checks, not to score architecture quality.

## Failure and missing-tool handling

- `rg` or `fd` missing → record the discovery dimension `tools_missing`; fall
  back to `grep` / `find` and say the search is slower/coarser.
- Generated/vendor noise overwhelms results → narrow with `git ls-files`, path
  globs, or package roots; do not paste raw dumps.
- A repo with sparse checkout, shallow history, or generated sources has partial
  discovery coverage. Record the limit before drawing conclusions.

## When to stop

Stop when you have enough paths to read and enough facts to choose the next
specialized tool. Return a short read-next list, not a full repository index. If
the question needs structural pattern proof, switch to `tools-ast-grep`; if it
needs real references/callers, switch to `tools-lsp-tree-sitter` or
`tools-codegraph`; if it needs co-change or volatility, switch to
`tools-gitnexus`.

## Hard rules

- Read only the files or ranges that answer the current question.
- Cite command + scope + file:line for evidence.
- Never score or assert boundary integrity from directory shape or text search
  alone.
- Separate facts found by search from hypotheses that need graph, LSP, language,
  or history confirmation.
