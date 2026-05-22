---
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: ts-tangled-baseline
date: 2026-05-22

target:
  repo: tests/fixtures/repos/ts-tangled
  scope: full
  out_of_scope: []

comparability:
  scope: full
  rubric_version: 1
  tool_coverage_level: standard

interview_context:
  system_goal: The degraded twin of ts-healthy, used as the unhealthy paired fixture.
  quality_goals:
    - change locality
    - testability
  intended_units:
    - domain
    - infra
  domains:
    core:
      - domain
    supporting: []
    generic:
      - infra
  volatile_areas:
    - order
  team_ownership:
    - fixture maintainer
  known_pain:
    - order and gateway leak into each other
  review_scope: full
  out_of_scope: []

system_map:
  languages:
    - typescript
  package_managers:
    - npm
  units:
    - order
    - gateway
  deploy_units:
    - single library
  public_interfaces:
    - none published
  declared_modules:
    - order (domain)
    - gateway (infra)
  observed_modules:
    - order+gateway fused cycle
  high_risk_entrypoints:
    - place function
  missing_evidence:
    - no git history shipped; churn not measurable

scores:
  boundary_integrity:
    value: 30
    band: poor
    confidence: high
    evidence_refs:
      - E2
      - E3
    gaps: []
  coupling_balance:
    value: 28
    band: poor
    confidence: high
    evidence_refs:
      - E3
    gaps: []
  dependency_graph_health:
    value: 25
    band: poor
    confidence: high
    evidence_refs:
      - E1
      - E2
    gaps: []
  cohesion_modularity:
    value: 38
    band: poor
    confidence: medium
    evidence_refs:
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
    value: 30
    band: poor
    confidence: medium
    evidence_refs:
      - E5
    gaps: []
  analysis_confidence:
    value: 72
    band: serviceable
    confidence: high
    evidence_refs:
      - E2
      - E3
    gaps:
      - no churn history

findings:
  - id: F1
    title: Import cycle between order and gateway
    severity: high
    dimension: dependency_graph_health
    evidence_refs:
      - E1
      - E2
    recommended_action: Break the cycle by having the domain expose an event the gateway subscribes to, instead of importing it.
  - id: F2
    title: Gateway reaches into a private domain internal
    severity: high
    dimension: boundary_integrity
    evidence_refs:
      - E3
    recommended_action: Publish a domain function and have the gateway call it; stop importing _applyTax.
  - id: F3
    title: Intrusive low-distance coupling between order and gateway
    severity: high
    dimension: coupling_balance
    evidence_refs:
      - E3
    recommended_action: Replace the private-internal import with an explicit, stable interface.
  - id: F4
    title: Gateway is a god module mixing transport, persistence, and tax math
    severity: medium
    dimension: cohesion_modularity
    evidence_refs:
      - E4
    recommended_action: Split transport, persistence, and pricing into separate modules.
  - id: F5
    title: No executable check enforces the intended boundaries
    severity: medium
    dimension: architecture_fitness
    evidence_refs:
      - E5
    recommended_action: Add a dependency-cruiser no-circular rule and wire it into CI.

evidence:
  - id: E1
    type: file
    ref: tests/fixtures/repos/ts-tangled/src/order.ts:1-2
    summary: Domain module order.ts imports gateway.ts; gateway.ts imports order.ts back.
  - id: E2
    type: command
    command: depcruise src --config .dependency-cruiser.cjs
    summary: Reports a circular dependency order <-> gateway and a cross-layer violation.
  - id: E3
    type: file
    ref: tests/fixtures/repos/ts-tangled/src/gateway.ts:4-5
    summary: Gateway imports the private _applyTax internal from the domain instead of a published API.
  - id: E4
    type: file
    ref: tests/fixtures/repos/ts-tangled/src/gateway.ts:1-22
    summary: One file owns transport (notifyPlaced), persistence (persist), and pricing (quote).
  - id: E5
    type: file
    ref: tests/fixtures/repos/ts-tangled/package.json:6-8
    summary: A depcruise script exists but no rule and no CI invocation enforce boundaries.
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

# Architecture report: ts-tangled

## Executive summary

ts-tangled is the degraded twin of ts-healthy and scores poorly for concrete,
cited reasons: a two-node import cycle, an infra module reaching into a private
domain internal, and a god module mixing three concerns. Structure and coupling
evidence is direct and high-confidence; only change locality is unmeasurable.

## Interview context

The maintainer already reports that order and gateway leak into each other. Core
domain is `order`; full scope.

## System map

Two declared modules (order = domain, gateway = infra). The observed graph fuses
them into one cycle — the declared layering does not hold.

## Intended architecture

domain (`order`) should be a leaf; infra (`gateway`) should depend on a published
domain API. Neither holds.

## Observed architecture

order imports gateway and gateway imports order (E1), a cycle confirmed by
dependency-cruiser (E2). gateway imports the private `_applyTax` (E3) and mixes
three responsibilities (E4).

## Score map

- boundary_integrity 30 (poor, high): private internal imported across the layer.
- coupling_balance 28 (poor, high): intrusive, low-distance coupling.
- dependency_graph_health 25 (poor, high): a confirmed cycle.
- cohesion_modularity 38 (poor, medium): god module.
- architecture_fitness 30 (poor, medium): no check enforces boundaries.
- change_locality 55 (mixed, low): no history to measure.

## Key findings

- F1 (high): Import cycle between order and gateway.
- F2 (high): Gateway reaches into a private domain internal.
- F3 (high): Intrusive low-distance coupling.
- F4 (medium): Gateway is a god module.
- F5 (medium): No executable boundary check.

## Coupling review

order<->gateway is intrusive strength (private internal), low distance (same
package), high volatility (order is core and changes often). High strength +
high volatility is the priority even at low distance.

## Boundary violations

F2: `gateway.ts` imports `_applyTax` from `order.ts` (E3).

## Change locality and hotspots

Not measurable: the fixture ships without git history (E6). Recorded as a
medium-impact coverage gap.

## Recommendations

Break the cycle (F1), invert the private-internal import behind a published API
(F2/F3), split the god module (F4), and add a no-circular check wired into CI
(F5). All incremental; no rewrite warranted.

## Evidence appendix

E1-E6 above; each re-checkable via the listed file range or command.

## Tool coverage and gaps

Discovery, structural, and dependency fully covered. Change skipped — no git
history (medium impact). Semantic not applicable to a two-file library.
