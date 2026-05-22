---
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: ccgram-dogfood-1
date: 2026-05-22

target:
  repo: ccgram
  scope: full
  out_of_scope:
    - dist/ legacy ccbot-* artifacts
    - .venv, caches

comparability:
  scope: full
  rubric_version: 1
  tool_coverage_level: standard

interview_context:
  system_goal: >-
    Telegram bot bridging Telegram Forum topics to tmux windows so users monitor
    and control AI coding agents (Claude Code, Codex, Gemini, Pi, shell) from a phone.
  quality_goals:
    - strict typing (0 pyright errors gate)
    - module isolation via per-handler subpackages and Protocol boundaries
    - pure decision kernel for polling (no side-effect deps in decide.py)
    - constructor DI for stores, no global singleton monkey-patching
    - lazy-import discipline enforced by a lint gate
    - make check green before commit
  intended_units:
    - providers (protocol + 5 agent impls + registry)
    - handlers (14 feature subpackages)
    - llm, whisper, tts (Protocol-based external integrations)
    - miniapp (optional aiohttp dashboard)
    - core modules (session, tmux_manager, bot, bootstrap, hook)
  domains:
    core:
      - handlers (Telegram UX)
      - providers (agent abstraction)
      - polling/status detection
      - miniapp
    supporting:
      - mailbox / inter-agent messaging
      - session monitoring and persistence
    generic:
      - tmux integration
      - PTB Telegram client
      - llm / whisper / tts HTTP adapters
  volatile_areas:
    - handlers/polling
    - handlers/recovery
    - handlers/commands
    - providers (capability matrix growth)
    - miniapp
  team_ownership:
    - single maintainer (alexei-led)
  known_pain:
    - polling_strategies hub split (now polling_state/polling_types)
    - two read paths coexist (window_query/session_query vs direct session_manager)
    - lazy-import comment gaps caught by lint gate
    - singleton-reset ceremony in tests
  review_scope: full
  out_of_scope:
    - dist/ legacy artifacts

system_map:
  languages:
    - Python (175 src files, ~46K LOC)
    - JavaScript (3 files, miniapp/static)
    - HTML (1 file, miniapp/static)
  package_managers:
    - uv (pyproject.toml + uv.lock)
    - hatchling + hatch-vcs build backend
  units:
    - single ccgram wheel with one console_script entrypoint
  deploy_units:
    - PyPI wheel (OIDC trusted publishing)
    - Homebrew formula (auto-generated)
  public_interfaces:
    - CLI (ccgram run / msg / doctor / status / hook)
    - Telegram bot commands (/send, /sessions, /resume, /panes, /live, ...)
    - Claude Code hook receiver (stdin events)
    - Mini App WS/REST (/ws/terminal, /api/panes, /api/transcript, /healthz)
  declared_modules:
    - providers
    - handlers (commands, interactive, live, messaging, messaging_pipeline, polling, recovery, send, shell, status, text, toolbar, topics, voice)
    - llm
    - whisper
    - tts
    - miniapp
  observed_modules:
    - providers cleanly factored behind AgentProvider Protocol + registry
    - handlers decomposed into 14 cohesive subpackages
    - session_manager remains a read/write hub referenced by 30 handler files
    - polling/polling_state holds 5 module-level singletons (import-time coupling)
  high_risk_entrypoints:
    - bot.py (application factory, top churn)
    - handlers/polling (every UX overhaul touches it)
    - session.py / session_map.py (state hub)
  missing_evidence:
    - dependency graph (gitnexus index stale; no Python dep-graph tool installed)
    - cycle detection (not run)
    - semantic call-graph (LSP not exercised)

