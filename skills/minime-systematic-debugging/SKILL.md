---
name: minime-systematic-debugging
description: Find and fix root causes of bugs, test failures, and unexpected behavior. Use before proposing any fix — do not suggest solutions without completing Phase 1.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-systematic-debugging

Find root cause before fixing. Symptom fixes mask underlying issues and create
new bugs. Systematic investigation is faster than repeated guessing.

## When to use

- Any test failure, bug, unexpected behavior, or performance regression.
- Especially under time pressure or when a "quick fix" seems obvious.
- Phases gate each other — do not skip forward.

## The Five Phases

### Phase 1 — Build a feedback loop

**This is the skill.** A fast, deterministic, agent-runnable pass/fail signal
makes every later phase mechanical. Without it, no amount of code reading will
reliably find the bug.

Spend disproportionate effort here. Try these in order:

1. **Failing test** at whatever seam reaches the bug — unit, integration, or e2e.
2. **CLI invocation** with a fixture input, diffing output against a known-good snapshot.
3. **HTTP script** against a running dev server.
4. **Headless browser script** if the bug is UI-only.
5. **Replay a captured trace** — save a real network request or event log; replay in isolation.
6. **Throwaway harness** — minimal subset of the system that exercises the failing code path.
7. **Property/fuzz loop** — if the bug is "sometimes wrong output," run many random inputs.
8. **Bisection harness** — if the bug appeared between two known states, automate the check.
9. **Differential loop** — same input through old vs new version; diff outputs.

Once you have a loop, make it faster and sharper: narrow scope, pin time and RNG,
isolate filesystem, assert on the specific symptom not just "didn't crash."

If you genuinely cannot build a loop: say so explicitly. List what you tried. Ask
for access to the reproducing environment, a captured artifact (log, trace, HAR),
or permission to add temporary instrumentation. Do not proceed to Phase 2 without
a loop you believe in.

### Phase 2 — Reproduce and investigate

Run the loop. Confirm the failure matches what the user described — not a different
failure that happens to be nearby.

Then investigate at component boundaries: when the system has multiple layers, add
targeted instrumentation at each boundary. Log what enters and exits each component.
Run once to locate WHERE it breaks, then trace the data flow backward from the
symptom to its origin. Fix at source, not at symptom.

### Phase 3 — Hypothesize

Generate **3–5 ranked hypotheses** before testing any. Single-hypothesis generation
anchors on the first plausible idea.

Each hypothesis must be falsifiable:
> "If X is the cause, then changing Y will make the bug disappear."

If you cannot state the prediction, the hypothesis is a guess — sharpen or discard it.

Show the ranked list to the user before testing. They often have domain knowledge
that re-ranks instantly. Do not block on a response — proceed with your ranking
if the user does not reply.

### Phase 4 — Instrument and fix

Test one hypothesis at a time. Tag every debug log with a unique prefix
(e.g. `[DBG-a4f2]`) so cleanup is a single grep.

Fix at the root cause. Write the regression test **before the fix** — but only
if a correct seam exists. A correct seam exercises the real bug pattern, not a
shallow proxy. If no correct seam exists, document that finding.

If a fix does not work: STOP. Count attempts.
- Fewer than 3: return to Phase 3 with new information.
- 3 or more: the architecture may be the problem. Are fixes revealing new symptoms
  in different places? Discuss with the user before attempting another fix.

### Phase 5 — Cleanup and post-mortem

Before claiming done:

- [ ] Original reproduction no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes, or absence of a correct seam is documented
- [ ] All tagged debug instrumentation removed (grep the prefix)
- [ ] Throwaway harnesses deleted

Then ask: **what would have prevented this bug?** If the answer involves
architectural change, flag it for a follow-up architecture review — after the
fix is in, not before.

## Red flags — stop and return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see what happens"
- Making multiple changes at once
- Proposing solutions before completing Phase 1
- "One more fix attempt" when 2+ already failed
- Each fix reveals a new problem in a different place

## Quick reference

| Phase | Key activity | Exit criterion |
|---|---|---|
| 1. Feedback loop | Build a fast, deterministic pass/fail signal | Loop exists and is reliable |
| 2. Reproduce | Confirm failure matches user report; trace to origin | Know where and why |
| 3. Hypothesize | 3–5 ranked falsifiable hypotheses | Ranked list ready to test |
| 4. Fix | One change at a time; regression test first | Bug resolved, tests pass |
| 5. Cleanup | Remove debug artifacts; post-mortem | Instrumentation gone; finding documented |

## Common rationalizations

| Excuse | Reality |
|---|---|
| Issue seems simple | Simple issues have root causes too |
| Emergency, no time | Systematic is faster than thrashing |
| Try this first, then investigate | First fix sets the pattern; do it right |
| Multiple fixes at once | Cannot isolate what worked; introduces new bugs |
| 3+ failures, one more try | 3+ failures = architectural problem; stop |

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
