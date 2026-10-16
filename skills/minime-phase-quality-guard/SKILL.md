---
name: minime-phase-quality-guard
description: Verify project artifacts against common phase-specific quality failures before implementation, acceptance, or review. Owns cross-phase checks; defers per-phase rules to the owning skill.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-phase-quality-guard


Verify project artifacts against quality failure modes before treating a
planning, documentation, implementation, commit, or review slice as ready.

Use before accepting, implementing, or reviewing a vision, spec, decision,
architecture, milestone, implementation, commit, or PR. Do not use as a
rubber stamp; every check must be reconciled against the actual artifact.

## Cross-phase checks

Apply these before any phase-specific review:

- The artifact answers the question the downstream skill needs.
- Claims about existing code are cited with `path:line`.
- Scope matches the user's request; flag expansion.
- Open questions are closed or routed before implementation starts.
- Layered abstractions, flags, or config each have a current concrete use.
- DRY: duplicated workflow, docs, tests, skills, or implementation paths have a
  load-bearing standalone-consumption or authority-boundary reason.
- YAGNI: future-facing abstractions, flags, modes, schema fields, skills, or
  extension points are backed by a current requirement, caller, test, or accepted
  decision.
- Output can be checked by tests, docs, or reviewer action.

## Per-phase checklists

Apply only the relevant phase checklist. Treat a vague artifact as not
ready; return it with the blocking gap and the smallest correction needed.
Do not invent requirements, decisions, or scope to make the artifact pass.

**Vision:** Problem named before solution. Audience specific enough to
reject some users. Scope framed by user value. Non-goals are real
rejections, not future features.

**Spec:** Happy path, error paths, edge cases, and escalation paths
covered. Inputs have constraints, not just types. Outputs state meaning
and guarantees. Open questions resolved or explicitly blocked.

**Decision:** Context names the pressure or tradeoff that forced the
decision. Alternatives honestly evaluated against that pressure.
Consequences include downsides and follow-up obligations. No familiarity
or convenience disguised as technical merit. Recorded before or alongside
implementation, or marked as ratification.

**Architecture:** Abstractions justified by concrete use cases. Future
extensibility tied to an accepted requirement or decision. Every layer or
component has real behavior or responsibility. Interfaces shaped by caller
needs. Duplicate responsibilities have explicit boundaries. Complexity
appropriate to this project.

**Milestone:** Delivers user or operational value, not only code layers.
Risky unknowns scheduled early. Done criteria verifiable. MVP can ship a
meaningful slice. Stretch goals optional and not load-bearing.

**Implementation:** Title, scope, and diff describe the same single
coherent change. New abstractions have repeated need or documented reason.
Tests assert behavior, not implementation existence. Error handling
preserves actionable information. Duplicated logic is removed, merged, or
explicitly justified.

**Review:** Addresses correctness, behavior, safety, and tests. Logic and
edge cases receive explicit attention. Approval based on evidence, not
familiarity. Feedback resolution shows understanding, not only literal
compliance.

## Skeptic pass

- Do not trust an artifact because it sounds plausible; require a concrete
  check against each relevant phase rule.
- Treat any prior passed review tag as informational; re-verify on the
  current artifact.
- Stop and flag if the phase cannot be determined from the artifact itself.

## Output

- Phase being reviewed
- Verdict: pass | needs correction | blocked
- Blocking gaps
- Non-blocking concerns
- Minimal corrections
- Downstream skills or docs impacted

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
