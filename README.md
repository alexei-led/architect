# architect

[![CI](https://github.com/alexei-led/architect/actions/workflows/ci.yml/badge.svg)](https://github.com/alexei-led/architect/actions/workflows/ci.yml)
[![Version](https://img.shields.io/github/v/tag/alexei-led/architect?label=version&sort=semver)](https://github.com/alexei-led/architect/tags)
[![License](https://img.shields.io/github/license/alexei-led/architect)](LICENSE)
[![AI agents](https://img.shields.io/badge/AI%20agents-Claude%20Code%20%C2%B7%20Codex%20CLI%20%C2%B7%20Pi-111827)](#install)
[![Method](https://img.shields.io/badge/method-Balanced%20Coupling-0f766e)](docs/methodology.md)
[![Mode](https://img.shields.io/badge/reviews-read--only-2563eb)](docs/methodology.md)

Read-only architecture review and design for AI coding agents.

`architect` gives Claude Code, Codex CLI, and Pi a disciplined Architect role for:

- comparing intended vs observed architecture
- judging coupling with **Balanced Coupling**
- scoring with explicit evidence and confidence
- designing target boundaries, contracts, and fitness checks
- turning approved designs into executable refactor plans

It does not edit production code during review.

## Why AI developers use it

- **Read-only during audit** — review first, then hand off implementation.
- **Evidence first** — findings cite files, commands, or graph queries.
- **Balanced Coupling, not cargo-cult decoupling** — strength, distance, volatility.
- **Repeatable outputs** — report, design, and plan templates with validation.
- **Useful triage mode** — quick sweeps across several repos before deeper review.

## What you get

- `architecture` plugin/package
- Architect agent role
- skills for review, design, planning, scoring, methodology, and evidence gathering
- report, design, and plan templates
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

## Quick start

### Review one repo

```text
Review this repo's architecture. Find coupling problems, boundary violations, and testability risks.
```

### Compare several repos quickly

```text
Compare these repos with a quick architecture sweep. Name likely hotspots and next checks, but do not score them yet.
```

### Design a target architecture

```text
Design a target architecture for this service based on the current code and docs.
```

### Plan an incremental refactor

```text
Turn this approved architecture into an incremental implementation plan.
```

## Typical flows

- existing codebase: `architecture-review` → `architecture-design` → `architecture-plan`
- greenfield or requirements: `architecture-design`
- approved design, need sequencing: `architecture-plan`
- audit only: `architecture-review`
- multi-repo sample or triage: `architecture-review` quick sweep, then a full review only where the sweep finds real candidates

## CLI tools

```sh
architect-doctor --repo /path/to/repo
architect-validate-report path/to/report.md
architect-compare-reports base-report.md head-report.md
```

`architect-doctor` reports which local analysis tools are available and where coverage is missing.

## Read next

- [Methodology](docs/methodology.md)
- [Scoring](docs/scoring.md)
- [Report format](docs/report-format.md)
- [Tools](docs/tools.md)
- [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE)
