# Refactoring plan: ccgram gateway/router boundary

Derived from report `ccgram-2026-05-22`, findings F1 and F2. One boundary per
plan: the fused gateway/router cluster.

## Overview

The router imports a private gateway internal (F1) and no check enforces the
intended boundary (F2). This plan inverts the dependency and makes the boundary
executable. Source report: `ccgram-2026-05-22`.

## Success criteria

- [ ] Router no longer imports `gateway._client` (closes F1).
- [ ] An import-linter contract fails CI on gateway→router internal imports
      (closes F2).

## Phases

### Phase 1: Invert the gateway/router dependency

Justification: F1 / evidence E1 — `src/ccgram/router/dispatch.py:12-40` imports
`gateway._client`.

Preconditions: Characterization test covers current dispatch behavior.
Postconditions: Router depends on a transport interface, not a gateway internal.

- [ ] Add a characterization test for `dispatch` against the current behavior (E1).
- [ ] Define a `Transport` protocol in the router package (F1).
- [ ] Inject the gateway client as a `Transport` implementation at the seam (F1).

Verification:

- [ ] `ast-grep` finds no `gateway._client` import under `src/ccgram/router/`.
- [ ] Characterization test still passes.

### Phase 2: Make the boundary executable

Justification: F2 / evidence E5 — no import contracts in `pyproject.toml`.

Preconditions: Phase 1 merged.
Postconditions: CI fails on the forbidden import.

- [ ] Add an import-linter contract forbidding router→gateway internal imports (F2).
- [ ] Wire `lint-imports` into the CI workflow (F2).

Verification:

- [ ] `lint-imports` passes on the current tree.
- [ ] A deliberately reintroduced bad import makes `lint-imports` fail.

## Acceptance criteria

- [ ] Both success criteria met.
- [ ] No production behavior change beyond the dependency inversion.
- [ ] Fitness contract is green in CI.

## Safety notes

No elevated risk. Changes are confined to the router/gateway seam and a CI
config. The architect does not apply these changes; an engineer or mutator agent
executes this approved plan.
