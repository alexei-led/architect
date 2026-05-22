# Refactoring plan: ts-tangled order/gateway boundary

Derived from report `ts-tangled-baseline`, findings F1-F5. One boundary per
plan: the fused order/gateway cycle. Incremental throughout — no rewrite.

## Overview

`order` and `gateway` import each other (F1), the gateway reaches into a private
domain internal (F2/F3), and the gateway mixes three concerns (F4) with no check
to hold the line (F5). This plan breaks the cycle, publishes a stable seam,
splits the module, and makes the boundary executable. Source report:
`ts-tangled-baseline`.

## Success criteria

- [ ] `order.ts` no longer imports `gateway.ts` (closes F1).
- [ ] `gateway.ts` no longer imports `_applyTax` (closes F2/F3).
- [ ] Transport, persistence, and pricing live in separate modules (closes F4).
- [ ] A dependency-cruiser no-circular rule fails CI on a reintroduced cycle
      (closes F5).

## Phases

### Phase 1: Break the order/gateway cycle

Justification: F1 / evidence E1-E2 — `order.ts:1-2` imports `gateway.ts`, which
imports back; dependency-cruiser confirms the cycle.

Preconditions: A characterization test covers `place` behavior.
Postconditions: `order` is a leaf again; the gateway reacts to a domain event.

- [ ] Add a characterization test for `place` against current behavior (E1).
- [ ] Have the domain return a "placed" result instead of calling `notifyPlaced` (F1).
- [ ] Move the notify call into the caller/gateway side of the seam (F1).

Verification:

- [ ] `depcruise src` reports no circular dependency.
- [ ] Characterization test still passes.

### Phase 2: Publish a domain API and split the gateway

Justification: F2/F3/F4 / evidence E3-E4 — gateway imports private `_applyTax`
and mixes transport, persistence, and pricing.

Preconditions: Phase 1 merged.
Postconditions: Gateway calls a published `orderTotal`/`quote` API; transport,
persistence, and pricing are separate modules.

- [ ] Export a stable pricing function from the domain; delete the `_applyTax`
      re-export (F2/F3).
- [ ] Split `gateway.ts` into `transport`, `persistence`, and `pricing` (F4).

Verification:

- [ ] `ast-grep` finds no import of `_applyTax` outside the domain.
- [ ] Characterization test still passes.

### Phase 3: Make the boundary executable

Justification: F5 / evidence E5 — no rule or CI invocation enforces boundaries.

Preconditions: Phases 1-2 merged.
Postconditions: A reintroduced cycle or cross-layer import fails CI.

- [ ] Add a `.dependency-cruiser.cjs` no-circular and no-cross-layer rule (F5).
- [ ] Wire `depcruise` into CI (F5).

Verification:

- [ ] CI fails when a cycle is reintroduced on a scratch branch.

## Acceptance criteria

- [ ] All success criteria met.
- [ ] No module was rewritten from scratch; changes are incremental and each
      phase is independently verifiable.

## Safety notes

- Each phase ships behind a passing characterization test.
- No behavior change intended; pricing math is preserved, only relocated.
