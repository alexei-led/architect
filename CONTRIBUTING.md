# Contributing

Maintainer notes for `architect`. User-facing install and usage stay in [README.md](README.md).

## Requirements

- Python 3.12+
- `uv`
- `make`
- `gitleaks`
- optional: `markdownlint-cli2`

## Setup

```sh
make setup
```

Installs dev dependencies and sets Git hooks from `scripts/git-hooks/`.

## Checks

```sh
make build        # generate runtime artifacts into dist/
make check        # build + drift check + ruff + pytest
make evals        # paid Agent Skills evals
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
make release V=0.2.0
```

Requires a clean tree. Updates versioned files, rebuilds generated artifacts, runs checks, scans with Gitleaks, commits the release, and creates tag `vX.Y.Z`.

Push branch and tag to publish through GitHub Actions.

## Packaging

Source of truth is under `src/`. Generated artifacts in `dist/` are committed.

Main outputs:

```text
.claude-plugin/marketplace.json
.agents/plugins/marketplace.json
package.json
dist/claude/plugins/architecture/
dist/codex/plugins/architecture/
dist/codex/agents/architect.toml
dist/pi/{skills,agents,templates}/
```

When changing prompts, skills, templates, or plugin metadata:

1. edit `src/`
2. run `make build`
3. commit source and generated output together

`make check` fails on generated-artifact drift.

## Docs

- `README.md`: user-facing install and usage
- `CONTRIBUTING.md`: maintainer workflow
- `docs/`: methodology, scoring, report format, tool coverage

Templates and source contracts win if prose drifts.
