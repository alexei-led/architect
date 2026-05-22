---
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: ts-healthy-baseline
date: 2026-05-22

target:
  repo: tests/fixtures/repos/ts-healthy
  scope: full
  out_of_scope: []

comparability:
  scope: full
  rubric_version: 1
  tool_coverage_level: standard

interview_context:
  system_goal: A small order service used as the healthy paired fixture.
  quality_goals:
    - change locality
    - testability
  intended_units:
    - domain
    - app
    - infra
  domains:
    core:
      - domain
    supporting:
      - app
    generic:
      - infra
  volatile_areas:
    - app
  team_ownership:
    - fixture maintainer
  known_pain: []
  review_scope: full
  out_of_scope: []

system_map:
  languages:
    - typescript
  package_managers:
    - npm
  units:
    - domain
    - app
    - infra
  deploy_units:
    - single library
  public_interfaces:
    - OrderRepository port
  declared_modules:
    - domain
    - app
    - infra
  observed_modules:
    - domain (leaf)
    - app (depends on domain)
    - infra (implements domain port)
  high_risk_entrypoints:
    - placeOrder use-case
  missing_evidence:
    - no git history shipped; churn not measurable

scores:
  boundary_integrity:
    value: 85
    band: strong
    confidence: high
    evidence_refs:
      - E1
      - E2
    gaps: []
  coupling_balance:
    value: 82
    band: strong
    confidence: high
    evidence_refs:
      - E2
      - E3
    gaps: []
  dependency_graph_health:
    value: 88
    band: strong
    confidence: high
    evidence_refs:
      - E2
    gaps: []
  cohesion_modularity:
    value: 80
    band: serviceable
    confidence: high
    evidence_refs:
      - E3
      - E4
    gaps: []
  change_locality:
    value: 55
    band: mixed
    confidence: low
    evidence_refs:
      - E6
    gaps:
      - no git history shipped; churn not measurable
  architecture_fitness:
    value: 55
    band: mixed
    confidence: medium
    evidence_refs:
      - E5
    gaps:
      - depcruise config present but not wired into CI
  analysis_confidence:
    value: 72
    band: serviceable
    confidence: high
    evidence_refs:
      - E2
      - E5
    gaps:
      - no semantic call graph; no churn history

findings:
  - id: F1
    title: Architecture intent not yet enforced in CI
    severity: low
    dimension: architecture_fitness
    evidence_refs:
      - E5
    recommended_action: Wire the dependency-cruiser rule into CI so the inward dependency direction stays enforced.

evidence:
  - id: E1
    type: file
    ref: tests/fixtures/repos/ts-healthy/src/domain/repository.ts:1-9
    summary: Domain declares the OrderRepository port; infra implements it, so the dependency points inward.
  - id: E2
    type: command
    command: depcruise src --config .dependency-cruiser.cjs
    summary: No cycles and no cross-layer violations; infra->app->domain only.
  - id: E3
    type: file
    ref: tests/fixtures/repos/ts-healthy/src/app/place-order.ts:1-9
    summary: Use-case imports domain types and the port only; no infra import.
  - id: E4
    type: file
    ref: tests/fixtures/repos/ts-healthy/src/infra/memory-repository.ts:1-18
    summary: Adapter implements the domain port; not referenced by domain or app.
  - id: E5
    type: file
    ref: tests/fixtures/repos/ts-healthy/package.json:6-8
    summary: A depcruise script exists but is not invoked by any CI workflow.
  - id: E6
    type: interview
    summary: Fixture ships without git history by design; change locality cannot be measured from churn.

tool_coverage:
  - dimension: discovery
    tools_used:
      - fd
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
      - dependency-cruiser
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
  - dimension: change
    tools_used: []
    tools_skipped: []
    tools_missing:
      - git
    tools_failed: []
    confidence_impact: medium
---

# Architecture report: ts-healthy

## Executive summary

ts-healthy is a clean layered TypeScript service: dependencies point strictly
inward (infra->app->domain) with no cycles. It scores strong on structure and
coupling. The one gap is fitness — the dependency rule exists but is not enforced
in CI — and change locality is unmeasurable because the fixture ships no git
history.

## Interview context

A fixture standing in for a healthy order service. Core domain is `domain`; the
volatile area is the `app` use-case layer. Full scope, nothing excluded.

## System map

Single TypeScript library, three declared modules (domain, app, infra). The
observed import graph matches: domain is a leaf, app depends on domain, infra
implements a domain-owned port.

## Intended architecture

Inward dependency direction with domain at the center. The `OrderRepository`
port is owned by the domain and implemented by infra (E1).

## Observed architecture

dependency-cruiser reports zero violations and zero cycles (E2). app imports
only domain (E3); infra is referenced by no inner layer (E4).

## Score map

- boundary_integrity 85 (strong, high): port owned inward, no leaks.
- coupling_balance 82 (strong, high): explicit, low-strength integration.
- dependency_graph_health 88 (strong, high): no cycles.
- architecture_fitness 55 (mixed, medium): rule exists, not in CI.
- change_locality 55 (mixed, low): no history to measure.

## Key findings

- F1 (low): Architecture intent not yet enforced in CI.

## Coupling review

app->domain and infra->domain are explicit, low-strength, low-distance
integrations against stable domain types. Balanced: nothing to decouple.

## Boundary violations

None observed (E2).

## Change locality and hotspots

Not measurable: the fixture ships without git history (E6). Recorded as a
medium-impact coverage gap.

## Recommendations

Wire the dependency-cruiser rule into CI (F1) to keep the inward direction
enforced as the code grows. No structural change warranted.

## Evidence appendix

E1-E6 above; each re-checkable via the listed file range or command.

## Tool coverage and gaps

Discovery, structural, and dependency fully covered. Change skipped — no git
history (medium impact). Semantic not applicable to a three-file library.
