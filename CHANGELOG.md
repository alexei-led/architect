# Changelog

All notable changes to `architect` are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
major = breaking instruction/report contracts, minor = new skills or tooling,
patch = fixes and documentation updates.

## [Unreleased]

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
