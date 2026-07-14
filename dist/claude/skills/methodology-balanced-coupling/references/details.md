# Balanced Coupling — details

Supplementary notes for the methodology-balanced-coupling skill. Summary in our
own words; see `attribution.md` for source attribution and licensing.

## Implicit vs explicit coupling

Integration strength also tracks how visible the shared knowledge is:

- **Contract** coupling is the most explicit — the dependency is declared and
  stable.
- **Model** coupling is explicit but broader — the whole shared model is in
  play.
- **Functional** coupling is often **implicit** — duplicated business rules with
  no declared link still must change together.
- **Intrusive** coupling is the most implicit and fragile — the depended-on side
  may not know the dependency exists.

Implicit coupling is more dangerous than explicit coupling of the same strength:
nothing in the code points the next reader at the thing that will break. In a
review, surface implicit high-strength coupling even when no import edge
declares it (duplicated logic, shared DB tables, reflection, undocumented APIs).

## Distance is a trade-off

Lower distance makes co-evolution cheap but binds lifecycles — components close
together tend to build, test, and deploy together. **Lifecycle coupling** is the
counterforce to cost-of-change. Many monolith→microservices splits were really
about loosening lifecycle coupling, accepting higher co-evolution cost in
exchange.

- **Runtime coupling**: synchronous integration binds lifecycles tighter (a
  failure cascades); async messaging increases effective distance. If you
  increase distance this way, lower integration strength to keep balance.
  Async vs. sync changes distance, never integration strength — an event whose
  schema leaks the upstream domain model is still model (or stronger) coupling.
