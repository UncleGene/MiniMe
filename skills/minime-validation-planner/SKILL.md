---
name: minime-validation-planner
description: Design tests, release gates, and verification procedures for requirements and implementation changes. Use when a requirement, decision, pipeline, contract, or implementation needs acceptance tests and release gates.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-validation-planner


Design a test plan and release gates for a change. Do not treat existing
tests as coverage; tests must assert documented behavior, not
implementation existence.

## When to use

- When a requirement, decision, pipeline, contract, or implementation
  needs acceptance tests and release gates.
- As part of every code change to define the tests and checks that gate
  completion.

## Required validation themes

Confirm each applies and has a test case:

- Tests assert meaning and guarantees, not implementation existence.
- Input tests cover valid, invalid, boundary, and malformed values where
  relevant.
- Repeated operations are idempotent where required.
- Equivalent facts converge without duplicates where required.
- Invalid, ambiguous, or low-confidence data follows the project's
  escalation path.
- Provenance retained where required.
- AI-assisted steps are schema-constrained where applicable.
- Negative tests for documented error cases and invalid constraints.
- Strict type checks for changed typed code.
- Verification that broad catches surface actionable failures and do not
  hide data loss, auth failures, or contract violations.

## Procedure

1. For each item in scope, identify the required validation themes.
2. Design test cases covering: documented behavior, input constraints,
   output guarantees, error handling, idempotency, escalation paths,
   provenance where required.
3. Add artifact-specific checks required by the project guide or changed
   file types.
4. Define release gates: passing tests, type checks, simplification pass,
   review pass, docs updated, required artifact-specific checks.
5. Apply the project's quality guard when the validation plan depends on a
   new or changed spec, decision, architecture boundary, milestone, or
   implementation summary.
6. Return the output.

## Skeptic pass

- Do not trust existing tests as coverage; verify each test asserts
  documented behavior.
- Treat green CI as one signal, not proof of correctness.
- Stop if a required validation theme has no corresponding test case;
  surface it as a blocking gap.

## Output

- Scope (requirement, decision, or implementation being validated)
- Test cases (one per validation theme)
- Release gates (checklist of required passes)
- Quality guard review result
- Missing coverage (blocking gaps with remediation)
- Test commands to run

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
