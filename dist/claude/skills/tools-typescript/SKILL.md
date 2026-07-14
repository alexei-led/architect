---
{"description":"Gather TypeScript/JavaScript architecture evidence with dependency-cruiser, madge, knip, tsc, ESLint, and the package manager. Use when a TS/JS repo needs module graphs, workspace/package boundaries, import cycles, dependency direction, dead code, type errors, or boundary-rule violations for modularity and coupling review. NOT for Python (use tools-python), Go (use tools-go), exact text discovery (use tools-code-search), or generic structural patterns (use tools-ast-grep).","name":"tools-typescript"}
---

# TypeScript / JavaScript tools

Dependency and quality evidence for TS/JS targets. These tools give the module
graph, cycles, unused surface, and type/lint state — the inputs to dependency,
structural, and fitness scoring.

Evidence dimensions: **dependency**, **structural**, **semantic** (tsc).

## When to use

Use when the system map shows a `package.json` / `tsconfig.json`. Pick the tool
to the question: graph and cycles (dependency-cruiser, madge), workspace/package
boundaries, dead/unused exports and deps (knip), type correctness (tsc), boundary
lint rules (ESLint). Use the results to judge module boundaries, dependency
direction, coupling, and architecture fitness.

## Commands

Detect the package manager first, then prefer that runner (`pnpm exec`, `npm
exec`, `bunx`, configured scripts) so you don't mutate the target's deps. The
examples use `npm exec`; substitute the repo's runner. Redirect any cache to
`$TMPDIR`.

```sh
# Which package manager / lockfile (discovery)
ls package-lock.json yarn.lock pnpm-lock.yaml bun.lockb 2>/dev/null

# Module graph + boundary rules (config-driven; reports violations + cycles)
npm exec -- depcruise src --include-only "^src" --config .dependency-cruiser.cjs

# Circular dependencies, fast
npm exec -- madge --circular --extensions ts,tsx src

# Dead files, unused exports, unused dependencies
npm exec -- knip

# Type errors without emitting (semantic correctness)
npm exec -- tsc --noEmit

# Lint, including boundary plugins if configured
ESLINT_CACHE_LOCATION=$TMPDIR/eslint-cache npm exec -- eslint . --max-warnings 0
```

## Evidence output

Record:

- `dimension`: dependency, structural, or semantic.
- `source`: command, package/workspace scope, config file, and package manager.
- `facts`: module edges, cycles, boundary violations, unused surface, type/lint findings, or clean scope.
- `limits`: missing install, partial monorepo coverage, generated code, or config gaps.

## Confidence impact

- `depcruise`/`madge` cycle and boundary output is direct dependency evidence:
  `tools_used`, raises confidence for `dependency_graph_health` and
  `boundary_integrity`.
- An existing `.dependency-cruiser.cjs` with `forbidden` rules, or ESLint
  boundary rules wired into CI, is evidence of an enforced fitness check — count
  it toward `architecture_fitness` (see methodology-architecture-fitness). A rule
  you'd recommend adding is not.
- `tsc --noEmit` clean is semantic evidence the types hold; errors are concrete
  findings.

## Failure and missing-tool handling

- Tool not installed and `npx` blocked offline → dependency dimension
  `tools_missing` with install hint; fall back to ast-grep import scans + the
  code graph, recording reduced coverage.
- Some analysis tools return nonzero when they find issues. For example,
  `madge --circular` may exit nonzero when cycles exist. Inspect the output
  before labeling the command `tools_failed`; finding output is evidence, not a
  tool failure.
- `tsc`/eslint failing because the project doesn't install → `tools_failed`
  (build state), not "no type errors." Note it and cap confidence.
- Monorepo: run per-package or point configs at workspaces; a root-only run that
  misses packages is partial coverage — record which packages were covered.

## When to stop

One cycle tool plus one boundary/unused tool answers the dependency question for
a package. Don't run depcruise and madge and knip hunting for more if the graph
is already clear. Stop and record coverage once cycles, boundaries, and
dead surface are established; deeper call-level questions go to
tools-lsp-tree-sitter or tools-codegraph.

## Hard rules

- Distinguish an enforced boundary rule (raises fitness) from a recommended one.
- Tool failure from a non-installing project is `tools_failed`, not clean.
- Use the repo's detected package-manager runner for CLIs; fall back to `npx`
  only when no configured runner works. Do not reimplement graph analysis in
  package code.
