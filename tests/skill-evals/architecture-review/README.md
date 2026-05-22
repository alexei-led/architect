# Architecture-review skill evals

Deterministic baseline evals for the `architecture-review` skill. They check the
_observable contract_ a correct review must hold, not a live model run.

## Model

A live LLM eval is not reproducible in CI, so each behavior is encoded as a
**golden artifact** plus an **assertion type**:

- `baseline/*.report.md`, `baseline/*.plan.md` — hand-written goldens that encode
  the property a correct review would produce (e.g. the tangled report scores
  worse on the structural dimensions and every dropped dimension carries a
  finding).
- `cases.yaml` — enumerates eval cases, each naming a `behavior` and an
  `assertion` type with the params that assertion needs.
- `test_evals.py` — loads the cases and dispatches on `assertion` (a switch, one
  checker per type). Discovered by the repo's normal `testpaths = ["tests"]`.

Because goldens are static, "re-runs produce stable score bands" is trivially
true; the `stable_score_bands` case still verifies bands are a deterministic
function of values via the scorecard, so a hand-edited golden with a mismatched
band fails.

## Fixtures

The paired `ts-healthy` / `ts-tangled` fixtures under `tests/fixtures/repos/`
drive score discrimination. `python-boundaries`, `go-deps`, and `infra-mixed`
are referenced for lighter checks (presence and manifest coverage) — they do not
ship full goldens. Git history is omitted from every fixture by design (a nested
`.git` would conflict with the parent repo); change-locality is a recorded
coverage gap.

## Adding a case

1. Add or extend a golden under `baseline/`.
2. Add a case to `cases.yaml` with an existing `assertion` type.
3. If the behavior needs a genuinely new check, add one branch to `_CHECKERS`.
