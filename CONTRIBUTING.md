# Contributing

Maintainer notes for `architect`. User-facing install and usage stay in [README.md](README.md).

## Requirements

- Python 3.12+
- `uv`
- `make`
- `gitleaks`
- `agbun` on `PATH`
- optional: vendor CLIs for package smoke tests
- optional: `markdownlint-cli2`

## Setup

```sh
make setup
```

Installs dev dependencies and sets Git hooks from `scripts/git-hooks/`.

## Checks

```sh
make build         # generate every target tree into dist/
make check         # read-only `agbun` drift check + ruff + pytest
make package-smoke # build, then load/install all six targets with vendor CLIs
make evals         # paid Agent Skills evals
make evals FAST=1 # faster advisory eval loop
```

Run `make check` before opening a PR.

For docs-only changes, also run:

```sh
markdownlint-cli2 README.md CONTRIBUTING.md docs/*.md
```

## Secret scanning

Git hooks run `gitleaks`:

- pre-commit: staged diff
- pre-push: full history
- release: full history

Do not commit secrets, credential files, tokens, `.env`, or Gitleaks reports.

Before making the repo public:

```sh
gitleaks git --redact --no-banner
```

## Helper CLIs

Run from the repo:

```sh
uv run architect-doctor --repo /path/to/repo
uv run architect-validate-report path/to/report.md
uv run architect-compare-reports base-report.md head-report.md
```

Install on `PATH` during development:

```sh
uv tool install --editable .
```

## Release

```sh
make release V=X.Y.Z
```

Requires a clean tree. Updates versioned files, rebuilds generated artifacts, runs checks, scans with Gitleaks, commits the release, and creates tag `vX.Y.Z`.

Push branch and tag to publish through GitHub Actions.

## Packaging

Source of truth is `agentbundle.json` plus the declared files under `src/`.
Generated artifacts in `dist/` are committed. **Agent Bundler** is a system
prerequisite: the Makefile, hooks, CI, and release workflow invoke `agbun` from
`PATH`. Check the installed version with `agbun --version`; its value is recorded
in `dist/.agentbundler/build.json` after each build.

Main outputs:

```text
agentbundle.json
src/packages/architecture.json
dist/claude/{.claude-plugin,skills,agents,resources}/
dist/codex/{.codex-plugin,skills,agents,resources}/
dist/pi/{package.json,skills,agents,resources}/
dist/copilot/{plugin.json,skills,agents,resources}/
dist/grok/.grok/{skills,resources}/
dist/cursor/{.cursor-plugin,skills,agents,resources}/
```

Repository marketplace files remain integration metadata and point at the
corresponding `dist/claude`, `dist/codex`, `dist/copilot`, and `dist/cursor`
package roots. The repository-root `package.json` registers the generated Pi
skills and Architect role through `pi.subagents.agents`, with `pi-subagents` as
a declared dependency. Grok keeps a project tree; its installable route is the
Claude-compatible `dist/claude` package.

When changing prompts, skills, templates, or plugin metadata:

1. edit `src/` or the repository-owned marketplace/package metadata
2. run `make build`
3. run `make check`
4. run `make package-smoke` before a release when all vendor CLIs are available
5. commit source and generated output together

`agbun check` is read-only and fails on generated-artifact drift. Package tests
also require version/dependency coherence and equal Grok/Claude skill and template
inventories. `make package-smoke` isolates vendor homes where supported and uses
temporary workspaces; its Cursor check uses the current login for one authenticated
read-only model request.

## Docs

- `README.md`: user-facing install and usage
- `CONTRIBUTING.md`: maintainer workflow
- `docs/`: methodology, scoring, report format, tool coverage

Templates and source contracts win if prose drifts.
