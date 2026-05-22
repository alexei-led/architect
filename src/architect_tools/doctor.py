"""Report architecture-review tool availability and versions.

doctor inspects the local environment for the OSS CLIs the architect agent
calls directly. It classifies each tool as available, missing, or failed (found
but its version probe errored), marks applicability from a light repo scan, and
prints install hints for what is missing. It never wraps these tools; it only
checks that they are present.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

WhichFn = Callable[[str], str | None]
RunFn = Callable[[list[str]], tuple[bool, str]]


@dataclass(frozen=True)
class Tool:
    name: str
    dimension: str
    version_cmd: tuple[str, ...]
    install_hint: str
    # Languages/ecosystems this tool applies to; empty means always applicable.
    applies_to: tuple[str, ...] = ()


# Grouped by evidence dimension. Kept declarative so the registry stays the only
# place that knows about specific tools.
TOOLS: tuple[Tool, ...] = (
    Tool("fd", "discovery", ("fd", "--version"), "brew install fd / cargo install fd-find"),
    Tool("rg", "discovery", ("rg", "--version"), "brew install ripgrep"),
    Tool("git", "change", ("git", "--version"), "install git"),
    Tool("ast-grep", "structural", ("ast-grep", "--version"), "brew install ast-grep"),
    Tool("codegraph", "semantic", ("codegraph", "--version"), "see codegraph install docs"),
    Tool("gitnexus", "change", ("gitnexus", "--version"), "see GitNexus install docs"),
    Tool(
        "dependency-cruiser",
        "dependency",
        ("depcruise", "--version"),
        "npm i -g dependency-cruiser",
        ("typescript", "javascript"),
    ),
    Tool(
        "madge",
        "dependency",
        ("madge", "--version"),
        "npm i -g madge",
        ("typescript", "javascript"),
    ),
    Tool(
        "knip", "dependency", ("knip", "--version"), "npm i -g knip", ("typescript", "javascript")
    ),
    Tool(
        "import-linter",
        "dependency",
        ("lint-imports", "--help"),
        "uv pip install import-linter",
        ("python",),
    ),
    Tool("pydeps", "dependency", ("pydeps", "--version"), "uv pip install pydeps", ("python",)),
    Tool("pyright", "semantic", ("pyright", "--version"), "npm i -g pyright", ("python",)),
    Tool("deptry", "dependency", ("deptry", "--version"), "uv pip install deptry", ("python",)),
    Tool("ruff", "structural", ("ruff", "--version"), "uv pip install ruff", ("python",)),
    Tool(
        "goda", "dependency", ("goda", "version"), "go install github.com/loov/goda@latest", ("go",)
    ),
    Tool(
        "staticcheck",
        "semantic",
        ("staticcheck", "-version"),
        "go install honnef.co/go/tools/cmd/staticcheck@latest",
        ("go",),
    ),
    Tool(
        "govulncheck",
        "security",
        ("govulncheck", "-version"),
        "go install golang.org/x/vuln/cmd/govulncheck@latest",
        ("go",),
    ),
    Tool("helm", "operational", ("helm", "version"), "brew install helm", ("kubernetes",)),
    Tool(
        "kustomize",
        "operational",
        ("kustomize", "version"),
        "brew install kustomize",
        ("kubernetes",),
    ),
    Tool(
        "terraform",
        "operational",
        ("terraform", "version"),
        "brew install terraform",
        ("terraform",),
    ),
    Tool("trivy", "security", ("trivy", "--version"), "brew install trivy"),
    Tool("syft", "security", ("syft", "version"), "brew install syft"),
    Tool("jq", "report", ("jq", "--version"), "brew install jq"),
    Tool("yq", "report", ("yq", "--version"), "brew install yq"),
    Tool("mmdc", "report", ("mmdc", "--version"), "npm i -g @mermaid-js/mermaid-cli"),
)

# Marker files that imply an ecosystem is in play, for applicability.
ECOSYSTEM_MARKERS = {
    "python": ("pyproject.toml", "setup.py", "requirements.txt"),
    "typescript": ("tsconfig.json",),
    "javascript": ("package.json",),
    "go": ("go.mod",),
    "kubernetes": ("Chart.yaml", "kustomization.yaml"),
    "terraform": ("main.tf",),
}


def _default_run(cmd: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)  # noqa: S603
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    out = (proc.stdout or proc.stderr).strip().splitlines()
    return proc.returncode == 0, out[0] if out else ""


def detect_ecosystems(repo: Path) -> set[str]:
    """Detect ecosystems present in repo from marker files (non-recursive + one level)."""
    found: set[str] = set()
    for eco, markers in ECOSYSTEM_MARKERS.items():
        for marker in markers:
            if (repo / marker).exists() or any(repo.glob(f"*/{marker}")):
                found.add(eco)
                break
    return found


@dataclass
class ToolStatus:
    tool: Tool
    state: str  # available | missing | failed
    applicable: bool
    detail: str = ""


def probe_tool(
    tool: Tool,
    ecosystems: set[str] | None,
    which: WhichFn = shutil.which,
    run: RunFn = _default_run,
) -> ToolStatus:
    # ecosystems is None means "no repo context" — assume applicable.
    applicable = (
        not tool.applies_to or ecosystems is None or bool(set(tool.applies_to) & ecosystems)
    )
    if which(tool.version_cmd[0]) is None:
        return ToolStatus(tool, "missing", applicable)
    ok, detail = run(list(tool.version_cmd))
    return ToolStatus(tool, "available" if ok else "failed", applicable, detail)


def run_doctor(
    repo: Path | None = None,
    which: WhichFn = shutil.which,
    run: RunFn = _default_run,
) -> list[ToolStatus]:
    ecosystems = detect_ecosystems(repo) if repo is not None else None
    return [probe_tool(t, ecosystems, which, run) for t in TOOLS]


def render(statuses: list[ToolStatus]) -> str:
    lines = ["Architecture-review tool check", ""]
    for st in sorted(statuses, key=lambda s: (s.tool.dimension, s.tool.name)):
        mark = {"available": "ok", "missing": "MISSING", "failed": "FAILED"}[st.state]
        scope = "" if st.applicable else " (n/a for this repo)"
        line = f"  [{mark:7}] {st.tool.dimension:11} {st.tool.name}{scope}"
        if st.state == "available" and st.detail:
            line += f" — {st.detail}"
        lines.append(line)
        if st.state == "missing" and st.applicable:
            lines.append(f"            install: {st.tool.install_hint}")
        if st.state == "failed":
            lines.append(f"            version probe failed: {st.detail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check architecture-review tool availability.")
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="repo path to mark per-tool applicability from detected ecosystems",
    )
    args = parser.parse_args(argv)
    statuses = run_doctor(args.repo)
    print(render(statuses))
    # Missing applicable tools are advisory, not fatal: agents record coverage gaps.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
