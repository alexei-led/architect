# Scoring

Scores come from a fixed rubric in `src/templates/scorecard.yaml`. The
`architecture-scorecard` skill describes how to apply it; this page summarizes it
for readers. The rubric file is the source of truth — if this page and the file
disagree, the file wins.

## Dimensions

Six architecture dimensions plus one meta-dimension that scores the review itself:

| Dimension                 | Measures                                                                                                                                |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `boundary_integrity`      | Whether code respects intended module, layer, and ownership boundaries.                                                                 |
| `coupling_balance`        | Integration strength vs distance vs volatility (Balanced Coupling), scored from per-relationship records rather than prose impressions. |
| `dependency_graph_health` | Cycles, hubs, bypassed layers, clusters vs intended modules.                                                                            |
| `cohesion_modularity`     | Whether modules group related behavior; size skew; vocabulary mixing.                                                                   |
| `change_locality`         | Whether changes stay inside intended boundaries over history.                                                                           |
| `architecture_fitness`    | Whether architecture intent is executable via checks, not just docs.                                                                    |
| `analysis_confidence`     | Meta: how trustworthy this review is given tool coverage and evidence.                                                                  |

## Score bands

Each dimension takes a `0..100` value mapped to a band (edges inclusive):

| Band        | Range  | Anchor                                                                                                                         |
| ----------- | ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| critical    | 0–20   | Boundaries absent or routinely bypassed; changes ripple unpredictably; intent neither documented nor enforced.                 |
| poor        | 21–40  | Some structure exists but is widely violated; frequent cross-boundary coupling and cycles; intent and reality diverge sharply. |
| mixed       | 41–60  | Structure holds in parts; notable violations and hotspots remain; intent partly enforced, partly aspirational.                 |
| serviceable | 61–80  | Boundaries mostly respected; few cycles; most change stays local; some intent enforced by checks.                              |
| strong      | 81–100 | Boundaries explicit and enforced; healthy dependency graph; change stays local; intent executable via fitness checks.          |

For repeatability, score **band-first**: choose the band whose anchor best fits
the evidence, then choose a value inside that band. Default to the band midpoint
unless the evidence clearly supports an edge. The band must be the one whose
range contains the value. Band/value disagreement is a hard error caught by
`architect-validate-report`.

## Confidence

Confidence describes how trustworthy the assessment is, **independent of the
quality value**:

- **low** — thin or indirect evidence; key tools missing or failed; scores
  provisional.
- **medium** — multiple evidence sources, but coverage or recency gaps remain.
- **high** — applicable evidence dimensions covered with working tools and direct
  file/graph references.

Missing or failed tools lower confidence (see [tools.md](tools.md)).

## Rules the rubric enforces

- **Band matches value** — the band must contain the value.
- **Evidence per score** — every non-meta score carries at least one evidence ref;
  no evidence means no score (record a coverage gap instead).
- **Balanced Coupling needs relationship records** — `coupling_balance` is scored
  from relationship-level strength, distance, volatility, and evidence records,
  not from repo-level vibes.
- **Low confidence caps high quality** — a `serviceable` or `strong` band requires
  at least `medium` confidence. A low-confidence review cannot present high
  quality as settled; lower the band or raise coverage.
- **Never score from directory shape alone** — only observed, enforced behavior
  counts; a tidy folder tree is not evidence of boundary integrity.

These are enforced mechanically by `architect-validate-report`; a draft that
breaks them will not validate.

## Comparability

`rubric_version` versions the rubric. Bump it whenever a dimension, band edge, or
anchor changes — reports built under different rubric versions are not directly
comparable. Two reports compare only when **scope**, **rubric_version**, and
**tool_coverage_level** (`minimal` | `standard` | `deep`) all match.
`architect-compare-reports` separates score deltas from confidence deltas and
emits an explicit non-comparability reason rather than inventing a trend when the
keys differ.
