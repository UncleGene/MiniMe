---
name: minime-project-commit
description: Shape atomic commits and PR descriptions with traceability to plan, spec, and decisions. Use when a change is ready to be committed or reviewed.
metadata:
  minime_kind: target-reusable
  model_tier: fast
  model_tier_strictness: preferred
---

# minime-project-commit


Prepare a change for commit with a traceable, atomic commit message.

## Commit rules

- One logical change per commit.
- The title and diff must match; split commits that mix unrelated behavior,
  docs, refactors, or config.
- Conventional commit title: `type(scope): imperative summary`.
- Body explains why, not just what.
- Reference the plan item, spec section, and decision when relevant.
- Avoid newly extracted abstractions until the duplication or behavior
  pressure exists at least twice.
- Do not introduce config or feature flags without a real second value and
  a documented owner.
- Do not commit duplicated workflow, docs, tests, helpers, or skills unless the
  commit message or plan records the standalone-consumption or authority-boundary
  reason.
- Do not commit YAGNI infrastructure: speculative abstractions, flags, modes,
  schema fields, extension points, or new skills without a current requirement,
  caller, test, or accepted decision.
- In autopilot mode, commit each finished slice before moving to the next.
- Do not leave a completed implementation at an arbitrary uncommitted state. If
  the change is ready, continue through this commit procedure; if it is not
  ready, report the blocker and remaining gate.
- After the required checks pass and no user-facing decision remains, stage and
  create the commit in the same turn. Do not stop at "commit-ready," and do not
  ask whether to continue with the commit procedure.

## Pre-commit checks

Pick the tier first. Light tier: every changed file is documentation and no
requirement, decision, acceptance or safety text changes (status, history,
notes, checkpoints, typos, links); run doc-sync, scope, simplifier and the full
project checks, and skip the reviewer. Any code, test, build/config, skill or
procedure change uses the full tier below. A spec or plan edit that adds a
default, rule or option is requirement or decision text, so it takes the full
tier. When in doubt, use the full tier. The strictest applicable rule wins:
when a user, memory or project-guide rule requires a check the tier would
skip, run it. State the choice in a reply line, `Commit tier: light — <why>`
or `Commit tier: full`; the installed agent commit gate lets a turn that
states the light tier skip the reviewer, and one that states the data tier
(below) skip every check skill.

Data files: a repository may set the git attribute `commit-data` on paths that
hold records rather than code or docs (`git check-attr --cached commit-data --
<path>` reports `set`). Those files are outside the doc, scope, simplifier
and reviewer checks: each runs on the rest of the staged diff,
`git diff --cached -- . ':(exclude,attr:commit-data)'`, and the tier is picked
from that rest. When every staged path has `commit-data` set, use the data
tier: state `Commit tier: data — <why>`, run only the full project check the
project guide names (or the full test, lint and type gates when it names
none), re-read the diff, write the message and commit the index with
`git commit -m '<message>'` (or `-F <file>`) alone in its call, after staging
in an earlier call. The installed gate verifies the attribute and that shape.

In the light and full tiers, execute these checks sequentially — delegate to
each named skill by reading its file and following its procedure. After each
check passes with no blocking findings and no user decision required, proceed
immediately to the next check in the same turn — do not end the turn between
sequential passing gates.

- Read the minime-doc-sync skill file and execute it against the staged
  diff; confirm README and all other docs reflect the changes. Stale docs
  are a commit defect, not a follow-up task.
- Read the minime-scope-boundary skill file and execute it against the
  staged diff.
- Read the minime-code-simplifier skill file and follow its procedure
  against the staged diff — simplify before review so the reviewer sees
  clean code. This step is mandatory in both tiers.
- Invoke `minime-code-reviewer` through the host's skill mechanism, so a host
  that runs it in a fresh context can; if the host has none, read its skill
  file and follow its procedure. Pass the staged diff as its scope. This step is
  mandatory in the full tier; fix all blocking
  issues before proceeding. Do NOT perform the review inline — only full delegation
  produces the required structured output (Verdict / Blocking issues /
  Suggestions / Missing tests).
- When the staged diff spans 3+ logical changes or completes a phase, check
  whether the project guide defines a reflection gate. If it does, trigger a
  reflection — examine the session for workflow gaps and plan gaps, route
  findings per the reflection contract — before committing.
- Confirm DRY and YAGNI were applied to the staged diff, especially for changes
  touching skills, tests, docs, flags, modes, schemas, or abstractions.
- Re-read the diff before writing the message — do not summarize from
  memory of intent.
- Run full project test, lint, and type-check gates before treating the commit
  as ready unless the user or project guide explicitly defers them. Changed-file
  tests, changed-file lint, and narrow smoke checks are supporting evidence, not
  commit readiness evidence, unless such a deferral is explicit.
- If any full project gate fails, the repo is not commit-ready. This includes
  pre-existing unrelated lint, test, or type-check failures outside the current
  slice. Use touched-file checks only as supporting diagnostic evidence while
  fixing or escalating the broken repo state; do not commit around the failure.
- Do not disable lint rules, type checks, tests, or quality gates to make a
  commit pass unless the user explicitly approved that suppression or an
  accepted project decision already requires it. Fix the underlying issue first.
  Any suppression in the diff must include the reason, scope, and removal
  condition; otherwise the commit is blocked.

## Output

- Verdict: pass | fix | route
- Commit message: type(scope): summary + body
- Repository state: branch, HEAD short SHA, whether the working tree has
  uncommitted changes, and changed file paths
- Verification state: test, lint, and type-check status or exact not-run reason
- Commit readiness: committed | commit-ready | not commit-ready
- Next action: the next concrete action

After a **pass** verdict and successful commit, delegate to
minime-decision-prompt. Read its skill file and follow its procedure —
produce a "what next?" menu. Do NOT end the session without presenting this
prompt. Typical options:

- **Continue to next slice** — route to `minime-implementation-step-selector`.
- **Stop and reflect** — write a session checkpoint and update learnings.
- **Stop here** — session complete.

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
