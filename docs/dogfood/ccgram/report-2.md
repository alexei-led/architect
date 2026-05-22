---
artifact: architecture-report
schema_version: 1
rubric_version: 1
report_id: ccgram-dogfood-2
date: 2026-05-22
supersedes: ccgram-dogfood-1

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
    - session.py remains a 30-importer read/write hub (graph-confirmed this pass)
    - polling/polling_state holds 5 module-level singletons (import-time coupling)
    - 8 import 2-cycles, mostly intra-package re-export coupling (graph-confirmed)
  high_risk_entrypoints:
    - bot.py (application factory, top churn)
    - handlers/polling (every UX overhaul touches it)
    - session.py / session_map.py (state hub, 30 importers)
  missing_evidence:
    - cycle severity ranking (only 2-hop import cycles enumerated, not full SCCs)
    - Python import-contract enforcement (import-linter/pydeps still not installed)
    - semantic call-graph confidence (codegraph not initialized for this repo)

scores:
  boundary_integrity:
    value: 74
    band: serviceable
    confidence: medium
    evidence_refs: [E2, E5]
    gaps:
      - read-layer migration nearly complete; 10 handler direct refs remain
  coupling_balance:
    value: 56
    band: mixed
    confidence: medium
    evidence_refs: [E2, E4, E6]
    gaps:
      - session.py 30-importer hub; 8 import cycles graph-confirmed
  dependency_graph_health:
    value: 58
    band: mixed
    confidence: medium
    evidence_refs: [E6]
    gaps:
      - import-linter/pydeps absent; cycles enumerated 2-hop only
  cohesion_modularity:
    value: 64
    band: serviceable
    confidence: medium
    evidence_refs: [E3]
    gaps:
      - four modules still exceed 1000 LOC, unchanged since pass 1
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
      - fitness checks cited from repo config; not re-executed in this pass
  analysis_confidence:
    value: 64
    band: serviceable
    confidence: medium
    evidence_refs: [E6]
    gaps:
      - dependency dimension now graph-backed; import-contract tooling still absent

findings:
  - id: F1
    title: Read-layer migration nearly complete — 10 handler files still reference session_manager directly
    severity: low
    dimension: boundary_integrity
    evidence_refs: [E2]
    recommended_action: >-
      Migrate the remaining 10 direct read call sites to window_query/session_query,
      then tighten the AST-walk enforcement test to fail on any new direct read.
      Down from 30 in pass 1 — the gate is working.
  - id: F2
    title: God modules over 1000 LOC concentrate change risk
    severity: medium
    dimension: cohesion_modularity
    evidence_refs: [E3]
    recommended_action: >-
      Split tmux_manager.py (1199), hook.py (1141), directory_callbacks.py (1091),
      and polling/polling_state.py (1017) along the seams already implied by their
      internal sections. Unchanged since pass 1.
  - id: F3
    title: Module-level singletons in polling_state create import-time coupling
    severity: medium
    dimension: coupling_balance
    evidence_refs: [E4]
    recommended_action: >-
      Continue the documented kernel split; move the 5 singletons behind
      constructor DI so the pure decide.py kernel is not transitively bound to them.
  - id: F5
    title: Executable architecture-fitness checks exist and gate commits
    severity: low
    dimension: architecture_fitness
    evidence_refs: [E5]
    recommended_action: >-
      Keep. The AST-walk read-path test, lazy-import lint, pyright 0-errors gate,
      and make check make intent enforceable rather than aspirational — a strength.
  - id: F6
    title: Eight import cycles, mostly intra-package re-export coupling
    severity: low
    dimension: dependency_graph_health
    evidence_refs: [E6]
    recommended_action: >-
      Cycles cluster in handlers/recovery, handlers/topics, and handlers/live
      (sibling re-export coupling) plus cli<->main and bot<->main bootstrap pairs.
      Add an import-linter contract to forbid new sibling cycles; the bootstrap
      pairs are benign. None cross a domain boundary.

