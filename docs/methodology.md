# Methodology

Two methodology skills drive the qualitative judgments behind the scores:
`methodology-balanced-coupling` (the `coupling_balance` dimension) and
`methodology-architecture-fitness` (the `architecture_fitness` dimension). This
page summarizes both; the skills are the source of truth.

## Balanced Coupling

Coupling is not the enemy — it is what makes a system more than its parts. The
question is never "is this coupled?" but "is this coupling _balanced_?" The model
evaluates the **connection** between two components along three dimensions:

1. **Integration strength** — how much knowledge the components share (the
   _likelihood_ a change in one forces a change in the other), strongest to
   weakest: **intrusive** (private internals, shared DBs) → **functional** (shared
   business requirements) → **model** (shared domain model) → **contract**
   (explicit, stable interface hiding internals — the goal for high-distance
   integration).
2. **Distance** — how far apart the components sit (the _cost_ of a cascading
   change): methods → objects → packages → services → systems. Relative to the
   level analyzed, and socio-technical (different teams = further apart). In
   reviews, record distance as separate signals when possible: **code** distance,
   **ownership** distance, **runtime** distance, and **deploy** distance. Runtime
   coupling counts: synchronous calls bind lifecycles tighter than async.
3. **Volatility** — how likely a component is to change at all. Estimated from the
   business domain (DDD subdomains), not commit history: **core** (competitive
   advantage) → high; **supporting** and **generic** → low functional volatility.
   Commit churn and co-change support volatility claims, but they do not define
   domain volatility. A stable component coupled to a volatile one inherits
   **inferred volatility** — score it by what it must change with, not its own
   subdomain alone. Provider swaps, SDK churn, or leaking vendor DTOs are a
   separate **implementation/provider volatility** signal that can justify a
   stronger boundary even when business volatility is low.

**The balance rule:** modularity emerges when strength and distance
_counterbalance_ (one high, one low); complexity emerges when they _match_. Read
it two ways — a quick binary rule, and a graded equation that scores each
dimension 1–10 from evidence:

```text
BALANCE = (STRENGTH XOR DISTANCE) OR NOT VOLATILITY
BALANCE = max( |STRENGTH - DISTANCE|, 10 - VOLATILITY ) + 1
```

High strength + low distance = healthy cohesion; low strength + high distance =
healthy loose coupling. **High strength + high distance = tight coupling** — the
step toward a distributed monolith. Volatility is the override: unbalanced
coupling on something that never changes is tolerable. The worst case, flagged
first, is **high strength + high distance + high volatility**.

The graded read keeps the numbers honest by anchoring each input to evidence —
distance is mostly tool-derivable (paths, package graph, deploy units, ownership);
strength is a tool-found edge whose _kind_ of knowledge (model vs. contract,
same-rule duplication) is classified by reading the code; volatility is a domain
judgment corroborated by change history and propagated as inferred volatility
along dependency edges. The scores are reproducible estimates for ranking
relationships, not objective measurements. The skill carries the full
evidence→band rubric and the book's scale anchors.

Generic subdomains need extra suspicion. Their business function may be stable,
but their implementation can be volatile if provider swaps, dual-provider runs,
or vendor-specific errors and DTOs are plausible. In that case, provider leakage
into core code is still a coupling risk.

The skill does not recommend generic "decouple everything" advice — breaking
balanced (high-cohesion, low-distance) coupling adds distance and _unbalances_ it.
Fixes move one dimension: introduce a contract (lower strength), co-locate (lower
distance), or confirm low volatility leaves it alone — never a rewrite. Connascence is the
model's _degree_ axis within a strength type: static connascence (name → type →
meaning → algorithm → position) grades contract and model coupling; dynamic
connascence (execution → timing → value → identity), with symmetric functional
coupling on top, grades functional coupling. Use it to place the 1–10 strength
value and to break ties — shared meaning, algorithm, timing, or identity beats a
mere shared name for priority.

## How the review applies the model

A full architecture review scores `coupling_balance` from **relationship records**,
not prose impressions. For each important relationship, the review records:

- relationship and abstraction level;
- integration strength (type, connascence degree, and 1–10 estimate) plus evidence;
- distance split into code, ownership, runtime, and deploy signals, with a 1–10
  estimate, plus evidence;
- domain volatility first (1–10), with inferred, implementation/provider
  volatility and churn as supporting evidence;
- the computed BALANCE, balance verdict, severity, and the cheapest balancing move.

A quick sweep uses the same vocabulary, but returns **candidates and next checks**
instead of final findings or scores. No evidence means no finding; no full review
means no score.

When archfit is available, use it as the deterministic measurement layer:
`archfit analyze` supplies report-only classified edges, findings, tool coverage,
and agent tasks; add `--base <ref>` for delta evidence. Use `archfit check` (also
with `--base <ref>` for deltas) only when enforcing configured gates. The
architect then calibrates those facts against
intent, runtime/deploy context, and domain volatility. The combined loop is:
archfit facts → independent architect judgment → human-confirmed volatility and
labels → executable fitness checks → re-review. Do not chain archfit's LLM
narrative into architect as proof; the value comes from deterministic facts plus
independent judgment.

### Attribution and licensing

The Balanced Coupling model is the work of **Vlad Khononov** — see
[coupling.dev](https://coupling.dev) and the book _Balancing Coupling in Software
Design_. The reference material that inspired the skill (`vladikk-modularity`) is
licensed **CC BY-NC-SA 4.0**.

This extension uses Balanced Coupling **summary-only, in our own words, with
attribution.** That keeps the repo's MIT license clean: ShareAlike would
otherwise force any _adapted_ derivative under CC BY-NC-SA and bar commercial use.
Ideas and terminology are not copyrightable; specific expression is. Contributors
must not paste, quote, or closely paraphrase the source, or copy its tables and
diagrams. Anything beyond summary needs Vlad's sign-off (parked in the plan's
Post-Completion).

## Architecture fitness

Architecture intent that lives only in a doc is a suggestion; intent that runs in
CI is enforced. A **fitness function** is an automated check that fails the build
when the system drifts from an intended architectural property — a layering rule,
an allowed-dependency rule, a cycle ban, a size budget. This is Neal Ford /
_Building Evolutionary Architectures_ territory.

The review distinguishes two things, and conflating them inflates the score:

- **Existing check** — runs automatically (CI, pre-commit, test suite), can
  **fail** the build, and asserts an _architectural_ property. Only existing,
  enforced checks raise the `architecture_fitness` score, and they must be cited
  as evidence.
- **Recommended check** — proposed because intent is currently unenforced. It
  belongs in the report's recommendations and the plan; it does **not** raise the
  score.

A repo with thorough architecture docs and zero enforcement scores _low_ on
fitness, not high. In a refactoring plan, each boundary repair pairs with the
fitness check that holds it, ordered as a postcondition of the phase that fixes
the boundary, so the boundary cannot silently re-rot.
