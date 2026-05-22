# Fixture: python-boundaries

A small Python package whose intended boundaries are declared but violated.

Intended layering (declared in `importlinter.ini`):

- `shop.orders` and `shop.billing` are independent sibling contexts.
- Both may use `shop.shared`.
- `orders` must **not** import `billing` and vice versa.

Encoded violation (`boundary_integrity`, `coupling_balance`): `shop.orders.service`
imports `shop.billing.invoice` directly, breaking the independence contract.
`import-linter` run against `importlinter.ini` reports the broken contract.

Referenced as a lighter-weight fixture: the eval harness asserts the manifest
and the violating import are present; it does not ship a full golden report.

Git history omitted by design (no nested `.git`).
