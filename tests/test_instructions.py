import re
from pathlib import Path

from architect_tools._contract import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
AGENTS_DIR = SRC / "agents"
AGENT_FILE = AGENTS_DIR / "architect.md"
SKILLS_DIR = SRC / "skills"

TASK3_SKILLS = {
    "architecture-design",
    "architecture-review",
    "architecture-scorecard",
    "architecture-plan",
    "tools-archfit",
}
TEMPLATE_PATH_RE = re.compile(
    r"(?:src/templates|\.\./resources/templates|\.\./\.\./resources/templates|"
    r"\.\./\.\./\.\./resources/templates)/[\w./-]+"
)
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")


def skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def instruction_markdown_files() -> list[Path]:
    return [AGENT_FILE, *skill_files()]


def template_reference_files() -> list[Path]:
    return sorted([*AGENTS_DIR.rglob("*.md"), *SKILLS_DIR.rglob("*.md")])


def test_task3_skills_exist():
    present = {p.parent.name for p in skill_files()}
    assert present >= TASK3_SKILLS, f"missing skills: {TASK3_SKILLS - present}"


def test_single_plain_architect_role_exists():
    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    assert agent_files == [AGENT_FILE]
    text = AGENT_FILE.read_text()
    assert text.startswith("---\n")
    assert "# Architect\n" in text


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
    for path in template_reference_files():
        for ref in TEMPLATE_PATH_RE.findall(path.read_text()):
            referenced = REPO_ROOT / ref if ref.startswith("src/") else path.parent / ref
            assert referenced.is_file(), f"{path} references missing {ref}"


def test_structured_questions_do_not_depend_on_agent_overlays():
    text = (SKILLS_DIR / "architecture-review" / "SKILL.md").read_text()
    assert "active runtime's exposed tool list" in text
    assert "source agent metadata" in text
    assert "per-target overlays" in text
    assert "only when that tool is actually exposed" in text
    assert "ask exactly one plain prose question" in text


def test_typescript_tool_guidance_is_local_and_deterministic():
    text = (SKILLS_DIR / "tools-typescript" / "SKILL.md").read_text()
    flat = " ".join(text.split())

    assert "packageManager" in text
    assert "bun.lock" in text
    assert "conflicting" in text.lower()
    assert "Do not install or download" in text
    assert "npx" in text
    assert "pnpm dlx" in text
    assert "tools_missing" in text
    assert "dynamic imports" in text
    assert "hypotheses" in text
    assert "configured scripts" in flat
    assert "<detected-runner> run <configured-script>" in text
    assert "\nnpm run <configured-script>" not in text
    assert "test -x node_modules/.bin/eslint" in text


def test_architecture_plan_requires_confirmed_file_destination():
    text = (SKILLS_DIR / "architecture-plan" / "SKILL.md").read_text()
    assert "docs/plans/<kebab-case-target>.md" in text
    assert "Create `docs/plans/`\nonly after the destination is confirmed" in text
    assert "return it in the conversation unless they confirm a file path" in text
    assert "copy/symlink" in text


def test_architecture_plan_requires_task_runner_contract():
    text = (SKILLS_DIR / "architecture-plan" / "SKILL.md").read_text()
    assert "## Implementation Steps" in text
    assert "Final verification and documentation" in text
    assert "gitnexus impact <path-or-symbol>" in text
    assert "gitnexus detect-changes" in text
    assert "Manual checks" in text
    assert "Every task has a file list" in text


def test_archfit_calibration_instructions_exist():
    review = (SKILLS_DIR / "architecture-review" / "SKILL.md").read_text()
    agent = AGENT_FILE.read_text()
    tool = (SKILLS_DIR / "tools-archfit" / "SKILL.md").read_text()

    assert "archfit_calibration" in review
    assert "module_volatility" in review
    assert "confirmed" in review
    assert "severity_adjusted" in tool
    assert "false_positive_or_noise" in tool
    assert "missed_by_archfit" in tool
    assert "Do not pass through" in tool
    assert "calibration matrix" in agent


def test_coverage_gap_calibration_documented():
    raw = (SKILLS_DIR / "architecture-scorecard" / "SKILL.md").read_text()
    flat = " ".join(raw.split())
    assert "Coverage-gap calibration" in raw
    assert "primary" in raw.lower()
    assert "cap the band at `mixed`" in flat


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
