---
name: minime-system-updater
description: Update the current architecture or system snapshot when a durable component responsibility, data flow, or invariant changes. Keep the snapshot accurate without adding history.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-system-updater


Update the architecture or system snapshot after an accepted decision,
requirement change, or implementation change alters component
responsibilities, data flows, or invariants.

## When to use

- Use after a durable architecture or component responsibility change.
- Use after a public CLI surface change (new command, removed command,
  changed flags) to update README.md and any CLI reference docs.
- Use after a skill catalog change (new skills added or removed) to
  update user-facing documentation that lists or describes skills.
- Do not add abstractions, layers, or interfaces not justified by an
  active requirement, accepted decision, or concrete caller.

## Procedure

1. Identify which sections of the architecture snapshot or user-facing
   documentation (README, CLI reference) are affected.
2. Update only affected sections; preserve accurate unchanged content
   verbatim.
3. Describe interfaces from caller needs and guarantees, not from private
   implementation shape.
4. Remove purely ornamental layers (no behavior, no responsibility, no
   invariant).
5. Apply the project's quality guard for updates that introduce new
   abstractions, layers, interfaces, or cross-component boundaries.
6. Return the output.

## Rules

- Current truth only; no historical narrative.
- Use component responsibilities, data flow, and invariants.
- Link to relevant requirements and decisions.
- Keep alternative approaches in decisions, not in the system snapshot.
- Add abstractions, layers, and interfaces only when a concrete current
  use case needs them.
- Describe interfaces from the caller's need and invariant, not from the
  current implementation shape.
- Reject layers with no behavior of their own.
- Verify named identifiers and paths against source before writing them
  into the snapshot.
- When two architectures are defensible after a change, escalate to a
  human checkpoint before updating.

## Skeptic pass

- Do not trust the snapshot's current claims; diff them against accepted
  requirements and decisions before editing.
- Reject cosmetic edits that don't reflect a real architectural fact.
- Stop if a component's listed responsibility cannot be traced to an
  active requirement or accepted decision.

## Output

- Triggered by (requirement or decision IDs)
- Sections changed
- Sections unchanged
- Quality guard review result
- Links added

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
