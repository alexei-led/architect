# architect

Architecture review and design package for AI coding agents.

`architect` gives an agent a read-only Architect role for reviewing an existing codebase, designing a target architecture, or turning an approved design into an implementation plan. It works with Claude Code, Codex CLI, and Pi.

## What it does

Use it to:

- review architecture with cited evidence
- judge coupling with **Balanced Coupling**: integration strength, distance, and volatility
- score architecture quality with explicit confidence
- design target architecture from requirements or existing code
- produce an incremental refactor plan

It does not edit production code.

## What’s included

- `architecture` plugin/package
- Architect agent role
- skills for review, design, planning, scoring, and evidence gathering
- report and plan templates
- helper CLIs: `architect-doctor`, `architect-validate-report`, `architect-compare-reports`

## Install

### Claude Code

```sh
/plugin marketplace add alexei-led/architect
/plugin install architecture@architect
```

### Codex CLI

```sh
codex plugin marketplace add alexei-led/architect
codex plugin add architecture@alexei-led-architect
```

Optional custom agent file:

```text
dist/codex/agents/architect.toml
```

Copy or symlink it into `~/.codex/agents/` or `.codex/agents/` if you want subagent spawning.

### Pi

```sh
pi install git:github.com/alexei-led/architect
```

Project-local install:

```sh
pi install -l git:github.com/alexei-led/architect
```

### Helper CLIs

```sh
uv tool install git+https://github.com/alexei-led/architect.git
```

## Use

Typical flows:

- existing codebase: `architecture-review` → `architecture-design` → `architecture-plan`
- greenfield or requirements: `architecture-design`
- approved design, need sequencing: `architecture-plan`
- audit only: `architecture-review`
- multi-repo sample or triage: `architecture-review` quick sweep, then a full review only where the sweep finds real candidates

Example prompts:

- `Review this repo's architecture. Find coupling problems, boundary violations, and testability risks.`
- `Compare these three repos with a quick architecture sweep. Name likely hotspots and the next checks, but do not score them yet.`
- `Design a target architecture for this service based on the current code and docs.`
- `Turn this approved architecture into an incremental implementation plan.`

## CLI tools

```sh
architect-doctor --repo /path/to/repo
architect-validate-report path/to/report.md
architect-compare-reports base-report.md head-report.md
```

`architect-doctor` reports which local analysis tools are available and where coverage is missing.

## Docs

- [Methodology](docs/methodology.md)
- [Scoring](docs/scoring.md)
- [Report format](docs/report-format.md)
- [Tools](docs/tools.md)
- [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE)
