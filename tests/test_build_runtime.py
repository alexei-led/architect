import json
import re
import tomllib
from pathlib import Path

from architect_tools._contract import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_REFERENCE_RE = re.compile(r"`([^`]*resources/templates/[\w./-]+)`")


def read_json(path: str):
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def file_inventory(root: Path, directories: tuple[str, ...]) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for directory in directories
        for path in (root / directory).rglob("*")
        if path.is_file()
    }


def test_bundle_declares_every_agentbundler_target():
    manifest = read_json("agentbundle.json")
    assert manifest["targets"] == ["claude", "codex", "pi", "copilot", "grok", "cursor"]
    assert {entry["target"]: entry["profile"] for entry in manifest["composition"]} == {
        "claude": "package",
        "codex": "package",
        "pi": "package",
        "copilot": "package",
        "grok": "project",
        "cursor": "package",
    }

    assets = read_json("src/packages/architecture.json")["assets"]
    declared_skills = {asset["path"] for asset in assets if asset["path"].startswith("skills/")}
    source_skills = {
        path.parent.relative_to(REPO_ROOT / "src").as_posix()
        for path in (REPO_ROOT / "src/skills").glob("*/SKILL.md")
    }
    assert declared_skills == source_skills

    resources = next(asset for asset in assets if asset["path"] == "resources/templates")
    assert resources["targets"] == manifest["targets"]
    agent = next(asset for asset in assets if asset["path"] == "agents/architect.md")
    assert agent["targets"] == ["claude", "codex", "pi", "copilot", "cursor"]


