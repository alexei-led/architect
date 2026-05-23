# architect

Instruction-first architecture review for AI coding agents.

`architect` packages a read-only Architect role, portable Agent Skills, report and plan templates, and helper CLIs for evidence-based architecture review. It is built for Claude Code, Codex CLI, Pi, and other runtimes that can load Agent Skills-style capabilities.

The Architect does not rewrite systems. It establishes intended architecture, maps observed structure, gathers local evidence, scores architecture quality with confidence, and returns a cited report plus an optional incremental refactoring plan.

## Install

Install from GitHub through your runtime's plugin, marketplace, or package mechanism.

### Claude Code

```sh
/plugin marketplace add alexei-led/architect
/plugin install architecture@architect
```

Use `--scope project` if you want the plugin recorded in project settings.

### Codex CLI

Open Codex and install from the plugin marketplace:

```text
/plugins → Add marketplace → https://github.com/alexei-led/architect → install architecture
```

Equivalent config form:

```toml
[marketplaces.alexei-led-architect]
source_type = "git"
source = "https://github.com/alexei-led/architect.git"

[plugins."architecture@alexei-led-architect"]
enabled = true
```

Restart Codex after changing plugin configuration.

### Pi

```sh
pi install git:github.com/alexei-led/architect
```

Use project scope when the architecture-review package should travel with a repository:

```sh
pi install -l git:github.com/alexei-led/architect
```

Restart Pi or run `/reload` after installing.

### Helper CLIs

The Python CLIs can be installed directly from GitHub:

```sh
uv tool install git+https://github.com/alexei-led/architect.git
```

Then run:

```sh
architect-doctor --repo /path/to/repo
architect-validate-report path/to/report.md
architect-compare-reports base-report.md head-report.md
```

## What it contains

- One architecture-review plugin named `architecture`.
- A read-only Architect role for assessment and planning, not implementation.
- Review, scorecard, and planning skills for the core workflow.
- Methodology skills for Balanced Coupling and architecture fitness functions.
- Tool skills that guide evidence collection with local OSS CLIs.
- Report and plan templates with machine-checkable contracts.
- Helper CLIs for tool coverage checks, report validation, and report comparison.

## What it does

A full review follows this order:

1. Capture intended architecture and constraints from the user, docs, ADRs, manifests, and config.
2. Build a system map before judging quality.
3. Gather evidence across discovery, structural, semantic, dependency, change, operational, security, and report dimensions.
4. Score architecture dimensions with a fixed rubric and explicit confidence.
5. Write an architecture report with addressable evidence references.
6. Optionally write an incremental refactoring plan tied to findings and verification checks.

Hard boundaries:

- No source edits by the Architect.
- No finding without evidence.
- No score before the system map.
- No high-quality score on low-confidence evidence.
- No big-bang rewrite plans.

## Tools

`architect-doctor` checks whether useful local analysis tools are available and records gaps as coverage limits, not fatal errors. The skills guide the agent across these tool families:

- Discovery and change: `fd`, `rg`, `git`, GitNexus.
- Structural search: `ast-grep`, language linters.
- Semantic analysis: codegraph, LSP/tree-sitter, type checkers, static analyzers.
- Dependency graphs: dependency-cruiser, madge, knip, import-linter, pydeps, deptry, goda.
- Operational and security evidence: Helm, Kustomize, Terraform, govulncheck, Trivy, Syft.
- Report support: `jq`, `yq`, Mermaid CLI.

Missing tools lower confidence and are recorded in report tool coverage. They do not justify pretending the evidence exists.

## Methodology

The review is built around two explicit models:

- **Balanced Coupling** — Vlad Khononov's model of integration strength, distance, and volatility. Coupling is not automatically bad; unbalanced coupling is. See [coupling.dev](https://coupling.dev/) and _Balancing Coupling in Software Design_. This project summarizes the model with attribution and does not copy source material.
- **Architecture fitness functions** — from Neal Ford and _Building Evolutionary Architectures_: architectural intent should be executable checks that can fail a build. Documentation alone does not raise the fitness score.

Domain volatility uses DDD-style core/supporting/generic distinctions when judging change risk. Recommendations favor seams, characterization tests, boundary repair, and fitness checks over cosmetic reshuffling.

## Docs

- [Methodology](docs/methodology.md) — Balanced Coupling and architecture fitness summaries.
- [Scoring](docs/scoring.md) — score dimensions, bands, confidence, and comparability.
- [Report and plan format](docs/report-format.md) — report frontmatter, evidence refs, tool coverage, and plan sections.
- [Tools and coverage](docs/tools.md) — tool registry, applicability, and confidence impact.
- [Contributing](CONTRIBUTING.md) — maintainer setup, packaging notes, tests, and validation.

The source templates and scorecard are the contract. If prose docs and templates disagree, templates win.

## License

[MIT](LICENSE)
