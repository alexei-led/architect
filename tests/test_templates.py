"""Artifact contract tests: report frontmatter, scorecard rules, plan structure.

These assert the Task 2 contract on the templates and example fixtures. The
shipped helper CLIs (Task 7) reuse the same rules; the checks here are kept local
and minimal so the contract is verifiable before those CLIs exist.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "src" / "templates"
REPORT_TEMPLATE = TEMPLATES / "report.md"
PLAN_TEMPLATE = TEMPLATES / "plan.md"
SCORECARD = TEMPLATES / "scorecard.yaml"
EXAMPLE_REPORT = REPO_ROOT / "tests" / "fixtures" / "reports" / "example.md"
EXAMPLE_PLAN = REPO_ROOT / "tests" / "fixtures" / "plans" / "example.md"

META_DIMENSION = "analysis_confidence"


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body) for a Markdown file with YAML frontmatter."""
    if not text.startswith("---\n"):
        raise AssertionError("file does not start with YAML frontmatter")
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm), body


def load_scorecard() -> dict:
    return yaml.safe_load(SCORECARD.read_text())


def band_for_value(value: int, bands: list[dict]) -> str:
    for band in bands:
        if band["min"] <= value <= band["max"]:
            return band["name"]
    raise AssertionError(f"value {value} fits no band")


def confidence_rank(level: str) -> int:
    return {"low": 0, "medium": 1, "high": 2}[level]


def comparability_reason(a: dict, b: dict, keys: list[str]) -> str | None:
    """Return an explicit reason two reports are not comparable, else None."""
    diffs = [k for k in keys if a.get(k) != b.get(k)]
    if not diffs:
        return None
    return "; ".join(f"{k} differs: {a.get(k)!r} vs {b.get(k)!r}" for k in diffs)


def test_report_template_frontmatter_parses():
    fm, body = split_frontmatter(REPORT_TEMPLATE.read_text())
    assert fm["artifact"] == "architecture-report"
    assert "## Executive summary" in body


def test_scorecard_parses_and_defines_contract():
    sc = load_scorecard()
    assert sc["rubric_version"] == 1
    assert {b["name"] for b in sc["bands"]} == {
        "critical",
        "poor",
        "mixed",
        "serviceable",
        "strong",
    }
    names = {d["name"] for d in sc["dimensions"]}
    expected = {
        "boundary_integrity",
        "coupling_balance",
        "dependency_graph_health",
        "cohesion_modularity",
        "change_locality",
        "architecture_fitness",
        "analysis_confidence",
    }
    assert names == expected
    # bands are contiguous 0..100 with inclusive edges
    edges = sorted((b["min"], b["max"]) for b in sc["bands"])
    assert edges[0][0] == 0 and edges[-1][1] == 100
    for (_, prev_max), (next_min, _) in zip(edges, edges[1:], strict=False):
        assert next_min == prev_max + 1


def test_example_report_has_scores_bands_confidence_evidence_coverage():
    sc = load_scorecard()
    fm, _ = split_frontmatter(EXAMPLE_REPORT.read_text())

    scores = fm["scores"]
    assert set(scores) == {d["name"] for d in sc["dimensions"]}

    evidence_ids = {e["id"] for e in fm["evidence"]}
    for name, score in scores.items():
        assert isinstance(score["value"], int) and 0 <= score["value"] <= 100
        assert score["band"] == band_for_value(score["value"], sc["bands"])
        assert score["confidence"] in {"low", "medium", "high"}
        # every non-meta score must carry resolvable evidence
        if name != META_DIMENSION:
            assert score["evidence_refs"], f"{name} has no evidence"
        for ref in score["evidence_refs"]:
            assert ref in evidence_ids, f"{name} cites unknown evidence {ref}"

    # findings reference known evidence and known dimensions
    for finding in fm["findings"]:
        assert finding["id"]
        assert finding["dimension"] in scores
        assert finding["severity"] in {"critical", "high", "medium", "low"}
        for ref in finding["evidence_refs"]:
            assert ref in evidence_ids

    # tool coverage records every state field per dimension
    assert fm["tool_coverage"]
    for cov in fm["tool_coverage"]:
        for field in ("tools_used", "tools_skipped", "tools_missing", "tools_failed"):
            assert field in cov
        assert cov["confidence_impact"] in {"none", "low", "medium", "high"}


def test_low_confidence_cannot_be_presented_as_high_quality():
    sc = load_scorecard()
    rule = sc["rules"]["high_quality_requires_confidence"]
    high_quality = set(rule["bands"])
    min_conf = confidence_rank(rule["min_confidence"])

    def violates(score: dict) -> bool:
        return score["band"] in high_quality and confidence_rank(score["confidence"]) < min_conf

    # the real fixture obeys the rule
    fm, _ = split_frontmatter(EXAMPLE_REPORT.read_text())
    assert not any(violates(s) for s in fm["scores"].values())

    # a serviceable score with low confidence must be caught
    assert violates({"band": "serviceable", "confidence": "low"})
    assert violates({"band": "strong", "confidence": "low"})
    assert not violates({"band": "serviceable", "confidence": "medium"})


def test_example_plan_has_required_structure():
    body = EXAMPLE_PLAN.read_text()
    for section in (
        "## Overview",
        "## Success criteria",
        "## Phases",
        "## Acceptance criteria",
        "## Safety notes",
    ):
        assert section in body, f"missing {section}"
    assert "### Phase 1" in body
    assert "Verification:" in body
    assert "- [ ]" in body  # checkbox tasks


def test_plan_template_has_required_structure():
    body = PLAN_TEMPLATE.read_text()
    for section in (
        "## Overview",
        "## Success criteria",
        "## Phases",
        "## Acceptance criteria",
        "## Safety notes",
    ):
        assert section in body


def test_non_comparable_reports_have_explicit_reason():
    sc = load_scorecard()
    keys = sc["comparability"]["must_match"]
    fm, _ = split_frontmatter(EXAMPLE_REPORT.read_text())
    base = fm["comparability"]

    # identical scope/rubric/coverage: comparable, no reason
    assert comparability_reason(base, dict(base), keys) is None

    # changed rubric version: not comparable, explicit reason names the field
    other = dict(base)
    other["rubric_version"] = base["rubric_version"] + 1
    reason = comparability_reason(base, other, keys)
    assert reason is not None
    assert "rubric_version" in reason