evidence:
  - id: E1
    type: command
    command: "git log --since=12mo --name-only -- src/ccgram"
    summary: >-
      Current-name hotspots unchanged in rank from pass 1: bot.py, handlers/cleanup.py,
      message_queue.py, tmux_manager.py, session.py. History pre-rename lives under src/ccbot.
  - id: E2
    type: command
    command: "rg -l session_manager src/ccgram/handlers; rg -l 'window_query|session_query' src/ccgram/handlers"
    summary: >-
      10 handler files still reference session_manager directly (was 30 in pass 1);
      37 import the window_query/session_query read layer. Migration nearly complete.
  - id: E3
    type: command
    command: "find src/ccgram -name '*.py' | xargs wc -l | sort -rn | head"
    summary: >-
      Largest modules unchanged: tmux_manager.py 1199, hook.py 1141,
      handlers/topics/directory_callbacks.py 1091, handlers/polling/polling_state.py 1017.
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
    type: graph-query
    query: "MATCH (a:File)-[r1:CodeRelation]->(b:File)-[r2:CodeRelation]->(a) WHERE r1.type='IMPORTS' AND r2.type='IMPORTS' AND a.filePath < b.filePath RETURN a.filePath, b.filePath"
    summary: >-
      gitnexus reindexed this pass (16,614 nodes, 37,969 edges, 1,437 IMPORTS edges).
      8 import 2-cycles, all intra-package or bootstrap (recovery/, topics/, live/,
      cli<->main, bot<->main). session.py has 30 file importers (hub confirmed).
      Closes the pass-1 dependency gap; confidence rises low->medium.

tool_coverage:
  - dimension: discovery
    tools_used: [git, fd, rg, wc]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
  - dimension: structural
    tools_used: [ast-grep, rg]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: low
  - dimension: semantic
    tools_used: []
    tools_skipped: [pyright, codegraph, tree-sitter]
    tools_missing: []
    tools_failed: []
    confidence_impact: medium
  - dimension: dependency
    tools_used: [gitnexus]
    tools_skipped: [codegraph]
    tools_missing: [pydeps, import-linter, deptry, pipdeptree]
    tools_failed: []
    confidence_impact: medium
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
    tools_missing: [syft, trivy]
    tools_failed: []
    confidence_impact: low
  - dimension: report
    tools_used: [ruff, jq]
    tools_skipped: []
    tools_missing: []
    tools_failed: []
    confidence_impact: none
---

# Architecture report: ccgram (pass 2)

## Executive summary

Second autonomous dogfood pass on ccgram, run after the pass-1 report identified an
under-evidenced dependency dimension. This pass reindexed the repo with `gitnexus`
(16,614 nodes / 37,969 edges) and queried the import graph directly, closing the
pass-1 gap. Two changes since pass 1 are material: the read-layer migration advanced
(handler files referencing `session_manager` directly fell from 30 to 10), and the
dependency graph is now real evidence rather than a coverage hole — its confidence
rises low → medium and the dimension score from 50 → 58. The persistent risks are
unchanged: four 1000+ LOC god modules and import-time singletons in polling. Eight
import 2-cycles surfaced; all are intra-package re-export coupling or bootstrap
pairs, none cross a domain boundary. Overall: serviceable-to-mixed, medium confidence.

## Interview context

No live interview (autonomous pass). Intent reconstructed from `CLAUDE.md`,
`.claude/rules/architecture.md`, the 2026-05-01 modularity review, and `CHANGELOG.md`,
identical to pass 1. Reconstructed intent remains lower-confidence than a live
interview.

## System map

Single deployable `ccgram` wheel, 175 Python source files (~46K LOC), one console
entrypoint with sub-commands. Declared module structure matches observed structure.
The graph this pass confirms two structural facts that pass 1 inferred: `session.py`
is a 30-importer hub, and the codebase has 8 short import cycles concentrated in the
recovery, topics, and live handler subpackages plus the cli/main and bot/main
bootstrap pairs.

## Intended architecture

