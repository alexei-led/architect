import re
from pathlib import Path

from architect_tools._contract import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
AGENTS_DIR = SRC / "agents"
AGENT_FILE = AGENTS_DIR / "architect" / "AGENT.md"
SKILLS_DIR = SRC / "skills"

TASK3_SKILLS = {
    "architecture-design",
    "architecture-review",
    "architecture-scorecard",
    "architecture-plan",
}
TEMPLATE_PATH_RE = re.compile(r"src/templates/[\w./-]+")
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")


def skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def instruction_markdown_files() -> list[Path]:
    return [AGENT_FILE, *skill_files()]


def test_task3_skills_exist():
    present = {p.parent.name for p in skill_files()}
    assert present >= TASK3_SKILLS, f"missing skills: {TASK3_SKILLS - present}"


def test_single_plain_architect_role_exists():
    agent_files = sorted(AGENTS_DIR.glob("*/AGENT.md"))
    assert agent_files == [AGENT_FILE]
    text = AGENT_FILE.read_text()
    assert text.startswith("# Architect\n")
    assert not text.startswith("---\n"), "source role prompt must not carry runtime frontmatter"


def test_skill_frontmatter_has_name_and_description():
    for path in skill_files():
        fm, body = split_frontmatter(path.read_text())
        assert fm.get("name"), f"{path} missing name"
        assert fm.get("description"), f"{path} missing description"
        assert body.strip(), f"{path} has empty body"


def test_agent_prompt_has_body():
    body = AGENT_FILE.read_text()
    assert "## Operating mode: read-only on source" in body
    assert "## Role + skill composition" in body


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


def test_structured_questions_do_not_depend_on_agent_overlays():
    text = (SKILLS_DIR / "architecture-review" / "SKILL.md").read_text()
    assert "active runtime's exposed tool list" in text
    assert "source agent metadata" in text
    assert "per-target overlays" in text
    assert "only when that tool is actually exposed" in text
    assert "ask exactly one plain prose question" in text


def test_architecture_plan_defaults_to_docs_plans_destination():
    text = (SKILLS_DIR / "architecture-plan" / "SKILL.md").read_text()
    assert "docs/plans/<kebab-case-target>.md" in text
    assert "Create `docs/plans/` if it is missing" in text
    assert "copy/symlink" in text


def test_architecture_plan_requires_task_runner_contract():
    text = (SKILLS_DIR / "architecture-plan" / "SKILL.md").read_text()
    assert "## Implementation Steps" in text
    assert "Final verification and documentation" in text
    assert "gitnexus impact <path-or-symbol>" in text
    assert "gitnexus detect-changes" in text
    assert "Manual checks" in text
    assert "Every task has a file list" in text


def test_architecture_next_skill_routing_is_conditional():
    agent = AGENT_FILE.read_text()
    review = (SKILLS_DIR / "architecture-review" / "SKILL.md").read_text()
    design = (SKILLS_DIR / "architecture-design" / "SKILL.md").read_text()
    plan = (SKILLS_DIR / "architecture-plan" / "SKILL.md").read_text()

    assert "Recommend exactly one primary next skill" in agent
    assert "Tool, methodology, and scorecard skills are supporting skills" in agent
    assert "Existing-code remediation: `architecture-review` → `architecture-design`" in agent
    assert "Greenfield or requirements-to-architecture work: `architecture-design`" in agent
    assert "choose one next skill" in review
    assert "no next skill when the user asked for audit/scoring only" in review
    assert "`architecture-plan` when an approved design already exists" in review
    assert "no next skill when the user only asked for design" in design
    assert "Missing approved target architecture: recommend `architecture-design` before" in plan
