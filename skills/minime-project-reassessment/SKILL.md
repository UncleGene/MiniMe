---
name: minime-project-reassessment
description: Take a fresh whole-project look at an inherited or drifted project, judge whether goals are clear and viable, docs, design, code and tests are adequate, and produce a prioritized repair plan. Use when inheriting a project, after roadmap churn or drift, or when a stronger model should re-examine the project.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-reassessment

Assess a project as an engineer inheriting it from earlier teams. Answer six
questions with evidence, then propose a repair sequence. Do not repair anything
inside this skill; repairs route through owner skills after the user approves.

## When to use

- Inheriting a project, or returning after long inactivity.
- Roadmap changes left docs, design, or tests describing several directions.
- A more capable model is available and the project deserves a re-examination.
- Do not use for current-state briefing (`minime-project-orient`), a pre-phase
  plan check (`minime-plan-review`), or a single feature or correction
  (`minime-course-correction-triage`).

## Inputs

- The user's goals for the project, taken from the invocation. If none are
  given, ask for them before step 1. This is a plain question with no options.
- Project guide, requirements, decisions, architecture, active plan, README.
- Code and test tree; git history for roadmap changes.
- Baseline gate results: run the project's tests, lint, and type checks first.
  Record failures as findings; never fix them during the assessment.

## Procedure

Answer each question with cited evidence (`path:line`, requirement or decision
ID, command output). Mark each answer: adequate, gap, or unknown.

1. **Goal clarity.** State the goal in two sentences from the docs alone. Where
   docs give conflicting goals, scopes, or users, list each source; do not
   pick one. Conflicting direction becomes a user decision, not a silent choice.
   Compare the docs' goal with the user's goals in a table with these columns:
   aspect, docs, user, relation. Raise each mismatch as its own decision.
   Answer steps 2–6 against the user's goals, not the docs' goal.
2. **Goal viability.** Check the goal against technical feasibility, external
   dependencies the project cannot control, and evidence the goal is being met.
   Passing checks that prove only registration, formatting, or presence do not
   prove the outcome. Name what would demonstrate the outcome.
3. **Documentation.** Delegate to `minime-doc-sync` with `all` scope in
   report-only mode. Add: does an agent reading only active docs get one current direction,
   or must it filter superseded roadmap history? Propose archiving history that
   active docs still carry rather than deleting it.
4. **Design fit.** Delegate to `minime-design-simplifier` for YAGNI/KISS. Add:
   does each major component serve the goal from step 1? A component serving a
   superseded goal is a finding even if it is simple.
5. **Code matches design.** Delegate to `minime-doc-sync` with `document` scope
   for the architecture and requirements docs. Reproduce suspected behavior gaps by
   running the code; mark unreproduced suspicions as unknown.
6. **Test adequacy.** Sample the suite against the requirements:
   - Insufficient: a high-priority requirement or safety invariant with no
     behavior test; a reproduced defect no test catches.
   - Implementation-coupled: assertions on prose wording, private helpers,
     internal call order, or exact structure that a correct refactor breaks.
   - Excessive: several tests asserting the same behavior, or tests for retired
     behavior. Propose replacing them with the requirement-level test.
   Cite test names; count only what you inspected.

Then:

7. Rate each finding high, medium, or low by its effect on the goal.
8. Group fixes into ordered repair milestones. The first milestone restores a
   single authoritative, executable baseline (current docs, passing gates);
   later ones follow by risk. Each milestone names its owner skills and an
   executable acceptance check.
9. Raise each conflicting direction or scope choice through
   `minime-decision-prompt`, one question per turn, highest blocking first.
   Record accepted choices via `minime-project-adr`.

## Gotchas

- Inherited docs are claims, not authority. Verify before citing.
- A docs-only goal can be internally consistent and still not be what the user
  wants. One assessment judged only against the docs missed every one of the
  user's goals.
- Do not bundle repairs into the assessment; a reviewed plan comes first.
- Instruction-text or snapshot assertions passing is not evidence of outcomes.
- Skill-size or similarity heuristics alone do not justify merging or deleting.
- Archive superseded plans with a successor link instead of rewriting history.

## Output

Write the assessment where the user chooses (default
`docs/project-reassessment.md`) with this shape:

```md
# Project reassessment
Date / baseline commit / status
## Conclusion            (3-5 sentences: viable? biggest risk?)
## Decisions needed      (open user choices; accepted ones recorded as ADRs)
## Answers               (the six questions: adequate | gap | unknown + evidence)
## Evidence and limits   (gates run with results; what was not inspected)
## Findings              (F01.. title, severity, evidence, owner skill)
## Repair sequence       (IDs unused by the existing plan; goal, owners, acceptance)
```

## Hand-off

Delegate by reading each owner skill and following its full procedure.

- Approved milestones → `minime-project-milestone`
- Requirement changes → `minime-requirements-manager`
- Architecture changes → `minime-system-updater`
- Cross-cutting repairs → `minime-impact-analyzer`
- Assessment commit → the project's commit skill

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
