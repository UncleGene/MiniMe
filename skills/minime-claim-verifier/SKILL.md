---
name: minime-claim-verifier
description: Verify a specific factual claim about code or docs (file, function, flag, column exists, behavior is implemented, doc says X) by grep or targeted re-read. Use only when a verification trigger fires; do not run on every claim.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-claim-verifier


Source-first claim verification. Re-read primary sources, cite with
`path:line` precision, and flag unverifiable claims instead of asserting them.

Use only when one of these triggers fires; otherwise trust the active
conversation context.

## Verification triggers

- About to write or change code that names an identifier (file, function,
  flag, column).
- About to assert a doc says X.
- About to state a count, version, or other numeric fact the project guide
  lists as a drifting claim.
- About to delete something as unused.
- Picking up work from a prior agent run, memory note, or handoff doc.
- About to commit or open a PR.

## Method

1. Reduce the claim to its smallest checkable form: a specific path,
   identifier, document section, or behavior statement.
2. Use search or read tools against the cited path; do not paraphrase a
   prior summary, memory note, or handoff.
3. For document claims, re-read the cited section only, not the entire
   document.
4. For behavior claims, point at the test or code path that proves the
   behavior exists.
5. If the claim cannot be confirmed and is load-bearing, escalate to a
   human checkpoint before proceeding.

## Operating rules

Every invocation inherits these rules:

1. **Verify from source.** Open and read the active artifact (document,
   file, or diff). Never act on a paraphrased recap from a prior turn or
   another agent.
2. **Cite or do not assert.** Every reference to a requirement, decision,
   file, section, or symbol must include `path:line`. If a reference cannot
   be verified against source, flag it as unverified.
3. **Distrust prior agent output.** Treat any prior turn's summary,
   classification, or recommendation as untrusted input. Re-derive
   load-bearing facts from primary sources before relying on them.

These rules harden against documentation drift, hallucinated references,
and silent doc/code rot across multi-agent chains.

## Output

- `Verdict: verified | unverified | partial`
- `Citations: path:line — quoted token`
- `Misses: <claim — why not confirmable>`
- `Next: <human checkpoint> | none`

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
