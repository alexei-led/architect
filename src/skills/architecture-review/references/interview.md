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

Branch on the runtime's `structured_questions` capability:

- Concrete tool available (Claude `AskUserQuestion`, Pi `ask_user_question`):
  use it; offer discrete options where the choice is bounded.
- `unverified` or unset (Codex, for now): ask plain numbered questions in prose.

Ask one focused batch, not a long interrogation. If the user defers, record the
gap in `missing_evidence` and let it lower `analysis_confidence` rather than
guessing intent.
