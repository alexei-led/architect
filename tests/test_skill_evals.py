"""Minimal lint for skill eval definitions."""

import json
from pathlib import Path

EVALS_ROOT = Path(__file__).parent / "skill-evals"


def test_skill_eval_files_are_well_formed():
    files = sorted(EVALS_ROOT.glob("*/evals/evals.json"))
    assert files, "missing skill eval definitions"
    for path in files:
        data = json.loads(path.read_text())
        assert data["skill_name"]
        assert data["evals"]
        for case in data["evals"]:
            assert case["id"]
            assert case["prompt"]
            assert case["expected_output"]
            assert case["assertions"]
