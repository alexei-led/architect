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

## Pi package

`dist/pi/` is the Pi package. Its `plugin.yaml` manifest enumerates the architect
agent and every skill, so Pi discovers them from the manifest paths — no
per-skill registration needed.

The Pi manifest declares one dependency:

```yaml
requires:
  - alexei-led/cc-thingz
```

`cc-thingz` provides the `ask_user_question` tool the architect's interview step
maps to on Pi (see `src/agents/architect/pi/frontmatter.yaml`). This extension
ships no local Pi question extension; `cc-thingz` is the single source of that
capability. Without it, the review skill falls back to plain numbered interview
questions.

Run the Python helpers through `uv` (entry points declared in `pyproject.toml`):

```sh
uv run architect-doctor --repo /path/to/repo   # tool availability + coverage
uv run architect-validate-report report.md     # validate a report
uv run architect-compare-reports a.md b.md      # compare or explain non-comparability
```

## Documentation

- [docs/install.md](docs/install.md) — install and update for Claude, Codex, and Pi.
- [docs/tools.md](docs/tools.md) — OSS CLI tools, coverage states, confidence impact.
- [docs/report-format.md](docs/report-format.md) — report and plan format.
- [docs/scoring.md](docs/scoring.md) — score dimensions, bands, confidence, comparability.
- [docs/methodology.md](docs/methodology.md) — Balanced Coupling and architecture fitness.
