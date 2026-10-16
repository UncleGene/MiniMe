---
name: minime-verification-gate
description: Gate that enforces evidence before completion claims. Before claiming a task is done, tests pass, or a phase is complete — identify the verification command, run it, read the full output, and only then make the claim. Use before any commit, phase transition, or success claim.
metadata:
  minime_kind: target-reusable
  model_tier: fast
  model_tier_strictness: preferred
---

# minime-verification-gate


Enforce evidence before completion claims. Claiming work is done without
verification is not efficiency — it is a false claim.

**Core principle: evidence before assertions, always.**

## When to use

- Before claiming tests pass, a bug is fixed, or requirements are met.
- Before committing, opening a PR, or marking a task complete.
- Before moving to the next implementation phase.
- Before delegating to another agent and reporting success.
- Whenever you are about to use "should", "probably", or "seems to".

## The gate

```
Before any completion claim:

1. IDENTIFY   What command proves this claim?
2. RUN        Execute the full command — fresh, complete, this message.
              Before commit, default to full project test, lint, and type-check
              gates unless the user or project guide explicitly defers them.
              If any full project gate fails, including a pre-existing unrelated
              failure, the repo is not commit-ready.
3. READ       Full output. Check exit code. Count failures.
4. VERIFY     Does the output confirm the claim?
              If NO: state actual status with evidence.
              If YES: state the claim WITH the evidence.
5. CLAIM ONLY after step 4 confirms.

Skipping any step = false claim, not verification.
```

## Common failure patterns

| Claim | Requires | Not sufficient |
|---|---|---|
| Tests pass | Test runner output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Commit ready | Full project test/lint/type-check gates pass, unless explicitly deferred | Changed-file tests or changed-file lint only |
| Full project gate fails | State not commit-ready and fix or escalate the broken repo state | Treating pre-existing unrelated failures as ignorable |
| Lint finding resolved | Underlying issue fixed, or approved suppression with reason, scope, and removal condition | Disabling the rule to make the check pass |
| Bug fixed | Original symptom tested and passing | Code changed, assumed fixed |
| Regression test works | Red-green cycle: revert fix → confirm test fails | Test passes once |
| Requirements met | Line-by-line checklist verified | Tests passing |
| Agent completed | VCS diff inspected | Agent reports success |
| Phase complete | Each acceptance criterion checked | Artifacts look right |

## Regression test red-green cycle

Writing a regression test is not enough. Verify the cycle explicitly:

```
Write test → Run (pass) → Revert fix → Run (must fail) → Restore → Run (pass)
```

Skipping the revert-and-fail step means the test may not actually catch the bug.

## Red flags — stop before claiming

- Using "should", "probably", "seems to", "looks correct"
- Expressing satisfaction before verification ("Done!", "All good!", "Fixed!",
  "Great!", "Perfect!", "This should work now")
- About to commit or move on without running the command
- Committing in the same shell command as the checks (`tests; lint && git
  commit`): the commit runs whatever the tests print. Read the results first,
  then commit as a separate step
- Trusting a prior run from an earlier turn
- Partial check on a subset of the affected surface
- Treating changed-file tests, changed-file lint, or a narrow smoke check as
  sufficient for commit readiness when the user or project guide did not
  explicitly defer the full project gate
- Treating touched-file checks as anything more than supporting diagnostic
  evidence after a full-project gate fails
- Attempts to disable lint rules, type checks, tests, or quality gates instead
  of fixing the finding. Fix the underlying issue first unless the user
  explicitly approved the suppression or an accepted project decision already
  requires it

## Rationalization to reject

| Excuse | Answer |
|---|---|
| "Should work now" | Run the verification |
| "I'm confident" | Confidence is not evidence |
| "Partial check is enough" | Partial proves nothing |
| "The full gate fails only on pre-existing unrelated issues" | The repo is not commit-ready |
| "Pre-existing issue, unrelated to my changes — not something to fix in this slice" | If it's in the diff's touched or reachable code, fix it now or stop and surface it for a scoping decision — do not pass over it |
| "Different phrasing so the rule doesn't apply" | Spirit over letter |

## Output

State the claim and the evidence together:

```
Claim: all tests pass
Evidence: `python -m unittest discover -s tests` → Ran <N> tests, OK
```

If verification fails, state the actual status and what needs fixing before
the claim can be made.

Before pausing, handing off, or reporting a blocked state, include branch, HEAD
short SHA, whether the working tree has uncommitted changes, the changed file
paths, and the next concrete action.

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
