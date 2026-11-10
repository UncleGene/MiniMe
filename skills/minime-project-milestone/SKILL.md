---
name: minime-project-milestone
description: Break work into shippable milestones tied to requirements and acceptance criteria. Use when sequencing work into deliverable slices or maintaining a project plan.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-milestone


Sequence work into deliverable slices. Use when requirements, decisions, or
code changes affect milestone state, done criteria, release gates, or next
steps. Do not add new milestones unless a requirement or decision justifies
them.

## Procedure

1. Identify which milestones, next tasks, or release gates are affected.
2. Keep completed work only where continuing work depends on it (a baseline,
   contract or known limit), stated as a current fact; label unfinished work
   partial, in progress, or needs refactor.
3. Realign future work. Remove achieved milestones and past items that
   continuing work does not need; git history keeps them.
4. Ensure every milestone has verifiable done criteria framed around user,
   operator, safety, or project value — not only code layers.
5. Schedule risky unknowns and irreversible choices early enough that later
   milestones do not depend on guesses.
6. Apply the project's quality guard for new or materially changed
   milestones.
7. Return the output.

## Milestone rules

- Each milestone should be shippable and reviewable.
- Map milestones back to explicit spec sections.
- Prefer the smallest cohesive user-value slice that closes a meaningful
  gap.
- Prefer a tracer-bullet route: ship the thinnest end-to-end slice that
  delivers user-visible value before building comprehensive infrastructure.
- Keep later milestones dependent on earlier contracts, not the other way
  around.
- Schedule risky unknowns early enough to affect the plan.
- Make the definition of done verifiable with tests, docs, or operational
  checks.
- Keep MVP slices independently useful; do not require every milestone
  before anything can ship.
- Mark stretch goals as optional and non-load-bearing.
- Include tests and docs updates in the definition of done.
- Link to a checklist that already lives in another doc; do not restate it.
- Leave out facts that go stale with the next commit (baseline SHAs, test
  or assertion counts) and session provenance ("the user selected ...").
- Reflect status changes in the plan and relevant specs.
- The plan is a workflow doc: write it for an agent resuming the work
  (see `minime-doc-sync` rules).
- Use a handoff contract when consuming a spec to confirm it answers what
  the milestone needs.

## Skeptic pass

- Do not trust milestone done markers without verifiable evidence (tests,
  code state, observable behavior).
- Stop if a milestone's done criteria is unverifiable or circular.

## Output

- Triggered by (requirement, decision, or change IDs)
- Milestones affected
- Changes made
- Milestones preserved unchanged
- Quality guard review result
- Next credible steps

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
