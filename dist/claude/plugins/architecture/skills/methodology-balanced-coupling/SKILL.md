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
question is never "is this coupled?" but "is this coupling _balanced_?"

This skill summarizes the model in our own words and maps it onto the scorecard.
It does not reproduce the source. For depth, send the user to the source.

## Attribution and licensing

The Balanced Coupling model is the work of **Vlad Khononov** — see
[coupling.dev](https://coupling.dev) and the book _Balancing Coupling in
Software Design_. The reference material that inspired this skill
(`vladikk-modularity`) is licensed **CC BY-NC-SA 4.0**.

Decision for this extension: **summary-only, in our own words, with
attribution.** That keeps the repo's MIT license clean — ShareAlike would
otherwise force any _adapted_ derivative under CC BY-NC-SA and bar commercial
use. Ideas and terminology are not copyrightable; specific expression is.

Hard rule for contributors: do not paste, quote, or closely paraphrase the
source. No copying its tables or diagrams. If you find yourself reaching for the
original to get the wording right, stop — you are crossing into a derivative
that requires permission. Anything beyond summary needs Vlad's sign-off (parked
in the plan's Post-Completion).

## When to use

Use when judging whether a coupling relationship is a problem — scoring the
`coupling_balance` dimension, deciding what to flag as structural risk, or
sanity-checking a "decouple this" recommendation. The architecture-review skill
reaches for this when it finds two components that share knowledge and asks
whether that sharing is balanced. Not for assigning the score itself
(architecture-scorecard) or for executable enforcement
(methodology-architecture-fitness).

## The three dimensions

Evaluate the _connection_ between two components, not the components. Three
dimensions, each answering a different question.

1. **Integration strength** — how much knowledge the components share, which
   sets the _likelihood_ a change in one forces a change in the other. Four
   levels, strongest to weakest:
   - **Intrusive** — integration through private internals: shared databases,
     undocumented APIs, implementation details. Fragile and often implicit; the
     intruded component may not know it is depended on.
   - **Functional** — components share business _requirements_ and must change
     together when requirements do. Duplicated business rules across
     frontend/backend is the classic implicit case.
   - **Model** — components share a domain _model_; a model change ripples to
     all sharers.
   - **Contract** — integration through an explicit, stable contract that hides
     internals (facade, published language, anti-corruption layer, DTOs). Lowest
     shared knowledge. The goal for high-distance integration.

2. **Distance** — how far apart the components sit, which sets the _cost_ of a
   cascading change. Rises through levels of abstraction: methods → objects →
   packages → services → systems. It is **relative** to the level you analyze —
   at any level, the highest distance is that level's own boundary. Two modules
   in one deployable can still be "high distance" relative to each other. It is
   **socio-technical**: two services owned by different teams are further apart
   than the same two owned by one team. Runtime coupling counts too —
   synchronous calls bind lifecycles tighter than async messaging.

3. **Volatility** — how likely a component is to change _at all_. Unbalanced
   coupling that never changes causes no pain. Estimate from the _business
   domain_, not commit history (poor design can inflate or suppress commit
   frequency):
   - **Core** subdomain (competitive advantage) → high volatility.
   - **Supporting** subdomain (needed, not differentiating) → low volatility.
   - **Generic** subdomain (solved problem, off-the-shelf) → low _functional_
     volatility, but watch _implementation_ volatility (swapping a provider).

Explain DDD terms in plain language on first use — do not assume the user knows
"core subdomain."

## The balance rule

Modularity emerges when strength and distance **counterbalance** — one high, the
other low. Complexity emerges when they **match** — both high or both low.

- High strength + **low** distance = high cohesion (good). Things that change
  together live together; cascades are cheap.
- **Low** strength + high distance = loose coupling (good). Far apart, but they
  barely share knowledge, so cascades are rare.
- Low strength + low distance = low cohesion. Unrelated things crammed together;
  drifts toward a big ball of mud.
- **High strength + high distance = tight coupling.** Frequent cascades that are
  expensive to make. A step toward a distributed monolith.

Volatility is the pragmatic override: unbalanced coupling on a component that
won't change is tolerable. The worst case — the thing to flag first — is **high
strength + high distance + high volatility**.

## Using it in a review

- Flag a finding when strength and distance are both high _and_ the area is
  volatile. That ordering is your severity signal — see severity mapping below.
- Don't recommend decoupling balanced coupling. High-cohesion, low-distance
  coupling is correct; breaking it adds distance and _unbalances_ it.
- To fix unbalanced coupling, move on one dimension: lower strength (introduce a
  contract), lower distance (co-locate), or confirm low volatility leaves it
  alone. Recommend the cheapest balancing move, not a rewrite.
- This feeds the `coupling_balance` scorecard dimension. This skill judges
  balance; architecture-scorecard assigns the number.

## Severity mapping

| Strength | Distance | Volatility | Severity                                  |
| -------- | -------- | ---------- | ----------------------------------------- |
| high     | high     | high       | critical — fix first                      |
| high     | high     | low        | medium — note, defer; volatility may rise |
| high     | low      | any        | low — high cohesion, usually fine         |
| low      | high     | any        | low — loose coupling, usually fine        |
| low      | low      | high       | medium — low cohesion in a churning area  |

See `references/details.md` for implicit-vs-explicit coupling, lifecycle and
runtime coupling, the fractal nature of levels, and DDD pattern mappings.
