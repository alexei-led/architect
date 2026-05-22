"""Instruction lint: the only automatable Task 3 verification gate.

Walks the architect agent and skills and asserts the structural contract every
instruction file must hold: parseable frontmatter with name/description, required
section headers, no TODO markers, no broken references to template paths, and
valid per-target overlays. The remaining Task 3 verification items are behavioral
and are exercised by the dogfood pass, not here.
"""

import re
from pathlib import Path

import yaml

from architect_tools._contract import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
AGENT_DIR = SRC / "agents" / "architect"
SKILLS_DIR = SRC / "skills"

# Skills introduced by Task 3. Later phases add more under SKILLS_DIR; the lint
# applies to whatever SKILL.md files exist.
TASK3_SKILLS = {
    "architecture-review",
    "architecture-scorecard",
    "architecture-plan",
}
OVERLAY_TARGETS = {"claude", "codex", "pi"}
TEMPLATE_PATH_RE = re.compile(r"src/templates/[\w./-]+")
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")


def skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def instruction_markdown_files() -> list[Path]:
    return [AGENT_DIR / "AGENT.md", *skill_files()]


def test_task3_skills_exist():
    present = {p.parent.name for p in skill_files()}
    assert present >= TASK3_SKILLS, f"missing skills: {TASK3_SKILLS - present}"


def test_agent_and_overlays_present():
    assert (AGENT_DIR / "AGENT.md").is_file()
    for target in OVERLAY_TARGETS:
        assert (AGENT_DIR / target / "frontmatter.yaml").is_file(), target


def test_markdown_frontmatter_has_name_and_description():
    for path in instruction_markdown_files():
        fm, body = split_frontmatter(path.read_text())
        assert fm.get("name"), f"{path} missing name"
        assert fm.get("description"), f"{path} missing description"
        assert body.strip(), f"{path} has empty body"


def test_skill_descriptions_are_activation_style():
    for path in skill_files():
        fm, _ = split_frontmatter(path.read_text())
        assert "use when" in fm["description"].lower(), f"{path} description not activation-style"


def test_skills_have_when_to_use_section():
    for path in skill_files():
        body = path.read_text()
        assert "## When to use" in body, f"{path} missing '## When to use'"


def test_no_todo_markers():
    for path in instruction_markdown_files():
        assert not TODO_RE.search(path.read_text()), f"{path} contains a TODO/FIXME marker"


def test_template_references_resolve():
    for path in instruction_markdown_files():
        for ref in TEMPLATE_PATH_RE.findall(path.read_text()):
            assert (REPO_ROOT / ref).is_file(), f"{path} references missing {ref}"


def test_overlays_parse_and_declare_capability():
    for target in OVERLAY_TARGETS:
        overlay = yaml.safe_load((AGENT_DIR / target / "frontmatter.yaml").read_text())
        assert overlay.get("name") == "architect", target
        assert overlay.get("description"), target
        caps = overlay.get("capabilities", {})
        assert "structured_questions" in caps, f"{target} overlay missing structured_questions"


def test_source_is_read_only_in_overlays():
    """Source-edit tools must be denied in every target overlay."""
    for target in OVERLAY_TARGETS:
        overlay = yaml.safe_load((AGENT_DIR / target / "frontmatter.yaml").read_text())
        denied = set(overlay.get("tools", {}).get("deny", []))
        assert {"Edit", "Write"} <= denied, f"{target} overlay does not deny source edits"


def test_codex_structured_questions_unverified():
    """Codex must not claim a structured-question tool until its runtime is verified."""
    overlay = yaml.safe_load((AGENT_DIR / "codex" / "frontmatter.yaml").read_text())
    assert overlay["capabilities"]["structured_questions"] == "unverified"
