---
# Architecture report frontmatter contract.
# Markdown body below carries prose; this frontmatter carries machine-checkable
# structure validated by validate-report and compared by compare-reports.
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: REPLACE-with-stable-slug
date: YYYY-MM-DD

target:
  repo: REPLACE-repo-name
  scope: full # full | path-subset | service-subset
  out_of_scope: []

# Comparability key. Two reports compare only when these match (see scorecard).
comparability:
  scope: full
  rubric_version: 1
  tool_coverage_level: standard # minimal | standard | deep

# Intended architecture and constraints captured from the user interview.
interview_context:
  system_goal: REPLACE
  quality_goals: [] # e.g. maintainability, change locality, deploy independence
  intended_units: [] # modules, services, packages, deploy units
  domains:
    core: []
    supporting: []
    generic: []
  volatile_areas: []
  team_ownership: []
  known_pain: []
  review_scope: full
  out_of_scope: []

# What exists, established before judging quality.
system_map:
  languages: []
  package_managers: []
  units: [] # apps, services, libraries, CLIs, jobs, workers
  deploy_units: []
  public_interfaces: [] # APIs, events, schemas, migrations, generated code
  declared_modules: [] # from manifests and directories
  observed_modules: [] # from dependency graphs, imports, ownership, churn
  high_risk_entrypoints: []
  missing_evidence: []

# Each score: value (0..100), band (must match value), confidence, evidence
# refs, and known gaps. analysis_confidence scores the review itself.
scores:
  boundary_integrity:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []
  coupling_balance:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []
  dependency_graph_health:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []
  cohesion_modularity:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []
  change_locality:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []
  architecture_fitness:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []
  analysis_confidence:
    value: 0
    band: critical
    confidence: low
    evidence_refs: []
    gaps: []

# Findings carry stable IDs reused across repeat reports for the same issue.
findings:
  - id: F1
    title: REPLACE
    severity: high # critical | high | medium | low
    dimension: boundary_integrity
    evidence_refs: [E1]
    recommended_action: REPLACE

# Evidence refs are addressable enough for a human or agent to re-check.
evidence:
  - id: E1
    type: file # file | command | graph-query | interview
    ref: path/to/file.ext:START-END
    summary: REPLACE

# Tool coverage per evidence dimension. Records used, skipped, missing, failed,
# and confidence impact even when no issue is found.
tool_coverage:
  - dimension: discovery # discovery|structural|semantic|dependency|change|operational|security|report
    tools_used: []
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none # none | low | medium | high
---

# Architecture report: REPLACE-repo-name

## Executive summary

REPLACE: top-level verdict, dominant risks, and overall confidence.

## Interview context

REPLACE: render the intended architecture and constraints captured above.

## System map

REPLACE: what exists. Established before judging quality.

## Intended architecture

REPLACE: intended structure by source order (interview, docs, manifests,
directories, inferred clusters). Report disagreements between sources.

## Observed architecture

REPLACE: what the code and operational files actually do.

## Score map

REPLACE: per-dimension value, band, confidence, and one-line justification.

## Key findings

REPLACE: prioritized findings, each tied to a finding ID and evidence.

## Coupling review

REPLACE: important integrations by strength, distance, volatility.

## Boundary violations

REPLACE: forbidden imports, internals access, layer/ownership violations.

## Change locality and hotspots

REPLACE: churn, co-change, cross-boundary fallout, trend vs prior reports.

## Recommendations

REPLACE: incremental, evidence-backed. No big-bang rewrites.

## Plan summary

REPLACE when a refactoring plan accompanies this report; otherwise omit.

## Evidence appendix

REPLACE: expanded evidence entries referenced by findings and scores.

## Tool coverage and gaps

REPLACE: covered, skipped, missing, and failed tools with confidence impact.
