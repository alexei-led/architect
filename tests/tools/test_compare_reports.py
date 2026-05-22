"""Tests for the compare-reports helper."""

import copy
from pathlib import Path

import yaml

from architect_tools import compare_reports as cr
from architect_tools._contract import load_report, load_scorecard

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE_REPORT = REPO_ROOT / "tests" / "fixtures" / "reports" / "example.md"
SCORECARD = REPO_ROOT / "src" / "templates" / "scorecard.yaml"


def _base():
    fm, _ = load_report(EXAMPLE_REPORT)
    return fm, load_scorecard(SCORECARD)


def test_identical_reports_are_comparable_with_zero_deltas():
    base, sc = _base()
    head = copy.deepcopy(base)
    out = cr.compare_reports(base, head, sc)
    assert out.comparable
    assert all(d == 0 for d in out.score_deltas.values())
    assert all(d == 0 for d in out.confidence_deltas.values())


def test_separates_score_and_confidence_deltas():
    base, sc = _base()
    head = copy.deepcopy(base)
    head["scores"]["boundary_integrity"]["value"] = 60
    head["scores"]["boundary_integrity"]["band"] = "mixed"
    head["scores"]["boundary_integrity"]["confidence"] = "high"
    out = cr.compare_reports(base, head, sc)
    assert out.score_deltas["boundary_integrity"] == 12  # 60 - 48
    assert out.confidence_deltas["boundary_integrity"] == 1  # medium -> high
    # value unchanged but confidence moved: only confidence delta is nonzero
    head["scores"]["coupling_balance"]["confidence"] = "high"
    out = cr.compare_reports(base, head, sc)
    assert out.score_deltas["coupling_balance"] == 0
    assert out.confidence_deltas["coupling_balance"] == 1


def test_bool_score_value_excluded_from_deltas():
    base, sc = _base()
    head = copy.deepcopy(base)
    # bool is an int subclass; True must not be treated as a numeric score 1.
    base["scores"]["boundary_integrity"]["value"] = True
    head["scores"]["boundary_integrity"]["value"] = 60
    out = cr.compare_reports(base, head, sc)
    assert "boundary_integrity" not in out.score_deltas


def test_finding_set_changes():
    base, sc = _base()
    head = copy.deepcopy(base)
    head["findings"] = [
        {"id": "F1", "severity": "high", "dimension": "boundary_integrity", "evidence_refs": []},
        {"id": "F9", "severity": "low", "dimension": "cohesion_modularity", "evidence_refs": []},
    ]
    out = cr.compare_reports(base, head, sc)
    assert out.new_findings == ["F9"]
    assert out.resolved_findings == ["F2"]
    assert out.persisting_findings == ["F1"]


def test_rejects_incompatible_rubric_version():
    base, sc = _base()
    head = copy.deepcopy(base)
    head["comparability"]["rubric_version"] = 2
    out = cr.compare_reports(base, head, sc)
    assert not out.comparable
    assert out.reason is not None and "rubric_version" in out.reason
    assert not out.score_deltas  # no invented trend


def test_rejects_incompatible_scope():
    base, sc = _base()
    head = copy.deepcopy(base)
    head["comparability"]["scope"] = "path-subset"
    out = cr.compare_reports(base, head, sc)
    assert not out.comparable
    assert out.reason is not None and "scope" in out.reason


def test_main_comparable_exit_zero(capsys):
    rc = cr.main([str(EXAMPLE_REPORT), str(EXAMPLE_REPORT), "--scorecard", str(SCORECARD)])
    assert rc == 0
    assert "COMPARABLE" in capsys.readouterr().out


def test_main_noncomparable_exit_one(tmp_path, capsys):
    base, _ = _base()
    head = copy.deepcopy(base)
    head["comparability"]["rubric_version"] = 2
    head_path = tmp_path / "head.md"
    head_path.write_text("---\n" + yaml.safe_dump(head) + "---\n# body\n")
    rc = cr.main([str(EXAMPLE_REPORT), str(head_path), "--scorecard", str(SCORECARD)])
    assert rc == 1
    assert "NOT COMPARABLE" in capsys.readouterr().out
