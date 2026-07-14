---
{"description":"Gather Python architecture evidence with import-linter, pydeps, pyright/basedpyright, ruff, deptry, pipdeptree, uv tree, radon/lizard, and vulture. Use when a Python repo needs import contracts, module graphs, layer-boundary checks, type state, complexity hotspots, dead code, or dependency health for modularity and coupling review. NOT for TS/JS (use tools-typescript), Go (use tools-go), exact text discovery (use tools-code-search), or generic structural patterns (use tools-ast-grep).","name":"tools-python"}
---

# Python tools

Dependency, complexity, and quality evidence for Python targets. These cover the
import graph, layering contracts, type state, dead code, and dependency hygiene.

Evidence dimensions: **dependency**, **structural**, **semantic** (type
checkers), and **complexity** hotspots.

## When to use

Use when the system map shows `pyproject.toml` / `setup.py` / `requirements`.
Pick to the question: layering contracts (import-linter), module graph (pydeps),
types (pyright/basedpyright), lint (ruff), dependency hygiene (deptry,
pipdeptree, uv tree), complexity/size (radon, lizard), dead code (vulture). Use
the results to judge module boundaries, dependency direction, cohesion, and
architecture fitness.

## Commands

Redirect caches to `$TMPDIR` (`RUFF_CACHE_DIR=$TMPDIR/ruff`). Prefer
`uv run`/`uvx` so the target env is untouched.

```sh
# Layering / boundary contracts (config in .importlinter or pyproject)
uvx --from import-linter lint-imports

# Import/module dependency graph (DOT for the system map)
uvx pydeps src/pkg --max-bacon 2 --noshow -T dot

# Type errors (semantic)
uvx pyright            # or: uvx basedpyright

# Lint (style + many bug classes)
RUFF_CACHE_DIR=$TMPDIR/ruff uvx ruff check .

# Declared-vs-used dependency mismatches
uvx deptry src

# Installed dependency tree
uvx pipdeptree            # or, for a uv project: uv tree

# Cyclomatic complexity / maintainability hotspots
uvx radon cc -s src      # or: uvx lizard src

# Dead code (unused functions/vars — confirm before trusting)
uvx vulture src
```

## Evidence output

Record:

- `dimension`: dependency, structural, semantic, or complexity hotspot.
- `source`: Python command, package path, environment/tool runner, and cache location.
- `facts`: import contracts, module edges, cycles, type/lint findings, dead-code hypotheses, or clean scope.
- `limits`: missing deps, dynamic imports, optional deps, cache failures, or partial package coverage.

## Confidence impact

- import-linter contracts and pydeps cycles are direct dependency/boundary
  evidence: `tools_used`, raises `dependency_graph_health` and
  `boundary_integrity` confidence.
- An existing import-linter contract run in CI is an enforced fitness check —
  count it toward `architecture_fitness`. A contract you'd recommend is not.
- radon/lizard complexity flags cohesion/size hotspots (god modules); pair with
  the dependency graph before scoring `cohesion_modularity`.
- vulture and deptry have false positives (dynamic imports, optional deps) —
  treat their output as hypotheses to confirm, not settled findings.

## Failure and missing-tool handling

- Tool missing and offline → dependency dimension `tools_missing` + install
  hint; fall back to ast-grep import scans and the code graph, recording reduced
  coverage.
- pyright failing because deps aren't installed → `tools_failed` (env state),
  not "no type errors." Note the env and cap confidence.
- A tool writing a cache into a read-only target fails on I/O, not on findings —
  redirect the cache and rerun before recording failure.

## When to stop

One graph/contract tool plus one type/lint pass answers the structural and
semantic questions for a package. Stop once cycles, contracts, types, and obvious
hotspots are recorded — don't run radon and lizard and vulture for the same
answer. Dynamic-dispatch reachability that static tools can't resolve is a
coverage gap: record it rather than guessing.

## Hard rules

- Distinguish an enforced import-linter contract (raises fitness) from a
  recommended one.
- vulture/deptry results are hypotheses until confirmed against dynamic usage.
- Tool failure from an uninstalled env is `tools_failed`, not clean.
- Use the CLIs; do not reimplement graph or type analysis in package code.
