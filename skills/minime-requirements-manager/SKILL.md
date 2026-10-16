---
name: minime-requirements-manager
description: Add, modify, split, or clarify functional requirements and scenarios. Use to define what a system must do in enough detail for implementation and validation.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-requirements-manager


Define and maintain functional requirements. Do not delete requirements; do
not bury functional behavior in references — link to them instead.

## Procedure

1. Assign a new sequential ID, or identify the existing ID to modify.
2. Name the user pain or value before describing solution features.
3. Define audience and scope narrowly enough to reject out-of-scope users,
   contexts, or workflows.
4. Include happy paths, error paths, edge cases, and escalation paths that
   affect implementation.
5. Constrain inputs and outputs by meaning, validity, bounds, and
   guarantees — not only by type or shape.
6. Resolve implementation-blocking open questions before marking the
   requirement active.
7. Apply the project's quality guard for substantial new or changed
   requirements before implementation planning.

## Skeptic pass

- Do not trust paraphrased requirements; check against the original source
  if it still exists.
- Treat status fields as possibly stale; re-evaluate against current
  implementation.
- Stop if an acceptance criterion is unverifiable or circular.

## Output

- ID and title
- Status: active | evolving | planned | deprecated
- Type: core | AI | data-integrity | safety | compliance | UI | export | performance | reference
- Priority: high | medium | low
- Description
- Functional behavior
- Scenarios (given/when/then format)
- Edge cases
- Acceptance criteria
- Links to decisions, architecture sections, and plan milestones

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
