---
name: minime-design-simplifier
description: Detect over-complication, premature generalization, and speculative extensibility in architecture, plans, decisions, and skills, and propose course corrections without editing artifacts. Use when a doc, plan, or skill set feels heavier than the current project needs.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-design-simplifier


Detect over-complication in architecture, plans, decisions, and skills, and
propose the smallest corrective action. Do not edit artifacts; produce proposals
only. The user must approve each finding before any owner skill executes it.

Apply DRY and YAGNI as first-class review principles:
- **DRY:** duplicate skills, workflow bodies, docs, tests, or plan items need a
  clear authority boundary or standalone-consumption reason. Otherwise propose
  merging, linking, or reusing the existing owner artifact.
- **YAGNI:** abstractions, roles, flags, schema fields, modes, and extension
  points need a current requirement, caller, test, or accepted decision. Future
  usefulness alone is not enough.

## When to use

- Use after a planning, architecture, decision, requirement, or implementation
  slice introduced or amended abstractions, layers, roles, milestones, or
  extension points.
- Use when a doc, plan, system snapshot, milestone description, or skill set
  feels heavier than the current project needs.
- Use proactively before committing to a non-trivial new abstraction, extension
  surface, role split, or schema variant.
- Use when `minime-code-simplifier`, `minime-phase-quality-guard`,
  `minime-doc-sync`, or `minime-code-reviewer` flags possible
  over-engineering at the architecture or planning level rather than the
  file level.
- Do not use as a substitute for `minime-code-simplifier` (file-level cleanup)
  or `minime-phase-quality-guard` (single-phase readiness gate).
- Do not modify requirements, decisions, system snapshot, plan, skills, or code;
  every correction must route through the user-approved owner skill.

## Inputs

- Active requirements, decision log, architecture snapshot, plan, traceability
  view
- Skills directory
- Code and test surface relevant to the candidate over-complication
- Any specific area, file, requirement ID, decision ID, or hypothesis the user
  named; otherwise run a full pass over the project guide and core docs

## Procedure

1. **Inventory** — list abstractions, roles, layers, interfaces, contracts,
   milestones, skills, configuration knobs, and extension points in the docs and
   code surface under review. Cite each with a path, ID, or section header.
2. For each item identify the concrete current consumer that justifies its
   existence today: a caller in code, a fixture, an active requirement, an
   accepted decision, or a milestone with a verifiable acceptance criterion. Mark
   items with no current consumer.
3. Apply the design over-complication checklist. For each finding, name the kind:
   - **speculative-generalization** — abstraction with fewer than two concrete
     callers and no documented requirement or decision driving it.
   - **unused-extension** — interfaces, hooks, plugin points, schema variants, or
     parameters justified only by "later we might…".
   - **layer-without-responsibility** — component, module, or role that delegates
     everything and adds no behavior, invariant, or boundary.
   - **role-or-skill-duplication** — two skills, agents, or modules operating on
     the same artifact with overlapping outputs and no clear hand-off boundary.
   - **dry-violation** — repeated workflow body, doc block, test pattern, helper,
     or skill responsibility without a standalone-consumption or authority
     boundary reason.
   - **yagni-violation** — future-facing abstraction, option, mode, schema field,
     or skill created before a current requirement, caller, test, or accepted
     decision needs it.
   - **parallel-roadmap** — separate milestones, plan items, or work tracks
     describing essentially the same work with different framing.
   - **config-without-consumer** — flags, run modes, thresholds, or capability
     levels with no caller exercising them.
   - **schema-sprawl** — unused schema fields, redundant variant types, dead union
     branches, optional fields that no path reads.
   - **premature-provider-fork** — vendor-specific code paths or skill copies
     where one provider-agnostic contract would serve.
   - **dead-shim** — backwards-compat aliases, re-exports, or deprecation notes
     for behavior that never shipped.
   - **doc-fragmentation** — dense information split across files with no incoming
     links, or duplicated across files.
