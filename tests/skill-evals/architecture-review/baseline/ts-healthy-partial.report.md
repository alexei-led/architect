---
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: ts-healthy-partial-baseline
date: 2026-05-22

target:
  repo: tests/fixtures/repos/ts-healthy
  scope: partial
  out_of_scope:
    - src/infra

comparability:
  scope: partial
  rubric_version: 1
  tool_coverage_level: standard

scores:
  boundary_integrity:
    value: 85
    band: strong
    confidence: high
    evidence_refs:
      - E1
  dependency_graph_health:
    value: 88
    band: strong
    confidence: high
    evidence_refs:
      - E1

evidence:
  - id: E1
    type: command
    command: depcruise src/domain src/app --config .dependency-cruiser.cjs
    summary: Partial run over domain and app only; infra excluded from this review.
---

# Architecture report: ts-healthy (partial scope)

A deliberately partial-scope re-review of ts-healthy (infra excluded). It exists
only to exercise non-comparability: compared against the full-scope baseline,
`compare-reports` must refuse to invent a trend and instead report that `scope`
differs.
