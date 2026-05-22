"""Architecture-review skill evals.

Loads ``cases.yaml`` and dispatches each case on its ``assertion`` type against
the golden artifacts under ``baseline/`` and the fixture repos under
``tests/fixtures/repos/``. The dispatcher is a plain switch — one checker per
assertion type — so adding a behavior is a new case plus (rarely) a new branch,
not bespoke per-case logic.

These are deterministic baseline evals, not a live model run: a golden encodes
the observable property a correct review produces, and each checker verifies the
contract that property implies. See cases.yaml for the rationale.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from architect_tools._contract import (
    META_DIMENSION,
    band_for_value,
    load_report,
    load_scorecard,
)
from architect_tools.compare_reports import compare_reports
from architect_tools.validate_report import validate_report

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
BASELINE = HERE / "baseline"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "repos"
OVERLAYS = REPO_ROOT / "src" / "agents" / "architect"
SCORECARD = load_scorecard()

CASES = yaml.safe_load((HERE / "cases.yaml").read_text())["cases"]


def _report(name: str):
    return load_report(BASELINE / name)


def _ids(cases):
    return [c["id"] for c in cases]


# --- per-assertion checkers ------------------------------------------------


def _check_validates_contract(case):
    fm, body = _report(case["report"])
    errors = validate_report(fm, body, SCORECARD)
    assert errors == [], f"{case['report']} violated the contract:\n  " + "\n  ".join(errors)


def _check_has_tool_coverage(case):
    fm, _ = _report(case["report"])
    coverage = fm.get("tool_coverage")
    assert coverage, "report has no tool_coverage block"
    for cov in coverage:
        assert "dimension" in cov and "confidence_impact" in cov


def _check_scores_discriminate(case):
    healthy, _ = _report(case["healthy"])
    tangled, _ = _report(case["tangled"])
    hs, ts = healthy["scores"], tangled["scores"]
    for dim in case["expect_worse"]:
        assert ts[dim]["value"] < hs[dim]["value"], (
            f"{dim}: tangled {ts[dim]['value']} not worse than healthy {hs[dim]['value']}"
        )


def _check_findings_target_dimensions(case):
    healthy, _ = _report(case["healthy"])
    tangled, _ = _report(case["tangled"])
    hs, ts = healthy["scores"], tangled["scores"]
    finding_dims = {f["dimension"] for f in tangled.get("findings", [])}
    dropped = [
        dim
        for dim, score in ts.items()
        if dim != META_DIMENSION and score["value"] < hs[dim]["value"]
    ]
    assert dropped, "expected at least one dropped dimension in the bad fixture"
    for dim in dropped:
        assert dim in finding_dims, f"{dim} scored worse but no finding points at it"


def _check_interview_before_score(case):
    fm, _ = _report(case["report"])
    interview = fm.get("interview_context") or {}
    system_map = fm.get("system_map") or {}
    assert interview.get("system_goal"), "no interview context: would be scoring from a cold start"
    assert system_map.get("observed_modules"), (
        "no observed modules: would be scoring from dir shape"
    )
    # Observed modules must be distinct evidence from the declared/intended ones.
    assert system_map.get("declared_modules"), "system map lacks declared modules"


def _check_tool_before_claim(case):
    fm, _ = _report(case["report"])
    for dim, score in fm["scores"].items():
        if dim == META_DIMENSION:
            continue
        assert score.get("evidence_refs"), f"{dim} scored without evidence"


def _check_evidence_cited(case):
    fm, _ = _report(case["report"])
    evidence_ids = {e["id"] for e in fm.get("evidence", [])}
    for finding in fm.get("findings", []):
        refs = finding.get("evidence_refs") or []
        assert refs, f"finding {finding.get('id')} cites no evidence"
        for ref in refs:
            assert ref in evidence_ids, f"finding {finding.get('id')} cites unknown evidence {ref}"


def _check_stable_score_bands(case):
    bands = SCORECARD["bands"]
    for name in case["reports"]:
        fm, _ = _report(name)
        for dim, score in fm["scores"].items():
            expected = band_for_value(score["value"], bands)
            assert score["band"] == expected, (
                f"{name}:{dim} band {score['band']} not derivable from value {score['value']}"
            )


def _check_plan_well_formed(case):
    text = (BASELINE / case["plan"]).read_text()
    for required in ("## Phases", "### Phase 1", "Verification:", "## Acceptance criteria"):
        assert required in text, f"plan missing {required!r}"


def _check_plan_no_rewrite(case):
    text = (BASELINE / case["plan"]).read_text().lower()
    for banned in ("rewrite from scratch", "ground-up rewrite", "greenfield rewrite"):
        assert banned not in text, f"plan proposes a rewrite: {banned!r}"
    assert "incremental" in text, "plan does not state it is incremental"


def _check_noncomparable_explained(case):
    base, _ = _report(case["base"])
    head, _ = _report(case["head"])
    result = compare_reports(base, head, SCORECARD)
    assert not result.comparable, "expected reports to be non-comparable"
    assert result.reason and case["must_mention"] in result.reason, (
        f"non-comparability reason {result.reason!r} does not mention {case['must_mention']!r}"
    )
    assert not result.score_deltas, "non-comparable reports must not invent score trends"


def _check_structured_question_capability(case):
    def cap(target: str):
        overlay = yaml.safe_load((OVERLAYS / target / "frontmatter.yaml").read_text())
        return overlay["capabilities"]["structured_questions"]

    for target in case["concrete"]:
        value = cap(target)
        assert value and value != "unverified", f"{target} has no concrete question tool: {value!r}"
    for target in case["unverified"]:
        assert cap(target) == "unverified", f"{target} must stay unverified"


def _check_fixtures_present(case):
    for name, files in case["fixtures"].items():
        root = FIXTURES / name
        assert (root / "FIXTURE.md").is_file(), f"{name} missing FIXTURE.md"
        for rel in files:
            assert (root / rel).is_file(), f"{name} missing {rel}"


def _check_operational_manifests_present(case):
    root = FIXTURES / case["fixture"]
    for rel in case["manifests"]:
        assert (root / rel).is_file(), f"{case['fixture']} missing operational manifest {rel}"


_CHECKERS = {
    "validates_contract": _check_validates_contract,
    "has_tool_coverage": _check_has_tool_coverage,
    "scores_discriminate": _check_scores_discriminate,
    "findings_target_dimensions": _check_findings_target_dimensions,
    "interview_before_score": _check_interview_before_score,
    "tool_before_claim": _check_tool_before_claim,
    "evidence_cited": _check_evidence_cited,
    "stable_score_bands": _check_stable_score_bands,
    "plan_well_formed": _check_plan_well_formed,
    "plan_no_rewrite": _check_plan_no_rewrite,
    "noncomparable_explained": _check_noncomparable_explained,
    "structured_question_capability": _check_structured_question_capability,
    "fixtures_present": _check_fixtures_present,
    "operational_manifests_present": _check_operational_manifests_present,
}


def test_every_assertion_type_has_a_checker():
    used = {c["assertion"] for c in CASES}
    assert used <= set(_CHECKERS), f"cases use unknown assertions: {used - set(_CHECKERS)}"


@pytest.mark.parametrize("case", CASES, ids=_ids(CASES))
def test_eval_case(case):
    _CHECKERS[case["assertion"]](case)
