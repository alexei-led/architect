---
name: methodology-balanced-coupling
description: >-
  Assess coupling with the Balanced Coupling model (integration strength,
  distance, volatility). Use when judging whether coupling is balanced or risky,
  scoring the coupling_balance dimension, or deciding what to flag as structural
  risk. Highest risk is high strength + high distance + high volatility together.
  NOT generic "decouple everything" advice. NOT for assigning the score itself
  (use architecture-scorecard) or for executable checks (use
  methodology-architecture-fitness).
---

# Balanced Coupling

A model for judging whether coupling between components is a problem or not.
Coupling is not the enemy — it is what makes a system more than its parts. The
question is never "is this coupled?" but "is this coupling balanced?"

This skill summarizes Vlad Khononov's model in our own words and maps it onto
the scorecard. For attribution and licensing, see
`references/attribution.md`. Do not paste, quote, closely paraphrase, or copy
tables/diagrams from the source.

## When to use

Use when judging whether a coupling relationship is a problem — scoring the
`coupling_balance` dimension, deciding what to flag as structural risk,
designing module boundaries, or sanity-checking a "decouple this"
recommendation. The architecture-review and architecture-design skills reach for
this when they find two components that share knowledge and ask whether that
sharing is balanced. Not for assigning the score itself (architecture-scorecard)
or for executable enforcement (methodology-architecture-fitness).

## Skill navigation

- Missing relationship evidence: return to `architecture-review` for observed
  code or `architecture-design` for proposed boundaries.
- Current skill: use `methodology-balanced-coupling` to classify strength,
  distance, volatility, severity, and balancing move.
- Next skill: use `architecture-scorecard` when scoring a review,
  `architecture-design` when revising target boundaries, or `architecture-plan`
  only when sequencing an approved balancing move.

## The three dimensions

Evaluate the connection between two components, not the components. Three
dimensions, each answering a different question.

1. **Integration strength** — how much knowledge the components share, which
   sets the likelihood a change in one forces a change in the other. Four
   levels, strongest to weakest:
   - **Intrusive** — integration through private internals: shared databases,
     undocumented APIs, implementation details. Fragile and often implicit; the
     intruded component may not know it is depended on.
   - **Functional** — components share business requirements and must change
     together when requirements do. Duplicated business rules across
     frontend/backend is the classic implicit case.
   - **Model** — components share a domain model; a model change ripples to all
     sharers.
   - **Contract** — integration through an explicit, stable contract that hides
     internals (facade, published language, anti-corruption layer, DTOs). Lowest
     shared knowledge. The goal for high-distance integration.

2. **Distance** — how far apart the components sit, which sets the cost of a
   cascading change. Rises through levels of abstraction: methods → objects →
   packages → services → systems. It is relative to the level you analyze —
   at any level, the highest distance is that level's own boundary. Two modules
   in one deployable can still be "high distance" relative to each other. It is
   socio-technical: two services owned by different teams are further apart
   than the same two owned by one team. Runtime coupling counts too —
   synchronous calls bind lifecycles tighter than async messaging.

3. **Volatility** — how likely a component is to change at all. Unbalanced
   coupling that never changes causes no pain. Estimate from the business
   domain first; use commit history only as supporting churn/change-locality
   evidence because poor design can inflate or suppress commit frequency:
   - **Core** subdomain (competitive advantage) → high volatility.
   - **Supporting** subdomain (needed, not differentiating) → low volatility.
   - **Generic** subdomain (solved problem, off-the-shelf) → low functional
     volatility, but watch implementation volatility (swapping a provider).

Explain DDD terms in plain language on first use — do not assume the user knows
"core subdomain."

## The balance rule

Modularity emerges when strength and distance counterbalance — one high, the
other low. Complexity emerges when they match — both high or both low.

- High strength + low distance = high cohesion (good). Things that change
  together live together; cascades are cheap.
- Low strength + high distance = loose coupling (good). Far apart, but they
  barely share knowledge, so cascades are rare.
