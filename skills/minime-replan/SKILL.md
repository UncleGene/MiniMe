---
name: minime-replan
description: Apply a surgical change to an active project plan without restarting the planning workflow. Classify the requested change, update only the affected artifacts, record the new status and next step in the plan, select the next implementation slice, and surface a continuation choice. Use when the user reports "the project is focusing on the wrong aspect," "I want to add a feature," or "we discovered a problem" mid-implementation.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-replan

Apply a surgical change to an active project plan. Treat the plan as a living
artifact, not a regenerated document. Mutate only what the change affects,
preserve completed work, and emit the next concrete implementation step.

## When to use

- The user reports a mid-project pivot: "the project is focusing on the wrong
  aspect," "I want to add a feature now," "we discovered a problem that
  invalidates a planned slice."
- A change is needed to requirements, spec, decisions, milestones, validation
  plan or architecture snapshot.
- Do not use for fresh planning (no plan exists yet) or wording-only edits.

## Inputs

- The change request as the user stated it.
- The active plan, requirements, decisions, architecture snapshot and
  validation artifacts (paths from the project guide; otherwise
  `docs/requirements.md`, `docs/implementation-plan.md`, `docs/decisions*`).
- Repo status: branch, uncommitted changes, base revision.

## Procedure

Run the steps in order. Only the step 1 and step 2 short-circuits may skip
steps; step 8 always runs.

1. **Triage** with `minime-course-correction-triage`: classify the change
   (priority shift, new feature, discovered constraint, implementation problem,
   scope reduction). If it is wording-only, report a no-op and go to step 8.
2. **Impact** with `minime-impact-analyzer`: list affected artifacts with a
   reason each. If none, record the operational change in the plan and go to
   step 8.
3. **Decisions:** whenever any step finds a real fork (non-trivial product,
   architecture or scope consequence), ask through `minime-decision-prompt`.
   Generic "confirm?" prompts are forbidden. Repeat as needed.
4. **Update artifacts surgically**, one owner each; never rewrite a whole
   document:
   - requirements → `minime-requirements-manager`
   - feature spec → `minime-project-spec`
   - decisions → `minime-project-adr`
   - architecture snapshot → `minime-system-updater`
   - validation plan → `minime-validation-planner`
   - milestones, plan status, open questions and next step →
     `minime-project-milestone`
5. **Reconnect references** with `minime-doc-sync` (`diff` scope) over the
   changed artifacts; resolve or surface broken links.
6. **Select the next slice** with `minime-implementation-step-selector`. If it
   returns a choice instead of a slice, go back to step 3.
7. **Quality guard** with `minime-phase-quality-guard` on the revised plan and
   slice. A block stops the chain; record the block reason as an open question
   in the plan.
8. **Continue.** If triage was unambiguous, no fork was raised, every updater
   finished cleanly, the guard passed and a single slice was selected, state
   the next action in one line and start it, so the user can interrupt.
   Otherwise present a menu through `minime-decision-prompt`:
   - guard passed: start the slice / review it first / queue another replan /
     stop and reflect;
   - guard blocked: fix the block and re-run / continue with the block as a
     warning / abort;
   - no-op or no impact: close / force the full chain.

## Failure modes

- **User aborts mid-chain:** record in the plan which steps ran, which
  artifacts changed and which decisions are pending, then stop. Do not roll
  back applied patches.
- **No answer to a decision prompt:** halt with the open question recorded in
  the plan; do not decide for the user.

## Skeptic pass

- Re-derive the classification from the current request and artifacts, even if
  an earlier run or the user's wording suggests one.
- Flag a classification that contradicts `minime`'s default
  routing or the rows the project guide adds to it.
- Re-read each artifact before patching it.

## Output

```text
Change classified as: <classification>
Artifacts changed: <paths>
Decisions made or pending: <list>
Plan updated: <status, open questions, next step>
Next implementation step: <slice and what it unblocks>
Continuation: <one-line start decision> OR <menu>
```

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
