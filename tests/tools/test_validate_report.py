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


def test_rejects_bool_score_value():
    fm, body, sc = _load()
    fm["scores"]["boundary_integrity"]["value"] = True  # bool is an int subclass
    errors = vr.validate_report(fm, body, sc)
    assert any("boundary_integrity" in e and "must be an int" in e for e in errors)


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


def test_catches_duplicate_evidence_id():
    fm, body, sc = _load()
    fm["evidence"].append({"id": "E1", "type": "file", "ref": "x", "summary": "dup"})
    errors = vr.validate_report(fm, body, sc)
    assert any("duplicate id 'E1'" in e for e in errors)


def test_catches_missing_evidence_summary():
    fm, body, sc = _load()
    fm["evidence"].append({"id": "EZ", "type": "file", "ref": "x"})
    errors = vr.validate_report(fm, body, sc)
    assert any("EZ" in e and "missing summary" in e for e in errors)


def test_catches_duplicate_finding_id():
    fm, body, sc = _load()
    existing = fm["findings"][0]
    fm["findings"].append(dict(existing))
    errors = vr.validate_report(fm, body, sc)
    assert any("duplicate id" in e for e in errors)


def test_catches_unknown_dimension_in_scores():
    fm, body, sc = _load()
    fm["scores"]["phantom"] = {"value": 50, "band": "mixed", "confidence": "medium"}
    errors = vr.validate_report(fm, body, sc)
    assert any("scores.phantom" in e and "unknown dimension" in e for e in errors)


def test_catches_non_dict_scores():
    fm, body, sc = _load()
    fm["scores"] = ["not", "a", "dict"]
    errors = vr.validate_report(fm, body, sc)
    assert any("scores: missing or not a mapping" in e for e in errors)


def test_catches_non_list_evidence_without_crash():
    fm, body, sc = _load()
    fm["evidence"] = "bad"
    errors = vr.validate_report(fm, body, sc)
    assert any("evidence: not a list" in e for e in errors)


def test_catches_missing_interview_context():
    fm, body, sc = _load()
    del fm["interview_context"]
    errors = vr.validate_report(fm, body, sc)
    assert any("interview_context" in e and "missing" in e for e in errors)


def test_catches_empty_interview_system_goal():
    fm, body, sc = _load()
    fm["interview_context"]["system_goal"] = ""
    errors = vr.validate_report(fm, body, sc)
    assert any("interview_context" in e and "system_goal" in e for e in errors)


def test_catches_missing_system_map():
    fm, body, sc = _load()
    del fm["system_map"]
    errors = vr.validate_report(fm, body, sc)
    assert any("system_map: missing" in e for e in errors)


def test_catches_empty_observed_modules():
    fm, body, sc = _load()
    fm["system_map"]["observed_modules"] = []
    errors = vr.validate_report(fm, body, sc)
    assert any("observed_modules" in e for e in errors)


def test_catches_missing_comparability():
    fm, body, sc = _load()
    del fm["comparability"]
    errors = vr.validate_report(fm, body, sc)
    assert any("comparability: missing" in e for e in errors)


def test_catches_empty_comparability_key():
    fm, body, sc = _load()
    fm["comparability"]["scope"] = None
    errors = vr.validate_report(fm, body, sc)
    assert any("comparability" in e and "scope" in e for e in errors)


def test_main_smoke(capsys):
    rc = vr.main([str(EXAMPLE_REPORT), "--scorecard", str(SCORECARD)])
    assert rc == 0
    assert capsys.readouterr().out.rstrip().endswith(": valid")


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


def test_main_exit_code_2_on_unreadable_file(tmp_path, capsys):
    rc = vr.main([str(tmp_path / "nope.md"), "--scorecard", str(SCORECARD)])
    assert rc == 2
    assert "error" in capsys.readouterr().err
