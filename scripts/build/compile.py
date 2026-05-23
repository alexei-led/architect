#!/usr/bin/env python3
"""Compile runtime plugin artifacts from src/ into dist/."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

GENERATED_DIRS = (
    "dist/claude",
    "dist/codex",
    "dist/pi",
    ".claude-plugin",
    ".agents/plugins",
)
TEMPLATE_REF_SOURCE = "src/templates/"

AGENT_DESCRIPTIONS = {
    "architect": (
        "Read-only architecture reviewer: maps intended vs observed structure, gathers "
        "evidence, scores architecture, and writes plans without editing source."
    ),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return dict(data)


def plugin_manifests(root: Path) -> list[dict[str, Any]]:
    plugins_root = root / "src" / "plugins"
    plugins: list[dict[str, Any]] = []
    for manifest in sorted(plugins_root.glob("*/plugin.yaml")):
        data = load_yaml(manifest)
        data.setdefault("name", manifest.parent.name)
        plugins.append(data)
    if not plugins:
        raise ValueError("no src/plugins/*/plugin.yaml files found")
    return plugins


def ensure_list(value: Any, field: str, manifest_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"plugin {manifest_name!r}: {field} must be a list of strings")
    return value


def reset_generated(root: Path) -> None:
    for rel in GENERATED_DIRS:
        path = root / rel
        if path.exists():
            shutil.rmtree(path)


def copytree(src: Path, dst: Path) -> None:
    if not src.is_dir():
        raise FileNotFoundError(src)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def template_ref_for(path: Path, template_dir: Path) -> str:
    rel = Path(os.path.relpath(template_dir, path.parent)).as_posix()
    if rel == ".":
        return ""
    return rel.rstrip("/") + "/"


def rewrite_template_refs(path: Path, template_dir: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    rewritten = text.replace(TEMPLATE_REF_SOURCE, template_ref_for(path, template_dir))
    if rewritten != text:
        path.write_text(rewritten, encoding="utf-8")


def rewrite_template_refs_in_tree(root: Path, template_dir: Path) -> None:
    for path in root.rglob("*.md"):
        rewrite_template_refs(path, template_dir)


def copy_templates(src_root: Path, dst_root: Path) -> Path:
    template_dir = dst_root / "templates"
    copytree(src_root / "src" / "templates", template_dir)
    return template_dir


def render_markdown(frontmatter: Mapping[str, Any], body: str) -> str:
    meta = yaml.safe_dump(
        dict(frontmatter),
        allow_unicode=True,
        sort_keys=False,
        width=100,
    )
    return f"---\n{meta}---\n\n{body.lstrip()}"


def agent_body(path: Path, out_path: Path, template_dir: Path) -> str:
    body = path.read_text(encoding="utf-8")
    return body.replace(TEMPLATE_REF_SOURCE, template_ref_for(out_path, template_dir))


def agent_description(name: str, plugin: Mapping[str, Any]) -> str:
    if name in AGENT_DESCRIPTIONS:
        return AGENT_DESCRIPTIONS[name]
    description = plugin.get("description")
    if isinstance(description, str) and description:
        return description
    return f"{name} agent"


def write_markdown_agent(
    src: Path, dst: Path, name: str, plugin: Mapping[str, Any], template_dir: Path
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(
        render_markdown(
            {"name": name, "description": agent_description(name, plugin)},
            agent_body(src / "AGENT.md", dst, template_dir),
        ),
        encoding="utf-8",
    )


def toml_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\b", "\\b")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\f", "\\f")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


def toml_multiline(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped.rstrip()}\n"""'


def write_codex_agent(
    src: Path, dst: Path, name: str, plugin: Mapping[str, Any], template_dir: Path
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            f"name = {toml_string(name)}",
            f"description = {toml_string(agent_description(name, plugin))}",
            'sandbox_mode = "read-only"',
            "developer_instructions = "
            + toml_multiline(agent_body(src / "AGENT.md", dst, template_dir)),
            "",
        ]
    )
    dst.write_text(text, encoding="utf-8")