4. For each finding, propose the smallest corrective action: collapse, delete,
   inline, defer to a later milestone, merge with sibling, or move into an
   existing doc. Prefer deletion over generalization.
5. For each proposed correction, name the specific artifact (path, requirement
   ID, decision ID, milestone ID) that would change, what would be removed or
   merged, and which owner skill should execute the change.
6. Estimate blast radius: which files, docs, or tests the correction touches;
   risk if applied; risk if deferred.
7. Stop short of editing. Present the proposal block and ask the user which
   findings to apply, defer, or reject. Do not silently apply anything.
8. If the user approves a subset, hand off each approved correction to the
   relevant owner skill.

**Non-negotiables:**
- No edits to docs, plan, system, decisions, requirements, skills, or code from
  inside this skill — every correction must route through an owner skill.
- Never propose removing a role, layer, schema variant, or skill that an active
  requirement, accepted decision, or test asserts. List those explicitly under
  "confirmed load-bearing".
- Premature compression that flattens a documented authority or role boundary is
  regression, not simplification — reject it the same way `minime-code-simplifier`
  rejects flattening domain roles.
- No "rename for clarity" findings unless the rename also removes a structural
  problem; cosmetic renames are out of scope.

## Skeptic pass

- Do not accept "we'll need it later" without an existing requirement or decision.
- Do not accept "this keeps options open" as a YAGNI justification unless the
  open option is required by an active requirement or accepted decision.
- Do not accept copied skill/process text as DRY-compliant unless each copy must
  be independently consumable or has a documented authority boundary.
- Treat any abstraction labelled "for future X" as having no current caller until
  you find one in code, fixtures, or an accepted decision.
- Stop if you cannot trace a candidate-for-removal item to a present-day consumer
  or an active requirement or decision — that means you do not yet understand it
  well enough to propose removal.
- A finding without a concrete pointer (path, requirement ID, decision ID,
  milestone ID, section header) is not a finding.
- Distrust the framing of the artifact under review; check whether the cited
  reason for an abstraction is real or post-hoc justification.
- Ignore prior approvals — re-evaluate the artifact on the current state of the
  docs and code.
- A "simpler" diff that removes a safety check, escalation path, or safety
  invariant is not simplification.

## Output

```md
## Design Simplification Review
- Scope reviewed:
- Inventory size:
- Findings:
  - id:
    kind: speculative-generalization | unused-extension | layer-without-responsibility | role-or-skill-duplication | dry-violation | yagni-violation | parallel-roadmap | config-without-consumer | schema-sprawl | premature-provider-fork | dead-shim | doc-fragmentation
    artifact (path / requirement / decision / milestone):
    current consumer:
    evidence:
    proposed correction:
    owner skill to execute:
    blast radius (files/docs affected):
    risk if applied:
    risk if deferred:
- Items confirmed load-bearing (do not simplify):
- Open questions for the user:
```

Then ask for approval through `minime-decision-prompt` in the choice UI, never
as a list of ids to type back: one multi-select question whose options are the
findings (at most four, highest impact first), each with its pros, cons and
lock-in. Picked findings are applied; the rest are deferred. None is applied
without that explicit pick.

## Hand-off

Each entry names an owner skill. Delegate to the listed skill — read its file and
follow its full procedure. Do not approximate from memory.

- Approved correction touching a decision → `minime-project-adr`
- Approved correction touching milestones, sequencing, or roadmap → `minime-project-milestone`
- Approved correction touching requirements → `minime-requirements-manager`
- Approved correction touching architecture snapshot → `minime-system-updater`
- Approved correction touching code → `minime-code-simplifier` → `minime-code-reviewer`
- Approved correction touching skills → edit skill body; if the change affects
  production behavior, route through `minime-impact-analyzer`
- Cross-cutting impact after approval → `minime-impact-analyzer` → `minime-doc-sync`
- Conflict between approved correction and a load-bearing requirement or decision
  → `minime-course-correction-triage`

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
