# Report, design, and plan format

The architecture report is one Markdown file: YAML frontmatter carries
machine-checkable structure, the body carries prose. `architect-validate-report`
checks the frontmatter; `architect-compare-reports` diffs two reports or explains
why they are not comparable. The canonical template is
`src/templates/report.md`; the design template is `src/templates/design.md`; the
plan template is `src/templates/plan.md`.

## Report frontmatter

```yaml
artifact: architecture-report
schema_version: 2
rubric_version: 1 # must match the scorecard the scores were assigned under
report_id: stable-slug
date: YYYY-MM-DD

target:
  repo: repo-name
  scope: full # full | path-subset | service-subset
  out_of_scope: []

comparability: # two reports compare only when all three match
  scope: full
  rubric_version: 1
  tool_coverage_level: standard # minimal | standard | deep

interview_context: { ... } # intended architecture and constraints from the interview
system_map: { ... } # what exists, established before judging quality
scores: { ... } # one entry per dimension (see scoring.md)
findings: [...] # stable IDs, severity, dimension, evidence refs, narrative, action
evidence: [...] # addressable refs a human/agent can re-check
tool_coverage: [...] # used/skipped/missing/failed + confidence impact per dimension
```

### interview_context

Captures intended architecture: `system_goal`, `quality_goals`,
`intended_units`, `domains` (`core` / `supporting` / `generic`),
`volatile_areas`, `team_ownership`, `known_pain`, `review_scope`, `out_of_scope`.
Filled from the interview before scoring; missing context triggers the interview.

### system_map

What actually exists, established before judging quality: `languages`,
`package_managers`, `units`, `deploy_units`, `public_interfaces`,
`declared_modules` (from manifests/dirs), `observed_modules` (from dependency
graphs, imports, ownership, churn), `high_risk_entrypoints`, and
`missing_evidence`. Declared vs observed are kept distinct so the report can flag
where intent and reality diverge.

### findings

Each finding has a stable `id` (`F1`, `F2`, …) reused across repeat reports for
the same issue, a `severity` (`critical` | `high` | `medium` | `low`), the
`dimension` it bears on, `evidence_refs`, a human-facing `narrative`, and a
`recommended_action`.

The narrative explains the issue in terms a maintainer can act on:
`problem`, `knowledge_or_boundary_leakage`, `complexity_impact`,
`cascading_change_scenarios`, `recommended_improvement`, and `tradeoffs`. The
validator requires this narrative for schema version 2 reports.

### evidence

Each ref has an `id` (`E1`, …), a `type` (`file` | `command` | `graph-query` |
`interview`), a `ref` addressable enough to re-check (e.g. `path/to/file.ext:12-40`),
and a one-line `summary`. Findings and scores point at these ids. The validator
rejects malformed refs.

### tool_coverage

One entry per evidence dimension (`discovery`, `structural`, `semantic`,
`dependency`, `change`, `operational`, `security`, `report`) listing
`tools_used`, `tools_skipped`, `tools_missing`, `tools_failed`, and
`confidence_impact`. Recorded even when no issue is found, so a clean dimension
is distinguishable from an uninspected one. Some analysis tools return nonzero
when they find issues; that output is evidence, not a tool failure. See
[tools.md](tools.md).

## Report body sections

In order: Executive summary, Interview context, System map, Intended
architecture, Observed architecture, Score map, Key findings, Coupling review,
Boundary violations, Change locality and hotspots, Recommendations, Plan summary
(when a plan accompanies the report), Evidence appendix, Tool coverage and gaps.
Key findings render the narrative fields above, not just severity labels.

The **Coupling review** section is structured, not free-form. For each important
relationship, record:

- relationship and abstraction level;
- strength classification plus evidence;
- distance split into code, ownership, runtime, and deploy distance plus evidence;
- volatility from domain classification first, with implementation/provider volatility and churn/history as supporting evidence;
- balance verdict and severity;
- balancing move.

For human-facing reports, a small Mermaid diagram may clarify the system map,
dependency clusters, or boundary drift. Keep the same facts in text. For
AI/agent-targeted reports, skip decorative diagrams, broad tables, and formatting
polish; use plain text evidence and adjacency lists.

Intended architecture is rendered by source order (interview → docs → manifests →
directories → inferred clusters), and disagreements between sources are reported
rather than silently resolved.

## Quick sweep format

When a full report would be too expensive — for example, when comparing several
repos — use an `architecture-review` **quick sweep** instead of forcing partial
scores. A quick sweep is still evidence-based, but it returns **candidates and
next checks**, not final findings or architecture scores.

Per target, include:

- `scope`
- `intent_evidence`
- `system_map`
- `commands_run`
- `tool_coverage`
- `dependency_snapshot`
- `coupling_candidates`
- `likely_findings` (confirmed only; otherwise say none)
- `next_checks`
- `quality_self_check`

The quality self-check explicitly answers: structure, clarity, usefulness,
repeatability, and helpfulness. If any are weak, rerun the sweep with one deeper
pass instead of pretending the result is good enough.

## Design format

The design artifact is plain Markdown for target architecture. It separates
requirements and intended architecture from observed implementation so stale docs
do not masquerade as code truth. It covers source inputs, drift notes,
domain/volatility map, module map, integration contracts, key flows, module test
specifications, architecture-fitness checks, trade-offs, self-review, risks, and
handoff.

Use review when judging current implementation health. Use design for
requirements-to-architecture work, review-driven target-state decisions, or
boundary/contract definitions. Use plan only when sequencing an approved design.
For existing-code remediation, the normal pipeline is review → design → plan;
for greenfield work it is design → plan; for pure audit it is review only.

## Plan format

The architecture plan is plain Markdown for humans, coding agents, and task
runners. Generated plan files default to `docs/plans/<kebab-case-target>.md`
unless the user gives a different path. If a plan is written outside the
configured plans directory, the handoff must name the exact execution path or say
to copy/symlink it into that directory. One hotspot, boundary, module, or flow
per plan unless a roadmap is requested; keep the next execution horizon to five
tasks or fewer before re-review.

- **Overview** — the problem the plan addresses.
- **Source artifact** — approved design ID plus design decisions, contract IDs,
  risks, or module names it derives from; include source report finding IDs and
  evidence refs when the design came from a review.
- **Success criteria** — observable outcomes, each tied to a finding, score
  dimension, design decision, contract, module responsibility, or risk.
- **Validation Commands** — project-wide commands the executor can run after
  task completion.
- **Implementation Steps** — executable work uses `### Task N:` or
  `### Iteration N:` headings. Each task carries a justification (finding ID +
  evidence ref), file list, preconditions, postconditions, concrete GitNexus
  `impact` / `detect-changes` commands or an explicit missing-tool fallback,
  concrete per-task verification commands, manual checks as plain bullets, and
  small independently-verifiable checkbox items. Checkboxes belong only inside
  task or iteration sections.
- **Acceptance criteria** — conditions for accepting the whole plan; prefer
  characterization tests, seam creation, boundary repair, and fitness checks
  before cosmetic cleanup.
- **Safety notes** — irreversible steps, data migrations, wide-blast-radius
  changes, or "No elevated risk." The architect never applies changes; an
  engineer or mutator agent executes the approved plan.

Plans recommend incremental implementation/refactoring only — no big-bang
rewrites — and each boundary repair pairs with a fitness check so it cannot
silently re-rot. The final executable task handles whole-plan verification,
documentation confirmation, GitNexus `detect-changes`, and scoped re-review
handoff. A plan ends by recommending a scoped `architecture-review` pass once
implementation lands.
