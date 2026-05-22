"""Tests for the source-to-dist build compiler (Task 8 verification)."""

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_compile():
    spec = importlib.util.spec_from_file_location(
        "architect_compile", REPO_ROOT / "scripts" / "build" / "compile.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compile = _load_compile()


def _agent_frontmatter(text: str) -> dict:
    fm, _ = compile.split_frontmatter(text)
    return fm


def test_renders_all_three_targets():
    rendered = compile.render_all()
    assert set(rendered) == set(compile.TARGETS)


def test_every_target_has_agent_skills_templates_manifest():
    rendered = compile.render_all()
    skill_names = {d.name for d in compile.skill_dirs()}
    for target, files in rendered.items():
        assert "agents/architect.md" in files, target
        assert "plugin.yaml" in files, target
        present_skills = {path.split("/")[1] for path in files if path.startswith("skills/")}
        assert present_skills == skill_names, target
        assert any(p.startswith("templates/") for p in files), target


def test_claude_agent_frontmatter_is_valid_and_flat_readonly():
    rendered = compile.render_all()
    fm = _agent_frontmatter(rendered["claude"]["agents/architect.md"])
    assert fm["name"] == "architect"
    assert fm["description"]
    # tools must be a flat allow-list, never the nested allow/deny overlay shape.
    assert isinstance(fm["tools"], list)
    assert "Read" in fm["tools"]
    # read-only: no source-edit tools leak into the emitted allow-list.
    assert not ({"Edit", "Write", "NotebookEdit"} & set(fm["tools"]))
    assert fm["capabilities"]["structured_questions"] == "AskUserQuestion"


def test_codex_avoids_unverified_structured_question_tool_names():
    rendered = compile.render_all()
    agent = rendered["codex"]["agents/architect.md"]
    fm = _agent_frontmatter(agent)
    # The capability stays a sentinel until the runtime tool name is verified.
    assert fm["capabilities"]["structured_questions"] == "unverified"
    # No concrete structured-question tool name may appear in Codex agent output.
    assert "AskUserQuestion" not in agent
    assert "ask_user_question" not in agent


def test_manifest_references_agent_and_all_skills():
    rendered = compile.render_all()
    skill_paths = {f"skills/{d.name}/SKILL.md" for d in compile.skill_dirs()}
    for target, files in rendered.items():
        manifest = yaml.safe_load(files["plugin.yaml"])
        assert manifest["agents"] == ["agents/architect.md"], target
        assert set(manifest["skills"]) == skill_paths, target
        assert manifest["name"] == "architecture"


def test_output_is_deterministic():
    assert compile.render_all() == compile.render_all()


def test_pi_manifest_requires_cc_thingz():
    """Pi declares its cc-thingz dependency so it can offer ask_user_question."""
    rendered = compile.render_all()
    manifest = yaml.safe_load(rendered["pi"]["plugin.yaml"])
    assert manifest["requires"] == ["alexei-led/cc-thingz"]


def test_only_pi_declares_requires():
    """Claude (native AskUserQuestion) and Codex (unverified) declare no deps."""
    rendered = compile.render_all()
    for target in ("claude", "codex"):
        manifest = yaml.safe_load(rendered[target]["plugin.yaml"])
        assert "requires" not in manifest, target


def test_pi_agent_maps_structured_questions_to_cc_thingz_tool():
    """Regression guard: the requires entry stays linked to the mapped tool."""
    rendered = compile.render_all()
    fm = _agent_frontmatter(rendered["pi"]["agents/architect.md"])
    assert fm["capabilities"]["structured_questions"] == "ask_user_question"


def test_pi_manifest_enumerates_all_skills_for_discovery():
    """Pi discovers skills from the manifest paths; every source skill is listed."""
    rendered = compile.render_all()
    manifest = yaml.safe_load(rendered["pi"]["plugin.yaml"])
    skill_paths = {f"skills/{d.name}/SKILL.md" for d in compile.skill_dirs()}
    assert set(manifest["skills"]) == skill_paths
    assert manifest["agents"] == ["agents/architect.md"]
    for path in manifest["skills"]:
        assert path in rendered["pi"], path


def test_committed_dist_matches_source():
    """The checked-in dist/ must be regenerated, not hand-edited."""
    rendered = compile.render_all()
    drift = compile.check_drift(compile.DEFAULT_DIST, rendered)
    assert drift == [], "dist/ is stale; run scripts/build/compile.py\n" + "\n".join(drift)


def test_drift_check_detects_hand_edits(tmp_path):
    rendered = compile.render_all()
    compile.write_dist(tmp_path, rendered)
    assert compile.check_drift(tmp_path, rendered) == []
    # Hand-edit a generated file.
    edited = tmp_path / "claude" / "agents" / "architect.md"
    edited.write_text(edited.read_text() + "\nhand edit\n")
    drift = compile.check_drift(tmp_path, rendered)
    assert any("differs from source" in line for line in drift)


def test_drift_check_detects_extra_file(tmp_path):
    rendered = compile.render_all()
    compile.write_dist(tmp_path, rendered)
    (tmp_path / "claude" / "stray.md").write_text("not from source")
    drift = compile.check_drift(tmp_path, rendered)
    assert any("not generated from source" in line for line in drift)


def test_flatten_tools_drops_deny():
    assert compile._flatten_tools({"allow": ["Read", "Bash"], "deny": ["Edit"]}) == [
        "Read",
        "Bash",
    ]
    assert compile._flatten_tools(["Read"]) == ["Read"]
    assert compile._flatten_tools(None) == []
