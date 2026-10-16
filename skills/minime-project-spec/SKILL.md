---
name: minime-project-spec
description: Write or refine feature specifications with inputs, outputs, error cases, non-goals, and open questions. Use when defining a feature or domain behavior in enough detail that it can be implemented and reviewed without guesswork.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-spec


Define a feature or domain behavior at a level that supports implementation
and review without guesswork.

## Required sections

- Summary
- Inputs (constraints, limits, validation rules, authority — not only types)
- Outputs (meaning and completeness guarantees — not only object shape)
- Error cases (invalid input, missing authority, conflicts, idempotency
  failures, dependency failures)
- Non-goals (explicit exclusions)
- Open questions
- Related decisions

## Rules

- Keep the spec concise and implementation-shaped.
- Trace it to the project overview, architecture snapshot, and relevant
  decisions.
- Define inputs by constraints, not only primitive type.
- Define outputs by meaning, not only object shape.
- Make error cases explicit.
- Close or route open questions before implementation starts.
- Prefer a tracer-bullet approach: specify the thinnest end-to-end slice
  that delivers user-visible value first, then layer completeness.
- Do not expand scope to match implementer assumptions; revise the spec
  first.
- Keep dense reference facts in reference documentation, not in the spec
  body.
- When an open question has more than one defensible answer, escalate to a
  human checkpoint.
- Verify any claim about existing behavior against source before writing it
  into the spec.

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