scores:
  boundary_integrity:
    value: 68
    band: serviceable
    confidence: medium
    evidence_refs: [E2, E5]
    gaps:
      - read-layer migration incomplete
  coupling_balance:
    value: 58
    band: mixed
    confidence: medium
    evidence_refs: [E2, E4]
    gaps:
      - dependency graph not built; coupling judged from imports + docs
  dependency_graph_health:
    value: 50
    band: mixed
    confidence: low
    evidence_refs: [E6]
    gaps:
      - gitnexus index stale; pydeps/import-linter/deptry missing; no cycle scan
  cohesion_modularity:
    value: 64
    band: serviceable
    confidence: medium
    evidence_refs: [E3]
    gaps:
      - several modules exceed 1000 LOC
  change_locality:
    value: 60
    band: mixed
    confidence: medium
    evidence_refs: [E1]
    gaps:
      - churn history split across ccbot->ccgram rename
  architecture_fitness:
    value: 78
    band: serviceable
    confidence: medium
    evidence_refs: [E5]
    gaps:
      - fitness checks cited from docs; not re-executed in this pass
  analysis_confidence:
    value: 58
    band: mixed
    confidence: medium
    evidence_refs: [E6]
    gaps:
      - dependency dimension thin; one structural tool (ast-grep) carried most load

findings:
  - id: F1
    title: Read-layer migration incomplete — 30 handler files still reference session_manager directly
    severity: medium
    dimension: boundary_integrity
    evidence_refs: [E2]
    recommended_action: >-
      Migrate remaining read call sites to window_query/session_query; keep the
      AST-walk enforcement test and tighten it to fail on new direct reads.
  - id: F2
    title: God modules over 1000 LOC concentrate change risk
    severity: medium
    dimension: cohesion_modularity
    evidence_refs: [E3]
    recommended_action: >-
      Split tmux_manager.py (1199), hook.py (1143), directory_callbacks.py (1086),
      and polling/polling_state.py (1017) along the seams already implied by their
      internal sections.
  - id: F3
    title: Module-level singletons in polling_state create import-time coupling
    severity: medium
    dimension: coupling_balance
    evidence_refs: [E4]
    recommended_action: >-
      Continue the documented kernel split; move the 5 singletons behind
      constructor DI so the pure decide.py kernel is not transitively bound to them.
  - id: F4
    title: Dependency-graph health is unverified (stale index, missing tools)
    severity: low
    dimension: dependency_graph_health
    evidence_refs: [E6]
    recommended_action: >-
      Re-run gitnexus analyze, install at least one Python dep-graph tool
      (import-linter or pydeps), then re-score this dimension with cycle data.
  - id: F5
    title: Executable architecture-fitness checks exist and gate commits
    severity: low
    dimension: architecture_fitness
    evidence_refs: [E5]
    recommended_action: >-
      Keep. The AST-walk read-path test, lazy-import lint, pyright 0-errors gate,
      and make check make intent enforceable rather than aspirational — a strength.

evidence:
  - id: E1
    type: command
    command: "git log --since=12mo --name-only -- src/ccgram"
    summary: >-
      Current-name hotspots: bot.py (26), handlers/cleanup.py (25),
      message_queue.py (22), tmux_manager.py (21), session.py (21),
      msg_broker.py (21), config.py (21). History pre-rename lives under src/ccbot.
  - id: E2
    type: command
    command: "grep -rl session_manager / window_query|session_query src/ccgram/handlers"
    summary: >-
      39 handler files import the window_query/session_query read layer; 30 still
      reference session_manager directly. Migration real but incomplete.
  - id: E3
    type: command
    command: "wc -l src/ccgram/**/*.py"
    summary: >-
      Largest modules: tmux_manager.py 1199, hook.py 1143,
      handlers/topics/directory_callbacks.py 1086, handlers/polling/polling_state.py 1017.
  - id: E4
    type: file
    ref: src/ccgram/handlers/polling/polling_state.py
    summary: >-
      Holds stateful poll/screen-buffer classes plus 5 module-level singletons;
      documented as the residue of the polling_strategies hub split.
  - id: E5
    type: file
    ref: scripts/lint_lazy_imports.py + AST-walk read-path test + Makefile (make check)
    summary: >-
      Architecture intent is enforced by executable checks: lazy-import lint,
      read-path AST-walk test, pyright 0-errors gate, make check before commit.
  - id: E6
    type: command
    command: "gitnexus status; command -v pydeps import-linter deptry"
    summary: >-
      gitnexus index stale (indexed commit != current); pydeps, import-linter,
      deptry, pipdeptree, radon not installed. Dependency dimension under-evidenced.

