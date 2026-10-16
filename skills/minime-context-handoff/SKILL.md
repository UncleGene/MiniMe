---
name: minime-context-handoff
description: Produce a minimal verifiable handoff envelope when work crosses an agent or session boundary, and verify an upstream artifact answers the questions the downstream skill needs. Use at phase boundaries and whenever a different agent picks up another agent's output.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-context-handoff


Handle agent and session boundary transitions. Two modes: produce a handoff
envelope (write mode) and verify an upstream-to-downstream contract (verify
mode).

## Write mode — produce a handoff envelope

Use when work crosses an agent boundary, a session reset, or when the next
step will be picked up by a different agent.

### Inputs
- Current branch or revision
- Active document set (paths only)
- Last completed step
- Next intended step
- Blocking open questions

### Procedure
1. Capture branch, base revision, and any uncommitted file paths.
2. List active source artifacts the next agent must read by path and ID —
   pointers only, no excerpts.
3. Pin requirement, decision, architecture, and plan IDs in scope. No text
   excerpts; the next agent reads them fresh.
4. State the next intended step as a one-line directive plus the skill that
   should pick it up.
5. List blocking open questions so the next agent does not invent answers.

### Output
- Branch or revision
- Uncommitted files
- Active docs (paths)
- IDs in scope (requirements, decisions, architecture, plan)
- Last completed step
- Next intended step
- Skill to invoke next
- Blocking open questions

### Skeptic pass
- Do not include narrative recaps; pointers only.
- Do not include what was done beyond the IDs touched — the diff and commit
  messages are the record.
- Stop if branch, revision, or required IDs cannot be confirmed against the
  live repo.
- Do not fabricate IDs to make the envelope feel complete; fewer verified
  pointers beats invented ones.

## Verify mode — verify a handoff contract

Use at phase boundaries to confirm the upstream artifact answers what the
downstream skill needs.

### Required questions per transition
- Vision to spec: named pain, named user, in-scope value, real non-goals.
- Spec to milestone: inputs with constraints, outputs with meaning, error
  cases, non-goals, closed open questions.
- Milestone to implementation: shippable slice, verifiable done, no
  unresolved spec gaps, no premature abstraction.
- Decision to spec or implementation: pressure named, alternatives
  evaluated, consequences including downsides.

### Output
- Verdict: pass | fix | route
- Missing: question — where to add — owner skill
- Next: skill to invoke

### Rules
- Do not fill the gap yourself; route to the owning skill.
- If multiple defensible fills exist, escalate to a human checkpoint.
- Cite the document section a missing answer should land in.

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
