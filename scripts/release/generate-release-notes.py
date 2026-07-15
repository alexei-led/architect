#!/usr/bin/env python3
"""Generate GitHub release notes from CHANGELOG.md and plugin metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path

TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
VERSION_HEADER_RE = re.compile(
    r"^## \[(?P<version>\d+\.\d+\.\d+)\](?:\s+-\s+.*)?\s*$", re.MULTILINE
)


class ReleaseNotesError(RuntimeError):
    """Release notes cannot be generated."""


def version_from_tag(tag: str) -> str:
    match = TAG_RE.fullmatch(tag.strip())
    if match is None:
        raise ReleaseNotesError(f"tag must match vX.Y.Z: {tag}")
    return match.group("version")


def extract_changelog_section(changelog: str, version: str) -> str:
    matches = list(VERSION_HEADER_RE.finditer(changelog))
    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(changelog)
        section = changelog[start:end].strip()
        if not has_body_content(section):
            raise ReleaseNotesError(f"CHANGELOG.md section for {version} is empty")
        return section
    raise ReleaseNotesError(f"CHANGELOG.md is missing section for {version}")


def has_body_content(section: str) -> bool:
    return any(line.strip() and not line.lstrip().startswith("#") for line in section.splitlines())


def read_plugin_metadata(path: Path) -> tuple[str, str, str]:
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            metadata = data.get("metadata", data)
        except (OSError, json.JSONDecodeError) as exc:
            raise ReleaseNotesError(f"cannot read {path}: {exc}") from exc
        name = data.get("id", data.get("name", ""))
        version = metadata.get("version", "")
        description = metadata.get("description", "")
        if not all(isinstance(value, str) and value for value in (name, version, description)):
            raise ReleaseNotesError(f"{path} missing name, version, or description")
        return name, version, description

    name = ""
    version = ""
    description_lines: list[str] = []
    in_description = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip("'\"")
            in_description = False
        elif line.startswith("version:"):
            version = line.split(":", 1)[1].strip().strip("'\"")
            in_description = False
        elif line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            in_description = value in {"|-", "|", ">-", ">"}
            if value and not in_description:
                description_lines.append(value.strip().strip("'\""))
        elif in_description:
            if line and not line.startswith(" "):
                in_description = False
                continue
            description_lines.append(line.strip().strip("'\""))

    description = " ".join(part for part in description_lines if part).strip()
    if not name:
        raise ReleaseNotesError(f"{path} missing name")
    if not version:
        raise ReleaseNotesError(f"{path} missing version")
    if not description:
        raise ReleaseNotesError(f"{path} missing description")
    return name, version, description


def markdown_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def build_release_notes(
    changelog_section: str,
    plugin_name: str,
    plugin_version: str,
    plugin_description: str,
    repository: str,
) -> str:
    return "\n".join(
        [
            "## Changes",
            "",
            changelog_section,
            "",
            "## Plugin",
            "",
            "| Plugin | Version | Description |",
            "| ------ | ------- | ----------- |",
            f"| **{markdown_cell(plugin_name)}** | {markdown_cell(plugin_version)} | "
            f"{markdown_cell(plugin_description)} |",
            "",
            "## Installation",
            "",
            "```sh",
            "pi install npm:@alexeiled/architect",
            "```",
            "",
            "```sh",
            f"claude plugin marketplace add {repository}",
            "claude plugin install architecture@alexei-led-architect",
            "```",
            "",
            "```sh",
            f"codex plugin marketplace add {repository}",
            "codex plugin add architecture@alexei-led-architect",
            "```",
            "",
            "```sh",
            f"uv tool install git+https://github.com/{repository}.git",
            "```",
            "",
        ]
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Release tag, for example v0.2.0")
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--plugin", type=Path, default=Path("src/packages/architecture.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--repository", required=True, help="GitHub repository, for example owner/repo"
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        version = version_from_tag(args.tag)
        changelog_section = extract_changelog_section(
            args.changelog.read_text(encoding="utf-8"), version
        )
        plugin_name, plugin_version, plugin_description = read_plugin_metadata(args.plugin)
        if plugin_version != version:
            raise ReleaseNotesError(
                f"plugin version {plugin_version} does not match tag version {version}"
            )
        notes = build_release_notes(
            changelog_section,
            plugin_name,
            plugin_version,
            plugin_description,
            args.repository,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(notes, encoding="utf-8")
    except (OSError, ReleaseNotesError) as exc:
        print(f"release notes: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
