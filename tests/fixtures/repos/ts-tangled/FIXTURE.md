# Fixture: ts-tangled

The same order service as `ts-healthy`, deliberately degraded to encode
**unhealthy** architecture. It is the paired bad fixture: it must score worse
than `ts-healthy` on the same dimensions, and every dropped dimension must be
explained by a finding.

Properties under test:

- **Import cycle** (`dependency_graph_health`, `boundary_integrity`):
  `order.ts` ↔ `gateway.ts` import each other.
- **Layer leak** (`boundary_integrity`, `coupling_balance`): the infra-level
  `gateway.ts` reaches into a private domain internal (`_applyTax`) instead of a
  published interface — intrusive coupling at low distance.
- **God module** (`cohesion_modularity`): `gateway.ts` mixes transport,
  persistence, and tax rules in one file.

Git history is omitted by design (no nested `.git`); change-locality evidence is
a recorded coverage gap in the baseline report.
