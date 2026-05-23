"""Tiny smoke tests for the doctor helper."""

from pathlib import Path

from architect_tools import doctor


def test_detect_ecosystems(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    (tmp_path / "go.mod").write_text("module x\n")
    assert doctor.detect_ecosystems(tmp_path) == {"python", "go"}


def test_missing_tool_renders_install_hint():
    statuses = doctor.run_doctor(which=lambda _name: None, run=lambda _cmd: (True, ""))
    out = doctor.render(statuses)
    assert "MISSING" in out
    assert "install:" in out


def test_main_smoke(capsys, monkeypatch):
    monkeypatch.setattr(doctor, "run_doctor", lambda repo=None: [])
    assert doctor.main([]) == 0
    assert "tool check" in capsys.readouterr().out
