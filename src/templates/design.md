# Architecture design: REPLACE-target

Plain Markdown. Use for target architecture, module contracts, and test
specifications before implementation. Keep intended design separate from observed
implementation; if code already exists, record where docs and code disagree.

## Overview

REPLACE: purpose, scope, source inputs, and whether this is greenfield design,
target-state redesign, or design repair after a review.

## Source inputs and drift notes

- Requirements: REPLACE.
- Existing docs/ADRs/reports: REPLACE.
- Existing implementation checked: yes/no; REPLACE scope checked.
- Drift risks: REPLACE where documents may not match code or where evidence is
  missing.

## Domain and volatility map

Explain DDD terms on first use: core = differentiating and likely to change;
supporting = necessary but not differentiating; generic = solved problem, with
possible provider/implementation volatility.

| Area    | Classification          | Volatility      | Rationale | Open questions |
| ------- | ----------------------- | --------------- | --------- | -------------- |
| REPLACE | core/supporting/generic | high/medium/low | REPLACE   | REPLACE        |

## Module map

| Module  | Responsibility | Owned knowledge | Public interface | Private internals | Owner/deploy expectation | Change vectors |
| ------- | -------------- | --------------- | ---------------- | ----------------- | ------------------------ | -------------- |
| REPLACE | REPLACE        | REPLACE         | REPLACE          | REPLACE           | REPLACE                  | REPLACE        |

## Integration contracts

For each relationship, define the contract and the Balanced Coupling rationale.

### REPLACE source -> target

- Strength: contract/model/functional/intrusive; REPLACE rationale.
- Distance: REPLACE abstraction, runtime, ownership, and deployment distance.
- Volatility: REPLACE domain and implementation volatility.
- Balanced: yes/no; REPLACE why.
- Contract: REPLACE API/event/schema/interface/published language.
- Knowledge shared: REPLACE what crosses the boundary and what stays private.
- Balancing move: lower strength, lower distance, or accept due to low
  volatility.
- Failure modes: REPLACE compatibility, latency, partial failure, data, security.

## Key flows

For each important user or system flow:

1. REPLACE flow name.
   - Participants: REPLACE.
   - Data/control path: REPLACE.
   - Boundary contracts: REPLACE.
   - Local-change expectation: REPLACE what should change together and what
     should not.

## Module test specifications

### REPLACE module

Behavior tests:

- REPLACE scenario and expected behavior.

Unit tests:

- REPLACE rule/edge case and expected behavior.

Contract tests:

- REPLACE contract and compatibility expectation.

Boundary tests:

- REPLACE invalid input, encapsulation, and leak prevention.

Architecture-fitness checks:

- REPLACE automated boundary/dependency/contract check that should prevent drift.

## Design decisions and trade-offs

- Decision: REPLACE.
  - Chosen because: REPLACE.
  - Alternatives considered: REPLACE.
  - Trade-offs: REPLACE.
  - Revisit when: REPLACE.

## Self-review

Review the design before handoff.

| Issue   | Severity                 | Evidence/rationale | Resolution |
| ------- | ------------------------ | ------------------ | ---------- |
| REPLACE | critical/high/medium/low | REPLACE            | REPLACE    |

## Open risks

- REPLACE unresolved risk, owner, and condition for revisiting.

## Handoff

- Recommended next step: `architecture-plan` when implementation sequencing is
  requested / no next skill when design-only / requirements clarification when
  unresolved choices remain / `architecture-review` after implementation lands.
- Implementation notes: REPLACE.
- Acceptance signals: REPLACE what proves the design has been implemented or
  remains aligned with code.
