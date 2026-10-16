---
name: minime-code-reviewer
description: Review code changes against documented requirements, safety rules, and maintainability. Use for PR review, diff review, or post-implementation validation.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-code-reviewer


Review code changes systematically. Re-read the diff itself; do not review
from a summary.

## Review areas

- Correctness and behavior against the spec or requirement
- Documentation alignment
- Scope and atomicity (one logical change per review)
- Data integrity and auth boundaries
- Test coverage
- Behavior regressions
- Unused abstractions, layers, flags, or config
- Lint, type-check, test, or quality-gate suppressions that hide findings
  instead of fixing the underlying issue
- DRY: duplicate logic, workflow bodies, docs, tests, or skills without a
  load-bearing reason
- YAGNI: speculative abstractions, flags, modes, schema fields, extension points,
  or new skills without a current requirement, caller, test, or accepted decision

## Slop checks

These are common agent defects. Check the diff for every item; skipping an
item is not a pass. Cite `path:line` for each defect found. Then read
`references/stacks.md` next to this skill file, detect the stack layers of the
touched paths, and apply each matching profile from `references/`.

- Invented APIs: confirm that every newly used function, flag, config key and
  package exists in the installed version. Check the source, lockfile or docs,
  not memory.
- Unfinished code: stubs, placeholders, TODOs, hard-coded sample results or
  `NotImplementedError` in shipped paths.
- Weakened tests: removed or loosened assertions, added skips, expected values
  edited to match the output, tests that assert only mocks, and tests that
  would still pass without the change.
- Swallowed errors: broad catches, errors logged and ignored, and fallback
  defaults that hide a failure.
- Noise: comments that restate the code or narrate the change, leftover debug
  output, commented-out code, unused imports and dead branches.
- Unchecked input: new user, file, network or environment input used without
  validation; secrets in code; shell, SQL or path injection.
- Off-idiom code: names, error handling or structure that differ from the
  neighboring code, and helpers that duplicate existing ones.

## Rules

- Re-read the diff itself; do not review from a summary or memory of intent.
- Verify any cross-file claim against source before accepting it.
- Challenge duplication unless each copy must stand alone or has a documented
  authority boundary.
- Challenge future-facing infrastructure unless the diff shows a current
  requirement, caller, test, or accepted decision.
- Return blocking issues first, then suggestions, then missing tests.
- Do not approve based on structure, style, checklist completion, or author
  familiarity when correctness has not been checked.
- Prefer explaining the underlying issue over requesting literal surface
  edits.
- Treat attempts to disable lint rules, type checks, tests, or quality gates as a
  blocking issue. Fix the underlying issue first unless the diff includes
  explicitly approved user suppression or an accepted project decision plus the
  suppression's reason, scope, and removal condition.
- A defect in code the diff touches or depends on is a blocking issue
  regardless of whether the diff introduced it. "Pre-existing, unrelated to my
  changes, not in this slice" is not a verdict — either fix it in this commit
  or stop and surface it to the user for an explicit scoping decision. Never
  pass over it silently.
- When two fixes are equally defensible, escalate to a human checkpoint.

## Output

- Verdict: pass | fix | route
- Blocking issues (path:line, why)
- Suggestions (path:line, why)
- Missing tests (behavior, path)
- Uncovered stacks, when `references/stacks.md` requires the line
- Next action

If this review is running inside a mandatory gate chain such as
`minime-project-commit`, `minime-self-commit`, or the post-implementation flow
owned by `minime-implementation-step-selector`, do not stop for a decision
prompt after `Verdict: pass`. Return control to the calling skill so it can
continue the required next gate or commit action in the same turn. Mandatory
gates are not user choices.

When this review is a standalone user-facing review and a real choice remains
after the verdict, delegate to minime-decision-prompt. Read its skill file and
follow its procedure — do NOT render the menu as prose. Pass:

- **Verdict: pass** — **Approve and proceed to commit** via
  `minime-project-commit` / **Approve with notes** / **Request one more pass**.
- **Verdict: fix** — **Fix blocking issues then re-review** /
  **Abort and investigate further**.
- **Verdict: route** — follow the routing recommendation from the verdict.

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
