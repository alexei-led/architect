import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "release" / "generate-release-notes.py"


def test_generate_release_notes(tmp_path: Path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [1.2.3] - 2026-05-23\n\n"
        "### Added\n\n- Useful change.\n",
        encoding="utf-8",
    )
    plugin = tmp_path / "plugin.yaml"
    plugin.write_text(
        "name: architecture\nversion: 1.2.3\ndescription: Evidence-based architecture review.\n",
        encoding="utf-8",
    )
    output = tmp_path / "notes.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--tag",
            "v1.2.3",
            "--changelog",
            str(changelog),
            "--plugin",
            str(plugin),
            "--output",
            str(output),
            "--repository",
            "alexei-led/architect",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    notes = output.read_text(encoding="utf-8")
    assert "Useful change." in notes
    assert "architecture" in notes
    assert "pi install git:github.com/alexei-led/architect" in notes
    assert "uv tool install git+https://github.com/alexei-led/architect.git" in notes


def test_generate_release_notes_reads_agentbundler_package_metadata(tmp_path: Path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [1.2.3] - 2026-05-23\n\n- Change.\n", encoding="utf-8")
    package = tmp_path / "architecture.json"
    package.write_text(
        '{"id":"architecture","metadata":{"version":"1.2.3","description":"Review."}}',
        encoding="utf-8",
    )
    output = tmp_path / "notes.md"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--tag",
            "v1.2.3",
            "--changelog",
            str(changelog),
            "--plugin",
            str(package),
            "--output",
            str(output),
            "--repository",
            "alexei-led/architect",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert "architecture" in output.read_text(encoding="utf-8")


def test_generate_release_notes_rejects_version_mismatch(tmp_path: Path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [2.0.0] - 2026-05-23\n\n- Change.\n",
        encoding="utf-8",
    )
    plugin = tmp_path / "plugin.yaml"
    plugin.write_text(
        "name: architecture\nversion: 1.0.0\ndescription: Review.\n",
        encoding="utf-8",
    )
    output = tmp_path / "notes.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--tag",
            "v2.0.0",
            "--changelog",
            str(changelog),
            "--plugin",
            str(plugin),
            "--output",
            str(output),
            "--repository",
            "alexei-led/architect",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "does not match" in result.stderr
