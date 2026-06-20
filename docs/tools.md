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

| Tool                               | Dimension                | Applies to            | Install hint                                           |
| ---------------------------------- | ------------------------ | --------------------- | ------------------------------------------------------ |
| `fd`                               | discovery                | all                   | `brew install fd` / `cargo install fd-find`            |
| `rg`                               | discovery                | all                   | `brew install ripgrep`                                 |
| `git`                              | change                   | all                   | install git                                            |
| `gitnexus`                         | change                   | all                   | see GitNexus install docs                              |
| `archfit`                          | dependency/change/report | all                   | see archfit install docs                               |
| `ast-grep`                         | structural               | all                   | `brew install ast-grep`                                |
| `tree-sitter`                      | structural               | all                   | `brew install tree-sitter-cli`                         |
| `ruff`                             | structural               | python                | `uv pip install ruff`                                  |
| `radon`                            | structural               | python                | `uv tool install radon`                                |
| `lizard`                           | structural               | python                | `uv tool install lizard`                               |
| `codegraph`                        | dependency/semantic      | all                   | see codegraph install docs                             |
| `pyright`                          | semantic                 | python                | `npm i -g pyright`                                     |
| `basedpyright`                     | semantic                 | python                | `uv tool install basedpyright`                         |
| `staticcheck`                      | semantic                 | go                    | `go install honnef.co/go/tools/cmd/staticcheck@latest` |
| `dependency-cruiser` (`depcruise`) | dependency               | typescript/javascript | `npm i -g dependency-cruiser`                          |
| `madge`                            | dependency               | typescript/javascript | `npm i -g madge`                                       |
| `knip`                             | dependency               | typescript/javascript | `npm i -g knip`                                        |
| `import-linter` (`lint-imports`)   | dependency               | python                | `uv pip install import-linter`                         |
| `pydeps`                           | dependency               | python                | `uv pip install pydeps`                                |
| `deptry`                           | dependency               | python                | `uv pip install deptry`                                |
| `pipdeptree`                       | dependency               | python                | `uv tool install pipdeptree`                           |
| `goda`                             | dependency               | go                    | `go install github.com/loov/goda@latest`               |
| `helm`                             | operational              | kubernetes            | `brew install helm`                                    |
| `kustomize`                        | operational              | kubernetes            | `brew install kustomize`                               |
| `kubeconform`                      | operational              | kubernetes            | `brew install kubeconform`                             |
| `kube-linter`                      | operational              | kubernetes            | `brew install kube-linter`                             |
| `terraform`                        | operational              | terraform             | `brew install terraform`                               |
| `tofu`                             | operational              | terraform             | `brew install tofu`                                    |
| `tflint`                           | operational              | terraform             | `brew install tflint`                                  |
| `hadolint`                         | operational              | docker                | `brew install hadolint`                                |
| `actionlint`                       | operational              | github-actions        | `brew install actionlint`                              |
| `conftest`                         | operational              | kubernetes/terraform  | `brew install conftest`                                |
| `govulncheck`                      | security                 | go                    | `go install golang.org/x/vuln/cmd/govulncheck@latest`  |
| `trivy`                            | security                 | all                   | `brew install trivy`                                   |
| `syft`                             | security                 | all                   | `brew install syft`                                    |
| `grype`                            | security                 | all                   | `brew install grype`                                   |
| `tfsec`                            | security                 | terraform             | `brew install tfsec`                                   |
| `zizmor`                           | security                 | github-actions        | `brew install zizmor`                                  |
| `jq`                               | report                   | all                   | `brew install jq`                                      |
| `yq`                               | report                   | all                   | `brew install yq`                                      |
| `mmdc`                             | report                   | all                   | `npm i -g @mermaid-js/mermaid-cli`                     |

Ecosystem applicability is detected from marker files: `pyproject.toml` /
`setup.py` / `requirements.txt` → python, `tsconfig.json` → typescript,
`package.json` → javascript, `go.mod` → go, `Chart.yaml` /
`kustomization.yaml` → kubernetes, `main.tf` → terraform. The skill suite covers
more commands per dimension (LSP, tree-sitter, `go list`, `go mod graph`,
OpenTofu, Docker, GitHub Actions, policy/SBOM tooling); `architect-doctor`
probes a representative subset above. Where a tool spans more than one review
dimension — for example, `codegraph` contributes both dependency and semantic
coverage — treat the table label as a compact reminder, not an exclusivity rule.

## Evidence ladder

Use the narrowest tool that can prove the claim, in this order:

1. `tools-code-search` / `fd` / `rg` / targeted reads — locate the path,
   symbol, or config.
2. `tools-archfit` when `.archfit.yaml` exists or archfit is available — gather
   deterministic scorecard, JSON findings, tool coverage, deltas, and
   `agent_tasks` for calibration.
3. `ast-grep` or `tree-sitter` — prove syntactic presence or absence of a pattern.
4. LSP — prove resolved definitions, references, implementations, and diagnostics.
5. `codegraph` or language dependency tools — prove graph shape: cycles, hubs,
   blast radius, dependency direction.
6. `GitNexus` or `git log` fallbacks — prove co-change, churn, and change locality.
7. Operational/security tools — prove deploy topology, runtime coupling, and
   supply-chain facts.

Do not use a weaker rung to claim a stronger fact. Example: `rg` or ast-grep can
show that an import exists, but only LSP or a fresh code graph can justify a
"no callers" claim.

## Skill coverage by tool family

The current split uses tool-family skills by language or operational surface,
plus one deterministic aggregate for archfit because it has a distinct
review-calibration workflow and machine-readable output contract.

- `tools-archfit` — archfit deterministic check/scorecard/delta/SARIF/JSON
  facts, tool coverage, and `agent_tasks`.
- `tools-lsp-tree-sitter` — LSP, tree-sitter.
- `tools-typescript` — dependency-cruiser, madge, knip, tsc, ESLint.
- `tools-python` — import-linter, pydeps, pyright/basedpyright, ruff,
  deptry, pipdeptree/uv tree, radon/lizard, vulture.
- `tools-go` — go list, go mod graph, goda, staticcheck, govulncheck,
  go-callvis.
- `tools-infra-operational` — helm, kustomize, kubeconform, kube-linter,
  terraform/tofu, tflint, tfsec, Docker/hadolint, GitHub Actions/actionlint,
  GitHub Actions/zizmor, conftest, syft, grype, trivy.
- `tools-report-markdown` — architect-validate-report, jq, yq, Mermaid, DOT,
  D2, link/spell/format checks.

Add a new standalone skill only when a tool family has a distinct routing
surface and workflow that would otherwise create overlap or ambiguity.

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
