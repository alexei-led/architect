# architect

An instruction-first architecture review extension for Claude Code, Codex CLI,
and Pi.

## What this is

`architect` ships an architecture review agent, a focused set of skills, report
and plan templates, and a few small Python helper tools. The agent inspects a
codebase, interviews for missing context, builds a system map, scores
architecture against a defined rubric, cites evidence for every claim, and
produces a refactoring plan.

## Instruction-first design

The behavior lives in instructions — agent prompts, skills, templates, and
rubrics — not in package code. Agents drive local OSS CLIs (ast-grep, LSP,
language-specific dependency analyzers, infra linters) directly rather than
through wrapped library logic.

Package code is intentionally thin. The Python helpers do only what an LLM
should not do by hand:

- `architect-doctor` — check tool availability and report coverage states.
- `architect-validate-report` — validate report frontmatter, scores, evidence
  refs, and tool coverage.
- `architect-compare-reports` — compare two reports or explain why they are not
  comparable.

Helpers never wrap evidence tools (ast-grep, codegraph, GitNexus, LSP,
tree-sitter); agents call those directly.

## Layout

Source lives under `src/` and compiles to per-runtime output under `dist/`:

- `src/agents/` — architect agent definition plus per-target frontmatter.
- `src/skills/` — review, scorecard, plan, methodology, and tool skills.
- `src/templates/` — report, scorecard, and plan templates.
- `src/architect_tools/` — Python helper CLIs.
- `src/plugins/` — plugin/package manifests.
- `scripts/build/` — source-to-dist compiler.
- `tests/` — pytest suite and fixtures.
- `dist/claude/`, `dist/codex/`, `dist/pi/` — generated runtime outputs.

## Development

Python 3.12+ with [uv](https://docs.astral.sh/uv/).

```sh
uv sync                     # install dev dependencies
uv run pytest               # run tests
uv run ruff check .         # lint
uv run ruff format --check .  # format check
```

`scripts/build/compile.py` regenerates `dist/` from `src/`. Do not hand-edit
generated files under `dist/`.

```sh
uv run python scripts/build/compile.py          # regenerate dist/
uv run python scripts/build/compile.py --check  # fail on drift / hand-edits
```

Each target (`claude`, `codex`, `pi`) gets the same layout: `agents/architect.md`
(AGENT.md body with the target frontmatter overlay merged in), `skills/<name>/`,
`templates/`, and a `plugin.yaml` manifest enumerating the agent and skills.
Output is deterministic, so `--check` catches both stale builds and hand edits.
