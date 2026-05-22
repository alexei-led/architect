---
document_title: Architect extension design
date: 2026-05-22
status: draft
scope: Claude Code, Codex CLI, Pi
approach: instruction-first agent and skill suite with Python helper tools
---

# Architect extension design

## Goal

Build an architect extension for AI coding agents.

The architect reviews existing codebases, especially large or AI-generated
repositories, and helps move them toward maintainable architecture.

The extension must support repeated analysis. Reports from different dates must
show improvement, degradation, or lack of comparability.

The target outcome is practical: untangle spaghetti AI-assisted code into
structured, modular code that humans and AI agents can understand without
loading the whole repository into context.

## Principles

- Instructions first. Code only where it adds clear value.
- Agents use existing tools directly.
- Do not wrap a CLI just to rename it.
- Cover all applicable evidence dimensions with available tools, but summarize
  results into bounded evidence and coverage. Tool output is evidence, not the
  report.
- Ask before scoring when domain or team context changes the result.
- Use structured question tools for interview questions when available.
- Inspect code and docs before asking answerable questions.
- Separate facts, hypotheses, scores, and recommendations.
- Every score needs evidence or lower confidence.
- Prefer local OSS tools with good CLI support.
- Focus v1 analysis on TypeScript, Python, Go, and operational dependencies.
- Use Python 3.12+ with uv for helper tools, build scripts, validation, and tests.
- Do not add dedicated PHP, Ruby, COBOL, Java, or JVM-only skills in v1.
- Reuse and adapt Vlad Khononov's Balanced Coupling material with attribution
  and within licensing limits.
- Do not recommend rewrites when incremental repair can reduce risk.

## Product shape

```text
src/
  agents/architect/AGENT.md
  skills/architecture-review/SKILL.md
  skills/architecture-scorecard/SKILL.md
  skills/architecture-plan/SKILL.md
  skills/methodology-balanced-coupling/SKILL.md
  skills/methodology-architecture-fitness/SKILL.md
  skills/tools-ast-grep/SKILL.md
  skills/tools-codegraph/SKILL.md
  skills/tools-gitnexus/SKILL.md
  skills/tools-lsp-tree-sitter/SKILL.md
  skills/tools-typescript/SKILL.md
  skills/tools-python/SKILL.md
  skills/tools-go/SKILL.md
  skills/tools-infra-operational/SKILL.md
  skills/tools-report-markdown/SKILL.md
  templates/report.md
  templates/scorecard.yaml
  templates/plan.md
  plugins/architecture/plugin.yaml
  architect_tools/doctor.py
  architect_tools/validate_report.py
  architect_tools/compare_reports.py
scripts/build/
  compile.py
pyproject.toml
uv.lock
dist/
  claude/
  codex/
  pi/
```

The Python helper package stays small. It checks tool availability, validates
reports, compares reports, and builds distribution artifacts. It does not
replace ast-grep, codegraph, GitNexus, LSP, tree-sitter, or language CLIs.

This project does not implement a Pi question extension. Pi users should install
`alexei-led/cc-thingz`, which already provides `ask_user_question`.

## User-facing flows

The extension supports three primary requests:

- Architecture review: build interview context and a system map, then produce an
  evidence-backed report with scores and confidence.
- Compare reports: compare two compatible reports and explain improvement,
  degradation, confidence changes, or non-comparability.
- Make refactoring plan: convert selected findings into small, verifiable phases
  for a mutator agent or human to implement.

The architect does not apply production code changes. It hands approved plans to
an engineer or mutator agent.

## Artifact contract

The architect produces four main artifacts. Every skill, tool recipe, and helper
must improve at least one of them.

### Interview context

Captures the user's intended architecture and constraints.

Includes:

- system goal
- main quality goals
- intended modules, services, packages, and deploy units
- core, supporting, and generic domains
- volatile areas
- team ownership
- known pain
- review scope
- out-of-scope areas

### System map

Describes what exists before judging quality.

Includes:

- languages and package managers
- apps, services, libraries, CLIs, jobs, and workers
- deploy units
- public APIs, events, schemas, migrations, and generated code
- declared modules from manifests and directories
- observed modules from dependency graphs, imports, ownership, and change history
- high-risk entry points and flows
- tool coverage and missing evidence

### Architecture report

Explains observed architecture, gaps, scores, confidence, and recommendations.
The report must cite evidence and distinguish facts from hypotheses.

### Refactoring plan

Converts findings into small, independently verifiable phases. Plans should be
usable by humans and coding agents. No big-bang rewrite unless the evidence shows
incremental repair is worse.

