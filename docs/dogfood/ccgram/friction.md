# Dogfood friction log — ccgram pass 1 (2026-05-22)

Friction surfaced running the architecture-review loop against
`/Users/alexei/Workspace/ccgram`. Each item is referenced by the tuning changes
applied to `src/skills/` and `src/templates/`.

## FR1 — Interview skill assumes an interactive user

The review procedure step 1 ("Interview if context is missing") asks the user
questions. In an autonomous/CI run there is no user. I reconstructed intent from
`CLAUDE.md`, `.claude/rules/architecture.md`, the modularity review, and the
CHANGELOG, then recorded it as lower-confidence context. The skill never says
this is allowed or how to flag it.
**Fix:** document a non-interactive fallback in the review skill and
`references/interview.md` — reconstruct from docs, label the context as
reconstructed, and cap confidence.

## FR2 — ast-grep boundary patterns must be derived, not guessed

I guessed `session_manager.get_$M` for read-path violations and got 0 matches;
the real accessors are named differently, and `session_manager.$METHOD`
over-matched by catching legitimate writes (`set_*`, `prune_*`, `sync_*`). A
single naive pattern conflates reads and writes.
**Fix (deferred to Task 6 ast-grep skill):** the ast-grep skill must say to
derive patterns from the actual codebase first (grep for the accessor names) and
to separate read from write patterns before counting. Recorded here so the Task 6
skill carries a concrete worked example.

## FR3 — Stale index handling is real and unaddressed in the loop

`gitnexus status` reported the index stale (indexed commit ≠ current). The review
skill step 3 says "use codegraph/GitNexus" but never says to check freshness
first. A stale graph silently produces wrong evidence.
**Fix:** review skill step 3 must require a freshness/staleness check before
trusting any persistent index, and record a coverage gap (not a false reading)
when stale.

## FR4 — Sandbox breaks language tools via cache writes

`ruff check` failed creating `.ruff_cache/.../.tmp...` under the target repo (sandbox
write deny). It only worked with `RUFF_CACHE_DIR=$TMPDIR/...`. Any tool that writes
a cache into the target repo will fail the same way.
**Fix:** note in the review skill (and later the language tool skills) to redirect
tool caches to a writable temp dir when scanning a target repo.

## FR5 — Missing Python dep-graph tools, no graceful degradation guidance

pydeps, import-linter, deptry, pipdeptree, radon are not installed. The dependency
dimension had no working tool except a stale gitnexus. The loop has no rule for
"applicable dimension, no working tool" beyond generic coverage recording.
**Fix:** review skill must state that a dimension with no working tool is recorded
as missing-tool coverage with explicit confidence impact, and must not be silently
scored from imports alone without flagging it. (Already partly covered; made
explicit.)

## FR6 — Churn analysis broken by directory rename

`git log --name-only` split each file's history across `src/ccbot/` (old) and
`src/ccgram/` (new), halving apparent churn and burying real hotspots. Naive churn
counting is wrong across renames.
**Fix:** review skill change-locality guidance must warn that renames split churn
and to scope churn to current paths or use `--follow` per file.

## FR7 — Report template `team_ownership` / `domains` cardinality friction (minor)

Filling `domains.core/supporting/generic` and `team_ownership` for a
single-maintainer repo felt like ceremony. Kept them (schema stability matters for
compare-reports) but worth noting the template offers no "single maintainer / not
applicable" guidance. **No change applied** — schema stability outweighs the minor
friction; recorded for a future pass.

## Tuning applied this pass

Traceable edits to source (see commit):

- Review SKILL.md step 1 + interview reference → FR1 (non-interactive fallback).
- Review SKILL.md step 3 → FR3 (index freshness check), FR4 (cache redirect),
  FR5 (no-working-tool coverage rule).
- Review SKILL.md change-locality guidance → FR6 (rename-aware churn).
- FR2 deferred to the Task 6 ast-grep skill with a worked example noted here.
- FR7 intentionally not applied (schema stability).
