import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_json(path: str):
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_runtime_discovery_manifests_point_to_generated_artifacts():
    assert read_json(".claude-plugin/marketplace.json")["plugins"][0]["source"] == (
        "./dist/claude/plugins/architecture"
    )
    assert read_json(".agents/plugins/marketplace.json")["plugins"][0]["source"] == {
        "source": "local",
        "path": "./dist/codex/plugins/architecture",
    }
    assert read_json("package.json")["pi"] == {"skills": ["./dist/pi/skills"]}

    codex_plugin = read_json("dist/codex/plugins/architecture/.codex-plugin/plugin.json")
    assert codex_plugin["skills"] == "./skills"
    assert "agents" not in codex_plugin


def test_compiled_runtime_artifacts_exist_and_use_compiled_template_paths():
    roots = [
        REPO_ROOT / "dist/claude/plugins/architecture",
        REPO_ROOT / "dist/codex/plugins/architecture",
        REPO_ROOT / "dist/pi",
    ]
    for root in roots:
        assert (root / "templates/scorecard.yaml").is_file()
        skill = root / "skills/architecture-review/SKILL.md"
        assert skill.is_file()
        assert (root / "skills/architecture-design/SKILL.md").is_file()
        assert (root / "templates/design.md").is_file()
        text = skill.read_text(encoding="utf-8")
        assert "src/templates/" not in text
        assert "../../templates/report.md" in text

    assert (REPO_ROOT / "dist/claude/plugins/architecture/agents/architect.md").is_file()
    assert (REPO_ROOT / "dist/pi/agents/architect.md").is_file()


def test_codex_custom_agent_is_standalone_toml():
    agent = tomllib.loads((REPO_ROOT / "dist/codex/agents/architect.toml").read_text())
    assert agent["name"] == "architect"
    assert agent["sandbox_mode"] == "read-only"
    assert "You design and review software architecture" in agent["developer_instructions"]
    assert "../templates/scorecard.yaml" in agent["developer_instructions"]
