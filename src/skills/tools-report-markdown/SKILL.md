---
name: tools-report-markdown
description: >-
  Produce and validate architecture-review report and plan artifacts: Markdown,
  YAML frontmatter, Mermaid diagrams, jq/yq checks, Graphviz/D2 graphs, links,
  spelling, and format. Use when writing or checking cited reports, system-map
  diagrams, score summaries, or refactoring plans. This is report-quality
  evidence, not architecture evidence. NOT for gathering findings (use
  tools-code-search, tools-codegraph, tools-ast-grep, tools-lsp-tree-sitter,
  language, and operational tool skills).
---

# Report and Markdown tools

The report is an artifact a human reads and a tool re-parses. These tools keep
its frontmatter machine-valid and its diagrams renderable, and they catch broken
links and typos before the report ships.

Evidence dimension: **report** (quality of the artifact, not the architecture).

## When to use

Use during the write-the-report step and before declaring a report or plan done.
Use to validate YAML frontmatter parses, render the system map as a diagram, and
check links/spelling. Diagrams are evidence summaries — a Mermaid module graph
beats a pasted edge list.

## Commands

```sh
# Validate report frontmatter parses as YAML (cheap gate before the helper)
yq '.scores' report.md          # yq reads frontmatter-style YAML
# extract + check a field with jq from a JSON intermediate
yq -o=json '.' report.md | jq '.tool_coverage'

# Render a Mermaid diagram to SVG (system map / dependency graph)
mmdc -i map.mmd -o map.svg

# Graphviz / D2 for graphs produced by pydeps, goda, go-callvis
dot -Tsvg graph.dot -o graph.svg
d2 graph.d2 graph.svg

# Link check (catches dead evidence refs and doc links)
lychee report.md docs/

# Spelling (technical dictionary as needed)
codespell report.md

# Format check (matches the repo's prose style if configured)
npx prettier --check "**/*.md"
```

The authoritative frontmatter/section validation is the
`validate-report` helper (Task 7) — these CLIs are for quick local checks and
diagram rendering, not a replacement for it.

## Evidence output

Record:

- `dimension`: report.
- `source`: validation/render/link/spell command and artifact path.
- `facts`: parsed frontmatter, rendered diagrams, valid links, or reported failures.
- `limits`: skipped cosmetic checks, missing renderer, or dropped diagrams.

## Confidence impact

This dimension does not affect architecture scores. A beautiful report with
thin evidence is still low confidence; a plain report with strong evidence is
high. Report tooling guards readability and machine-parseability only — never
let diagram polish stand in for evidence coverage.

## Failure and missing-tool handling

- Tool missing → skip the cosmetic check (record `tools_skipped` for the report
  dimension); it does not block a valid report. Frontmatter validity is the one
  thing that matters — if yq/the helper can't parse it, fix the frontmatter
  before shipping.
- `mmdc`/`dot` failing to render → the diagram source is malformed; fix it or
  drop the diagram. A broken diagram is worse than none.

## When to stop

Validate frontmatter, render the one or two diagrams the report needs, run a link
and spell pass. Stop there — don't generate a gallery of diagrams or chase
stylistic lint that doesn't change comprehension. Report tooling is the last
mile, not a place to spend the evidence budget.

## Hard rules

- Frontmatter must parse; everything else here is optional polish.
- Diagrams summarize evidence — they never substitute for cited refs.
- Report quality never raises an architecture score or its confidence.
- Use the CLIs; the authoritative schema check is the validate-report helper.