tool_coverage:
  - dimension: discovery
    tools_used: [git, ls, find, wc]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
  - dimension: structural
    tools_used: [ast-grep]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: low
  - dimension: semantic
    tools_used: []
    tools_skipped: [pyright, LSP, tree-sitter]
    tools_missing: []
    tools_failed: []
    confidence_impact: medium
  - dimension: dependency
    tools_used: []
    tools_skipped: [codegraph]
    tools_missing: [pydeps, import-linter, deptry, pipdeptree]
    tools_failed: [gitnexus]
    confidence_impact: high
  - dimension: change
    tools_used: [git]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: low
  - dimension: operational
    tools_used: []
    tools_skipped: [hadolint, kube tools]
    tools_missing: []
    tools_failed: []
    confidence_impact: none
  - dimension: security
    tools_used: []
    tools_skipped: [gitleaks, govulncheck-equivalent]
    tools_missing: []
    tools_failed: []
    confidence_impact: low
  - dimension: report
    tools_used: [ruff]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
---

# Architecture report: ccgram

## Executive summary

ccgram is a single-wheel Python application with deliberately strong, documented
architecture intent — Protocol boundaries, per-handler subpackages, a pure
polling decision kernel, and executable fitness checks that gate every commit.
The dominant risks are not chaos but residue: an incomplete read-layer migration
(30 handler files still reach into `session_manager` directly), a handful of
1000+ LOC god modules, and import-time singletons in the polling subsystem.
Overall the architecture is serviceable-to-mixed with **medium** confidence; the
dependency-graph dimension is under-evidenced (stale index, missing tools) and is
the weakest part of this assessment.

## Interview context

No live interview was possible — this dogfood ran autonomously, so the interview
was reconstructed from `CLAUDE.md`, `.claude/rules/architecture.md`, the
2026-05-01 modularity review, and `CHANGELOG.md`. Intended architecture: isolated
per-handler subpackages behind a `TelegramClient` Protocol and an `AgentProvider`
Protocol, a side-effect-free polling kernel, constructor DI for stores, and
commit-gating fitness checks. Quality goals center on change locality and strict
typing. (Reconstructed intent is lower-confidence than a live interview — see
friction.md item 1.)

## System map

Single deployable: the `ccgram` wheel with one console entrypoint and sub-commands
(`run`, `msg`, `doctor`, `status`, `hook`). 175 Python source files (~46K LOC),
plus a small JS/HTML Mini App. Declared modules: `providers/`, `handlers/` (14
subpackages), `llm/`, `whisper/`, `tts/`, `miniapp/`. Observed structure matches
the declared one closely — providers are cleanly factored behind a Protocol +
registry, and handlers are decomposed by feature. The notable divergence is
`session_manager`, which remains a read/write hub still referenced by 30 handler
files despite the intended `window_query`/`session_query` read layer.

## Intended architecture

Source order: live interview (unavailable) → `.claude/rules/architecture.md` and
`CLAUDE.md` → the 2026-05-01 modularity review → directory structure. All sources
agree: feature-isolated handlers, Protocol-bounded providers and external
integrations, a pure decision kernel, and DI'd stores. No source conflicts found.

## Observed architecture

Code matches intent in the large: the provider abstraction and handler
decomposition are real, not aspirational. The gaps are localized — the read-layer
migration is ~57% adopted by file count, and `polling/polling_state.py` still
exposes 5 module-level singletons that bind the otherwise-pure `decide.py` kernel
at import time.