def plugin_metadata(plugin: Mapping[str, Any]) -> dict[str, Any]:
    out = {
        "name": plugin["name"],
        "version": plugin.get("version", "0.0.0"),
    }
    for key in ("description", "author", "license", "homepage", "repository", "keywords"):
        value = plugin.get(key)
        if value is not None:
            out[key] = value
    return out


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compile_plugin(root: Path, plugin: Mapping[str, Any]) -> None:
    name = str(plugin["name"])
    skills = ensure_list(plugin.get("skills"), "skills", name)
    agents = ensure_list(plugin.get("agents"), "agents", name)

    claude_root = root / "dist" / "claude" / "plugins" / name
    codex_root = root / "dist" / "codex" / "plugins" / name
    pi_root = root / "dist" / "pi"

    claude_templates = copy_templates(root, claude_root)
    codex_plugin_templates = copy_templates(root, codex_root)
    codex_agent_templates = copy_templates(root, root / "dist" / "codex")
    pi_templates = copy_templates(root, pi_root)

    for skill in skills:
        src = root / "src" / "skills" / skill
        targets = (
            (claude_root / "skills", claude_templates),
            (codex_root / "skills", codex_plugin_templates),
            (pi_root / "skills", pi_templates),
        )
        for dst_root, template_dir in targets:
            dst = dst_root / skill
            copytree(src, dst)
            rewrite_template_refs_in_tree(dst, template_dir)

    for agent in agents:
        src = root / "src" / "agents" / agent
        if not src.is_dir():
            raise FileNotFoundError(src)
        write_markdown_agent(
            src, claude_root / "agents" / f"{agent}.md", agent, plugin, claude_templates
        )
        write_markdown_agent(src, pi_root / "agents" / f"{agent}.md", agent, plugin, pi_templates)
        write_codex_agent(
            src,
            root / "dist" / "codex" / "agents" / f"{agent}.toml",
            agent,
            plugin,
            codex_agent_templates,
        )

    write_json(claude_root / ".claude-plugin" / "plugin.json", plugin_metadata(plugin))

    codex_meta = plugin_metadata(plugin)
    if skills:
        codex_meta["skills"] = "./skills"
    write_json(codex_root / ".codex-plugin" / "plugin.json", codex_meta)


def write_root_manifests(root: Path, plugins: Sequence[Mapping[str, Any]]) -> None:
    first = plugins[0]
    version = str(first.get("version", "0.0.0"))

    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {
            "name": "alexei-led-architect",
            "plugins": [
                {
                    "name": plugin["name"],
                    "source": f"./dist/claude/plugins/{plugin['name']}",
                    "description": plugin.get("description", ""),
                    "version": plugin.get("version", version),
                }
                for plugin in plugins
            ],
            "version": version,
        },
    )

    write_json(
        root / ".agents" / "plugins" / "marketplace.json",
        {
            "name": "alexei-led-architect",
            "interface": {"displayName": "architect"},
            "plugins": [
                {
                    "name": plugin["name"],
                    "source": {
                        "source": "local",
                        "path": f"./dist/codex/plugins/{plugin['name']}",
                    },
                    "policy": {"installation": "AVAILABLE", "authentication": "ON_USE"},
                }
                for plugin in plugins
            ],
        },
    )

    write_json(
        root / "package.json",
        {
            "name": "architect",
            "version": version,
            "description": first.get("description", ""),
            "keywords": ["pi-package", "architecture", "code-review"],
            "license": first.get("license", "MIT"),
            "homepage": "https://github.com/alexei-led/architect",
            "repository": {
                "type": "git",
                "url": "https://github.com/alexei-led/architect.git",
            },
            "pi": {"skills": ["./dist/pi/skills"]},
        },
    )


def compile_runtime(root: Path) -> None:
    plugins = plugin_manifests(root)
    reset_generated(root)
    for plugin in plugins:
        compile_plugin(root, plugin)
    write_root_manifests(root, plugins)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repo_root())
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        compile_runtime(args.root.resolve())
    except (OSError, ValueError) as exc:
        print(f"compile: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
