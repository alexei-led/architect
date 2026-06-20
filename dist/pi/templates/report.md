---
# Architecture report frontmatter contract.
# Markdown body below carries prose; this frontmatter carries machine-checkable
# structure validated by validate-report and compared by compare-reports.
artifact: architecture-report
schema_version: 2
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

# Reusable domain/change-rate judgments. Domain role is primary; churn supports.
module_volatility:
  - module: REPLACE
    classification: core # core | supporting | generic | unknown
    volatility: high # high | medium | low | unknown
    source: architect-inferred # interview | docs | architect-inferred | archfit-label | git-history
    evidence_refs: []
    confidence: low # low | medium | high
    notes: REPLACE

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
    narrative:
      problem: REPLACE concise user-facing problem statement
      knowledge_or_boundary_leakage: REPLACE what leaks, drifts, or crosses a boundary
      complexity_impact: REPLACE why changes become harder or less predictable
      cascading_change_scenarios:
        - REPLACE concrete change that would ripple
      recommended_improvement: REPLACE concrete balancing or boundary repair
      tradeoffs: REPLACE cost, risk, or why not to over-decouple
    recommended_action: REPLACE one-line action used by comparison/planning tools

# Optional calibration when deterministic archfit evidence was used.
# Architect verifies these facts independently instead of passing through scores.
archfit_calibration:
  source_commands: []
  artifacts: []
  confirmed: []
  severity_adjusted: []
  false_positive_or_noise: []
  missed_by_archfit: []
  config_changes: []
  new_fitness_checks: []
  labels_to_confirm: []
  confidence_impact: none # none | low | medium | high

# Evidence refs are addressable enough for a human or agent to re-check.
# The addressable field is type-dependent: file -> ref, command -> command,
# graph-query -> query, interview -> (summary only). Using the wrong field fails
# validate-report.
evidence:
  - id: E1
    type: file # file | command | graph-query | interview
    ref: path/to/file.ext:START-END
    summary: REPLACE
  - id: E2
    type: command
    command: "rg -l session_manager src/pkg/handlers" # the exact, re-runnable command
    summary: REPLACE
  - id: E3
    type: graph-query
    query: "MATCH (a:File)-[:IMPORTS]->(b:File)-[:IMPORTS]->(a) RETURN a, b" # exact graph query
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

Audience note: for human-facing reports, use Mermaid diagrams sparingly when they
clarify module maps or boundary drift. For AI/agent-targeted reports, prefer
plain text adjacency lists and cited bullets; skip decorative diagrams, broad
tables, and formatting polish.

## Executive summary

REPLACE: top-level verdict, dominant risks, and overall confidence.

## Interview context

REPLACE: render the intended architecture and constraints captured above.

## System map

REPLACE: what exists. Established before judging quality. For human-facing
reports, a small Mermaid diagram may summarize this map; include the same facts
in text. For AI/agent-targeted reports, use plain text only.

## Intended architecture

REPLACE: intended structure by source order (interview, docs, manifests,
directories, inferred clusters). Report disagreements between sources.

## Module volatility

REPLACE: module-level core/supporting/generic and volatility judgments, evidence,
confidence, and labels that need human confirmation before deterministic tools
consume them.

## Observed architecture

REPLACE: what the code and operational files actually do.

## Score map

REPLACE: per-dimension value, band, confidence, and one-line justification.

## Key findings

REPLACE: prioritized findings, each tied to a finding ID and evidence. For each
finding include:

- Problem.
- Knowledge or boundary leakage / drift.
- Complexity impact.
- Cascading-change scenarios.
- Recommended improvement.
- Trade-offs.

## Coupling review

REPLACE: for each important relationship, record:

- relationship and abstraction level assessed;
- strength classification plus evidence;
- distance split into code, ownership, runtime, and deploy distance plus evidence;
- volatility from domain classification first, with implementation/provider volatility and churn/history as supporting evidence;
- balance verdict and severity;
- balancing move: lower strength, lower distance, or accept due to low volatility.

## Archfit calibration

REPLACE when archfit was used: confirmed findings, severity-adjusted findings,
false positives/noise, risks missed by archfit, config changes, new fitness
checks, labels to confirm, and confidence impact. Omit when archfit was not used.

## Boundary violations

REPLACE: forbidden imports, internals access, layer/ownership violations.

## Change locality and hotspots

REPLACE: churn, co-change, cross-boundary fallout, trend vs prior reports.

## Recommendations

REPLACE: incremental, evidence-backed. No big-bang rewrites.

## Plan summary

REPLACE when an architecture plan accompanies this report; otherwise omit.

## Evidence appendix

REPLACE: expanded evidence entries referenced by findings and scores.

## Tool coverage and gaps

REPLACE: covered, skipped, missing, and failed tools with confidence impact.
