"""Minimal template contract tests."""

from pathlib import Path

from architect_tools._contract import load_scorecard as _load_scorecard
from architect_tools._contract import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "src" / "templates"


def test_report_template_parses():
    fm, body = split_frontmatter((TEMPLATES / "report.md").read_text())
    assert fm["artifact"] == "architecture-report"
    assert "scores" in fm
    assert "## Executive summary" in body


def test_scorecard_parses():
    scorecard = _load_scorecard(TEMPLATES / "scorecard.yaml")
    assert scorecard["rubric_version"] == 1
    assert scorecard["dimensions"]
    assert scorecard["bands"]


def test_plan_template_has_core_sections():
    body = (TEMPLATES / "plan.md").read_text()
    for section in ("## Overview", "## Phases", "## Acceptance criteria"):
        assert section in body
