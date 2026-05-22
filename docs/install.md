# Install and update

`architect` is instruction-first: the shippable unit is a tree of agent and skill
Markdown files plus templates, generated per runtime under `dist/`. Installing
means placing one `dist/<target>/` tree where the runtime discovers it; updating
means regenerating that tree and replacing the installed copy.

## Build the outputs first

All three targets are generated from `src/` by the build compiler. Nothing under
`dist/` should be hand-edited.

```sh
uv sync                                          # dev dependencies
uv run python scripts/build/compile.py           # regenerate dist/claude, dist/codex, dist/pi
uv run python scripts/build/compile.py --check    # verify no drift / hand-edits
```

Each `dist/<target>/` has the same layout:

```
dist/<target>/
  agents/architect.md          # AGENT.md body + target frontmatter overlay
  skills/<name>/SKILL.md        # one dir per skill, references alongside
  templates/                    # report.md, scorecard.yaml, plan.md
  plugin.yaml                   # manifest enumerating the agent and every skill
```

## Claude Code

The Claude output (`dist/claude/`) is a Claude plugin: `plugin.yaml` plus
`agents/` and `skills/` trees. Claude's `AskUserQuestion` tool is native, so the
interview step needs no extra dependency.

- Install: make `dist/claude/` available to Claude as a plugin (preferred — the
  `templates/` tree ships at the plugin root where the instructions resolve it),
  or copy `dist/claude/agents/architect.md`, `dist/claude/skills/*`, and
  `dist/claude/templates/` into the `.claude/agents/`, `.claude/skills/`, and
  `.claude/templates/` directories of the repo (or your user `~/.claude/`) you
  want to review from. The skills read templates by the relative path
  `templates/<file>`, so the `templates/` tree must travel with the install.
- Update: re-run the build, run `--check` to confirm a clean regeneration, then
  replace the installed copy.

The architect agent's Claude frontmatter is a flat, read-only `tools` allow-list
— no `Edit`/`Write`. It reads code and writes reports/plans only with approval.

## Codex CLI

The Codex output (`dist/codex/`) carries the same agent and skills with the Codex
frontmatter overlay. Codex's structured-question support is unverified, so the
overlay keeps `structured_questions: unverified` and the interview falls back to
plain numbered questions; the build asserts no concrete question-tool name leaks
into Codex output.

- Install: place `dist/codex/agents/`, `dist/codex/skills/`, and
  `dist/codex/templates/` where your Codex CLI discovers agents and skills; the
  skills read templates by the relative path `templates/<file>`.
- Update: re-run the build and replace the installed copy.

## Pi

The Pi output (`dist/pi/`) is the Pi package. Its `plugin.yaml` enumerates the
architect agent (`agents/architect.md`) and every skill path, so Pi discovers
them from the manifest — no per-skill registration.

The manifest declares one dependency:

```yaml
requires:
  - alexei-led/cc-thingz
```

`cc-thingz` supplies the `ask_user_question` tool the interview step maps to on
Pi. This extension ships no local Pi question extension. Without `cc-thingz` the
review skill falls back to plain numbered interview questions.

- Install: install the Pi package and `alexei-led/cc-thingz` alongside it.
  `uv build` produces a wheel and sdist for the Python helpers.
- Update: re-run the build, reinstall.

## Python helpers

The helper CLIs install with the package and run through `uv` (entry points in
`pyproject.toml`):

```sh
uv run architect-doctor --repo /path/to/repo   # tool availability + coverage
uv run architect-validate-report report.md     # validate a report
uv run architect-compare-reports a.md b.md      # compare or explain non-comparability
```

See [tools.md](tools.md) for what `architect-doctor` checks.
