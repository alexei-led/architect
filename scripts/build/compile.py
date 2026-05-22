"""Source-to-dist compiler for the architect extension.

Compiles one source tree (`src/`) into per-runtime outputs under `dist/` for
Claude, Codex, and Pi. The behavior lives in instructions; this script only
moves and overlays those instructions per target.

Pattern inferred from `cc-thingz` source-to-dist (external; reconcile the exact
layout with cc-thingz when it is accessible). Layout, uniform across targets:

    dist/<target>/
      agents/architect.md          AGENT.md body + target frontmatter overlay
      skills/<name>/SKILL.md        copied verbatim (+ references/)
      templates/<file>              copied verbatim
      plugin.yaml                   manifest with agent + enumerated skills

Output is deterministic: sorted iteration, `safe_dump(sort_keys=False)`, no
timestamps. Recompiling an unchanged source tree reproduces byte-identical
output, which the drift check (`--check`) relies on.
"""

from __future__ import annotations

import argparse
import difflib
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
AGENT_DIR = SRC / "agents" / "architect"
SKILLS_DIR = SRC / "skills"
TEMPLATES_DIR = SRC / "templates"
PLUGIN_META = SRC / "plugins" / "architecture" / "plugin.yaml"
DEFAULT_DIST = REPO_ROOT / "dist"

TARGETS = ("claude", "codex", "pi")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a `---`-delimited YAML frontmatter file into (frontmatter, body)."""
    if not text.startswith("---\n"):
        raise ValueError("file does not start with YAML frontmatter")
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm) or {}, body


def _flatten_tools(tools: Any) -> list[str]:
    """Reduce an overlay `tools` block to a flat allow-list.

    The overlay expresses read-only intent as allow/deny lists. Targets honor a
    flat `tools:` list, and read-only discipline is also enforced by the agent
    prompt, so the deny list (the complement of allow) is dropped on emit.
    """
    if isinstance(tools, dict):
        return list(tools.get("allow", []))
    if isinstance(tools, list):
        return list(tools)
    return []


def build_agent_frontmatter(overlay: dict[str, Any]) -> dict[str, Any]:
    """Normalize an overlay into emitted agent frontmatter, key order fixed."""
    fm: dict[str, Any] = {
        "name": overlay["name"],
        "description": overlay["description"],
    }
    if "model" in overlay:
        fm["model"] = overlay["model"]
    fm["tools"] = _flatten_tools(overlay.get("tools"))
    if "capabilities" in overlay:
        fm["capabilities"] = overlay["capabilities"]
    return fm


def render_agent(target: str) -> str:
    """Render the target agent file: overlay frontmatter + AGENT.md body."""
    _, body = split_frontmatter((AGENT_DIR / "AGENT.md").read_text())
    overlay = yaml.safe_load((AGENT_DIR / target / "frontmatter.yaml").read_text())
    fm = build_agent_frontmatter(overlay)
    fm_text = yaml.safe_dump(fm, sort_keys=False, default_flow_style=False).rstrip("\n")
    return f"---\n{fm_text}\n---\n{body}"


def skill_dirs() -> list[Path]:
    return sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))


def template_files() -> list[Path]:
    return sorted(p for p in TEMPLATES_DIR.iterdir() if p.is_file() and p.name != ".gitkeep")


def render_manifest(target: str) -> str:
    """Build a per-target manifest: static metadata + enumerated agent/skills."""
    meta = yaml.safe_load(PLUGIN_META.read_text())
    manifest: dict[str, Any] = {
        "name": meta["name"],
        "version": meta["version"],
        "description": meta["description"],
        "author": meta.get("author"),
        "license": meta.get("license"),
        "target": target,
        "agents": ["agents/architect.md"],
        "skills": [f"skills/{d.name}/SKILL.md" for d in skill_dirs()],
    }
    return yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False)


def render_target(target: str) -> dict[str, str]:
    """Return the full set of {relative_path: content} for one target."""
    out: dict[str, str] = {"agents/architect.md": render_agent(target)}
    for skill in skill_dirs():
        for path in sorted(skill.rglob("*")):
            if path.is_file():
                rel = path.relative_to(SKILLS_DIR)
                out[f"skills/{rel.as_posix()}"] = path.read_text()
    for tmpl in template_files():
        out[f"templates/{tmpl.name}"] = tmpl.read_text()
    out["plugin.yaml"] = render_manifest(target)
    return out


def render_all() -> dict[str, dict[str, str]]:
    return {target: render_target(target) for target in TARGETS}


def write_dist(dist_root: Path, rendered: dict[str, dict[str, str]]) -> None:
    for target, files in rendered.items():
        target_root = dist_root / target
        if target_root.exists():
            shutil.rmtree(target_root)
        for rel, content in files.items():
            dest = target_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)


def check_drift(dist_root: Path, rendered: dict[str, dict[str, str]]) -> list[str]:
    """Return human-readable drift lines; empty means dist matches source."""
    drift: list[str] = []
    for target, files in rendered.items():
        target_root = dist_root / target
        expected_paths = set(files)
        actual_paths = (
            {p.relative_to(target_root).as_posix() for p in target_root.rglob("*") if p.is_file()}
            if target_root.exists()
            else set()
        )
        for rel in sorted(expected_paths - actual_paths):
            drift.append(f"{target}/{rel}: missing in dist")
        for rel in sorted(actual_paths - expected_paths):
            drift.append(f"{target}/{rel}: not generated from source (hand-edited?)")
        for rel in sorted(expected_paths & actual_paths):
            current = (target_root / rel).read_text()
            if current != files[rel]:
                diff = "".join(
                    difflib.unified_diff(
                        current.splitlines(keepends=True),
                        files[rel].splitlines(keepends=True),
                        fromfile=f"dist/{target}/{rel}",
                        tofile=f"source -> {target}/{rel}",
                    )
                )
                drift.append(f"{target}/{rel}: differs from source\n{diff}")
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile src/ into dist/ per runtime.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify dist/ matches source without writing; non-zero exit on drift.",
    )
    parser.add_argument(
        "--dist",
        type=Path,
        default=DEFAULT_DIST,
        help="Output root (default: ./dist).",
    )
    args = parser.parse_args(argv)
    rendered = render_all()

    if args.check:
        drift = check_drift(args.dist, rendered)
        if drift:
            print("dist/ is out of date or hand-edited:\n", file=sys.stderr)
            for line in drift:
                print(line, file=sys.stderr)
            print("\nRun `uv run python scripts/build/compile.py` to regenerate.", file=sys.stderr)
            return 1
        print("dist/ matches source.")
        return 0

    write_dist(args.dist, rendered)
    total = sum(len(f) for f in rendered.values())
    print(f"Wrote {total} files across {len(rendered)} targets to {args.dist}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