## Score map

| Dimension               | Value | Band        | Confidence | Justification                                                                 |
| ----------------------- | ----- | ----------- | ---------- | ----------------------------------------------------------------------------- |
| boundary_integrity      | 68    | serviceable | medium     | Boundaries explicit and test-enforced; read-layer migration incomplete (F1).  |
| coupling_balance        | 58    | mixed       | medium     | Protocol boundaries good; session_manager hub + polling singletons drag (F3). |
| dependency_graph_health | 50    | mixed       | low        | No graph built — stale index, missing tools (F4). Provisional.                |
| cohesion_modularity     | 64    | serviceable | medium     | Strong subpackage decomposition; several 1000+ LOC modules (F2).              |
| change_locality         | 60    | mixed       | medium     | Active decomposition of hotspots; churn split by rename.                      |
| architecture_fitness    | 78    | serviceable | medium     | Executable checks gate commits (F5).                                          |
| analysis_confidence     | 58    | mixed       | medium     | One structural tool carried most load; dependency dimension thin.             |

## Key findings

- **F1 (medium, boundary):** 30 handler files reference `session_manager`
  directly; the intended read layer (`window_query`/`session_query`) is imported
  by 39. Migration is real but incomplete.
- **F2 (medium, cohesion):** `tmux_manager.py` (1199), `hook.py` (1143),
  `directory_callbacks.py` (1086), `polling_state.py` (1017) concentrate change
  risk.
- **F3 (medium, coupling):** 5 module-level singletons in `polling_state.py`
  create import-time coupling that undercuts the pure-kernel goal.
- **F4 (low, dependency):** dependency-graph health unverified — score is
  provisional pending a fresh index and a dep-graph tool.
- **F5 (low, strength):** executable fitness checks gate commits — a genuine
  strength, kept as a finding so repeat reports track it.

## Coupling review

Strongest, most distant integrations are the provider adapters — but these are
correctly behind a Protocol, so high distance pairs with low strength (balanced).
The unbalanced spot is `session_manager`: high strength (30 direct call sites),
low distance (in-process), moderate volatility (state hub touched by UX work).
The polling singletons add implicit coupling at import time. No distributed
monolith risk — this is a single process.

## Boundary violations

No forbidden cross-language or cross-service leaks (single process, single wheel).
The one standing boundary issue is the read-path bypass (F1): handlers reading
state through `session_manager` instead of the query layer. Enforced direction is
correct; enforcement is partial.

## Change locality and hotspots

Current-name hotspots: `bot.py`, `handlers/cleanup.py`, `message_queue.py`,
`tmux_manager.py`, `session.py`, `msg_broker.py`, `config.py`. The recent history
shows active decomposition (commands/, polling/, recovery/ splits), which is the
right trend. Churn analysis is impaired by the `ccbot`→`ccgram` rename, which
splits each file's history across two paths unless `--follow` is used per file.

## Recommendations

Incremental only. (1) Finish the read-layer migration (F1) and harden the AST-walk
test to fail on new direct reads. (2) Split the four 1000+ LOC modules (F2) along
existing internal sections. (3) Move polling singletons behind DI (F3). (4) Refresh
the gitnexus index and install a Python dep-graph tool, then re-score dependency
health (F4). No rewrites.

## Plan summary

See `plan.md` in this directory — a phased plan derived from F1–F4.

## Evidence appendix

E1–E6 in frontmatter. All evidence is re-checkable via the cited commands/files.
Dependency evidence (E6) is a coverage gap, not a finding of health.

## Tool coverage and gaps

Carried mostly by `ast-grep` and `git`. **Dependency dimension is the gap:**
gitnexus index stale (failed as authoritative), and pydeps/import-linter/deptry
not installed. Semantic dimension skipped (LSP/pyright not exercised for graphs).
This caps `analysis_confidence` at medium and `dependency_graph_health` at low.
