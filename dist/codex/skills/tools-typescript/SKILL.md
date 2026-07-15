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

Resolve the package root and runner without changing dependency state:

1. Read `package.json` for `packageManager`, `scripts`, and `workspaces`.
2. Check workspace manifests and current lockfiles: `pnpm-workspace.yaml`,
   `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lock`, and
   `bun.lockb`.
3. If those signals conflict, record the runner as ambiguous and use only an
   explicit configured script or ask which package root owns the check.
4. Prefer a configured script after inspecting it for install or download
   commands. Otherwise run only a proven executable already in that package
   root's `node_modules/.bin`.

Do not install or download analysis tools during a review. `npm exec`, `npx`,
`bunx`, `pnpm dlx`, and `yarn dlx` can acquire missing packages; do not use them
as an installation fallback. Redirect caches to `$TMPDIR`.

```sh
# Package-manager, workspace, and script discovery
node -e 'const p=require("./package.json"); console.log(JSON.stringify({packageManager:p.packageManager??null,workspaces:p.workspaces??null,scripts:p.scripts??{}},null,2))'
ls package-lock.json yarn.lock pnpm-lock.yaml pnpm-workspace.yaml bun.lock bun.lockb 2>/dev/null

# Use an inspected configured script with the detected package manager
# pnpm: pnpm run; npm: npm run; Yarn: yarn run; Bun: bun run
<detected-runner> run <configured-script>

# Otherwise prove each local binary exists, then run it directly

test -x node_modules/.bin/depcruise && node_modules/.bin/depcruise src --include-only "^src" --config .dependency-cruiser.cjs
test -x node_modules/.bin/madge && node_modules/.bin/madge --circular --extensions ts,tsx src
test -x node_modules/.bin/knip && node_modules/.bin/knip
test -x node_modules/.bin/tsc && node_modules/.bin/tsc --noEmit
test -x node_modules/.bin/eslint && ESLINT_CACHE_LOCATION=$TMPDIR/eslint-cache node_modules/.bin/eslint . --max-warnings 0
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
- Knip unused-file, export, and dependency output is a hypothesis until checked
  against configured entrypoints, generated code, dynamic imports, workspace
  boundaries, and build/test scripts. Confirm it before promoting it to a
  finding or moving a score.

## Failure and missing-tool handling

- No configured script or proven local executable → dependency dimension
  `tools_missing`; name the missing tool and fall back to ast-grep import scans
  plus the code graph, recording reduced coverage. Do not install or download
  the tool to complete the review.
- Conflicting package-manager or workspace signals → record the ambiguity and
  narrow to a confirmed package root before running commands.
- Some analysis tools return nonzero when they find issues. For example,
  `madge --circular` may exit nonzero when cycles exist. Inspect the output
  before labeling the command `tools_failed`; finding output is evidence, not a
  tool failure.
- `tsc`/ESLint failing because project dependencies are absent or broken →
  `tools_failed` (build state), not "no type errors." Note it and cap confidence.
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
- Use configured scripts or proven local executables only. Never install or
  download a missing analysis tool during a review.
- Treat Knip dead/unused output as hypotheses until dynamic and generated usage
  is checked.
- Use the CLIs; do not reimplement graph analysis in package code.
