"""Shared artifact-contract helpers for the architect CLIs.

Single source of the report/scorecard rules used by validate_report and
compare_reports, and by the contract tests. These functions parse and reason
about the artifact contract; they never wrap evidence tools.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - declared dependency
    raise SystemExit(
        "PyYAML is required for architect helpers. Install it with `uv sync` "
        "or `pip install pyyaml`."
    ) from exc

PACKAGE_ROOT = Path(__file__).resolve().parent
# Default scorecard ships with the package source tree.
DEFAULT_SCORECARD = PACKAGE_ROOT.parent / "templates" / "scorecard.yaml"

META_DIMENSION = "analysis_confidence"
CONFIDENCE_LEVELS = ("low", "medium", "high")
SEVERITIES = ("critical", "high", "medium", "low")
EVIDENCE_TYPES = ("file", "command", "graph-query", "interview")
# Type-dependent required field per evidence entry.
EVIDENCE_REQUIRED_FIELD = {
    "file": "ref",
    "command": "command",
    "graph-query": "query",
}
COVERAGE_DIMENSIONS = (
    "discovery",
    "structural",
    "semantic",
    "dependency",
    "change",
    "operational",
    "security",
    "report",
)
COVERAGE_IMPACTS = ("none", "low", "medium", "high")
COVERAGE_STATE_FIELDS = ("tools_used", "tools_skipped", "tools_missing", "tools_failed")

# Body H2 sections every report must carry. "Plan summary" is conditional and
# omitted here on purpose.
REQUIRED_SECTIONS = (
    "## Executive summary",
    "## Interview context",
    "## System map",
    "## Intended architecture",
    "## Observed architecture",
    "## Score map",
    "## Key findings",
    "## Coupling review",
    "## Boundary violations",
    "## Change locality and hotspots",
    "## Recommendations",
    "## Evidence appendix",
    "## Tool coverage and gaps",
)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter dict, body) for a Markdown file with YAML frontmatter."""
    if not text.startswith("---\n"):
        raise ValueError("file does not start with YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter is not closed by a '---' line")
    _, fm, body = parts
    parsed = yaml.safe_load(fm)
    if not isinstance(parsed, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return parsed, body


def load_report(path: Path) -> tuple[dict[str, Any], str]:
    return split_frontmatter(Path(path).read_text())


def load_scorecard(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or DEFAULT_SCORECARD).read_text())


def is_int_score(value: Any) -> bool:
    """True for genuine integer scores, excluding bool (a subclass of int)."""
    return isinstance(value, int) and not isinstance(value, bool)


def band_for_value(value: int, bands: list[dict[str, Any]]) -> str | None:
    for band in bands:
        if band["min"] <= value <= band["max"]:
            return band["name"]
    return None


def confidence_rank(level: str) -> int:
    return {"low": 0, "medium": 1, "high": 2}[level]


def comparability_reason(a: dict[str, Any], b: dict[str, Any], keys: list[str]) -> str | None:
    """Return an explicit reason two reports are not comparable, else None.

    A must-match key absent (None) from either report is itself a
    non-comparability reason: comparability cannot be established without it,
    so two reports that both omit the comparability block are not comparable.
    """
    reasons = []
    for k in keys:
        av, bv = a.get(k), b.get(k)
        if av is None or bv is None:
            reasons.append(f"{k} missing: {av!r} vs {bv!r}")
        elif av != bv:
            reasons.append(f"{k} differs: {av!r} vs {bv!r}")
    if not reasons:
        return None
    return "; ".join(reasons)