## Runtime and write contract

The architect is read-only for source code by default.

Allowed without extra approval:

- inspect files
- run read-only commands
- run local analysis tools
- emit reports and plans in the chat response

Needs explicit user approval:

- write reports or plans to disk
- create `.architect/config.yaml`
- create baseline report directories
- run expensive scans on very large repos

Not allowed for the architect role:

- edit production source code
- apply refactors
- change tests
- mutate infrastructure

When implementation is requested, route to an engineer or mutator agent with the
approved plan.

## Workflow

1. Confirm scope and write mode.
2. Inspect available docs and repository shape.
3. Interview only for missing context that changes the review.
4. Detect available tools and record tool coverage.
5. Triage the repository.
6. Build the system map by covering applicable evidence dimensions with
   available tools.
7. Map intended architecture.
8. Map observed architecture.
9. Compare intended vs observed.
10. Score with evidence, confidence, and rubric version.
11. Write report.
12. Write plan when requested.

## Interview

Run interview before full scoring when context is missing.

Ask one question at a time. Ask only questions that change the analysis.
Use the runtime's structured question tool. Do not ask as plain prose with a
numbered list unless no structured tool exists.

Platform mapping:

- Claude Code: use `AskUserQuestion`.
- Pi: use `ask_user_question` from `alexei-led/cc-thingz`.
- Codex: use the runtime's structured user-input tool when available. If the
  runtime exposes `request_user_input`, use it. Otherwise use the native
  multi-choice or structured-question facility. Do not hard-code a Codex tool
  name in shared instructions without a target-runtime overlay.

Question rules:

- Prefer single-select with 2-4 meaningful options.
- Use multi-select only for non-exclusive answers.
- Allow free text unless the answer must be from a closed set.
- Use short headers.
- Use stable machine values for options when the tool supports them.
- Include an `Other` or free-text path when the listed options may be incomplete.
- If the user cancels, stop the interview and record what is missing.
- Store structured answers in config or report context.

Fallback:

- If no structured question tool exists, ask one plain-text question.
- Include options as labels, not numbers only.
- Tell the user they can answer with a label or free text.
- Mark the answer as lower confidence if parsing is ambiguous.

Capture:

- system goal
- main quality goals
- intended modules, services, packages, and deploy units
- core, supporting, and generic domains
- volatile areas
- team ownership
- known pain
- review scope
- out-of-scope areas

Store answers in `.architect/config.yaml` only with approval. Otherwise include
them in the report context.

## Triage

Build a system map before judging quality.

Find:

- languages and package managers
- apps, services, libraries, CLIs, jobs, and workers
- public APIs, events, schemas, migrations, and generated code
- docs, ADRs, ownership files, and context files
- declared modules from manifests and directories
- observed modules from dependency graphs and change history
- high-risk entry points and flows

## Intended architecture

Use this source order:

1. User interview.
2. Existing docs, ADRs, `CONTEXT.md`, and ownership files.
3. Manifests, package boundaries, and deploy configuration.
4. Directory structure.
5. Inferred clusters from dependencies and change history.

If sources disagree, report the disagreement. Do not silently pick the cleanest
story.

## Observed architecture

Observed architecture is what the code and operational files actually do.

Evidence sources include:

- import and package dependency graphs
- call graph or symbol graph where available
- public APIs, routes, messages, events, and schemas
- database and migration ownership
- build graph and workspace manifests
- CI checks and architecture fitness functions
- git churn and co-change history
- generated code boundaries
- operational manifests and deploy topology

## Tool coverage and routing

The architect should cover every applicable evidence dimension with available
tools, but not every installed tool is applicable to every repo.

Tool routing exists to improve confidence, evidence quality, and context
management. It is not a reason to cut tools from v1.

Definitions:

- Available: installed and runnable in the current environment.
- Applicable: matches the repo language, artifact type, risk area, and review
  scope.
- Covered: the tool ran successfully and produced usable evidence.
- Missing: tool is relevant but absent, failed, or could not inspect the target.

Tool budget and stop rules:

- Discovery runs first and is cheap: files, manifests, docs, ownership, and git
  history when available.
- For each relevant language or deploy surface, run enough tools to cover the
  applicable evidence dimensions. Prefer one strong signal over three redundant
  weak ones.
- Run expensive scans only with approval or a clear local budget. If a scan is
  skipped, record the reason and confidence impact.
- Stop when additional tools are unlikely to change a finding, then report the
  remaining gap instead of turning the review into a tool safari.
