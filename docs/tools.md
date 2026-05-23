# Tools and coverage

The architect agent gathers evidence by driving local OSS CLIs directly. The
package never wraps these tools — it only checks they are present
(`architect-doctor`) and validates the reports they feed.

`architect-doctor` classifies each tool as **available**, **missing**, or
**failed** (found, but its version probe errored), marks applicability from a
light repo scan, and prints an install hint for anything missing. The tool
registry in `src/architect_tools/doctor.py` is the source of truth; this page
mirrors it.

## Tools by evidence dimension

The `tools-code-search` skill covers the always-applicable discovery pass with
`fd`, `rg`, `git grep`, `git ls-files`, targeted file reads, and `git log`
fallbacks. Use it before heavier AST, graph, language, or history tools.

Tools without an applicability column are always applicable; the rest apply only
when the matching ecosystem marker is present in the repo.

| Tool                               | Dimension   | Applies to            | Install hint                                           |
| ---------------------------------- | ----------- | --------------------- | ------------------------------------------------------ |
| `fd`                               | discovery   | all                   | `brew install fd` / `cargo install fd-find`            |
| `rg`                               | discovery   | all                   | `brew install ripgrep`                                 |
| `git`                              | change      | all                   | install git                                            |
| `gitnexus`                         | change      | all                   | see GitNexus install docs                              |
| `ast-grep`                         | structural  | all                   | `brew install ast-grep`                                |
| `ruff`                             | structural  | python                | `uv pip install ruff`                                  |
| `codegraph`                        | semantic    | all                   | see codegraph install docs                             |
| `pyright`                          | semantic    | python                | `npm i -g pyright`                                     |
| `staticcheck`                      | semantic    | go                    | `go install honnef.co/go/tools/cmd/staticcheck@latest` |
| `dependency-cruiser` (`depcruise`) | dependency  | typescript/javascript | `npm i -g dependency-cruiser`                          |
| `madge`                            | dependency  | typescript/javascript | `npm i -g madge`                                       |
| `knip`                             | dependency  | typescript/javascript | `npm i -g knip`                                        |
| `import-linter` (`lint-imports`)   | dependency  | python                | `uv pip install import-linter`                         |
| `pydeps`                           | dependency  | python                | `uv pip install pydeps`                                |
| `deptry`                           | dependency  | python                | `uv pip install deptry`                                |
| `goda`                             | dependency  | go                    | `go install github.com/loov/goda@latest`               |
| `helm`                             | operational | kubernetes            | `brew install helm`                                    |
| `kustomize`                        | operational | kubernetes            | `brew install kustomize`                               |
| `terraform`                        | operational | terraform             | `brew install terraform`                               |
| `govulncheck`                      | security    | go                    | `go install golang.org/x/vuln/cmd/govulncheck@latest`  |
| `trivy`                            | security    | all                   | `brew install trivy`                                   |
| `syft`                             | security    | all                   | `brew install syft`                                    |
| `jq`                               | report      | all                   | `brew install jq`                                      |
| `yq`                               | report      | all                   | `brew install yq`                                      |
| `mmdc`                             | report      | all                   | `npm i -g @mermaid-js/mermaid-cli`                     |

Ecosystem applicability is detected from marker files: `pyproject.toml` /
`setup.py` / `requirements.txt` → python, `tsconfig.json` → typescript,
`package.json` → javascript, `go.mod` → go, `Chart.yaml` /
`kustomization.yaml` → kubernetes, `main.tf` → terraform. The skill suite covers
more commands per dimension (LSP, tree-sitter, `go list`, `go mod graph`,
OpenTofu, Docker, GitHub Actions, policy/SBOM tooling); `architect-doctor`
probes the representative subset above.

## Coverage states and confidence impact

A report records tool coverage **per dimension**, not just per tool, in the
`tool_coverage` frontmatter — even when no issue is found. Each entry tracks four
states:

- **used** — the tool ran and produced evidence.
- **skipped** — applicable but deliberately not run (redundant, too expensive, or
  another tool already covered the dimension).
- **missing** — applicable but not installed. Record it as a coverage gap.
- **failed** — present but errored on this repo. Record it as a coverage gap.

Each entry also carries a `confidence_impact` (`none` | `low` | `medium` |
`high`): how much the gaps in that dimension drag down trust in the related
scores. Missing or failed tools in a dimension lower the `confidence` of scores
that rely on it, and they accumulate into the meta `analysis_confidence` score.

Missing applicable tools are advisory, not fatal — `architect-doctor` exits 0 and
the agent records a coverage gap rather than refusing to review. The rule the
agent must not break: when a dimension's evidence is thin, lower the confidence
(and, if quality is high, lower the band per the scorecard caps) — never present
a shaky high score as settled. See [scoring.md](scoring.md).

## Stop rule

Coverage is breadth across dimensions, not depth in one tool. Start with
`tools-code-search` to find the paths and concepts, then switch to the narrowest
specialized tool that can prove the claim. When a dimension is already covered,
stop and record any remaining gap instead of running another redundant or
expensive scan. Tool output is summarized into evidence refs, never pasted
wholesale into the report.