- **Socio-technical distance**: org structure moves distance independently of
  code (Conway's Law). Same code, two teams = further apart than one team.

## Fractal levels

The model applies at every level — methods, objects, packages, services,
systems — but what counts as a contract, a model, or an intrusive dependency
shifts with the level. A class's public interface is a contract at the object
level but an implementation detail at the service level.

Always state which level of abstraction you are assessing before applying the
rule. The same relationship can read as balanced or unbalanced depending on the
level. At any level, the highest distance available is that level's boundary —
so cross-module coupling inside one service is genuinely "high distance" for a
module-level review.

## DDD pattern mapping (volatility and contracts)

- **Bounded contexts** set medium-distance, shared-lifecycle boundaries around a
  shared model (model coupling).
- **Context integration patterns** set the knowledge-sharing level: shared
  kernel / partnership share more; anti-corruption layer and open-host service
  encapsulate behind a contract (contract coupling) — use these when distance is
  high.
- **Aggregates / value objects** co-locate (low distance) things with strong
  functional coupling — balanced by closeness.
- **Subdomains** are the primary volatility tool: core = high, supporting = low,
  generic = low functional volatility but variable implementation volatility.
  DDD explicitly tolerates pragmatic shortcuts in low-volatility supporting
  subdomains — low volatility neutralizes unbalanced coupling.

## Essential vs accidental volatility

Judge volatility from the domain, not the git log:

- **Accidental volatility** — a component churns because it is badly designed,
  not because the domain demands it.
- **Accidental involatility** — a component looks stable only because changing
  it is too risky; the business wants to change it but can't.

Either way, commit frequency is a hint, not the measure. Confirm against
subdomain classification before letting volatility move a finding.

## Inferred volatility

Volatility is a property of the upstream component, but it propagates. A
supporting- or generic-subdomain component that depends on a core (volatile)
upstream is **effectively volatile** — it is dragged into change every time the
upstream changes. Score volatility by the most volatile thing the component must
change with, not by its own subdomain in isolation, and propagate that estimate
along dependency edges (take the maximum along the path).

This is where a dependency or call graph earns its keep: it shows which
low-volatility components inherit a high-volatility upstream. A reviewer scoring
volatility by subdomain alone will under-rate the coupling risk of a quiet module
wired to a churning core. Eliminating infrastructural or core-domain knowledge
from a stable layer is often how you remove inherited (accidental) volatility.

## Generic subdomains and provider volatility

Generic functionality can be stable while its implementation is not. Auth,
payments, search, notifications, storage, AI providers, and media processing are
often solved problems at the business level, but the chosen vendor or library may
change. Design/review questions to ask:

- Is swapping providers plausible within the product horizon?
- Must multiple providers run at the same time?
- Do provider-specific DTOs, errors, retry rules, or limits leak into core code?
- Would a provider change be localized to one adapter, or would it ripple across
  business modules?

If provider churn is plausible, treat implementation volatility as high enough to
justify explicit contracts or anti-corruption boundaries even when functional
volatility is low. If provider churn is implausible and switching cost is
accepted, document the trade-off instead of manufacturing abstraction theater.

## Degree within each strength level (connascence)

Integration strength has two axes: the interface **type** (contract, model,
functional, intrusive — the coarse band) and the **degree** of knowledge inside
that type. Connascence is the degree axis; it picks the 1–10 value within a band:

- **Contract and model coupling** are graded by **static connascence**, weakest
  to strongest: name → type → meaning → algorithm → position. Even the strongest
  contract degree shares less knowledge than the weakest model degree — a model
  exposes implementation knowledge a contract hides.
- **Functional coupling** is graded by **dynamic connascence**, weakest to
  strongest: execution (order) → timing → value → identity, with **symmetric
  functional coupling** on top. Even the weakest functional degree ranks high on
  the strength scale.
- **Intrusive coupling** has no degree axis — it is always the strongest type.

Symmetric functional coupling — two modules implementing the same business rule,
which must change together — is the one strength level with **no dependency
edge**: the components need not call each other or even know each other exists.
Graph and call tools cannot see it; only reading both sides reveals it. It sits
just below intrusive in strength.

Do not lead with terminology. Lead with the shared knowledge and the change
scenario; use connascence to explain why one similar-looking dependency is worse
than another, and to place the 1–10 strength value within its type band.

## The graded balance equation

The binary rule (`(STRENGTH XOR DISTANCE) OR NOT VOLATILITY`) answers yes/no. To
rank relationships and compare options, score each dimension 1–10 and compute:

```text
MODULARITY = |STRENGTH - DISTANCE| + 1
BALANCE    = max( |STRENGTH - DISTANCE|, 10 - VOLATILITY ) + 1
```

Modularity is the gap between strength and distance — maximal when one is high
and the other low. BALANCE then lets low volatility compensate for low
modularity: the trailing `+ 1` makes the volatility term `11 - VOLATILITY`,
volatility's complement over the 1–10 range, so a stable upstream keeps BALANCE
high even when strength and distance both run high. Low BALANCE marks the
relationships to fix first.

Anchor values (the book's illustrative 1–10 scale, ch10 — see `attribution.md`):

- Strength: contract ~1, model ~3, functional ~8, symmetric functional ~9,
  intrusive ~10. The model→functional jump is deliberate — contract and model
  are "low strength," everything functional and up is "high strength." Leave 4–7
  sparse; let the connascence degree nudge ±1 within a type.
- Distance: methods in one object ~1, objects in one package ~2, different
  packages ~3–7, different libraries ~8, services in one system ~9, separate
  vendors/systems ~10.
- Volatility: legacy/frozen ~1, supporting or generic subdomain ~3, core
  subdomain (or inferred volatility from one) ~10.

The numbers are subjective estimates, not measurements — the book is explicit
that no objective metric exists today, and the same relationship scores
differently at different levels of abstraction. Their value is reproducibility
and comparison: anchor each input to observable evidence (below) so two reviewers
land near the same number, not so you can claim a precise score.

## Grounding the inputs in evidence

The book's author hoped a tool would one day derive strength, distance, and
volatility automatically; until then, anchor each input to the strongest evidence
available and reserve judgment for what no tool can decide. Tools name candidate
edges and metrics — they do not pronounce balance.

**Strength** — type first (sets the band), then connascence degree (nudges ±1):

- Find the edge and the symbols crossing it: dependency/call-graph tools
  (codegraph, language graphs like `go list`, dependency-cruiser, madge) and
  resolved references (LSP).
- Intrusive (~10): structural-pattern and text search (ast-grep, ripgrep) plus
  operational config — the same DB table or schema written by more than one
  module, reflection into private members, imports of internal-only paths.
- Functional execution/timing/transactional (~8): required call ordering, shared
  transaction scope, publish-then-write or saga pairs (ast-grep over call sites;
  message-bus and infra config).
- Symmetric functional (~9): duplication signals (jscpd, lizard) with no import
  edge — then read both copies to confirm they encode the same business rule.
- Model vs. contract (~3 vs. ~1): the crossing type is a rich domain entity
  (model) or a thin integration DTO that hides internals (contract). Tools
  surface the type; deciding whether it encapsulates or merely mirrors internals
  is LLM judgment — a renamed mirror of an internal entity is still model
  coupling (the DTO trap).

LLM judgment is irreducible for the _kind_ of knowledge: model vs. contract,
same-rule duplication, and atomicity requirements are semantic, not syntactic.

**Distance** — mostly tool-derivable:

- Closest common ancestor from file paths and the package/dependency graph (code
  search, codegraph, language graphs).
- Deploy units and runtime topology: operational config (Helm/Kustomize/K8s,
  Compose) and sync-vs-async call style (ast-grep). Async raises effective
  distance.
- Ownership: CODEOWNERS and git authorship (change-history tools, `git log`).
  Two teams are further apart than one.

Combine the three sub-signals (abstraction, runtime, ownership) into one 1–10
value; that combination is the only judgment step.

**Volatility** — domain-led, history-corroborated, graph-propagated:

- Subdomain classification sets the band — core vs. supporting vs. generic. No
  tool knows which subdomain is the company's competitive edge; this is domain
  judgment from the code's purpose and, when available, the interview.
- Change-history tools (GitNexus co-change, `git log` churn) corroborate within
  the band — high churn supports high volatility, but watch accidental
  volatility (bad design churns) and accidental involatility (too risky to
  touch). History adjusts, it does not override the subdomain call.
- The dependency graph propagates inferred volatility from volatile upstreams.
- Generic subdomains: functional volatility low, but judge implementation/provider
  volatility separately — whether provider DTOs leak (ast-grep) and whether a
  swap is plausible (judgment/interview).

Net: distance is largely evidenced, strength is a tool-found edge with an
LLM-classified kind, and volatility is a domain judgment with tool corroboration.
Record which inputs are evidenced and which are judgment so the BALANCE score
carries its own confidence — and when the edge is unclassified, follow the
`coupling_balance` coverage-gap rule in architecture-scorecard (low confidence,
cap at `mixed`) rather than asserting a number.

## Prior models, incorporated

Integration strength refines the classic module-coupling vocabulary (content,
common/external/control, stamp, data) and uses connascence levels for
finer-grained comparison within a level. You don't need that vocabulary to apply
the model, but it explains why the four levels are ordered as they are.
