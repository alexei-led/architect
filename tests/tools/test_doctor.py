"""Tests for the doctor helper. Tool probing is faked; no real binaries needed."""

from pathlib import Path

from architect_tools import doctor


def fake_which(present: set[str]):
    return lambda name: f"/usr/bin/{name}" if name in present else None


def fake_run(ok: bool, text: str = "v1.0"):
    return lambda _cmd: (ok, text)


def test_available_tool():
    tool = doctor.TOOLS[0]
    st = doctor.probe_tool(
        tool, ecosystems=None, which=fake_which({tool.version_cmd[0]}), run=fake_run(True, "1.2.3")
    )
    assert st.state == "available"
    assert st.detail == "1.2.3"


def test_missing_tool():
    tool = doctor.TOOLS[0]
    st = doctor.probe_tool(tool, ecosystems=None, which=fake_which(set()), run=fake_run(True))
    assert st.state == "missing"


def test_present_but_version_fails_is_failed():
    tool = doctor.TOOLS[0]
    st = doctor.probe_tool(
        tool,
        ecosystems=None,
        which=fake_which({tool.version_cmd[0]}),
        run=fake_run(False, "boom"),
    )
    assert st.state == "failed"
    assert st.detail == "boom"


def test_applicability_from_ecosystems():
    pydeps = next(t for t in doctor.TOOLS if t.name == "pydeps")  # python-only
    st_py = doctor.probe_tool(pydeps, ecosystems={"python"}, which=fake_which(set()))
    st_go = doctor.probe_tool(pydeps, ecosystems={"go"}, which=fake_which(set()))
    assert st_py.applicable
    assert not st_go.applicable


def test_universal_tool_always_applicable():
    git = next(t for t in doctor.TOOLS if t.name == "git")  # applies_to empty
    st = doctor.probe_tool(git, ecosystems={"go"}, which=fake_which(set()))
    assert st.applicable


def test_detect_ecosystems(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    (tmp_path / "go.mod").write_text("module x\n")
    eco = doctor.detect_ecosystems(tmp_path)
    assert "python" in eco
    assert "go" in eco
    assert "terraform" not in eco


def test_render_shows_missing_install_hint():
    statuses = doctor.run_doctor(which=fake_which(set()), run=fake_run(True))
    out = doctor.render(statuses)
    assert "MISSING" in out
    assert "install:" in out


def test_main_smoke(capsys):
    rc = doctor.main([])
    assert rc == 0
    assert "tool check" in capsys.readouterr().out
