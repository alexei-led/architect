---
name: architecture-design
description: >-
  Design a modular architecture from requirements, intended architecture notes,
  or an approved redesign brief. Use when asked to create architecture docs,
  define module boundaries, integration contracts, test specifications, or a
  target architecture before implementation. Blends Balanced Coupling,
  architecture-fitness thinking, and evidence from existing code when present.
  NOT for auditing current implementation quality (use architecture-review) or
  sequencing an already-approved design (use architecture-plan).
---

# Architecture design

Design a target architecture. The architect writes design artifacts; it does not
edit production source or implement the design.

## When to use

Use when the user wants a new or revised architecture from functional
requirements, product requirements, an ADR brief, or a known redesign goal. Use
also when an existing system needs target-state module docs, integration
contracts, or module test specifications before implementation.

If the user asks whether the existing implementation is healthy, start with
`architecture-review` instead. If the user has an architecture report with
findings but no approved target design, continue here before planning. If the
user already has an approved architecture design and wants execution steps, use
`architecture-plan` instead.

## Skill navigation

- Missing or untrusted picture of the existing implementation: run
  `architecture-review` first. Architecture docs may describe original intent;
  code, deploy files, and tests may have drifted.
- Current skill: use `architecture-design` to turn requirements, validated
  context, or review findings into target architecture artifacts.
- Next skill after design approval: recommend exactly one primary next step:
  `architecture-plan` when implementation sequencing is requested, or stop when
  the user only asked for design.
- Next skill after plan implementation: run `architecture-review` with comparable
  scope to verify actual code matches the design.
- If design questions expose unclear requirements, pause design and get the
  missing requirement clarified before continuing.

## Task list discipline

Maintain a visible task list for the design flow. Track at least:

1. Requirements and scope confirmed.
2. Existing docs/code drift checked when code exists.
3. Domain and volatility map approved.
4. Module map and integration contracts approved.
5. Design artifacts written.
6. Test specifications and fitness checks written.
7. Self-review complete.
8. Next skill recommendation made.

Keep task names outcome-based. Do not expose runtime-specific mechanics in the
instructions or report.

## Inputs

Accept, in order:

1. A requirements/design brief path supplied by the user.
2. Existing repository docs/ADRs/product notes plus explicit user confirmation
   that they are sufficient.
3. A short user brief captured through questions.

Do not design from a blank prompt. If requirements are missing or ambiguous, ask
one high-impact question at a time. Prefer bounded choices. Ask only questions
whose answers change module boundaries, coupling strength, volatility,
ownership, deployment, data ownership, or fitness checks.

## Procedure

1. **Route correctly.** Decide whether this is greenfield design, target-state
   redesign, or review-driven remediation design. If the request is really an
   audit, switch to `architecture-review`. If the request is really sequencing
   an already-approved design, switch to `architecture-plan`. Findings alone are
   not an implementation plan; turn them into target design decisions first.

2. **Read intent and reality before designing.** Read requirements, README,
   docs, ADRs, manifests, ownership files, deploy/config files, and any prior
   architecture or modularity reports. When code exists, sample enough code and
   tests to compare intended design with observed implementation. Treat existing
   design docs as intent, not truth. Record drift risks explicitly; do not let
   stale docs become design evidence.

3. **Build and validate the working model.** Present a concise working model
   before proposing boundaries:
   - functional areas and business capabilities;
   - candidate modules/services and responsibilities;
   - known constraints: teams, deployments, data, latency, compliance, runtime;
   - domain classification: core, supporting, generic, with plain-language
     explanations;
   - volatility and likely change vectors;
   - assumptions and drift risks from docs vs code.

   Ask for confirmation or correction. Do not continue to module design until
   the model is approved or the unresolved gaps are recorded as design risks.

4. **Design the module map.** Define modules around cohesive knowledge and
   change vectors. For each module, state:
   - responsibility;
   - owned knowledge: domain concepts, rules, data, policies, infrastructure;
   - subdomain classification and volatility;
   - public interface and private internals;
   - ownership/deployment expectations;
   - changes expected to stay local;
   - deterministic-tool labels to confirm when archfit or similar gates will use
     them (`subdomain`, `volatility`, public/private boundary, deploy unit).

5. **Design integrations with Balanced Coupling.** For every important
   integration, evaluate integration strength, distance, and volatility. Use the
   balance rule from `methodology-balanced-coupling`. Prefer high cohesion for
   high-strength relationships and explicit contracts for high-distance
   relationships. Do not recommend generic decoupling; choose the cheapest
   balancing move: lower strength, lower distance, or accept low-volatility
   coupling.

6. **Define contracts and tests.** For each boundary, specify the contract:
   API, events, schema, message, file format, function interface, or published
   language. Add module-level test specifications:
   - behavior tests for user-visible capability;
   - unit tests for internal rules;
   - contract tests for integration boundaries;
   - boundary tests for invalid inputs and encapsulation;
   - architecture-fitness checks that keep intended boundaries from drifting.

7. **Write design artifacts.** Use `../../resources/templates/design.md` as the skeleton
   unless the repo already has a stronger architecture-doc convention. Write
   artifacts only after the user approves the destination. Produce, at minimum:
   - architecture overview;
   - module design sections;
   - integration contract sections;
   - module test specifications;
   - architecture-fitness checks;
   - risks, trade-offs, and open questions.

8. **Self-review the design.** Before declaring done, review the proposed design
   for critical or significant coupling imbalances, missing contracts, vague
   ownership, untestable boundaries, and drift-prone intent. If critical or
   significant issues exist, revise the design before handing off.

9. **Recommend the next primary skill.** End with one clear next step:
   - `architecture-plan` when the design is approved and implementation needs
     sequencing;
   - no next skill when the user only asked for design;
   - requirements clarification when unresolved choices would change the
     architecture;
   - `architecture-review` only after implementation lands and must be checked
     against the design.

## Output

Return or write design artifacts shaped like `../../resources/templates/design.md` with:

- `source_inputs`: requirements, docs, reports, and code/doc drift notes used.
- `domain_map`: core/supporting/generic areas and volatility, plus labels that
  deterministic tools should not consume until human-approved.
- `module_map`: modules, responsibilities, owned knowledge, public interfaces,
  private internals, ownership/deployment expectations, change vectors.
- `integration_contracts`: relationships, strength, distance, volatility,
  contract definition, and balancing rationale.
- `test_specifications`: behavior, unit, contract, boundary, and fitness checks.
- `self_review`: critical/significant/minor design issues and resolutions.
- `handoff`: recommended next skill and implementation notes.

## Failure handling

- Missing requirements or unreadable input: stop and ask for the requirements or
  a brief. Do not invent a product.
- Existing-code redesign with unreviewed or stale docs: recommend
  `architecture-review` first, unless the user explicitly wants greenfield
  target-state design.
- Missing approval for write destination: return the design in the conversation
  or ask for a path. Do not create files silently.
- User requests implementation: stop at design and recommend `architecture-plan`
  for sequencing, then a mutator or engineer for source changes.

## Hard rules

- No production source edits.
- No architecture from requirements you have not read or had confirmed.
- No trusting architecture docs as current implementation truth without checking
  for drift when code exists.
- No module boundary without owned knowledge and change-vector rationale.
- No integration without strength, distance, volatility, and contract rationale.
- No design completion without self-review and an explicit next-step decision.
