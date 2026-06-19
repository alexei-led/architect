# Changelog

All notable changes to `architect` are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
major = breaking instruction/report contracts, minor = new skills or tooling,
patch = fixes and documentation updates.

## [Unreleased]

## [0.4.0] - 2026-06-19

### Architecture review workflow

- Added a quick-sweep review mode for multi-repo or low-budget comparisons that returns evidence-backed candidates, next checks, and an explicit quality self-check instead of forcing partial scores.
- Tightened review guidance so `coupling_balance` is grounded in per-relationship records: strength, distance, volatility, evidence, severity, and balancing move.
- Clarified that nonzero exits from analysis tools can be confirmed findings rather than tool failures.

### Methodology and documentation

- Aligned README, methodology, scoring, report-format, and tools docs with Balanced Coupling terminology and the current review workflow.
- Documented the distance split used in reviews: code, ownership, runtime, and deploy distance.
- Clarified domain volatility versus implementation/provider volatility and how quick sweeps differ from full reviews.

### Tooling

- Expanded `architect-doctor` coverage for newly supported analysis, operational, and security tools including `tree-sitter`, `basedpyright`, `pipdeptree`, `radon`, `lizard`, `kubeconform`, `kube-linter`, `hadolint`, `actionlint`, `tflint`, `tofu`, `conftest`, `grype`, `tfsec`, and `zizmor`.
- Improved repo applicability detection for Docker, GitHub Actions, recursive Terraform markers, and Kubernetes manifests.
- Updated release automation to bump `src/architect_tools/__init__.py` version during tagged releases.

## [0.3.2] - 2026-06-06

### Skill instructions

- Tightened architecture skill write-safety, runtime-tool, scoped validation, and package-runner guidance.

## [0.3.1] - 2026-05-24

### Plugin marketplace metadata

- Fixed Claude Code marketplace metadata to satisfy the current manifest schema.
- Updated Codex marketplace and plugin metadata for current plugin installation and UI surfaces.

## [0.3.0] - 2026-05-23

### Architecture workflow

- Added conditional next-skill routing for architecture review, design, and plan flows.
- Made architecture plans task-runner executable with implementation steps, per-task file lists, GitNexus impact checks, concrete verification commands, manual checks, and final verification/documentation handoff.
- Added regression tests for the executable plan-template contract.

## [0.2.1] - 2026-05-23

### Architecture design

- Added `architecture-design` for requirements-to-architecture work, including module maps, integration contracts, module test specifications, fitness checks, self-review, and skill-flow handoff.
- Added `src/templates/design.md` for target architecture artifacts.

### Review and reporting

- Added Mermaid guidance for human-facing reports while keeping AI-targeted reports plain text.
- Added skill navigation and outcome-based task-list discipline to design/review/plan flows.
- Strengthened architecture-review with working-model validation, stale-doc suspicion, and human-facing finding narratives.
- Expanded Balanced Coupling guidance with the balance-rule mnemonic, examples, generic-provider volatility, and connascence tie-breakers.
- Extended architecture-plan to sequence work from approved design artifacts as well as review findings.

## [0.2.0] - 2026-05-23

### Architecture-review routing

- Added `tools-code-search` for local `fd`/`rg`/`git grep` discovery and targeted read evidence.
- Tightened architecture-review and tool skill descriptions around modularity, coupling, dependency direction, blast radius, and fragility.
- Added evidence-output contracts to tool skills for repeatable architecture-report evidence collection.

### Runtime packaging

- Included `tools-code-search` in Claude, Codex, and Pi runtime plugin artifacts.
- Clarified tool coverage docs for discovery, generated/vendor scope, and specialized-tool handoff.
- Fixed brittle shell quoting in the code-search import/dependency search example.
- Removed obsolete `.gitkeep` files from populated template directories.

## [0.1.0] - 2026-05-23

### Added

- Initial architecture-review package with a read-only Architect role.
- Review, scorecard, planning, methodology, and tool-focused Agent Skills.
- Report, plan, and scorecard templates with validation helpers.
- Local CI targets, Git hooks, Gitleaks scanning, and GitHub Actions workflows.
