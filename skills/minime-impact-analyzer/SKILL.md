---
name: minime-impact-analyzer
description: Trace the impact of requirement, decision, system, plan, and code changes across documentation layers. Use after non-trivial changes to determine what else must change so docs and implementation remain coherent.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-impact-analyzer


Trace how a change affects documents, plans, code, tests, and decisions.
Identify what must be updated and what is unaffected.

Use after a non-trivial change to determine what else must change so docs
and implementation remain coherent. Do not skip for changes labelled minor
or wording-only; classify the change type first.

## Procedure

1. Identify the changed artifact and its IDs.
2. Classify the change: wording | behavioral | structural | safety |
   architecture | sequencing | reference | implementation.
3. Trace upstream and downstream across the project's documentation layers:
   requirements, decisions, architecture snapshot, plan, tests, code,
   references, user-facing documentation (README, CLI reference, report
   definitions). Verify every linked ID resolves in source before listing
   it as impacted; do not rely on memory or prior turns.
4. List required edits per impacted area and explicitly name no-change
   areas.
5. Determine if the project's quality guard is needed before downstream
   implementation.
6. Flag scope growth, post-hoc decisions, architecture boundary changes,
   plan dependency inversions, non-atomic diffs, and missing behavior
   tests.
7. Return the output.

## Skeptic pass

- Do not trust prior impact analyses; recompute from current document
  state.
- Treat no impact as requiring positive evidence — confirm each no-change
  area explicitly.
- Stop if a linked requirement or decision ID cannot be located in the
  active source.

## Output

- Changed item
- Change type
- Impacted requirements and decisions
- Impacted architecture sections
- Impacted plan items
- Impacted user-facing docs (README, CLI reference, report definitions)
- Impacted reference docs
- Impacted code and tests
- Required updates
- No-change areas
- Quality guard review needed
- Risk level
- Next action

## Rules

- Cite `path:line` for each impacted area.
- Flag dormant doc drift when a document may no longer match the code.
- When two downstream paths are defensible, escalate to a human
  checkpoint rather than picking.

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