- Missing or skipped optional tools lower confidence. They do not block a useful
  report.

Coverage levels:

- Discovery: repo shape, manifests, docs, ownership, git history.
- Structural: AST patterns, imports, exports, generated code markers.
- Semantic: LSP definitions, references, diagnostics, symbol graphs.
- Dependency: package graphs, build graphs, module graphs, cycles, fan-in/out.
- Change: churn, co-change, hotspots, trend versus previous reports.
- Operational: Kubernetes, Terraform/OpenTofu, Docker, GitHub Actions, policies.
- Security/supply chain: vulnerability and SBOM tools when relevant to architecture
  risk.
- Report quality: Markdown, links, diagrams, spelling, schema validation.

Output rules:

- Summarize tool findings. Do not paste full noisy output into the report.
- Keep the top findings per dimension and link to evidence refs.
- Record tool coverage and gaps even when no issue is found.
- Deduplicate findings from multiple tools.
- Prefer exact file ranges, graph query names, and command summaries.
- Missing optional tools lower confidence; they do not block the review.
- Failed tools are reported as coverage gaps with the failure reason.

## Evidence schema

Each evidence reference should fit one of these shapes.

```yaml
evidence:
  - type: file
    ref: src/orders/service.ts:42-88
    summary: Order service imports payment internals directly.
  - type: command
    command: dependency-cruiser src --output-type json
    summary: 3 forbidden imports from feature modules into infrastructure.
  - type: graph-query
    tool: gitnexus
    query: impact OrderService upstream depth=3
    summary: 18 upstream callers cross 5 modules.
  - type: interview
    question: intended-module-boundaries
    summary: User says billing and orders should be separate core domains.
```

Evidence must be enough for a human or agent to re-check the claim. Weak
evidence lowers confidence.

## Scoring

Use scores from `0` to `100`, but report bands rather than pretending the exact
integer is scientific.

Score bands:

- `0-20`: critical
- `21-40`: poor
- `41-60`: mixed
- `61-80`: serviceable
- `81-100`: strong

Each score includes:

- value
- band
- confidence
- rubric version
- evidence refs
- known gaps

Core dimensions:

- boundary integrity
- coupling balance
- dependency graph health
- cohesion and modularity
- change locality
- architecture fitness
- analysis confidence

Analysis confidence is not architecture quality. It says how trustworthy the
review is.

Reports are comparable only when they use compatible scope, rubric version, and
tool coverage. If not, `compare-reports` must say why comparison is unsafe.

## Boundary integrity

Check whether code respects intended boundaries.

Evidence examples:

- forbidden imports
- direct access to another module's internals
- direct database or schema access across ownership boundaries
- layer violations
- framework leakage into domain code
- bypassed module APIs

## Coupling balance

Use Balanced Coupling.

Assess each important integration by:

- strength
- distance
- volatility

Strength levels:

- intrusive: private internals, internal databases, undocumented APIs
- functional: shared business rules or duplicated requirement logic
- model: shared domain model
- contract: explicit API, DTO, event, facade, or published language

Worst case: high strength, high distance, high volatility.

Do not recommend decoupling everything. Recommend changing strength, distance,
or volatility risk only when the evidence supports it.

## Dependency graph health

Check topology risk.

Evidence examples:

- cycles
- fan-in and fan-out hubs
- bypassed layers
- cross-language or build-system coupling
- graph clusters that disagree with intended modules

## Cohesion and modularity

Check whether modules group related behavior.

Evidence examples:

- intra-module vs inter-module dependency ratio
- module size skew
- graph clusters vs declared modules
- change clusters vs declared modules
- mixed domain vocabulary in one module
- unrelated components in one module

## Change locality

Check whether changes stay inside intended boundaries.

Evidence examples:

- commits touching many modules
- files that change together often
- hotspots from churn and complexity
- recurring cross-boundary test fallout
- trend compared with previous reports

## Architecture fitness

Check whether architecture intent is executable.

Evidence examples:

- dependency rules
- import contracts
- architecture tests
- ADR-linked checks
- CI checks
- policy checks for infrastructure

Documents do not enforce architecture. Checks do.

## Tool skills

Tool skills are operating guides, not wrappers.

The architect should use tool skills to cover applicable evidence dimensions.
Tool skills explain how to choose commands, collect evidence, and summarize
output without flooding the agent context.

Required or central tools:

- ast-grep or sg
- rg and fd
- git
- tree-sitter
- LSP servers
- codegraph
- GitNexus
- semgrep OSS
- Code Maat
- lizard
- scc or tokei

