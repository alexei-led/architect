# architect

[![CI](https://github.com/alexei-led/architect/actions/workflows/ci.yml/badge.svg)](https://github.com/alexei-led/architect/actions/workflows/ci.yml)
[![Version](https://img.shields.io/github/v/tag/alexei-led/architect?label=version&sort=semver)](https://github.com/alexei-led/architect/tags)
[![License](https://img.shields.io/github/license/alexei-led/architect)](LICENSE)
[![AI agents](https://img.shields.io/badge/AI%20agents-6%20targets-111827)](#install)
[![Method](https://img.shields.io/badge/method-Balanced%20Coupling-0f766e)](docs/methodology.md)
[![Mode](https://img.shields.io/badge/reviews-read--only-2563eb)](docs/methodology.md)

<p align="center">
  <img src="https://raw.githubusercontent.com/alexei-led/architect/master/assets/architect-card.png" alt="Architect extension card" width="160" height="100">
</p>

Read-only architecture review and design for AI coding agents.

`architect` packages its architecture skills for Claude Code, Codex CLI, Pi,
GitHub Copilot, Grok Build, and Cursor. Claude, Codex, Pi, GitHub Copilot, and Cursor also get the disciplined
Architect role for:

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
- **Deterministic-tool calibration** — when archfit is available, use its hard facts without outsourcing judgment.
- **Useful triage mode** — quick sweeps across several repos before deeper review.

## What you get

- `architecture` plugin/package
- Architect agent role
- skills for review, design, planning, scoring, methodology, and evidence gathering
- report, design, and plan templates
- helper CLIs: `architect-doctor`, `architect-validate-report`, `architect-compare-reports`
- optional `tools-archfit` workflow for calibrated archfit scorecards, JSON findings, deltas, and agent tasks

## Install

Local package development requires `agbun` on `PATH`. It is not installed by
this repository; verify it with `agbun --version` before running `make build` or
`make generated-check`. GitHub Actions runs CI-safe Ruff, pytest, and npm tarball
checks; generated-package builds and drift checks stay local.

### Claude Code

The repository marketplace installs the lean npm plugin payload.

```sh
claude plugin marketplace add alexei-led/architect
claude plugin install architecture@alexei-led-architect
```

The generated Architect agent requests Claude Fable 5 at `xhigh` effort. Claude
Code uses the inherited model instead when an organization allowlist excludes
the requested model.

### Codex CLI

```sh
codex plugin marketplace add alexei-led/architect
codex plugin add architecture@alexei-led-architect
```

The generated Codex package includes `agents/architect.toml`. Copy it into
`~/.codex/agents/` or `.codex/agents/` if you want subagent spawning.

### Pi

The Architect role is a [`pi-subagents`](https://github.com/nicobailon/pi-subagents)
agent. The npm package declares that runtime dependency.

```sh
pi install npm:@alexeiled/architect
```

For local development:

```sh
make build
pi install -l .
```

Pi discovers the registered `architect` subagent. Ask it to design or review
architecture, or run it directly with `/run architect <task>`.

### GitHub Copilot

```sh
copilot plugin marketplace add alexei-led/architect
copilot plugin install architecture@alexei-led-architect
```

The generated Architect agent requests `MAI-Code-1-Flash`; availability depends
on the organization's Copilot model policy.

For local development, build then install `dist/copilot` as a local Copilot plugin.

### Grok Build

Grok Build accepts the Claude-compatible package, including the Architect role:

```sh
grok plugin install --trust alexei-led/architect#dist/claude
```

For project-local skills only, copy `dist/grok/.grok/` into the consumer project.

### Cursor

Install from the repository marketplace or load the generated local package:

```sh
make build
cursor-agent --plugin-dir "$PWD/dist/cursor"
```

The generated package includes the Architect agent, all skills, templates, and
a `README.md`.

Grok receives all architecture skills and shared templates through its project
tree; use the Claude-compatible package when the Architect role is required.

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
If `archfit` and `.archfit.yaml` are present, architecture reviews can start from
archfit's deterministic scorecard, JSON findings, delta output, and `agent_tasks`,
then verify and calibrate them against code, intent, and runtime/deploy context.

## Read next

- [Methodology](docs/methodology.md)
- [Scoring](docs/scoring.md)
- [Report format](docs/report-format.md)
- [Tools](docs/tools.md)
- [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE)
