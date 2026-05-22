---
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: ccgram-2026-05-22
date: 2026-05-22

target:
  repo: ccgram
  scope: full
  out_of_scope:
    - vendored third-party code under vendor/

comparability:
  scope: full
  rubric_version: 1
  tool_coverage_level: standard

interview_context:
  system_goal: Bridge tmux Claude sessions to Telegram for inter-agent messaging.
  quality_goals:
    - change locality
    - testability
  intended_units:
    - bot gateway
    - session registry
    - message router
  domains:
    core:
      - message router
    supporting:
      - session registry
    generic:
      - telegram transport
  volatile_areas:
    - message router
  team_ownership:
    - solo maintainer
  known_pain:
    - router and transport leak into each other
  review_scope: full
  out_of_scope:
    - vendored third-party code under vendor/

system_map:
  languages:
    - python
  package_managers:
    - uv
  units:
    - gateway service
    - router library
  deploy_units:
    - single long-running process
  public_interfaces:
    - telegram webhook
    - tmux control socket
  declared_modules:
    - ccgram.gateway
    - ccgram.router
    - ccgram.registry
  observed_modules:
    - gateway+router fused cluster
    - registry
  high_risk_entrypoints:
    - webhook handler
  missing_evidence:
    - no call graph; gopls/LSP not applicable to single-language repo gaps

scores:
  boundary_integrity:
    value: 48
    band: mixed
    confidence: medium
    evidence_refs:
      - E1
    gaps:
      - import-linter contracts not yet defined
  coupling_balance:
    value: 52
    band: mixed
    confidence: medium
    evidence_refs:
      - E1
      - E3
    gaps: []
  dependency_graph_health:
    value: 61
    band: serviceable
    confidence: high
    evidence_refs:
      - E2
    gaps: []
  cohesion_modularity:
    value: 55
    band: mixed
    confidence: medium
    evidence_refs:
      - E2
    gaps: []
  change_locality:
    value: 58
    band: mixed
    confidence: medium
    evidence_refs:
      - E4
    gaps:
      - shallow git history limits churn analysis
  architecture_fitness:
    value: 30
    band: poor
    confidence: high
    evidence_refs:
      - E5
    gaps: []
  analysis_confidence:
    value: 68
    band: serviceable
    confidence: high
    evidence_refs:
      - E2
      - E5
    gaps:
      - no semantic call graph

findings:
  - id: F1
    title: Router imports gateway internals directly
    severity: high
    dimension: boundary_integrity
    evidence_refs:
      - E1
    recommended_action: Introduce a router-facing interface and invert the import.
  - id: F2
    title: No executable architecture fitness checks
    severity: medium
    dimension: architecture_fitness
    evidence_refs:
      - E5
    recommended_action: Add import-linter contracts wired into CI.

evidence:
  - id: E1
    type: file
    ref: src/ccgram/router/dispatch.py:12-40
    summary: Router imports gateway._client, a private gateway internal.
  - id: E2
    type: command
    command: pydeps src/ccgram --max-bacon 2 --noshow
    summary: One cluster fuses gateway and router; registry is cleanly separated.
  - id: E3
    type: graph-query
    tool: gitnexus
    query: impact dispatch upstream depth=3
    summary: 6 upstream callers cross the gateway/router boundary.
  - id: E4
    type: command
    command: git log --format= --name-only since=90.days
    summary: Gateway and router files co-change in 70% of commits.
  - id: E5
    type: file
    ref: pyproject.toml:1-40
    summary: No import-linter or architecture test configuration present.

tool_coverage:
  - dimension: discovery
    tools_used:
      - fd
      - git
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
  - dimension: structural
    tools_used:
      - ast-grep
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
  - dimension: dependency
    tools_used:
      - pydeps
    tools_skipped: []
    tools_missing:
      - import-linter
    tools_failed: []
    confidence_impact: low
  - dimension: change
    tools_used:
      - git
    tools_skipped: []
    tools_missing:
      - code-maat
    tools_failed: []
    confidence_impact: low
  - dimension: semantic
    tools_used: []
    tools_skipped:
      - lsp
    tools_missing: []
    tools_failed: []
    confidence_impact: low
---

# Architecture report: ccgram

## Executive summary

ccgram is serviceable on dependency topology but mixed on boundary integrity:
the router and gateway are fused. Architecture intent is not enforced by any
check (poor fitness). Overall confidence is high for structure and dependency
evidence, lower for change history due to shallow git log.

## Interview context

Solo-maintained Telegram bridge. Core domain is the message router; the
maintainer already feels router/transport leakage. In-scope: all first-party
code. Out-of-scope: vendored code.

## System map

Single Python process, uv-managed. Declared modules gateway/router/registry;
observed graph fuses gateway and router into one cluster, registry separate.

## Intended architecture

Interview and directory layout agree on three units. Manifests do not declare
boundaries (no import contracts), so intent is aspirational below the directory
level.

## Observed architecture

pydeps shows gateway and router as one cluster. Router reaches into a private
gateway client (F1).

## Score map

- boundary_integrity 48 (mixed, medium): router→gateway internals.
- dependency_graph_health 61 (serviceable, high): no cycles, one fused cluster.
- architecture_fitness 30 (poor, high): no executable checks.
- analysis_confidence 68 (serviceable, high): structural evidence is direct.

## Key findings

- F1 (high): Router imports gateway internals directly.
- F2 (medium): No executable architecture fitness checks.

## Coupling review

gateway↔router: intrusive strength (private internals), low distance (same
process/package), high volatility (router is core and changes often). High
strength + high volatility is the priority even at low distance.

## Boundary violations

F1: `src/ccgram/router/dispatch.py` imports `gateway._client`.

## Change locality and hotspots

Gateway and router co-change in 70% of recent commits (E4), consistent with the
fused cluster.

## Recommendations

Introduce a router-facing transport interface (invert F1). Add import-linter
contracts and wire them into CI (F2). Incremental; no rewrite warranted.

## Plan summary

See refactoring plan: invert the gateway/router dependency, then add a fitness
contract.

## Evidence appendix

E1–E5 above. Each is re-checkable via the listed file range, command, or graph
query.

## Tool coverage and gaps

Discovery and structural fully covered. Dependency covered by pydeps;
import-linter missing (low impact). Semantic skipped (no call graph). Change
covered by git only; Code Maat missing (low impact).
