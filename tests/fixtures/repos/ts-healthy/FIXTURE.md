# Fixture: ts-healthy

A small layered TypeScript service that encodes **healthy** architecture.

Property under test: clean layering with no cross-boundary leaks.

- `src/domain/` — pure domain types and rules. Imports nothing from `app` or `infra`.
- `src/app/` — use-cases. Depends on `domain` only.
- `src/infra/` — adapters. Depends on `domain` (via interfaces) only; never imported by `domain`.

There are no import cycles, and the dependency direction is strictly inward
(`infra` → `app` → `domain`). A dependency-cruiser run would report zero
violations.

Git history is omitted by design — a nested `.git` would conflict with the
parent repository. Change-locality evidence is therefore out of scope for this
fixture and recorded as a coverage gap in the baseline report.
