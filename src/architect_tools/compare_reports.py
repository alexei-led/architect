"""Compare two architecture reports.

Reports are comparable only when scope, rubric version, and tool coverage level
match. When they differ, this emits an explicit non-comparability reason and
refuses to invent trends. When they match, it reports score deltas and
confidence deltas as separate sections, plus finding-set and tool-coverage
changes.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from architect_tools._contract import (
    comparability_reason,
    confidence_rank,
    load_report,
    load_scorecard,
)


@dataclass
class Comparison:
    comparable: bool
    reason: str | None = None
    score_deltas: dict[str, int] = field(default_factory=dict)
    confidence_deltas: dict[str, int] = field(default_factory=dict)
    new_findings: list[str] = field(default_factory=list)
    resolved_findings: list[str] = field(default_factory=list)
    persisting_findings: list[str] = field(default_factory=list)


def compare_reports(
    base: dict[str, Any],
    head: dict[str, Any],
    scorecard: dict[str, Any],
) -> Comparison:
    """Compare base→head. Non-comparable reports return a reason and no trends."""
    keys = scorecard["comparability"]["must_match"]
    reason = comparability_reason(
        base.get("comparability") or {},
        head.get("comparability") or {},
        keys,
    )
    if reason is not None:
        return Comparison(comparable=False, reason=reason)

    base_scores = base.get("scores") or {}
    head_scores = head.get("scores") or {}
    score_deltas: dict[str, int] = {}
    confidence_deltas: dict[str, int] = {}
    for name in sorted(set(base_scores) & set(head_scores)):
        b, h = base_scores[name], head_scores[name]
        if isinstance(b.get("value"), int) and isinstance(h.get("value"), int):
            score_deltas[name] = h["value"] - b["value"]
        if b.get("confidence") in {"low", "medium", "high"} and h.get("confidence") in {
            "low",
            "medium",
            "high",
        }:
            confidence_deltas[name] = confidence_rank(h["confidence"]) - confidence_rank(
                b["confidence"]
            )

    base_ids = {f["id"] for f in base.get("findings") or [] if f.get("id")}
    head_ids = {f["id"] for f in head.get("findings") or [] if f.get("id")}
    return Comparison(
        comparable=True,
        score_deltas=score_deltas,
        confidence_deltas=confidence_deltas,
        new_findings=sorted(head_ids - base_ids),
        resolved_findings=sorted(base_ids - head_ids),
        persisting_findings=sorted(base_ids & head_ids),
    )


def render(cmp: Comparison) -> str:
    if not cmp.comparable:
        return f"NOT COMPARABLE: {cmp.reason}"

    lines = ["COMPARABLE", "", "Score deltas (head - base):"]
    for name, delta in cmp.score_deltas.items():
        sign = "+" if delta > 0 else ""
        trend = "improved" if delta > 0 else "degraded" if delta < 0 else "unchanged"
        lines.append(f"  {name}: {sign}{delta} ({trend})")

    lines += ["", "Confidence deltas (head - base):"]
    for name, delta in cmp.confidence_deltas.items():
        sign = "+" if delta > 0 else ""
        lines.append(f"  {name}: {sign}{delta}")

    lines += ["", "Findings:"]
    lines.append(f"  new: {', '.join(cmp.new_findings) or 'none'}")
    lines.append(f"  resolved: {', '.join(cmp.resolved_findings) or 'none'}")
    lines.append(f"  persisting: {', '.join(cmp.persisting_findings) or 'none'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two architecture reports.")
    parser.add_argument("base", type=Path, help="baseline report")
    parser.add_argument("head", type=Path, help="newer report")
    parser.add_argument("--scorecard", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        base_fm, _ = load_report(args.base)
        head_fm, _ = load_report(args.head)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read report: {exc}", file=sys.stderr)
        return 2

    scorecard = load_scorecard(args.scorecard)
    cmp = compare_reports(base_fm, head_fm, scorecard)
    print(render(cmp))
    # Non-comparable reports are rejected with a nonzero exit; no trend is emitted.
    return 0 if cmp.comparable else 1


if __name__ == "__main__":
    raise SystemExit(main())
