# Interview reference

The interview captures intended architecture and constraints before any quality
judgment. Its output populates `interview_context` in the report frontmatter.

## Inspect before you ask

Never ask a question the repository already answers. Read first:

- READMEs, `docs/`, ADRs, design notes — stated intent and goals.
- Manifests and config — declared modules, packages, ownership, deploy units.
- Directory structure — candidate units and layers.

Then ask only what inspection cannot settle, and only questions whose answers
change the assessment. Confirm what you inferred rather than asking it open-ended
("I see three deploy units — A, B, C. Correct?") .

## Fields to capture

Maps directly to `interview_context` in `src/templates/report.md`:

- `system_goal` — what the system is for.
- `quality_goals` — e.g. maintainability, change locality, deploy independence.
- `intended_units` — modules, services, packages, deploy units as intended.
- `domains` — core, supporting, generic (DDD subdomains; explain on first use).
- `volatile_areas` — what changes often or is expected to.
- `team_ownership` — who owns what; team boundaries.
- `known_pain` — where the user already feels friction.
- `review_scope` / `out_of_scope` — what to assess and what to exclude.

## Asking questions

Use whatever structured-question tool the active runtime exposes
(`AskUserQuestion`, `ask_user_question`, or equivalent). Offer discrete options
where the choice is bounded.

If no structured-question tool is available, ask one plain question in prose.
Include concise labeled options when useful, understand the answer from text, and
continue. If the answer is ambiguous or the user defers, record the gap in
`missing_evidence` and let it lower `analysis_confidence` rather than guessing
intent.

## Non-interactive mode

When no user is reachable (CI, autonomous loop), do not skip the interview —
reconstruct it. Read CLAUDE.md, `.claude/rules/`, ADRs, design docs, modularity
or architecture reviews, and the changelog, and fill `interview_context` from
them. State in the report that the context is reconstructed, not interview-sourced,
and cap `analysis_confidence` at `medium`. Never invent goals or ownership the
sources do not support; leave unknowns in `missing_evidence`.
