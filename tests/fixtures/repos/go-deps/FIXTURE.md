# Fixture: go-deps

A small Go module encoding a **dependency-shape** smell. Go forbids true import
cycles, so the smell is a layering inversion plus a hub package:

- `internal/model` is meant to be the leaf (pure types) but imports
  `internal/store`, inverting the intended direction
  (`handler` → `store` → `model`).
- `internal/store` and `internal/handler` both depend on `model`, making it a
  hub whose every change ripples outward (`dependency_graph_health`,
  `change_locality`).

Evidence sources: `go list -deps ./...`, `go mod graph`, `goda` if available.

Referenced as a lighter-weight fixture: the harness asserts `go.mod` exists and
the inverted import is present; no full golden report ships for it.

Git history omitted by design (no nested `.git`).
