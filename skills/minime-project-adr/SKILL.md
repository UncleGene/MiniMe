---
name: minime-project-adr
description: Record durable technical decisions as concise ADRs with context, decision, alternatives, and consequences. Use when a decision is hard to reverse, non-obvious, or likely to be questioned later.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-adr


Maintain append-only architecture and product decisions. Use when
implementation direction, architecture, authority policy, role boundaries,
data model strategy, provider strategy, or safety constraints change.

Do not delete or overwrite existing decisions; always supersede.

## Procedure

1. Find any existing decision this supersedes; mark it superseded and add a
   Superseded By pointer.
2. Assign the next sequential ID.
3. Draft the decision with the required fields below. Context must name the
   pressure, constraint, or tradeoff that forced the decision. Consequences
   must include downsides and follow-up obligations.
4. Evaluate alternatives honestly against the stated pressure; do not
   present familiarity or convenience as technical merit.
5. Apply the project's quality guard on new or superseding decisions before
   downstream architecture, plan, or implementation work.
6. List downstream updates required.

## Required fields

- Status: proposed | accepted | superseded
- Date
- Context: the pressure, constraint, or tradeoff that forced the decision
- Decision: what was decided
- Consequences: downsides, migration cost, and future limits, not only benefits
- Alternatives considered: evaluate each honestly, state why each loses
- Follow-up updates required

## Rules

- Keep decisions short and specific.
- Use decisions for durable choices, not for routine implementation details.
- Reference the spec section or plan item that triggered the decision.
- Do not justify technology purely by familiarity when technical constraints
  are claimed.
- If code already exists, state whether the decision is confirming,
  superseding, or correcting it — do not reverse-engineer a justification.
- Do not rewrite history; supersede decisions when they are no longer valid.
- Treat the project's stack constraints as durable decisions unless the user
  changes them.
- When the choice has more than one defensible direction, escalate to a
  human checkpoint before drafting.

## Skeptic pass

- Do not trust an existing decision's stated alternatives or consequences
  without checking they still hold; flag staleness.
- Treat decisions written after the code as ratification, not evidence of
  correctness; identify any drift.
- Stop if the decision contradicts an active requirement without a
  documented resolution.

## Interaction rules

- End with `Recommended next action: <one concrete step>`. If that step is a
  check or gate that needs no user input, run it now instead of stopping.
- Before a feature or behavior change, check it against accepted requirements
  and decisions, name its impact, and confirm its value; route non-trivial
  cases through `minime-course-correction-triage`.
- Ask any question whose answer changes an artifact through
  `minime-decision-prompt`: one question per turn, named options with pros,
  cons and impact, in the host's choice UI when available.
- Never skip a failing test, lint, type or doc check because it pre-existed;
  fix it or escalate before committing.
- When a step names another skill, read that skill's file and follow its full
  procedure.
