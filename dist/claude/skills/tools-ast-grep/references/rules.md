# ast-grep rules for architecture evidence

Named YAML rules for patterns the review reuses. Run with
`ast-grep scan -r <file>.yml`. Each rule uses relational matchers (`inside`,
`has`, `not`) that an inline `-p` pattern can't express. Keep rules small and
named after the finding class they catch.

## Forbidden import inside a layer

Domain/core code must not import infrastructure packages directly.

```yaml
id: domain-imports-orm
language: typescript
rule:
  pattern: import $$$ from "$PKG"
  inside:
    kind: program
constraints:
  PKG:
    regex: "typeorm|pg|mysql2"
```

Scope to the layer with a path on the scan: `ast-grep scan -r rule.yml src/domain`.

## Direct DB access outside the data layer

```yaml
id: direct-db-access
language: typescript
rule:
  any:
    - pattern: createConnection($$$)
    - pattern: $POOL.query($$$)
```

## Routes declared outside the router module

A framework leak: HTTP routes wired up far from the routing layer.

```yaml
id: stray-route
language: typescript
rule:
  pattern: $APP.$METHOD($PATH, $$$)
constraints:
  METHOD:
    regex: "^(get|post|put|patch|delete)$"
```

Run this scoped to everything except the router dir; surviving hits are leaks.

## Framework type leaking past a boundary

```yaml
id: request-type-leak
language: python
rule:
  pattern: $REQ
  inside:
    kind: typed_parameter
constraints:
  REQ:
    regex: "Request|Response"
```

Scope to the domain package — a web `Request` type in domain signatures couples
the core to the transport.

## Exported surface survey

```yaml
id: exports
language: typescript
rule:
  pattern: export $$$
```

Counts and lists the public surface; a growing count between reviews flags
surface-area creep (pair with knip / exported-symbol diff in tools-typescript).

## Notes

- Constraints use `regex` on metavariables to keep one rule covering a family of
  packages or methods.
- A rule that returns zero hits is evidence of absence only if the language and
  scope are right. Confirm the rule matches a known positive before trusting a
  clean result.
- These are evidence-gathering rules, not enforcement. To stop a pattern from
  returning, the refactoring plan turns the rule into a CI fitness check (see
  methodology-architecture-fitness).
