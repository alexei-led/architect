#!/usr/bin/env python3
"""Stage and verify lean npm packages for supported coding agents."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "build" / "npm"
REPOSITORY = "https://github.com/alexei-led/architect"
IMAGE_URL = (
    "https://raw.githubusercontent.com/alexei-led/architect/master/assets/architect-card.png"
)
FORBIDDEN_PARTS = {
    "__pycache__",
    "docs",
    "media",
    "temp",
    "tests",
    "tmp",
}
MAX_UNPACKED_SIZE = 500_000


@dataclass(frozen=True)
class PackageSpec:
    target: str
    name: str
    title: str
    description: str
    files: tuple[str, ...]
    install: str


PACKAGE_SPECS = (
    PackageSpec(
        target="pi",
        name="@alexeiled/architect",
        title="Architect for Pi",
        description="Evidence-based architecture design and review skills and subagent for Pi.",
        files=("agents", "resources", "skills"),
        install="pi install npm:@alexeiled/architect",
    ),
    PackageSpec(
        target="claude",
        name="@alexeiled/architect-claude",
        title="Architect for Claude Code",
        description="Evidence-based architecture design and review plugin for Claude Code.",
        files=(".claude-plugin", "agents", "resources", "skills"),
        install=(
            "claude plugin marketplace add alexei-led/architect\n"
            "claude plugin install architecture@alexei-led-architect"
        ),
    ),
    PackageSpec(
        target="codex",
        name="@alexeiled/architect-codex",
        title="Architect for Codex",
        description="Evidence-based architecture design and review plugin for OpenAI Codex.",
        files=(".codex-plugin", "agents", "resources", "skills"),
        install=(
            "codex plugin marketplace add alexei-led/architect\n"
            "codex plugin add architecture@alexei-led-architect"
        ),
    ),
)


def read_root_package() -> dict[str, Any]:
    return json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))


def package_manifest(spec: PackageSpec, root_package: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "name": spec.name,
        "version": root_package["version"],
        "description": spec.description,
        "keywords": [
            f"{spec.target}-plugin" if spec.target != "pi" else "pi-package",
            "architecture",
            "code-review",
            "coding-agent",
        ],
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "git+https://github.com/alexei-led/architect.git",
        },
        "homepage": f"{REPOSITORY}#readme",
        "bugs": {"url": f"{REPOSITORY}/issues"},
        "files": list(spec.files),
        "publishConfig": {"access": "public"},
    }
    if spec.target == "pi":
        manifest["dependencies"] = root_package["dependencies"]
        manifest["pi"] = {
            "skills": ["./skills"],
            "subagents": {"agents": ["./agents"]},
            "image": IMAGE_URL,
        }
    return manifest


def package_readme(spec: PackageSpec) -> str:
    return f"""<p align=\"center\">
  <img src=\"{IMAGE_URL}\" alt=\"Architect extension card\" width=\"160\" height=\"100\">
</p>

# {spec.title}

{spec.description}

This is the npm runtime payload generated from [{REPOSITORY}]({REPOSITORY}).
It contains only the plugin manifest, agent definitions, skills, and templates required at runtime.

## Install

```sh
{spec.install}
```

## License

MIT
"""


def stage_packages(output: Path) -> None:
    root_package = read_root_package()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for spec in PACKAGE_SPECS:
        source = REPO_ROOT / "dist" / spec.target
        if not source.is_dir():
            raise RuntimeError(f"generated package missing: {source}")
        destination = output / spec.target
        shutil.copytree(source, destination)
        shutil.copy2(REPO_ROOT / "LICENSE", destination / "LICENSE")
        (destination / "README.md").write_text(package_readme(spec), encoding="utf-8")
        (destination / "package.json").write_text(
            json.dumps(package_manifest(spec, root_package), indent=2) + "\n",
            encoding="utf-8",
        )


def parse_pack_output(output: str) -> dict[str, Any]:
    data = json.loads(output)
    if isinstance(data, list):
        if len(data) != 1:
            raise RuntimeError(f"expected one npm package, got {len(data)}")
        return data[0]
    if isinstance(data, dict) and "files" in data:
        return data
    if isinstance(data, dict):
        packages = [
            value for value in data.values() if isinstance(value, dict) and "files" in value
        ]
        if len(packages) == 1:
            return packages[0]
    raise RuntimeError("unexpected npm pack --json output")


def verify_package(spec: PackageSpec, directory: Path) -> None:
    result = subprocess.run(
        ["npm", "pack", "--dry-run", "--json"],
        cwd=directory,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"npm pack failed for {spec.name}:\n{result.stderr.strip()}")

    packed = parse_pack_output(result.stdout)
    packed_paths = {entry["path"] for entry in packed["files"]}
    staged_paths = {
        path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()
    }
    if packed_paths != staged_paths:
        missing = sorted(staged_paths - packed_paths)
        extra = sorted(packed_paths - staged_paths)
        raise RuntimeError(f"{spec.name} tarball mismatch: missing={missing}, extra={extra}")

    top_level = {path.split("/", 1)[0] for path in packed_paths}
    expected_top_level = {"LICENSE", "README.md", "package.json", *spec.files}
    if top_level != expected_top_level:
        raise RuntimeError(
            f"{spec.name} top-level files differ: expected={sorted(expected_top_level)}, "
            f"actual={sorted(top_level)}"
        )

    forbidden = sorted(
        path for path in packed_paths if FORBIDDEN_PARTS.intersection(Path(path).parts)
    )
    if forbidden:
        raise RuntimeError(f"{spec.name} contains forbidden files: {forbidden}")

    unpacked_size = int(packed["unpackedSize"])
    if unpacked_size > MAX_UNPACKED_SIZE:
        raise RuntimeError(f"{spec.name} is too large: {unpacked_size} > {MAX_UNPACKED_SIZE} bytes")

    manifest = json.loads((directory / "package.json").read_text(encoding="utf-8"))
    if manifest["name"] != spec.name:
        raise RuntimeError(f"unexpected package name for {spec.target}: {manifest['name']}")
    if manifest["version"] != read_root_package()["version"]:
        raise RuntimeError(f"version mismatch for {spec.name}")

    print(
        f"{spec.name}@{manifest['version']}: {len(packed_paths)} files, "
        f"{packed['size']} packed bytes, {unpacked_size} unpacked bytes"
    )


def verify_packages(output: Path) -> None:
    for spec in PACKAGE_SPECS:
        verify_package(spec, output / spec.target)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="run npm pack checks after staging")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        stage_packages(args.output)
        if args.check:
            verify_packages(args.output)
    except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"npm packages: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
