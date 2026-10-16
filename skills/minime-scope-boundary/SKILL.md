---
name: minime-scope-boundary
description: Quick check that a proposed plan or diff stays inside the slice the user asked for. Flags opportunistic additions, refactors, and unrequested file churn. Use before commit, before opening a PR, and whenever a plan grows unprompted.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-scope-boundary


Verify that proposed changes stay within the user's requested scope.
Surface out-of-scope items for user decision; do not delete them silently.

## Out-of-scope triggers

- Touches files unrelated to the named change.
- Adds abstraction not required by the current slice.
- DRY: adds duplicate workflow, docs, tests, helper paths, or skills instead of
  reusing the existing owner artifact.
- YAGNI: adds a flag, mode, schema field, extension point, or generic framework
  without a current requirement, caller, test, or accepted decision.
- Bundles formatting or rename churn into a behavior change.
- Resolves a separate task the user did not name.
- Crosses a frozen stack or architectural boundary.

## Output

- Verdict: in-scope | out-of-scope | mixed
- Out-of-scope items: change, reason, route (path:line for each)
- Next action

## Rules

- Do not delete out-of-scope work silently. Surface it so the user can
  split, defer, or accept.
- Cite `path:line` for each flagged change.

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
