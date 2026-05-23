# Balanced Coupling — details

Supplementary notes for the methodology-balanced-coupling skill. Summary in our
own words; see `attribution.md` for source attribution and licensing.

## Implicit vs explicit coupling

Integration strength also tracks how _visible_ the shared knowledge is:

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
- **Socio-technical distance**: org structure moves distance independently of
  code (Conway's Law). Same code, two teams = further apart than one team.

## Fractal levels

The model applies at every level — methods, objects, packages, services,
systems — but what counts as a contract, a model, or an intrusive dependency
_shifts_ with the level. A class's public interface is a contract at the object
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

- **Accidental volatility** — a component churns because it is _badly designed_,
  not because the domain demands it.
- **Accidental involatility** — a component looks stable only because changing
  it is too risky; the business _wants_ to change it but can't.

Either way, commit frequency is a hint, not the measure. Confirm against
subdomain classification before letting volatility move a finding.

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

## Connascence as tie-breaker

Use connascence when two relationships sit in the same broad strength level and
you need finer prioritization:

- Static coupling visible in code: shared names, types, meanings, positions, or
  algorithms. Algorithm/meaning coupling is usually riskier than name coupling.
- Dynamic coupling visible in behavior: required call order, timing, shared
  values, identity, or execution context. Timing/order coupling is especially
  fragile across high-distance boundaries.

Do not lead with terminology. Lead with the shared knowledge and change scenario;
use connascence only to explain why one similar-looking dependency is worse than
another.

## Prior models, incorporated

Integration strength refines the classic module-coupling vocabulary (content,
common/external/control, stamp, data) and uses connascence levels for
finer-grained comparison within a level. You don't need that vocabulary to apply
the model, but it explains why the four levels are ordered as they are.
