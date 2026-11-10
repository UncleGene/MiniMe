---
name: minime-project-adr
description: Record durable technical decisions as concise ADRs with context, decision, alternatives, and consequences. Use when a decision is hard to reverse, non-obvious, or likely to be questioned later.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-adr


Maintain the architecture and product decisions in force. Use when
implementation direction, architecture, authority policy, role boundaries,
data model strategy, provider strategy, or safety constraints change.

The decision record holds only decisions in force. When a decision that
overrides an earlier one is accepted, remove the earlier one, or the
overridden part, in the same change; git history keeps it. While the new
decision is only proposed, the earlier one stays in force.

## Procedure

1. Read every earlier decision that governs the same behavior, not only the
   one this may override, and state for each whether the new decision
   overrides it or is compatible with it. On acceptance, remove an
   overridden one, or trim a partly overridden one to what still holds; keep
   the remaining IDs stable and never reuse a removed ID. Add one line to the
   new Context ("Replaces Decision N: ..."). Stop on a conflict the new
   decision does not override.
2. Assign the next sequential ID.
3. Draft the decision with the required fields below. Context must name the
   pressure, constraint, or tradeoff that forced the decision. Consequences
   must include downsides and follow-up obligations.
4. Evaluate alternatives honestly against the stated pressure; do not
   present familiarity or convenience as technical merit.
5. Apply the project's quality guard on new or overriding decisions before
   downstream architecture, plan, or implementation work.
6. List downstream updates required. Repoint every reference to a removed
   decision ID to the decision that replaced it, or drop it, so none dangles.

## Required fields

- Status: proposed | accepted
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
  overriding, or correcting it — do not reverse-engineer a justification.
- The decision record is a workflow doc: write it for agent consumption
  (see `minime-doc-sync` rules).
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
