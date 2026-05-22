# Triage reference

Between evidence gathering and scoring, triage. The goal is to turn raw tool
output into a small set of evidence-backed findings, and to keep facts,
hypotheses, scores, and recommendations from blurring together.

## Sort every observation

For each thing a tool surfaced, classify it:

- **Fact** — directly shown by a file, command, or graph query. Has an
  addressable evidence ref. Eligible to move a score.
- **Hypothesis** — a plausible inference not yet confirmed. Either confirm it
  with another query or label it as a hypothesis in the report. Does not move a
  score on its own.
- **Noise** — true but irrelevant to any dimension, or a tool artifact. Drop it.
  Do not pad the report.

## Promote facts to findings

A finding needs: a stable ID, a dimension, a severity, at least one evidence
ref, and a recommended (incremental) action. If you cannot cite evidence, it is
not a finding yet — it is a hypothesis or a coverage gap.

Reuse a finding's ID across repeat reviews of the same issue so
`architect-compare-reports` can track it.

## Map findings to dimensions

Each finding attaches to one scorecard dimension (see
`src/templates/scorecard.yaml`). Severity and the weight of evidence inform the
band; missing coverage informs confidence, not the value. Resist scoring a
dimension you have not actually gathered evidence for — record the gap and let
`analysis_confidence` reflect it.

## Stop rule

When additional scans would be redundant or expensive and would not change a
score, stop. Record the untouched area as a coverage gap in `tool_coverage`
rather than running another tool for completeness theater.
