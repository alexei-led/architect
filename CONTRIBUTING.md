# Contributing

Development notes for `architect`. User install instructions live in [README.md](README.md).

## Requirements

- Python 3.12+
- `uv`
- `make`
- Optional: `markdownlint-cli2` for Markdown linting

## Setup

```sh
make setup
```

This installs development dependencies with `uv` and points Git hooks at `scripts/git-hooks/`.

## Local checks

```sh
make lint               # instruction lint + ruff check + ruff format --check
make lint-instructions  # agent and skill instruction checks only
make test               # pytest
make check              # lint + tests
```

Run `make check` before sending changes. For README or docs-only edits, also run:

```sh
markdownlint-cli2 README.md CONTRIBUTING.md docs/*.md
```

If `markdownlint-cli2` is not installed, state that in the change notes.

## Skill evals

Paid Agent Skills evals read `OPENAI_API_KEY` from the environment or local `.env`.
The `.env` file is ignored and must not be committed.

```sh
make skill-evals-prepare  # build /tmp/architect-skill-eval-root from src/skills + fixtures
make skill-evals          # run evals with baseline and HTML report
make skill-evals-fast     # no baseline, no HTML report, advisory exit
make skill-evals-summary  # summarize latest workspace
```

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

The hand-edited source of truth is under `src/`: role prompts, skills, templates, plugin metadata, and helper CLIs. Generated target artifacts are not committed here.

When adding runtime-native packaging:

- Keep target-specific generated output out of source directories.
- Keep user install instructions in `README.md` focused on GitHub marketplace/plugin/extension install paths.
- Keep build, compile, validation, and drift-check instructions in this file.
- Do not duplicate score dimensions, report schema, or tool registry in prose when a source contract already exists.

## Documentation rules

- README is for users: what the package does, how to install it, and where to read more.
- CONTRIBUTING is for maintainers: setup, compile/package work, tests, validation, release mechanics.
- Docs under `docs/` explain methodology, report contracts, scoring, and tool coverage.
- Source templates and `src/templates/scorecard.yaml` win when prose docs disagree.
