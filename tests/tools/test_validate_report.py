"""Tests for the validate-report helper."""

import copy
from pathlib import Path

from architect_tools import validate_report as vr
from architect_tools._contract import load_report, load_scorecard

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE_REPORT = REPO_ROOT / "tests" / "fixtures" / "reports" / "example.md"
SCORECARD = REPO_ROOT / "src" / "templates" / "scorecard.yaml"


def _load():
    fm, body = load_report(EXAMPLE_REPORT)
    return fm, body, load_scorecard(SCORECARD)


def test_valid_example_report_has_no_violations():
    fm, body, sc = _load()
    assert vr.validate_report(fm, body, sc) == []


def test_catches_missing_score():
    fm, body, sc = _load()
    del fm["scores"]["coupling_balance"]
    errors = vr.validate_report(fm, body, sc)
    assert any("coupling_balance" in e and "missing" in e for e in errors)


def test_catches_missing_confidence():
    fm, body, sc = _load()
    del fm["scores"]["boundary_integrity"]["confidence"]
    errors = vr.validate_report(fm, body, sc)
    assert any("invalid confidence" in e for e in errors)


def test_catches_band_value_mismatch():
    fm, body, sc = _load()
    fm["scores"]["boundary_integrity"]["band"] = "strong"  # value is 48 -> mixed
    errors = vr.validate_report(fm, body, sc)
    assert any("does not match value" in e for e in errors)


def test_catches_low_confidence_high_quality():
    fm, body, sc = _load()
    s = fm["scores"]["dependency_graph_health"]  # 61 serviceable, high
    s["confidence"] = "low"
    errors = vr.validate_report(fm, body, sc)
    assert any("requires at least medium confidence" in e for e in errors)


def test_catches_malformed_evidence_ref():
    fm, body, sc = _load()
    fm["scores"]["boundary_integrity"]["evidence_refs"] = ["E999"]
    errors = vr.validate_report(fm, body, sc)
    assert any("E999" in e and "not found" in e for e in errors)


def test_catches_bad_evidence_type_and_required_field():
    fm, body, sc = _load()
    fm["evidence"].append({"id": "EX", "type": "bogus", "summary": "x"})
    fm["evidence"].append({"id": "EY", "type": "file", "summary": "no ref"})
    errors = vr.validate_report(fm, body, sc)
    assert any("invalid type" in e for e in errors)
    assert any("requires field 'ref'" in e for e in errors)


def test_catches_bad_finding():
    fm, body, sc = _load()
    fm["findings"].append(
        {"id": "FZ", "severity": "bogus", "dimension": "nope", "evidence_refs": ["E404"]}
    )
    errors = vr.validate_report(fm, body, sc)
    assert any("invalid severity" in e for e in errors)
    assert any("unknown dimension" in e for e in errors)
    assert any("E404" in e for e in errors)


def test_catches_missing_section():
    fm, body, sc = _load()
    body = body.replace("## Recommendations", "## Suggestions")
    errors = vr.validate_report(fm, body, sc)
    assert any("Recommendations" in e for e in errors)


def test_catches_bad_tool_coverage():
    fm, body, sc = _load()
    fm["tool_coverage"][0]["confidence_impact"] = "enormous"
    del fm["tool_coverage"][0]["tools_failed"]
    errors = vr.validate_report(fm, body, sc)
    assert any("invalid confidence_impact" in e for e in errors)
    assert any("missing field 'tools_failed'" in e for e in errors)


def test_main_smoke(capsys):
    rc = vr.main([str(EXAMPLE_REPORT), "--scorecard", str(SCORECARD)])
    assert rc == 0
    assert "valid" in capsys.readouterr().out


def test_main_reports_violations(tmp_path, capsys):
    fm, body, _ = _load()
    broken = copy.deepcopy(fm)
    broken["scores"]["boundary_integrity"]["band"] = "strong"
    # rebuild a broken report file
    import yaml

    report = tmp_path / "broken.md"
    report.write_text("---\n" + yaml.safe_dump(broken) + "---\n" + body)
    rc = vr.main([str(report), "--scorecard", str(SCORECARD)])
    assert rc == 1
    assert "violation" in capsys.readouterr().out