TypeScript analysis tools:

- dependency-cruiser
- madge
- knip
- tsc
- eslint boundary and import rules
- pnpm, npm, yarn, nx, or turbo commands when present

Python analysis tools:

- import-linter
- pydeps
- pyright or basedpyright
- ruff
- deptry
- pipdeptree
- uv tree
- radon or lizard
- vulture

Go tools:

- go list
- go mod graph
- goda
- gopls
- staticcheck
- govulncheck
- go-callvis

Operational tools:

- helm
- kustomize
- kubectl
- kubeconform
- kube-linter
- kube-score
- polaris
- pluto
- conftest or opa
- kyverno CLI
- terraform or tofu
- tflint
- checkov or terrascan
- terraform-config-inspect
- terraform-docs
- docker compose config
- hadolint
- actionlint
- syft
- grype
- osv-scanner
- trivy

Report tools:

- markdownlint-cli2
- markdown-link-check or lychee
- cspell
- prettier or mdformat
- doctoc or markdown-toc
- pandoc when export is needed
- jq
- yq
- mermaid-cli
- Graphviz dot
- D2

Use Mermaid as the default embedded report diagram format when a diagram helps.
Do not add diagrams to instruction files unless they remove ambiguity.

## Report

Reports are Markdown with YAML frontmatter.

Required sections:

- executive summary
- interview context
- system map
- intended architecture
- observed architecture
- score map
- key findings
- coupling review
- boundary violations
- change locality and hotspots
- recommendations
- plan summary when present
- evidence appendix
- tool coverage and gaps

Each finding includes:

- id
- title
- severity
- dimension
- evidence
- recommended action

Finding IDs must be stable across repeat reports when the underlying issue is the
same. If a finding changes enough that stability is misleading, close the old ID
and open a new one.

## Plan

The plan is plain Markdown.

Required structure:

- overview
- success criteria
- phases
- tasks with checkboxes
- verification per phase
- acceptance criteria
- safety notes when risk is high

Plans should be useful to agents and humans. Keep them direct. Avoid brand names
or tool-specific assumptions unless the finding depends on a specific tool.

Planning constraints:

- Choose one hotspot, boundary, or flow per plan unless the user asks for a
  roadmap.
- Keep the next execution horizon to five phases or fewer before re-review.
- Each task cites the finding or evidence that justifies it.
- Each task includes preconditions, postconditions, and verification.
- Prefer characterization tests, seam creation, boundary repair, and fitness
  checks before cosmetic cleanup.

Plan tasks should be small enough to verify independently.

## Python helpers

Use Python 3.12+ and uv.

Dependency rule:

- Prefer stdlib for helpers.
- Allow PyYAML for YAML frontmatter and scorecard parsing. Do not maintain a
  homemade YAML parser.
- If PyYAML is unavailable, fail with an install hint rather than parsing YAML
  loosely.

Code rules:

- prefer stdlib: argparse, pathlib, json, dataclasses, subprocess, typing
- use typed functions and concrete data shapes
- fail fast with guard clauses
- keep command runners explicit and safe
- add pytest coverage for happy path and invalid input
- run ruff format, ruff check, pytest, and pyright if configured

Python helpers:

- `doctor`: check local tool availability and versions
- `validate-report`: check frontmatter, scores, sections, evidence refs, and tool
  coverage
- `compare-reports`: compare score maps, finding IDs, confidence, scope, rubric
  version, and tool coverage
- `compile`: build Claude, Codex, and Pi outputs from source files

Reuse the `cc-thingz` Python compiler approach where practical.

## Packaging

Use the source-to-dist pattern from `cc-thingz`, implemented in Python.

Build targets:

- Claude Code
- Codex CLI
- Pi

Generated files must come from source files. Do not hand-edit `dist/`.

## Evaluation

Use fixture repos for:

- healthy TypeScript
- tangled TypeScript monorepo
- Python package with import boundary issues
- Go service with dependency issues
- mixed repo with operational manifests

Dogfood on real code, not this empty planning repo. Primary dogfood target:
`/Users/alexei/Workspace/ccgram`, because it is AI-heavy code that is maintained
in practice and needs architecture pressure.

Eval checks:

- architect asks for missing context before scoring
- architect covers all applicable evidence dimensions with available tools before
  claims
- architect records tool coverage and gaps
- report cites evidence
- scores include confidence
- recommendations are incremental
- plan has phases, tasks, and verification
- repeat reports explain improvement, degradation, or non-comparability
