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
`src/templates/scorecard.yaml` — read it; do not restate or invent values here.

## When to use

Use whenever you are about to assign or revise a score on any architecture
dimension. The architecture-review skill calls this before writing scores into a
report.

## Procedure

1. **Read the rubric.** `src/templates/scorecard.yaml` is the source of truth for
   dimension names, 0..100 bands and their anchors, confidence levels, and the
   enforced rules. If you find yourself typing a dimension name or band edge from
   memory, stop and read the file — drift from the scorecard is a bug.

2. **Per dimension, gather the evidence first.** A score with no evidence ref is
   invalid for every non-meta dimension. If you have no evidence, do not score —
   record a coverage gap and let `analysis_confidence` absorb it.

3. **Pick the value, then the band.** Choose a 0..100 value justified by evidence
   and the band anchors. The band must be the one whose range contains the value.
   Band and value disagreeing is a hard error.

4. **Set confidence independently of quality.** Confidence reflects how
   trustworthy the assessment is — coverage, recency, directness of evidence —
   not how good the architecture is. Missing or failed tools lower it.

5. **Apply the caps.** A high-quality band (per the rubric's
   `high_quality_requires_confidence` rule) cannot stand on low confidence. If
   evidence is thin, either lower the band or raise coverage — never present a
   shaky high score as settled.

6. **Score the meta-dimension.** `analysis_confidence` scores the review itself:
   how much of the applicable evidence you actually covered. It is where missing
   tools and unanswered interview questions land.

## Failure handling

- Missing or unreadable `src/templates/scorecard.yaml`: stop; do not recreate the
  rubric from memory.
- Missing evidence for a non-meta dimension: do not score it. Record a coverage
  gap and lower `analysis_confidence`.
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

These are also enforced mechanically by `architect-validate-report`; failing
them in a draft means the report will not validate.
