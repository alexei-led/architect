# Dogfood friction log — ccgram pass 2 (2026-05-22)

Second autonomous pass against `/Users/alexei/Workspace/ccgram`, run after pass 1.
Goal of this pass: close the pass-1 dependency-evidence gap and exercise the helper
tools (validate-report, compare-reports) on real artifacts before release.

## FR8 — Report template omitted command/graph-query evidence examples (real defect)

`architect-validate-report` rejected the pass-1 report with 4 violations:
`evidence[E1/E2/E3/E6]: type 'command' requires field 'command'`. Root cause: the
report template (`src/templates/report.md`) only showed a single `file`-type
evidence example using `ref:`. The author copied that shape for command-type
evidence, but the contract requires a type-dependent field (`file→ref`,
`command→command`, `graph-query→query`). The template never showed the other shapes.
**Fix applied this pass:**

- `src/templates/report.md` now shows command and graph-query evidence examples and
  states the type→field mapping explicitly.
- Pass-1 `report.md` fixed in place (`ref:`→`command:` on E1/E2/E3/E6); it now
  validates. The shipped artifact and the shipped validator now agree.

## FR9 — gitnexus reindex is the right move, but it is not cheap

`gitnexus analyze` reindexed ccgram in 33s (incremental; 16,614 nodes, 37,969 edges).
Acceptable for an on-demand pass, but the review loop should not reindex blindly on
every run. Pass-1 FR3 already added a freshness check; this pass confirms the cost is
bounded for incremental reindex. **No new change** — FR3 guidance stands; recorded
that a full (non-incremental) index would be materially slower and should be a
deliberate, user-acknowledged step on large repos.

## FR10 — gitnexus Cypher schema is not obvious; queries need discovery

Cycle detection required discovering the graph schema by trial: relationships are a
single `CodeRelation` label with a `type` property (`IMPORTS`, `CALLS`, ...), not
typed edges; file nodes key on `filePath`, not `path`. Three failed queries before a
working one. **Fix (deferred to the GitNexus tool skill):** the skill should record
the concrete schema (`CodeRelation.type`, `File.filePath`) and a ready-to-run
import-cycle Cypher query, so an agent does not rediscover it each time. Worked query
is captured in pass-2 report E6.

## FR11 — doctor "missing" vs target-declared tools

`architect-doctor` reported `deptry` MISSING (not on the architect env PATH), but
ccgram's `pyproject.toml` declares `deptry>=0.23.0` in its dev group. doctor checks
the _running_ environment, not what the target repo declares. That is correct for
"can I run this now", but a reviewer could misread it as "the project lacks dependency
tooling". **No code change** — documented in the release notes known-limitations
section so the distinction is explicit.

## What changed since pass 1 (evidence, not friction)

- Read-layer migration advanced: handler files with direct `session_manager` refs
  fell 30 → 10. boundary_integrity 68 → 74.
- Dependency dimension moved from a high-impact coverage gap to graph-backed:
  dependency_graph_health 50 → 58, confidence low → medium.
- F4 ("dependency-graph health unverified") resolved; replaced by concrete F6
  (8 import cycles, all intra-package or bootstrap, none domain-crossing).
- God modules (F2) and polling singletons (F3) unchanged — correctly reported as
  persisting, not re-discovered.

## Tuning applied this pass

- `src/templates/report.md` → FR8 (command + graph-query evidence examples, type→field
  rule). This is the only source change; it is friction-driven, not speculative.
- FR10 deferred to the GitNexus tool skill (worked Cypher query recorded in E6).
- FR9, FR11 recorded, no change (FR3 already covers freshness; FR11 is a
  documentation matter, handled in release notes).
