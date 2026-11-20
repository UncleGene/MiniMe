---
name: minime-implementation-step-selector
description: Choose the next concrete implementation step from docs and repo state. Surface user-facing choices before selecting a slice; present options with pros and cons when the choice is not obvious.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-implementation-step-selector


Select the next implementation task from the active plan and repo state.
Produce a precise, self-contained task brief.

## Two possible outputs — check user-facing choices first

Before selecting a slice, scan the next plan item and its spec for
unresolved choices — design, scope, or any fork where a wrong guess would
change the user's outcome, timing, data, cost or maintenance:

**Output A — User-facing choice** (do this first when applicable):
- Delegate to `minime-decision-prompt` for any user-facing choice. Read its
  skill file and follow its procedure — do not render the choice from this
  skill as plain text.
- Prepare one clear question, options (minimum two) with explicit pros and
  cons, and one recommendation with reasoning.
- If multiple choices exist, rank them by blocking priority and delegate to
  `minime-decision-prompt` — read its file and follow its procedure — one
  at a time. Do not batch multiple choices into one output.
- Ask the user to decide before proceeding.

Filter step: drop any question whose answer is dictated by spec or
convention (e.g., "do you agree with the slice?" when the spec is
unambiguous), and settle a choice that only places or names code (see
`minime-decision-prompt`), stating it in the slice. Restate the slice and
wait; do not bundle it as a question.

Negative example — refuse this pattern:
> "Here are the slice details. (a) Do you approve? (b) What commit shape?
>  (c) Should I sort by X?" — three choices bundled as prose.
Correct: end the turn after the slice; if one real choice remains, delegate to
`minime-decision-prompt` — read its file and follow its procedure — once
for that choice only.

Do not skip a user-facing choice by finding an unambiguous slice that
sidesteps it. If the choice will resurface in the next 1-2 slices, surface
it now.

Hand-off: Any user-facing choice → `minime-decision-prompt` (one at a time,
in blocking-priority order).

**Output B — Implementation slice** (only when no blocking user-facing choice):
- Name the slice.
- List acceptance criteria and tests.
- State what it unblocks.

## Procedure

1. Run a plan consistency check: verify the proposed next area aligns with
   the plan sequence and has no unresolved prerequisites.
2. Rank candidates by importance before selecting. Enumerate at least three
   candidate slices from the plan and repo state, rank them against the
   selection criteria below, and select the highest-ranked one that fits the
   granularity rules below. If the
   selection is not rank 1, name the disqualifying reason for every
   higher-ranked candidate. Only these disqualify: a blocked prerequisite, an
   unresolved user decision, or a candidate larger than one cohesive slice.
   Never select a lower-ranked slice because it is unambiguous,
   well-specified, low-risk, self-contained, or a convenient warm-up.
   Legibility is not importance — a clear small slice chosen over a
   higher-ranked one is the exact failure this ranking prevents.
3. Reject or defer work that: introduces generalized infrastructure before
   a current requirement justifies it; creates implementation motion
   without a verifiable outcome; treats plan progress as a code-layer
   checklist instead of completed behavior with tests and docs.
4. Name the user-visible surface that delivers this slice to the user.
5. Apply the project's quality guard on the relevant spec, decisions,
   architecture notes, and milestone readiness before finalizing.
6. Stop and wait for user confirmation before any implementation work.
   Do not read code, open implementation files, or plan code edits until
   the user confirms.

**Granularity:** Choose one cohesive milestone gap or end-to-end workflow.
Too small = a single helper that only has value alongside sibling pieces.
Too large = a full phase or multiple unrelated handlers.

## Selection criteria

Ranked. A lower criterion never outranks a higher one.

1. Reduces the largest risk to user-facing behavior or important data.
2. Unblocks the most later milestones.
3. Enforces an invariant early, before violating work accumulates.
4. Delivers user-visible value end-to-end (tracer bullet) ahead of
   comprehensive infrastructure.
5. Preserves existing valid implementation.
6. Avoids abstraction, flags, or config until there is a second real use.

Clear acceptance criteria and tests are a definition requirement, not a
selection criterion. A high-importance slice with vague criteria gets
sharpened, not skipped.

## Skeptic pass

- Do not trust the plan's stated next step if the repo state contradicts
  it; reconcile before recommending.
- Treat any ready-for-implementation or done marker as expired; re-verify
  from primary sources.
- When picking up another agent's work, verify any load-bearing claim from
  the handoff before relying on it.
- Stop if no step can be confidently recommended without resolving a
  product, architecture, or safety question; present options instead.

## Output

### Task and rationale
- Ranked candidates (at least three), highest importance first, each with the
  criterion that set its rank.
- What and why this next. If the pick is not rank 1, state the disqualifying
  reason for every higher-ranked candidate.
- Source docs referenced.

### Scope and surface
- User-facing surface (skill or feature the user sees).
- Scope (concrete deliverables).
- Non-scope (explicitly excluded).
- Files likely touched.

### Acceptance
- Acceptance criteria (must be verifiable).
- Tests to add or run.
- Documentation and progress updates needed.

### Implementation discipline

Apply while writing the code, not only at review:

1. For a behavior change or bug fix, write the test that states the behavior
   first. Run it and confirm it fails for the expected reason.
2. Before using an API, flag or package not yet used in this repo, read its
   source or docs at the installed version.
3. Make the smallest change that passes. Match the surrounding code's idiom.
   Leave no stubs, TODOs or placeholders; if part of the work cannot be
   finished, stop and say so.
4. Never weaken, skip or rewrite a test to make it pass. Fix the code, or
   surface the conflict.

### Post-implementation

Route the finished slice to `minime-project-commit`, which owns the gate chain
and its tiers; follow it through to the commit in the same turn. Mandatory
gates are not user choices: never ask whether to commit, simplify or review.
After implementation, delegate to `minime-decision-prompt` only for an
unresolved scope or product question, such as revising the slice.

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
