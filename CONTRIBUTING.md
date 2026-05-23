# Contributing

Development notes for `architect`. User install instructions live in [README.md](README.md).

## Requirements

- Python 3.12+
- `uv`
- `make`
- `gitleaks` for secret scanning before commit/push
- Optional: `markdownlint-cli2` for Markdown linting

## Setup

```sh
make setup
```

This installs development dependencies with `uv` and points Git hooks at `scripts/git-hooks/`.

## Local checks

```sh
make build       # compile runtime artifacts from src/ into dist/
make check        # build + generated-artifact drift check + ruff + pytest
make evals        # paid Agent Skills evals
make evals FAST=1 # advisory eval loop: no baseline, no HTML, higher concurrency
```

Run `make check` before sending changes. For README or docs-only edits, also run:

```sh
markdownlint-cli2 README.md CONTRIBUTING.md docs/*.md
```

If `markdownlint-cli2` is not installed, state that in the change notes.

## Secret scanning

The local git hooks run Gitleaks directly:

- pre-commit: staged diff
- pre-push and release: full history

`.env` and other local secret material are ignored. Do not commit real keys,
credential files, tokens, or generated Gitleaks reports. Before making the repo
public, run `make check` and `gitleaks git --redact --no-banner` from a clean tree.

## Skill evals

Paid Agent Skills evals read `OPENAI_API_KEY` from the environment or local `.env`.
The `.env` file is ignored and must not be committed.

```sh
make evals        # run evals with baseline and HTML report
make evals FAST=1 # no baseline, no HTML report, advisory exit
```

## Release

Release tags require curated changelog notes and a clean tree:

```sh
make release V=0.2.0
```

The release script updates `pyproject.toml`, `uv.lock`, and
`src/plugins/architecture/plugin.yaml`, promotes the `CHANGELOG.md` Unreleased
section when needed, rebuilds runtime artifacts, runs ruff, pytest, and a
full-history Gitleaks scan, commits the version bump plus generated artifacts,
and creates an annotated `vX.Y.Z` tag. Push the branch and tag to publish through
GitHub Actions.

## Helper CLIs

Run CLIs from the checkout while developing:

```sh
uv run architect-doctor --repo /path/to/repo
uv run architect-validate-report path/to/report.md
uv run architect-compare-reports base-report.md head-report.md
```

Install locally when you need command names on `PATH`:

```sh
uv tool install --editable .
```

## Packaging and compile notes

The hand-edited source of truth is under `src/`: role prompts, skills, templates, plugin metadata, and helper CLIs. `make build` compiles runtime artifacts into:

```text
.claude-plugin/marketplace.json      # Claude marketplace → ./dist/claude/plugins/*
.agents/plugins/marketplace.json     # Codex marketplace → ./dist/codex/plugins/*
package.json                         # Pi package manifest → ./dist/pi/skills
dist/claude/plugins/architecture/    # Claude plugin root
dist/codex/plugins/architecture/     # Codex plugin root, skills only
dist/codex/agents/architect.toml     # Codex custom agent TOML
dist/pi/{skills,agents,templates}/   # Pi flat package tree
```

Generated runtime artifacts are committed. Edit `src/`, then run `make build`, then commit source and generated output together. `make check` fails when generated artifacts drift.

Rules:

- Keep target-specific generated output out of source directories.
- Keep user install instructions in `README.md` focused on GitHub marketplace/plugin/extension install paths.
- Keep build, compile, validation, and drift-check instructions in this file.
- Do not duplicate score dimensions, report schema, or tool registry in prose when a source contract already exists.

## Documentation rules

- README is for users: what the package does, how to install it, and where to read more.
- CONTRIBUTING is for maintainers: setup, compile/package work, tests, validation, release mechanics.
- Docs under `docs/` explain methodology, report contracts, scoring, and tool coverage.
- Source templates and `src/templates/scorecard.yaml` win when prose docs disagree.
