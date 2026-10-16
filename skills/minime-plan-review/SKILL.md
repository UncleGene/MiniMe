---
name: minime-plan-review
description: Run a full quality pass over the active plan and its supporting artifacts. Orchestrates minime-phase-quality-guard, minime-claim-verifier, minime-scope-boundary, and minime-doc-sync (document and all scopes) in sequence. Use before moving to a new implementation phase, before a major commit, or whenever the plan has grown significantly.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-plan-review


Orchestrate a structured quality pass over the active plan. Runs five checks
in sequence, surfaces blocking gaps before they become implementation debt,
and produces a single verdict with a prioritised fix list.

## When to use

- Before moving to a new implementation phase — confirm the prior phase is
  actually done and the plan is consistent with what shipped.
- After a large batch of commits — catch plan drift before it compounds.
- Whenever the plan has grown noticeably since the last review.
- Do not substitute for per-artifact owner skills (e.g. use
  `minime-project-adr` to record a decision, not this skill).

## Inputs

- Active plan file (e.g. `docs/implementation-plan.md`)
- Active requirements, decision log, and architecture snapshot when present
- Current repo state (uncommitted changes, test status)

## Procedure

Run the five checks in this order. Each check informs the next.

### Check 1 — Phase readiness (`minime-phase-quality-guard`)

Apply the phase-quality-guard cross-phase checklist to the plan's current
phase and the artifacts it references:

- Claims about existing code cite `path:line`.
- Scope matches the phase description; no silent expansion.
- Open questions are closed or explicitly blocked before work starts.
- Layered abstractions and flags each have a current concrete use.
- Output can be verified by tests, docs, or reviewer action.

Flag any blocking gaps. Record: phase being reviewed, verdict
(pass / needs correction / blocked), and the minimal corrections needed.

### Check 2 — Factual claim verification (`minime-claim-verifier`)

Using the plan's Verifiable Claims Index (from CLAUDE.md or equivalent),
verify each listed numeric fact and reference against source:

- Test count matches the test runner output.
- Skill count matches the actual count in this project.
- Any other plan-specific numeric claims listed in the index.

For any claim not in the index, scan the plan for bold numbers, commit
refs, and quoted command outputs and verify them on sight.

Flag stale facts as auto-fixable; surface ambiguous ones for user decision.

### Check 3 — Scope boundary (`minime-scope-boundary`)

Review the diff since the last documented review commit (or since the start
of the current phase) against the phase description:

- Are all changes within the stated phase scope?
- Are there files touched that the plan did not intend to touch?
- Are there unrequested refactors, renames, or speculative additions?

Record: verdict (in-scope / out-of-scope / mixed), and any out-of-scope
items with routing suggestion (split, defer, or accept).

### Check 4 — Plan against code (`minime-doc-sync`, `document` scope)

Check the plan file itself claim by claim:

- Every command in the plan runs on the current codebase.
- Every path and file reference exists.
- Every "completed" claim is backed by actual committed code.
- Every "planned" item has not already shipped.

Flag drift items as: still-true, drifted, removed, or ambiguous.
Route each drifted item to the appropriate owner skill.

### Check 5 — Cross-doc coherence (`minime-doc-sync`, `all` scope)

Run the whole-set sweep in `report-only` mode over the full
documentation surface (project guide, README, requirements, decisions,
architecture, plan, procedures, templates, troubleshooting):

- Cross-doc references resolve.
- Authority and project-rule statements match across the project guide,
  core docs, and README.
- Status claims ("complete", "in progress", "planned") match the code and
  tests.
- Procedure executability: every referenced command exists.
- No stale gate language from completed phases.

Flag findings by kind (`blocking` / `consistency` / `clarity` / `currency`).
Phase transitions are the natural trigger for this check; per-commit
`minime-doc-sync` only sees changed files, so dormant cross-doc drift
accumulates between sweeps.

## Output

```md
## Plan Review

### Check 1 — Phase readiness
Verdict: pass | needs correction | blocked
Blocking gaps:
Non-blocking concerns:

### Check 2 — Claim verification
Auto-fixable: (list with corrected values)
Needs user decision: (list)

### Check 3 — Scope boundary
Verdict: in-scope | out-of-scope | mixed
Out-of-scope items: (path:line, routing)

### Check 4 — Doc-code consistency
Drift items: (claim, evidence, fix direction)

### Check 5 — Cross-doc coherence
Findings by kind: (blocking, consistency, clarity, currency)
Apply-mode candidates:

### Overall verdict
pass | fix-before-proceeding | blocked
Priority fix list: (ordered by severity)
Next action:
```

## Rules

- Run all five checks even if Check 1 finds a blocker. A blocked phase
  readiness plus stale facts is more useful than stopping early.
- Do not fix issues inside this skill — route each to the owning skill
  and list the fix in the priority list.
- If the plan has no Verifiable Claims Index, note the gap in Check 2
  output and scan manually.
- Check 5 runs in `report-only` mode here. To apply coherence fixes, invoke
  `minime-doc-sync` with `all` scope in `apply` mode after this review.

## Hand-off

Each entry names an owner skill. Delegate to the listed skill — read its file and
follow its full procedure. Do not approximate from memory.

- Blocking phase gap → `minime-phase-quality-guard` (per-phase rules)
- Stale numeric facts → `minime-claim-verifier` → auto-fix or `minime-doc-sync`
- Out-of-scope changes → `minime-scope-boundary` → split or defer
- Drifted plan claims → owner skill named in Check 4
- Cross-doc drift surfaced in Check 5 → `minime-doc-sync` (`all`, apply mode)
- Decision gap surfaced → `minime-project-adr`
- Architecture drift → `minime-system-updater`

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
