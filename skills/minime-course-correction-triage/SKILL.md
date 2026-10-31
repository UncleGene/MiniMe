---
name: minime-course-correction-triage
description: Intake gate for feature requests and course corrections. Evaluate the request in full project context before any implementation — check it against accepted assumptions, trace its impact, challenge its value, and verify its premise — then classify and route it. Use when the user asks to add a feature, change behavior, or gives a correction, concern, or new direction.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-course-correction-triage


Evaluate an incoming feature request or course correction before
implementation, then route it to the right documentation or code path. This is
the intake gate that stops requests being taken at face value: do not jump to
code even when the target file looks obvious. A request that looks like a
one-line fix still passes intake, scaled to its risk tier — the point is to
catch the request that quietly breaks an assumption, ripples wider than it
appears, or adds little value, before any code is written.

## Risk tier (pick first)

Pick the tier from what the change touches, not from its size. When in doubt,
pick the higher tier.

- **Low:** reversible and local; contradicts no accepted requirement, decision
  or invariant, and changes no requirement, decision, acceptance, safety,
  security, data-format or public-interface text or behavior. State one line,
  `Intake: low — contradicts nothing accepted; <why>; improvement:
  <classification>`, and proceed; skip the category list and the output below.
- **Standard:** neither low nor high. State each intake check below in a
  sentence, then route to the owning skill.
- **High:** changes a requirement, decision, safety or security rule, data
  format or public interface, or is hard to reverse. Run the full procedure and
  output, and hand off to `minime-impact-analyzer`.

Commit gate tiers (light or full) are chosen separately and are unchanged.

## Intake checks (standard and high tiers)

1. **Assumption check** — does the request contradict an accepted requirement,
   decision, or key invariant? If yes, flag the conflict and resolve it in docs
   before any code path.
2. **Impact check** — name the blast radius across requirements, decisions,
   architecture, plan, docs, and tests. When it reaches beyond the touched
   files, hand off to `minime-impact-analyzer`.
3. **Value check** — state what value the change adds and confirm implementation
   is the smallest delivery. Challenge the request when the value is unclear, or
   when a doc/decision change or no-op would serve. "The user asked for it" is
   not a value justification on its own.
4. **Premise check** — can the request work as stated, and what does it
   assume? Name the load-bearing assumption (data that must be observable,
   context another agent would lack, a cause the user has inferred) and verify
   it from evidence when a search, a file read or a log lookup can. If it fails
   or cannot be checked, say so with the evidence before any design question.

## Classify the correction as

- Functional requirement
- Scenario or edge case
- Architecture decision
- System snapshot update
- Plan update
- Reference update
- Code task
- Validation requirement
- Phase quality or slop risk
- Dormant doc drift
- Improvement opportunity

## Rules

- Propose the minimal safe edit path. Do not expand scope.
- Preserve current valid work where possible.
- Route to the appropriate document or code area based on classification.
- Examine every user input and user-identified problem for improvement
  opportunity. Classify the opportunity as:
  - **local-project improvement** — should change the current project's docs,
    requirements, plan, implementation, tests, or project guide.
  - **reusable-skill improvement** — should change or create a reusable skill
    because the issue can recur across projects.
  - **both** — local fix now plus reusable skill improvement.
  - **no action** — no durable improvement justified; record why.
- When the concern names vagueness, scope creep, post-hoc rationale,
  unverifiable done criteria, premature abstraction, or weak review,
  route to the project's quality guard first.
- In a target project, do not write MiniMe-specific references into the target
  repo. Surface reusable-skill improvements as host/user-level MiniMe work or
  handoff notes. Describe the target project generically there: no project
  names, local paths, or commit references.
- When the concern points at a document that may no longer match the code,
  route to a consistency check before making code changes.
- When the destination is genuinely ambiguous between two defensible
  routes, escalate to a human checkpoint rather than picking.
- If a quality gap is detected, block downstream edits until the quality
  guard clears it.
- If implementation-blocking ambiguity exists, keep it out of code scope
  until resolved in docs.

## Skeptic pass

- Do not trust the user's own classification; re-classify from the
  artifact content.
- Stop and flag if the correction contradicts an accepted decision without
  a clear supersession path.

## Output

- Intake verdict: assumption check (clear | conflicts with <artifact>), impact
  check (touched files only | wider — names areas), value check (justified | weak
  — recommend doc/decision/no-op instead), premise check (holds | fails —
  <evidence> | unverified — <what would check it>)
- Classification (one or more categories from above)
- Improvement opportunity: local-project improvement | reusable-skill improvement | both | no action, with rationale
- Primary targets (docs or files)
- Secondary impacted areas
- Skill chain
- Safe immediate edits
- Risks if ignored
- Clarifying question (only if needed to resolve ambiguity)

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
