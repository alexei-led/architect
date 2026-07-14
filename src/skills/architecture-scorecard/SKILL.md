---
name: architecture-scorecard
description: >-
  Assign architecture scores against the fixed rubric. Use when scoring or
  re-scoring architecture dimensions, choosing a band, setting confidence, or
  checking that a score is defensible. Enforces band-matches-value,
  evidence-per-score, and low-confidence caps. NOT for gathering evidence (use
  architecture-review) or writing plans (use architecture-plan).
---

# Architecture scorecard

How to score, honestly and reproducibly. The rubric itself lives in
`../../resources/templates/scorecard.yaml` — read it; do not restate or invent values here.

## When to use

Use whenever you are about to assign or revise a score on any architecture
dimension. The architecture-review skill calls this before writing scores into a
report.

## Skill navigation

- Missing evidence or system map: return to `architecture-review`; scores are
  not a substitute for evidence.
- Current skill: use `architecture-scorecard` only to assign defensible values,
  bands, confidence, and score rationales.
- Next skill: write the `architecture-review` report, then recommend one primary
  next step: `architecture-design` when findings need target-state decisions,
  `architecture-plan` only when an approved design already exists and sequencing
  is requested, or no next skill for pure audit/scoring.

## Procedure

1. **Read the rubric.** `../../resources/templates/scorecard.yaml` is the source of truth for
   dimension names, 0..100 bands and their anchors, confidence levels, and the
   enforced rules. If you find yourself typing a dimension name or band edge from
   memory, stop and read the file — drift from the scorecard is a bug.

2. **Per dimension, gather the evidence first.** A score with no evidence ref is
   invalid for every non-meta dimension. If you have no evidence, do not score —
   record a coverage gap and let `analysis_confidence` absorb it. Absence of
   findings counts as positive evidence only when a current tool actually covered
   that finding class.

3. **Pick the band, then the value.** Choose the band whose anchor best fits the
   evidence first. Then choose a 0..100 value within that band; default to the
   band midpoint unless the evidence clearly supports an edge. The band must be
   the one whose range contains the value. Band and value disagreeing is a hard
   error.

4. **Set confidence independently of quality.** Confidence reflects how
   trustworthy the assessment is — coverage, recency, directness of evidence —
   not how good the architecture is. Missing or failed tools lower it.

5. **Apply the caps.** A high-quality band (per the rubric's
   `high_quality_requires_confidence` rule) cannot stand on low confidence. If
   evidence is thin, either lower the band or raise coverage — never present a
   shaky high score as settled. Do not give `serviceable` or `strong` to a
   dimension whose core evidence is missing, stale, unclassified, or based only
   on another tool's green summary.

   **Coverage-gap calibration (reproducible magnitude).** When the _primary_
   evidence for a dimension is missing, partial, or stale and you did not
   independently re-establish the claim, set `confidence: low` and cap the band
   at `mixed` (value ≤ 60); default to the band midpoint (~50). Raise above
   `mixed` only with direct evidence you gathered yourself. Primary evidence per
   dimension:
   - `coupling_balance`: classified edges (scip / codegraph / `go list` /
     dependency-cruiser). No classified edges means a tool's "balanced, no
     classified edges" default is not proof — low confidence, cap at `mixed`.
   - `dependency_graph_health`: a real import/dependency graph with adequate
     coverage.
   - `change_locality`: git history / GitNexus covering most changed files;
     partial file coverage caps at `mixed`.
   - `cohesion_modularity`: size/complexity/duplication signals (LOC, lizard,
     jscpd).
   - `boundary_integrity`: classified cross-boundary edges or enforced rules.
     This keeps down-calibration of tool false-greens reproducible in magnitude,
     not only direction.

6. **Score the meta-dimension.** `analysis_confidence` scores the review itself:
   how much of the applicable evidence you actually covered. It is where missing
   tools and unanswered interview questions land.

## Failure handling

- Missing or unreadable `../../resources/templates/scorecard.yaml`: stop; do not recreate the
  rubric from memory.
- Missing evidence for a non-meta dimension: do not score it. Record a coverage
  gap and lower `analysis_confidence`. If the report format requires a numeric
  placeholder, use a low-confidence provisional value and make the gap explicit;
  never use a green placeholder.
- Band/value mismatch, missing evidence refs, or low-confidence high-quality
  claim: fix the score before reporting.

## Output

For each scored dimension, return:

- `dimension`: exact scorecard key.
- `value`: 0..100.
- `band`: band containing the value.
- `confidence`: independent coverage/confidence level.
- `evidence_refs`: refs supporting the score, empty only for meta dimensions.
- `rationale`: one or two sentences tied to evidence and band anchors.
- `rules_checked`: band/value match, evidence refs, confidence cap.

## Rules you must not break

- Band matches value.
- Every non-meta score carries at least one evidence ref.
- Low confidence caps high-quality claims.
- Never score from directory shape alone — only observed, enforced behavior.
- Never infer high quality from missing evidence, missing classified edges, or a
  deterministic tool score that has not been calibrated against coverage.
- Missing, partial, or stale primary evidence forces low confidence and a band
  no higher than `mixed` until you re-establish the claim with your own evidence.

These are also enforced mechanically by `architect-validate-report`; failing
them in a draft means the report will not validate.
