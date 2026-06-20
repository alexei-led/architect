# Enhancement plan: architect + archfit Balanced Coupling loop

Source: the 2026-06-20 archfit-vs-architect Balanced-Coupling comparison reports
(OpenAI and Claude tracks), produced from local runs across five repositories.

## Goal

Make architect better at Balanced Coupling reviews by using archfit's
deterministic facts when available, while preserving architect's strength:
independent intent, domain-volatility, runtime/deploy, and design judgment.

## Key findings from the comparison

1. archfit is the better measurement/gate engine: repeatable scorecards, JSON,
   SARIF, deltas, tool coverage, findings, and `agent_tasks`.
2. architect is the better interpretation/design engine: intent reconstruction,
   domain volatility, composition-root semantics, runtime/deploy context, and
   fitness-check design.
3. The best loop is: archfit deterministic scan -> architect calibration ->
   human-confirmed labels -> archfit gates -> architect re-review.
4. Missing evidence must lower confidence. A green score without classified
   dependency/tool coverage is false reassurance.
5. Architect quick sweeps need stable command logs, coverage, failed/skipped
   tools, and machine-readable calibration blocks.
6. Architect should export subdomain/volatility/strength judgments so deterministic
   tools can reuse them after human approval.

## Implemented in this repo change

- Added `tools-archfit` skill for deterministic archfit facts, scorecards,
  deltas, SARIF/JSON, tool coverage, `agent_tasks`, and calibration output.
- Registered the skill in the architecture plugin manifest.
- Added archfit to `architect-doctor` and the tools documentation.
- Updated `architecture-review` to run/calibrate archfit when available and to
  include `module_volatility` and `archfit_calibration` in full reports and quick sweeps.
- Updated scoring instructions so missing/thin evidence cannot support green
  scores.
- Updated Balanced Coupling guidance so deterministic edges/cycles are evidence,
  not final judgment.
- Updated architecture-fitness and planning guidance to prefer archfit gates when
  a repo already uses archfit.
- Updated report/design/plan templates to carry reusable volatility judgments,
  calibration, labels to confirm, fitness-gate slots, and archfit verification commands.
- Added coverage-gap calibration (`coverage_gap_caps_quality`): missing/partial/
  stale primary evidence forces low confidence and caps the band at `mixed`
  (default midpoint), so down-calibration of tool false-greens is reproducible in
  magnitude, not only direction.

## Live validation (2026-06-20)

Ran the combination in three independent fresh-context sessions over the five
repos against deterministic archfit artifacts:

- archfit `full.json` was byte-identical on re-run for all five repos.
- Overall band agreed across sessions for 4/5 repos; mean overall range 3.2 pts.
- All sessions independently rejected archfit's false-green `coupling_balance 90`
  on the scip-absent repos (pumba, spotinfo, codegraph).
- Finding-level detail converged (codegraph god hub + cycles, ccgram cycles/god
  modules, archfit enforced ring test).
- Residual variance was confidence assignment on coverage-blind dimensions; the
  coverage-gap calibration rule above closes that gap.

## Follow-up backlog

0. (done) Coverage-gap calibration rule for reproducible down-calibration magnitude.
1. Add validator support for `module_volatility` and `archfit_calibration` shapes.
   - Check `confidence_impact` enum.
   - Check list fields are arrays.
   - Keep `archfit_calibration` optional for reports that did not use archfit.
2. Add report comparison support for archfit calibration deltas.
   - New confirmed vs resolved vs repeated false-positive counts.
   - Highlight new `labels_to_confirm` and `new_fitness_checks`.
3. Add fixture tests for a report with `archfit_calibration`.
4. Add examples showing the combined loop on a small repo with `.archfit.yaml`.
5. Consider an `architect-archfit-import` helper only if manual report assembly
   proves repetitive. Do not wrap archfit prematurely; the current architecture
   intentionally keeps evidence tools external.

## Acceptance criteria

- `make check` passes.
- Generated runtime artifacts include `tools-archfit` for Claude, Codex, and Pi.
- Instruction tests assert archfit calibration guidance exists.
- Reviews using archfit produce calibrated facts, not pass-through scores.
