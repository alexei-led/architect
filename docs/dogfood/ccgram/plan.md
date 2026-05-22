# Refactoring plan: ccgram read-layer and hotspot decomposition

Plain Markdown. Derived from report `ccgram-dogfood-1`, findings F1–F4.

## Overview

The ccgram architecture is sound but carries localized residue. This plan
addresses the standing boundary issue (incomplete read-layer migration, F1), the
import-time coupling in polling (F3), and the largest god modules (F2), plus the
analysis gap that left dependency health unscored (F4). Source: report
`ccgram-dogfood-1` (`report.md`, this directory). No rewrites — every phase is an
independently verifiable seam repair.

## Success criteria

- [ ] All handler reads of window/session state go through
      `window_query`/`session_query`; no handler file references `session_manager`
      for reads (F1, boundary_integrity).
- [ ] The polling decision kernel (`decide.py`) has no transitive import-time
      dependency on the 5 `polling_state` singletons (F3, coupling_balance).
- [ ] No module in `src/ccgram` exceeds ~700 LOC without a documented reason (F2,
      cohesion_modularity).
- [ ] dependency_graph_health is re-scored with a fresh index and a cycle scan
      (F4, dependency_graph_health).

## Phases

### Phase 1: Re-establish dependency evidence

Justification: F4 / E6 — dependency_graph_health is `low` confidence because the
gitnexus index is stale and no Python dep-graph tool is installed. Fix the
evidence before refactoring so later phases can be measured.

Preconditions: gitnexus and codegraph installed (confirmed present).
Postconditions: a current dependency graph and a baseline cycle count exist.

- [ ] Re-run `gitnexus analyze` to refresh the stale index (F4).
- [ ] Install one Python dep-graph tool (`import-linter` preferred for contract
      enforcement; `pydeps` for visualization) (F4).
- [ ] Capture a baseline import-cycle count and the session_manager fan-in.

Verification:

- [ ] `gitnexus status` reports a fresh index (indexed commit == current).
- [ ] A cycle count and fan-in number are recorded for the next report.

### Phase 2: Finish the read-layer migration

Justification: F1 / E2 — 30 handler files still reference `session_manager`
directly while 39 use the intended query layer.

Preconditions: Phase 1 fan-in baseline exists.
Postconditions: handler reads go through the query layer; writes remain explicit.

- [ ] Classify the 30 `session_manager` references into reads vs writes (writes
      like `set_*`/`prune_*`/`sync_*` are legitimate and stay).
- [ ] Migrate the read call sites to `window_query`/`session_query` (F1).
- [ ] Harden the AST-walk read-path test to fail on any new direct read.

Verification:

- [ ] The AST-walk test passes and fails on a deliberately reintroduced direct
      read.
- [ ] `make check` is green.

### Phase 3: Break polling import-time coupling

Justification: F3 / E4 — 5 module-level singletons in `polling_state.py` bind the
pure `decide.py` kernel at import time.

Preconditions: read-layer migration done (Phase 2) to avoid overlapping edits.
Postconditions: singletons constructed and injected, not module-global.

- [ ] Move the 5 singletons behind constructor DI or a single poll-context object
      (F3).
- [ ] Confirm `decide.py` imports no stateful singleton.

Verification:

- [ ] `decide.py` import graph contains no `polling_state` singleton (verify with
      the Phase 1 dep tool).
- [ ] Existing polling tests pass without singleton-reset ceremony for the kernel.

### Phase 4: Decompose god modules

Justification: F2 / E3 — `tmux_manager.py` (1199), `hook.py` (1143),
`directory_callbacks.py` (1086), `polling_state.py` (1017).

Preconditions: Phases 2–3 complete (polling_state will already shrink).
Postconditions: each module split along its existing internal sections.

- [ ] Split `tmux_manager.py` by operation group (windows / panes / send-keys /
      capture).
- [ ] Split `hook.py` (CLI install/uninstall vs stdin event receiver).
- [ ] Split `directory_callbacks.py` (navigation vs worktree flow vs confirm).

Verification:

- [ ] No `src/ccgram` module exceeds ~700 LOC without a noted exception.
- [ ] `make check` is green; no behavior change (characterization tests pass).

## Acceptance criteria

- [ ] Read-path AST-walk test enforces the query layer with zero direct-read
      escapes.
- [ ] Dependency dimension re-scored at `medium`+ confidence with a fresh index.
- [ ] Polling kernel proven free of singleton import coupling.
- [ ] God-module count (>1000 LOC) reduced to zero.
- [ ] All changes land behind characterization tests before cosmetic cleanup.

## Safety notes

Low elevated risk — all changes are in-process refactors with an existing
`make check` gate and characterization-test coverage. No data migrations, no
irreversible steps. The largest blast radius is the `session_manager` read
migration (Phase 2); stage it per-handler-subpackage. The architect does not apply
these changes — an engineer or mutator agent executes the approved plan.
