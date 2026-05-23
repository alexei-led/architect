from pathlib import Path

from architect_tools._contract import load_scorecard as _load_scorecard
from architect_tools._contract import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "src" / "templates"


def task_sections(body: str) -> list[str]:
    sections: list[str] = []
    current: list[str] = []

    for line in body.splitlines():
        if line.startswith(("### Task ", "### Iteration ")):
            if current:
                sections.append("\n".join(current))
            current = [line]
            continue

        if current and line.startswith("## "):
            sections.append("\n".join(current))
            current = []
            continue

        if current:
            current.append(line)

    if current:
        sections.append("\n".join(current))

    return sections


def test_report_template_parses():
    fm, body = split_frontmatter((TEMPLATES / "report.md").read_text())
    assert fm["artifact"] == "architecture-report"
    assert fm["schema_version"] == 2
    assert "scores" in fm
    assert "## Executive summary" in body


def test_scorecard_parses():
    scorecard = _load_scorecard(TEMPLATES / "scorecard.yaml")
    assert scorecard["rubric_version"] == 1
    assert scorecard["dimensions"]
    assert scorecard["bands"]


def test_plan_template_has_core_sections():
    body = (TEMPLATES / "plan.md").read_text()
    for section in (
        "## Overview",
        "## Source artifact",
        "## Validation Commands",
        "## Implementation Steps",
        "## Acceptance criteria",
        "## Safety notes",
        "## Re-review",
    ):
        assert section in body
    assert "## Phases" not in body


def test_plan_template_uses_executable_task_sections():
    body = (TEMPLATES / "plan.md").read_text()
    assert "### Task 1:" in body
    assert "### Task 3: Final verification and documentation" in body
    assert "### Phase" not in body

    in_executable_task = False
    for line in body.splitlines():
        if line.startswith("### Task ") or line.startswith("### Iteration "):
            in_executable_task = True
        elif line.startswith("## "):
            in_executable_task = False

        if line.lstrip().startswith(("- [ ]", "- [x]")):
            assert in_executable_task, f"checkbox outside executable task section: {line}"


def test_plan_template_tasks_have_execution_metadata():
    body = (TEMPLATES / "plan.md").read_text()
    sections = task_sections(body)
    assert len(sections) >= 3
    assert "gitnexus impact" in body
    assert "gitnexus detect-changes" in body
    assert "copy/symlink" in body

    for section in sections:
        for label in (
            "Justification:",
            "Files:",
            "Preconditions:",
            "Postconditions:",
            "Impact commands:",
            "Verification commands:",
            "Manual checks:",
        ):
            assert label in section

        assert "- [ ]" in section
        assert section.index("Manual checks:") < section.index("- [ ]")


def test_design_template_has_core_sections():
    body = (TEMPLATES / "design.md").read_text()
    for section in ("## Domain and volatility map", "## Module map", "## Handoff"):
        assert section in body