Source order unchanged from pass 1: live interview (unavailable) →
`.claude/rules/architecture.md` and `CLAUDE.md` → modularity review → directory
structure. No source conflicts.

## Observed architecture

Code matches intent in the large. The read-layer migration is now ~79% adopted by
handler file count (37 query-layer importers vs 10 direct holdouts), up from ~57% in
pass 1 — the AST-walk gate is working. `polling/polling_state.py` still exposes 5
module-level singletons. The import graph shows no domain-crossing cycles.

## Score map

| Dimension               | Value | Band        | Confidence | Δ vs pass 1         | Justification                                                          |
| ----------------------- | ----- | ----------- | ---------- | ------------------- | ---------------------------------------------------------------------- |
| boundary_integrity      | 74    | serviceable | medium     | +6                  | Read-path direct refs 30→10; gate enforced (F1).                       |
| coupling_balance        | 56    | mixed       | medium     | -2                  | Hub + singletons + 8 graph-confirmed cycles (F3, F6).                  |
| dependency_graph_health | 58    | mixed       | medium     | +8, conf low→medium | Graph built this pass; gap closed (F6). import-linter still absent.    |
| cohesion_modularity     | 64    | serviceable | medium     | 0                   | Four 1000+ LOC modules unchanged (F2).                                 |
| change_locality         | 60    | mixed       | medium     | 0                   | Active decomposition; churn split by rename.                           |
| architecture_fitness    | 78    | serviceable | medium     | 0                   | Executable checks gate commits (F5).                                   |
| analysis_confidence     | 64    | serviceable | medium     | +6                  | Dependency dimension now graph-backed; import-contract tooling absent. |

## Key findings

- **F1 (low, boundary):** read-path migration nearly done — 10 direct
  `session_manager` refs remain (was 30). Severity downgraded from medium.
- **F2 (medium, cohesion):** four 1000+ LOC god modules, unchanged since pass 1.
- **F3 (medium, coupling):** 5 import-time singletons in `polling_state.py`.
- **F5 (low, strength):** executable fitness checks gate commits — kept as a tracked
  strength.
- **F6 (low, dependency):** 8 import cycles, all intra-package re-export or bootstrap;
  none cross a domain boundary. New this pass — only visible because the graph was built.

Resolved since pass 1: **F4** ("dependency-graph health unverified") — the graph is
now built, so the gap finding no longer applies. It is replaced by the concrete F6.

## Coupling review

Provider adapters: high distance, low strength (behind Protocol) — balanced. The
unbalanced spot remains `session.py`: high strength (30 importers, graph-confirmed),
low distance (in-process), moderate volatility. Polling singletons add implicit
import-time coupling. The 8 cycles are short and local; none indicate a distributed
monolith (single process).

## Boundary violations

No cross-language or cross-service leaks. The read-path bypass (F1) is the standing
boundary issue and is shrinking. No domain-crossing import cycles.

## Change locality and hotspots

Hotspot ranking unchanged from pass 1. Churn analysis still impaired by the
`ccbot`→`ccgram` rename. No new hotspots introduced.

## Recommendations

Incremental only. (1) Finish the read-layer migration (F1, now only 10 sites) and
harden the gate. (2) Split the four god modules (F2). (3) Move polling singletons
behind DI (F3). (4) Add an import-linter contract forbidding new sibling cycles (F6);
leave the benign bootstrap pairs. No rewrites.

## Plan summary

See `plan-2.md` in this directory — a phased plan derived from F1, F2, F3, F6.

## Evidence appendix

E1–E6 in frontmatter. E6 is now a real graph query (gitnexus), not a coverage gap.
All evidence is re-checkable via the cited commands/queries/files.

## Tool coverage and gaps

Dependency dimension upgraded from a high-impact gap to graph-backed (gitnexus
reindexed this pass). Remaining gaps: no Python import-contract tool
(import-linter/pydeps), codegraph not initialized, semantic call-graph not exercised.
This caps `analysis_confidence` at serviceable/medium rather than higher.