def test_runtime_versions_and_dependencies_match_canonical_package():
    source_package = read_json("src/packages/architecture.json")
    version = source_package["metadata"]["version"]
    dependencies = source_package["metadata"]["dependencies"]

    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    assert pyproject["project"]["version"] == version
    lock = tomllib.loads((REPO_ROOT / "uv.lock").read_text())
    architect_lock = next(package for package in lock["package"] if package["name"] == "architect")
    assert architect_lock["version"] == version
    init = (REPO_ROOT / "src/architect_tools/__init__.py").read_text()
    assert re.search(rf'^__version__ = "{re.escape(version)}"$', init, re.MULTILINE)

    root_pi = read_json("package.json")
    assert root_pi["version"] == version
    assert root_pi["dependencies"] == dependencies

    claude_marketplace = read_json(".claude-plugin/marketplace.json")
    assert claude_marketplace["version"] == version
    assert claude_marketplace["plugins"][0]["version"] == version
    for path in (".github/plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
        marketplace = read_json(path)
        assert marketplace["version"] == version
        assert marketplace["metadata"]["version"] == version
    assert read_json(".github/plugin/marketplace.json")["plugins"][0]["version"] == version

    generated_manifests = (
        "dist/claude/.claude-plugin/plugin.json",
        "dist/codex/.codex-plugin/plugin.json",
        "dist/pi/package.json",
        "dist/copilot/plugin.json",
        "dist/cursor/.cursor-plugin/plugin.json",
    )
    for path in generated_manifests:
        assert read_json(path)["version"] == version
    assert read_json("dist/pi/package.json")["dependencies"] == dependencies
    assert read_json("dist/.agentbundler/build.json")["compiler"]["version"]


def test_runtime_discovery_manifests_point_to_generated_artifacts():
    claude_marketplace = read_json(".claude-plugin/marketplace.json")
    assert (
        claude_marketplace["$schema"] == "https://json.schemastore.org/claude-code-marketplace.json"
    )
    assert claude_marketplace["owner"] == {"name": "Alexei Ledenev"}
    assert claude_marketplace["plugins"][0]["source"] == "./dist/claude"
    assert claude_marketplace["plugins"][0]["author"] == {"name": "Alexei Ledenev"}
    codex_marketplace_plugin = read_json(".agents/plugins/marketplace.json")["plugins"][0]
    assert codex_marketplace_plugin["source"] == {
        "source": "local",
        "path": "./dist/codex",
    }
    assert codex_marketplace_plugin["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
    assert codex_marketplace_plugin["category"] == "Productivity"

    copilot_marketplace = read_json(".github/plugin/marketplace.json")
    assert copilot_marketplace["plugins"][0]["source"] == "./dist/copilot"
    cursor_marketplace = read_json(".cursor-plugin/marketplace.json")
    assert cursor_marketplace["plugins"][0]["source"] == "dist/cursor"

    root_pi_package = read_json("package.json")
    assert root_pi_package["dependencies"] == {"pi-subagents": "0.34.0"}
    assert root_pi_package["pi"] == {
        "skills": ["./dist/pi/skills"],
        "subagents": {"agents": ["./dist/pi/agents"]},
    }

    claude_plugin = read_json("dist/claude/.claude-plugin/plugin.json")
    assert (
        claude_plugin["$schema"] == "https://json.schemastore.org/claude-code-plugin-manifest.json"
    )
    assert claude_plugin["author"] == {"name": "Alexei Ledenev"}
    assert claude_plugin["homepage"] == "https://github.com/alexei-led/architect"
    assert claude_plugin["keywords"] == ["architecture", "code-review", "modularity"]

    codex_plugin = read_json("dist/codex/.codex-plugin/plugin.json")
    assert codex_plugin["author"] == {"name": "Alexei Ledenev"}
    assert codex_plugin["homepage"] == "https://github.com/alexei-led/architect"
    assert codex_plugin["interface"]["displayName"] == "Architect"
    assert codex_plugin["interface"]["category"] == "Productivity"
    assert codex_plugin["interface"]["capabilities"] == ["Read"]
    assert codex_plugin["skills"] == "./skills"
    assert "agents" not in codex_plugin

    copilot_plugin = read_json("dist/copilot/plugin.json")
    assert copilot_plugin["skills"] == ["skills/"]
    assert copilot_plugin["agents"] == "agents/"


def test_compiled_runtime_artifacts_exist_and_use_compiled_template_paths():
    package_roots = [
        REPO_ROOT / "dist/claude",
        REPO_ROOT / "dist/codex",
        REPO_ROOT / "dist/pi",
        REPO_ROOT / "dist/copilot",
        REPO_ROOT / "dist/cursor",
    ]
    project_roots = [REPO_ROOT / "dist/grok/.grok"]
    assert (REPO_ROOT / "dist/copilot/plugin.json").is_file()
    assert (REPO_ROOT / "dist/cursor/.cursor-plugin/plugin.json").is_file()
    pi_package = read_json("dist/pi/package.json")
    assert pi_package["dependencies"] == {"pi-subagents": "0.34.0"}
    assert pi_package["pi"] == {
        "skills": ["./skills"],
        "subagents": {"agents": ["./agents"]},
    }
    expected_skills = {path.parent.name for path in (REPO_ROOT / "src/skills").glob("*/SKILL.md")}
    for root in package_roots + project_roots:
        generated_skills = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
        assert generated_skills == expected_skills
        assert (root / "resources/templates/scorecard.yaml").is_file()
        skill = root / "skills/architecture-review/SKILL.md"
        assert skill.is_file()
        assert (root / "skills/architecture-design/SKILL.md").is_file()
        assert (root / "resources/templates/design.md").is_file()
        text = skill.read_text(encoding="utf-8")
        assert "src/templates/" not in text
        assert "../../resources/templates/report.md" in text

    assert (REPO_ROOT / "dist/copilot/agents/architect.agent.md").is_file()
    assert not (REPO_ROOT / "dist/grok/.grok/agents").exists()
    assert (REPO_ROOT / "dist/claude/agents/architect.md").is_file()
    assert (REPO_ROOT / "dist/cursor/agents/architect.md").is_file()
    assert (REPO_ROOT / "dist/codex/agents/architect.toml").is_file()
    pi_agent = REPO_ROOT / "dist/pi/agents/architect.md"
    assert pi_agent.is_file()
    assert "name: architect" in pi_agent.read_text(encoding="utf-8")
    assert "inheritProjectContext: true" in pi_agent.read_text(encoding="utf-8")
    assert "inheritSkills: true" in pi_agent.read_text(encoding="utf-8")
    for target in ("claude", "codex", "pi", "copilot", "cursor"):
        assert (REPO_ROOT / "dist" / target / "README.md").is_file()


def test_grok_project_tree_matches_claude_package_content():
    claude_root = REPO_ROOT / "dist/claude"
    grok_root = REPO_ROOT / "dist/grok/.grok"
    assert file_inventory(grok_root, ("skills", "resources")) == file_inventory(
        claude_root, ("skills", "resources")
    )
    assert (claude_root / "agents/architect.md").is_file()
    assert not (grok_root / "agents").exists()


def test_generated_template_references_resolve_for_every_target():
    for target in ("claude", "codex", "pi", "copilot", "grok", "cursor"):
        root = REPO_ROOT / "dist" / target
        for path in sorted([*root.rglob("*.md"), *root.rglob("*.toml")]):
            for ref in TEMPLATE_REFERENCE_RE.findall(path.read_text(encoding="utf-8")):
                assert (path.parent / ref).is_file(), f"{path} references missing {ref}"


def test_architect_target_models_are_rendered():
    claude_overlay = read_json("src/agents/.agentbundler/targets/claude.json")
    assert claude_overlay["frontmatterPatch"] == {
        "model": "fable",
        "effort": "xhigh",
    }
    copilot_overlay = read_json("src/agents/.agentbundler/targets/copilot.json")
    assert copilot_overlay["frontmatterPatch"] == {"model": "MAI-Code-1-Flash"}

    claude_frontmatter, _ = split_frontmatter(
        (REPO_ROOT / "dist/claude/agents/architect.md").read_text(encoding="utf-8")
    )
    assert claude_frontmatter["model"] == "fable"
    assert claude_frontmatter["effort"] == "xhigh"

    copilot_frontmatter, _ = split_frontmatter(
        (REPO_ROOT / "dist/copilot/agents/architect.agent.md").read_text(encoding="utf-8")
    )
    assert copilot_frontmatter["model"] == "MAI-Code-1-Flash"

    for path in (
        "dist/pi/agents/architect.md",
        "dist/cursor/agents/architect.md",
    ):
        frontmatter = (REPO_ROOT / path).read_text(encoding="utf-8").split("---", 2)[1]
        assert '"model"' not in frontmatter and "\nmodel:" not in frontmatter, path
        assert '"effort"' not in frontmatter and "\neffort:" not in frontmatter, path

    codex_agent = tomllib.loads(
        (REPO_ROOT / "dist/codex/agents/architect.toml").read_text(encoding="utf-8")
    )
    assert "model" not in codex_agent
    assert "effort" not in codex_agent


def test_architect_sandbox_mode_is_codex_only():
    codex_agent = tomllib.loads(
        (REPO_ROOT / "dist/codex/agents/architect.toml").read_text(encoding="utf-8")
    )
    assert codex_agent["name"] == "architect"
    assert codex_agent["sandbox_mode"] == "read-only"
    assert "You design and review software architecture" in codex_agent["developer_instructions"]
    assert "../resources/templates/scorecard.yaml" in codex_agent["developer_instructions"]

    for target, path in {
        "claude": "dist/claude/agents/architect.md",
        "pi": "dist/pi/agents/architect.md",
        "copilot": "dist/copilot/agents/architect.agent.md",
        "cursor": "dist/cursor/agents/architect.md",
    }.items():
        agent = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert "sandbox_mode" not in agent, target