- Low strength + low distance = low cohesion. Unrelated things crammed together;
  drifts toward a big ball of mud.
- High strength + high distance = tight coupling. Frequent cascades that are
  expensive to make. A step toward a distributed monolith.

Use the compact decision rule as a mnemonic, not fake math:

```text
BALANCE = (STRENGTH XOR DISTANCE) OR NOT VOLATILITY
```

That means a relationship is acceptable when strength and distance counterbalance
or when the relationship is unlikely to change. The worst case — the thing to
flag first — is high strength + high distance + high volatility.

Keep the level of abstraction explicit. A public class method can be a contract
inside one module and still be private implementation detail across a service
boundary. If the level changes, reclassify the relationship instead of reusing
the same label.

## Examples to calibrate judgment

- A module reads another module's private table or storage layout: intrusive
  strength. If those modules are owned or deployed apart and the domain changes,
  this is a priority finding.
- Frontend and backend duplicate a pricing rule: functional strength even when
  no import edge exists. The coupling is implicit; a requirement change must hit
  both sides.
- Two services share a broad `Customer` model: model strength. This may be fine
  inside one bounded context; across distant teams it needs a narrower contract.
- A payment adapter exposes provider DTOs everywhere: contract in name only. The
  provider model leaks, so implementation volatility should push toward an
  anti-corruption boundary.
- A single module keeps strongly-related rules and state together: high strength
  plus low distance. Do not split it merely to make a diagram cleaner. Diagrams,
  being obedient liars, will applaud anything.

## Using it in review and design

- Flag a review finding when strength and distance are both high and the area is
  volatile. That ordering is your severity signal — see severity mapping below.
- In a design, choose boundaries so high-strength relationships sit close and
  high-distance relationships use explicit contracts.
- Don't recommend decoupling balanced coupling. High-cohesion, low-distance
  coupling is correct; breaking it adds distance and unbalances it.
- To fix unbalanced coupling, move on one dimension: lower strength (introduce a
  contract), lower distance (co-locate), or confirm low volatility leaves it
  alone. Recommend the cheapest balancing move, not a rewrite.
- Deterministic tools such as archfit, codegraph, dependency-cruiser, madge,
  or GitNexus can supply candidate edges, cycles, hubs, and churn. Use those as
  evidence, not as the final Balanced Coupling judgment.
- Import cycles, layer inversions, and runtime/deploy entanglement may be scored
  primarily under dependency graph or boundary dimensions, but they still inform
  the coupling narrative because they raise cascade cost and distance.
- If the strength classifier is absent (no classified edges), you cannot assert
  balance. Record low confidence and cap `coupling_balance` at `mixed` until you
  establish the edges independently — a tool's "balanced, no classified edges"
  default is a coverage gap, not evidence of balance.
- This feeds the `coupling_balance` scorecard dimension. This skill judges
  balance; architecture-scorecard assigns the number.

## Severity mapping

- High strength + high distance + high volatility: critical — fix first.
- High strength + high distance + low volatility: medium — note and defer;
  volatility may rise.
- High strength + low distance: low — high cohesion, usually fine.
- Low strength + high distance: low — loose coupling, usually fine.
- Low strength + low distance + high volatility: medium — low cohesion in a
  churning area.

## Output

When applying the model, report:

- `relationship`: components and abstraction level assessed.
- `strength`: intrusive, functional, model, or contract; cite evidence.
- `distance`: abstraction, ownership, and runtime distance; cite evidence.
- `volatility`: domain volatility first, git/churn as supporting evidence.
- `deterministic_evidence`: tool IDs or commands that found the edge, cycle,
  co-change, or metric, plus any coverage limits.
- `severity`: mapped risk level.
- `balancing_move`: lower strength, lower distance, or leave alone.

See `references/details.md` for implicit-vs-explicit coupling, lifecycle and
runtime coupling, the fractal nature of levels, and DDD pattern mappings.
