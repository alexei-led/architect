"""Validate an architecture report against the scorecard contract.

Checks frontmatter structure, score bands and confidence, the
low-confidence ceiling on high quality, evidence references and their schema,
finding IDs, required body sections, and tool-coverage shape. Reuses the rules
in :mod:`architect_tools._contract`; it does not re-derive them.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from architect_tools._contract import (
    CONFIDENCE_LEVELS,
    COVERAGE_DIMENSIONS,
    COVERAGE_IMPACTS,
    COVERAGE_STATE_FIELDS,
    EVIDENCE_REQUIRED_FIELD,
    EVIDENCE_TYPES,
    FINDING_NARRATIVE_FIELDS,
    META_DIMENSION,
    REQUIRED_SECTIONS,
    SEVERITIES,
    band_for_value,
    confidence_rank,
    load_report,
    load_scorecard,
)


def validate_report(frontmatter: dict[str, Any], body: str, scorecard: dict[str, Any]) -> list[str]:
    """Return a list of contract violations; empty means the report is valid."""
    errors: list[str] = []
    bands = scorecard["bands"]
    dimensions = [d["name"] for d in scorecard["dimensions"]]
    rules = scorecard["rules"]

    _check_structural_blocks(frontmatter, scorecard, errors)

    scores = frontmatter.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores: missing or not a mapping")
        scores = {}

    missing = set(dimensions) - set(scores)
    for name in sorted(missing):
        errors.append(f"scores.{name}: missing score for required dimension")

    evidence_ids = _check_evidence(frontmatter.get("evidence"), errors)

    _check_scores(scores, dimensions, bands, rules, evidence_ids, errors)
    schema_version = frontmatter.get("schema_version")
    _check_findings(
        frontmatter.get("findings"),
        dimensions,
        evidence_ids,
        errors,
        require_narrative=isinstance(schema_version, int) and schema_version >= 2,
    )
    _check_tool_coverage(frontmatter.get("tool_coverage"), errors)
    _check_sections(body, errors)

    return errors


def _check_structural_blocks(
    frontmatter: dict[str, Any], scorecard: dict[str, Any], errors: list[str]
) -> None:
    """Enforce the three structural frontmatter blocks every report must carry."""
    interview = frontmatter.get("interview_context")
    if not isinstance(interview, dict):
        errors.append("interview_context: missing or not a mapping")
    elif not interview.get("system_goal"):
        errors.append("interview_context: missing or empty system_goal")

    system_map = frontmatter.get("system_map")
    if not isinstance(system_map, dict):
        errors.append("system_map: missing or not a mapping")
    else:
        for key in ("observed_modules", "declared_modules"):
            if not system_map.get(key):
                errors.append(f"system_map: missing or empty {key}")

    comparability = frontmatter.get("comparability")
    if not isinstance(comparability, dict):
        errors.append("comparability: missing or not a mapping")
        return
    must_match = scorecard.get("comparability", {}).get("must_match", [])
    for key in must_match:
        if comparability.get(key) in (None, ""):
            errors.append(f"comparability: missing or empty {key}")


def _check_evidence(evidence: Any, errors: list[str]) -> set[str]:
    evidence_ids: set[str] = set()
    if evidence is None:
        evidence = []
    if not isinstance(evidence, list):
        errors.append("evidence: not a list")
        return evidence_ids
    for i, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{i}]: not a mapping")
            continue
        eid = item.get("id")
        if not eid:
            errors.append(f"evidence[{i}]: missing id")
        else:
            if eid in evidence_ids:
                errors.append(f"evidence[{i}]: duplicate id {eid!r}")
            evidence_ids.add(eid)
        etype = item.get("type")
        if etype not in EVIDENCE_TYPES:
            errors.append(f"evidence[{eid or i}]: invalid type {etype!r}")
            continue
        required = EVIDENCE_REQUIRED_FIELD.get(etype)
        if required and not item.get(required):
            errors.append(f"evidence[{eid or i}]: type {etype!r} requires field {required!r}")
        if not item.get("summary"):
            errors.append(f"evidence[{eid or i}]: missing summary")
    return evidence_ids


def _check_scores(
    scores: dict[str, Any],
    dimensions: list[str],
    bands: list[dict[str, Any]],
    rules: dict[str, Any],
    evidence_ids: set[str],
    errors: list[str],
) -> None:
    high_rule = rules["high_quality_requires_confidence"]
    high_bands = set(high_rule["bands"])
    min_conf = confidence_rank(high_rule["min_confidence"])

    for name, score in scores.items():
        if name not in dimensions:
            errors.append(f"scores.{name}: unknown dimension")
            continue
        if not isinstance(score, dict):
            errors.append(f"scores.{name}: not a mapping")
            continue

        value = score.get("value")
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
            errors.append(f"scores.{name}: value must be an int in 0..100, got {value!r}")
            value = None

        confidence = score.get("confidence")
        if confidence not in CONFIDENCE_LEVELS:
            errors.append(f"scores.{name}: invalid confidence {confidence!r}")
            confidence = None

        band = score.get("band")
        if value is not None:
            expected = band_for_value(value, bands)
            if band != expected:
                errors.append(
                    f"scores.{name}: band {band!r} does not match value {value} "
                    f"(expected {expected!r})"
                )

        # Low confidence cannot be presented as high quality.
        if band in high_bands and confidence is not None and confidence_rank(confidence) < min_conf:
            errors.append(
                f"scores.{name}: band {band!r} requires at least "
                f"{high_rule['min_confidence']} confidence, got {confidence!r}"
            )

        refs = score.get("evidence_refs") or []
        if rules.get("score_requires_evidence") and name != META_DIMENSION and not refs:
            errors.append(f"scores.{name}: missing evidence_refs")
        for ref in refs:
            if ref not in evidence_ids:
                errors.append(f"scores.{name}: evidence ref {ref!r} not found in evidence")


def _check_findings(
    findings: Any,
    dimensions: list[str],
    evidence_ids: set[str],
    errors: list[str],
    *,
    require_narrative: bool,
) -> None:
    if findings is None:
        findings = []
    if not isinstance(findings, list):
        errors.append("findings: not a list")
        return
    seen: set[str] = set()
    for i, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"findings[{i}]: not a mapping")
            continue
        fid = finding.get("id")
        if not fid:
            errors.append(f"findings[{i}]: missing id")
        else:
            if fid in seen:
                errors.append(f"findings[{i}]: duplicate id {fid!r}")
            seen.add(fid)
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"findings[{fid or i}]: invalid severity {finding.get('severity')!r}")
        if finding.get("dimension") not in dimensions:
            errors.append(f"findings[{fid or i}]: unknown dimension {finding.get('dimension')!r}")
        if not finding.get("recommended_action"):
            errors.append(f"findings[{fid or i}]: missing recommended_action")
        if require_narrative:
            _check_finding_narrative(finding, fid or i, errors)
        for ref in finding.get("evidence_refs") or []:
            if ref not in evidence_ids:
                errors.append(f"findings[{fid or i}]: evidence ref {ref!r} not found in evidence")


def _check_finding_narrative(finding: dict[str, Any], label: str | int, errors: list[str]) -> None:
    narrative = finding.get("narrative")
    if not isinstance(narrative, dict):
        errors.append(f"findings[{label}]: missing narrative")
        return
    for field in FINDING_NARRATIVE_FIELDS:
        value = narrative.get(field)
        if field == "cascading_change_scenarios":
            if not isinstance(value, list) or not value or not all(value):
                errors.append(f"findings[{label}].narrative.{field}: missing non-empty list")
            continue
        if not value:
            errors.append(f"findings[{label}].narrative.{field}: missing or empty")


def _check_tool_coverage(coverage: Any, errors: list[str]) -> None:
    if coverage is None or coverage == []:
        errors.append("tool_coverage: missing or empty")
        return
    if not isinstance(coverage, list):
        errors.append("tool_coverage: not a list")
        return
    for i, cov in enumerate(coverage):
        if not isinstance(cov, dict):
            errors.append(f"tool_coverage[{i}]: not a mapping")
            continue
        dim = cov.get("dimension")
        if dim not in COVERAGE_DIMENSIONS:
            errors.append(f"tool_coverage[{i}]: invalid dimension {dim!r}")
        for field in COVERAGE_STATE_FIELDS:
            if field not in cov:
                errors.append(f"tool_coverage[{dim or i}]: missing field {field!r}")
        if cov.get("confidence_impact") not in COVERAGE_IMPACTS:
            errors.append(
                f"tool_coverage[{dim or i}]: invalid confidence_impact "
                f"{cov.get('confidence_impact')!r}"
            )


def _check_sections(body: str, errors: list[str]) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"body: missing required section {section!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an architecture report.")
    parser.add_argument("report", type=Path, help="path to the report Markdown file")
    parser.add_argument(
        "--scorecard",
        type=Path,
        default=None,
        help="path to a scorecard.yaml (defaults to the packaged scorecard)",
    )
    args = parser.parse_args(argv)

    try:
        frontmatter, body = load_report(args.report)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read report: {exc}", file=sys.stderr)
        return 2

    scorecard = load_scorecard(args.scorecard)
    errors = validate_report(frontmatter, body, scorecard)
    if errors:
        print(f"{args.report}: {len(errors)} violation(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"{args.report}: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
