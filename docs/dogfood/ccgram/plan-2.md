# Refactoring plan: ccgram read-layer, hotspots, and cycle contract (pass 2)

Plain Markdown. Derived from report `ccgram-dogfood-2`, findings F1, F2, F3, F6.
Supersedes the pass-1 plan: Phase 1 of that plan (re-establish dependency evidence)
is done — the graph was rebuilt this pass and F4 resolved.

## Overview

ccgram remains architecturally sound with localized residue. Since pass 1 the
read-layer migration advanced (30 → 10 direct `session_manager` handler refs) and
the dependency graph is now real evidence. This plan finishes the read-layer
migration (F1), breaks polling import-time coupling (F3), decomposes the four god
modules (F2), and adds an import-contract that pins the now-measured cycle baseline
(F6). Source: report `ccgram-dogfood-2` (`report-2.md`). No rewrites — every phase
is an independently verifiable seam repair.

## Success criteria

- [ ] No handler file references `session_manager` for reads; the remaining 10 sites
      go through `window_query`/`session_query` (F1, boundary_integrity).
- [ ] The polling decision kernel (`decide.py`) has no transitive import-time
      dependency on the 5 `polling_state` singletons (F3, coupling_balance).
- [ ] No module in `src/ccgram` exceeds ~700 LOC without a documented reason (F2,
      cohesion_modularity).
- [ ] An import-linter contract forbids new sibling import cycles; the 8 measured
      cycles do not grow (F6, dependency_graph_health).

## Phases

### Phase 1: Finish the read-layer migration

Justification: F1 / E2 — 10 handler files still reference `session_manager` directly
while 37 use the intended query layer. Down from 30; the gate is working.

Preconditions: none (graph baseline already captured this pass).
Postconditions: handler reads go through the query layer; writes remain explicit.

- [ ] Classify the 10 remaining `session_manager` references into reads vs writes
      (writes like `set_*`/`prune_*`/`sync_*` stay).
- [ ] Migrate the read call sites to `window_query`/`session_query` (F1).
- [ ] Harden the AST-walk read-path test to fail on any new direct read.

Verification:

- [ ] The AST-walk test passes and fails on a deliberately reintroduced direct read.
- [ ] `make check` is green.

### Phase 2: Pin the import-cycle baseline

Justification: F6 / E6 — 8 import 2-cycles exist (recovery/, topics/, live/ sibling
re-export coupling plus cli↔main, bot↔main bootstrap). None cross a domain boundary,
but nothing prevents new ones.

Preconditions: gitnexus graph current (done this pass).
Postconditions: a contract fails CI when a new sibling cycle is introduced.

- [ ] Install `import-linter` (preferred for contract enforcement).
- [ ] Add a `forbidden`/`independence` contract for the handler subpackages that
      currently have sibling cycles, allowlisting only the existing bootstrap pairs.
- [ ] Wire the contract into `make check`.

Verification:

- [ ] `lint-imports` passes on the current tree and fails on a deliberately added
      sibling cycle.
- [ ] The cycle count does not exceed the recorded baseline of 8.

### Phase 3: Break polling import-time coupling

Justification: F3 / E4 — 5 module-level singletons in `polling_state.py` bind the
pure `decide.py` kernel at import time.

Preconditions: Phase 1 done to avoid overlapping edits in polling handlers.
Postconditions: singletons constructed and injected, not module-global.

- [ ] Move the 5 singletons behind constructor DI or a single poll-context object (F3).
- [ ] Confirm `decide.py` imports no stateful singleton.

Verification:

- [ ] `decide.py` import graph contains no `polling_state` singleton (verify via
      gitnexus or the Phase 2 import-linter contract).
- [ ] Existing polling tests pass without singleton-reset ceremony for the kernel.

### Phase 4: Decompose god modules

Justification: F2 / E3 — `tmux_manager.py` (1199), `hook.py` (1141),
`directory_callbacks.py` (1091), `polling_state.py` (1017). Unchanged since pass 1.

Preconditions: Phases 1–3 complete (polling_state will already shrink).
Postconditions: each module split along its existing internal sections.

- [ ] Split `tmux_manager.py` by operation group (windows / panes / send-keys / capture).
- [ ] Split `hook.py` (CLI install/uninstall vs stdin event receiver).
- [ ] Split `directory_callbacks.py` (navigation vs worktree flow vs confirm).

Verification:

- [ ] No `src/ccgram` module exceeds ~700 LOC without a noted exception.
- [ ] `make check` is green; no behavior change (characterization tests pass).

## Acceptance criteria

- [ ] Read-path AST-walk test enforces the query layer with zero direct-read escapes.
- [ ] Import-linter contract pins the cycle baseline and fails on new sibling cycles.
- [ ] Polling kernel proven free of singleton import coupling.
- [ ] God-module count (>1000 LOC) reduced to zero.
- [ ] All changes land behind characterization tests before cosmetic cleanup.

## Safety notes

Low elevated risk — all changes are in-process refactors with an existing `make check`
gate and characterization-test coverage. No data migrations, no irreversible steps.
The largest blast radius is the remaining `session_manager` read migration (Phase 1);
stage it per-handler-subpackage. The architect does not apply these changes — an
engineer or mutator agent executes the approved plan.
