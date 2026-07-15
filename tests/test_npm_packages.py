import json
import struct
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STAGE_SCRIPT = REPO_ROOT / "scripts" / "release" / "stage_npm_packages.py"
IMAGE = REPO_ROOT / "assets" / "architect-card.png"

EXPECTED = {
    "pi": {
        "name": "@alexeiled/architect",
        "top_level": {"LICENSE", "README.md", "agents", "package.json", "resources", "skills"},
    },
    "claude": {
        "name": "@alexeiled/architect-claude",
        "top_level": {
            ".claude-plugin",
            "LICENSE",
            "README.md",
            "agents",
            "package.json",
            "resources",
            "skills",
        },
    },
    "codex": {
        "name": "@alexeiled/architect-codex",
        "top_level": {
            ".codex-plugin",
            "LICENSE",
            "README.md",
            "agents",
            "package.json",
            "resources",
            "skills",
        },
    },
}


def test_stage_npm_packages_contains_only_runtime_files(tmp_path: Path):
    output = tmp_path / "npm"
    result = subprocess.run(
        [sys.executable, str(STAGE_SCRIPT), "--output", str(output)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    version = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    for target, expected in EXPECTED.items():
        package_dir = output / target
        top_level = {path.name for path in package_dir.iterdir()}
        manifest = json.loads((package_dir / "package.json").read_text(encoding="utf-8"))

        assert top_level == expected["top_level"]
        assert manifest["name"] == expected["name"]
        assert manifest["version"] == version
        assert manifest["publishConfig"] == {"access": "public"}
        assert "test" not in top_level
        assert "tests" not in top_level
        assert "media" not in top_level


def test_pi_package_references_extension_image(tmp_path: Path):
    output = tmp_path / "npm"
    subprocess.run(
        [sys.executable, str(STAGE_SCRIPT), "--output", str(output)],
        cwd=REPO_ROOT,
        check=True,
    )
    manifest = json.loads((output / "pi" / "package.json").read_text(encoding="utf-8"))

    assert manifest["pi"]["image"].endswith("/assets/architect-card.png")


def test_extension_image_is_optimized_card_size():
    data = IMAGE.read_bytes()

    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert (width, height) == (160, 100)
    assert len(data) < 100_000
