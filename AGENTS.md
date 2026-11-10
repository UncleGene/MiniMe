# MiniMe Agent Operating Guide

## Project

MiniMe is a cross-project engineering skill library for AI coding agents. Its
goals (Decision 1) are:
1. An anti-slop, production-quality bar met without the user catching defects.
2. Token, model and effort cost, ranked below quality.
3. Portability: Codex and Claude Code are verified hosts; OpenCode and
   GitHub Copilot are supported (Decision 4).

The user is a single author on a budget plan directing agents to write nearly
all of the code; quality keeps slop from compounding cost and keeps projects
fit to share (Decisions 1/2).

Skills install at host/user level, and Python 3.14+ is required. Planted-defect
fixtures, not formal comparison trials, evidence the bar (Decision 9).
Automated scanning and CLI writes to consuming repos are out of scope, and no
MiniMe trace may land in them (Decision 3).

Current CLI behavior is read-only by default. User-level installation with
`--write` (host skills, the slop-scan git hook and the agent commit gate) is
the only CLI write path; the CLI does not edit consuming repos.

Authority: accepted user decisions override inherited guidance. Current
requirements live in `docs/requirements.md`, architecture in `docs/concepts.md`,
and implementation status/next work in `docs/implementation-plan.md`.
Decisions live in `docs/decisions.md`. See `docs/development.md` for
development-tool setup.

## Quick Commands

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
scripts/minime doctor
scripts/minime skills list --json
ruff check --no-cache scripts/minime tests
mypy --python-version 3.14 --cache-dir /tmp/minime-check-mypy scripts/minime tests
scripts/minime host-registration-audit --skills-root ~/.codex/skills --json
scripts/minime host-registration-audit --skills-root ~/.claude/skills --json
scripts/minime host-registration-audit --skills-root ~/.config/opencode/skills --json
scripts/minime host-registration-audit --skills-root ~/.copilot/skills --json
scripts/minime transparent-audit --repo <path> --json
scripts/minime transcript-audit --since <ISO date>
```

Run unittest before catalog/host checks: suite fixtures temporarily alter
`skills/`. Include the extensionless `scripts/minime` explicitly in lint/type
checks. The typing command uses default mypy checks targeting Python 3.14;
strict-typing migration is out of scope. Registration checks do not prove live
host discovery or workflow outcomes. Use the available supported interpreter;
particular-version enforcement is very low priority (Decision 5).

## Completion Gates

Before any commit or completion claim for a MiniMe change, pick the gate tier
(Decision 7). The light tier applies only when every changed file is
documentation and no requirement, decision, acceptance or safety text changes:
status, history, notes, checkpoints, typos and links. It runs gates 1, 2, 3, 5
and 6 and skips review. Any code, test, build/config, skill or
procedure change uses the full tier, gates 1–6. When in doubt, use the full tier.

1. Run `minime-doc-sync` against the diff — confirm README and all other docs
   reflect the changes before committing. Stale docs are a commit defect, not
   a follow-up task.
2. Run `minime-scope-boundary` against the diff.
3. Run `minime-code-simplifier` against the diff — simplify before review so
   the reviewer sees clean code.
4. Run `minime-code-reviewer` against the diff.
5. Run `minime-verification-gate` with the required project checks.
   If any test fails during verification, apply `minime-systematic-debugging`
   — do not attempt a fix without completing Phase 1 (feedback loop).
   A failing full-project gate means the repo is not commit-ready, including
   pre-existing unrelated lint, test, or type-check failures. Touched-file
   checks are supporting diagnostic evidence only; they do not satisfy the
   "never commit broken repo" rule.
6. Use `minime-self-commit` to shape the final commit. **Never run `git
   commit` directly.** Always read the minime-self-commit skill file and
   follow its procedure first — it is the only path to a commit that
   enforces the selected gate tier and MiniMe-internal gates. Direct
   `git commit` via Bash bypasses every gate in this list.

Do not stop after implementation at an arbitrary uncommitted state unless the
user explicitly asked not to commit. If the change is ready, route through
`minime-self-commit` (read its skill file and follow its procedure); if
it is not ready, state the blocker and the
exact gate that remains.

Every completion, pause, handoff, or blocked-state response must report:

- branch and HEAD short SHA;
- working-tree state, including whether there are uncommitted changes and the
  changed file paths;
- verification, lint, and type-check status, or the exact reason each was not
  run;
- whether the work is committed, commit-ready, or not commit-ready;
- the next concrete action.

Do not disable lint rules, type checks, tests, or quality gates to make a check
pass unless the user explicitly approved that suppression or an accepted project
decision already requires it. Fix the underlying issue first. Any suppression in
a diff must include the reason, scope, and removal condition; otherwise it is a
blocking review finding.

For changes that add a skill, abstraction, workflow, repeated text block,
configuration option, or future-facing extension point, explicitly apply DRY
and YAGNI before committing:

- DRY: merge or reuse existing skills, helpers, docs, and tests when they have
  the same responsibility. Keep duplication only when each copy must stand alone
  for host/user-level consumption, and record that reason.
- YAGNI: do not add a new abstraction, skill, flag, mode, schema field, or
  extension point without a current requirement, caller, test, or accepted
  decision that needs it now.

## Shared Interaction Contract

Apply this contract to every MiniMe skill flow. Each reusable skill ends with an
identical `## Interaction rules` section carrying its consumer-facing subset, so
installed skills keep it outside this repo (Decision 6); edit all copies
together. Reflection and checkpoint rules below are MiniMe-only. It applies equally on Codex, Claude Code, OpenCode and GitHub
Copilot, whatever model the host runs; host differences do not weaken the
workflow contract.

**Every response must end with `Recommended next action: <one concrete next step>`.
No exceptions — not for simple fixes, not for terminology changes, not for doc
updates. If in doubt, include it.**

**The recommended-action chain must not break across skill boundaries.** After
completing any skill procedure or workflow step, scan the active plan and
session checkpoint for the natural next action. Recommend it. A skill that
completes without a recommendation leaves the session stranded — this is a
contract violation, not a neutral handoff.

**When the recommended next action is a gate, check, or workflow step that
requires no user input or decision, execute it in the same turn — do not
stop at an arbitrary uncommitted state.** Only stop to present the
recommendation when the next step requires user confirmation, input, or
choice.

**Never treat a pre-existing lint, test, type-check, doc-consistency, or
gate failure as OK to skip. The repo must be clean before any commit,
regardless of whether the failure existed before the current change. This
applies to every gate — doc consistency, lint, tests, type checks, and
verification. Escalate or fix pre-existing failures; do not commit over
them.**

**Before implementing any feature addition or behavior change, run a recorded
intake evaluation — do not take the request at face value.** Scale it to the
change's risk tier, defined in `minime-course-correction-triage` (Decision 16):
a low-risk change states one intake line; a standard one passes the four
checks below, stated in the response; a high-risk one runs the full triage.

- **Assumption check** — does the request contradict an accepted requirement,
  decision, or key invariant? If so, stop and route through
  `minime-course-correction-triage`; resolve the conflict in docs before code.
- **Impact check** — name the blast radius across requirements, decisions,
  architecture, plan, docs, and tests. If it reaches beyond the touched files,
  run `minime-impact-analyzer` before implementing.
- **Value check** — state what value the change adds and confirm implementation
  is the smallest delivery. If the value is unclear, or a doc/decision change or
  no-op would serve, challenge the request before writing code.
- **Premise check** — can the request work as stated, and what does it
  assume? Name the load-bearing assumption (data that must be observable,
  context another agent would lack, a cause the user has inferred) and verify
  it from evidence when a search, a file read or a log lookup can. If it fails
  or cannot be checked, say so with the evidence before any design question or
  code.

This rule overrides any "the target is clear, route directly" shortcut. A
request that looks like a one-line fix still passes intake at its tier. The
intake gate is `minime-course-correction-triage`; route both feature requests
and corrections through it at their tier, and through the full triage when any
check is non-trivial.

- Ask a concise clarifying question when any required input, scope boundary,
  artifact authority, or next-step choice is unclear. Ask one question per
  turn — if multiple questions exist, rank by blocking priority (which one
  would halt implementation if left unresolved?) and ask the highest-priority
  one first. Wait for the answer before asking the next.
- **Every question the agent asks the user must carry the
  `minime-decision-prompt` shape — named options, each with pros, cons, and
  stated impact — never raw prose.** This holds for any question whose answer
  would change an artifact, implementation, validation, or handoff, regardless
  of which skill is running or whether a listed ambiguity trigger fired, except
  the low-tier stated default below.
  Before asking, read `minime-decision-prompt` and follow its procedure, then
  render the result per the structured-choice rule below. Reject these shapes:
  a bare open question ("How would you like me to handle X?"), a yes/no with
  no stated consequence, and a prose paragraph that buries the choice in
  narrative. Only a question with no material consequence — a factual lookup
  the agent cannot resolve from the repo — may be asked as plain prose. In the
  low risk tier, a reversible choice with a conventional default is stated, not
  asked.
- Do not silently choose between materially different interpretations when the
  answer would change the artifact, implementation, validation, or handoff; a
  stated low-tier default is not silent.
- Examine every user input and user-identified problem for an opportunity to
  improve MiniMe's project guidance, requirements, implementation, tests, or
  reusable skills. Route actionable opportunities through the appropriate
  MiniMe skill instead of treating them as one-off conversation fixes.
- When presenting two or more materially different next-step options to the
  user, render them as a structured interactive choice through the host's
  choice UI when one is available (for example, `AskUserQuestion` in Claude
  Code; equivalents in other agentskills.io clients). Free-form bulleted
  text lists for multi-option choices put the typing burden on the user
  and obscure the recommended option. A single recommended next action
  remains text per the prior rule; a menu of two or more options is a
  structured choice. If the structured choice UI is unavailable on the
  current surface, use a fallback numbered text menu, state the recommended
  option, and still end with `Recommended next action:`. Do not omit the
  next step because the preferred UI is unavailable.
- Every reflection must produce an action, not a passive record. When a
  reflection is triggered, examine session content for gaps in MiniMe
  workflows (missing skills, broken conventions, process friction) and gaps
  in the development plan (stale claims, missing items, deferrals ready to
  activate). Also check for deferred-trigger conditions: skill size
  approaching ceiling, verbosity above peer median, or utility gaps
  surfaced during the session. Route each gap: implement the fix directly
  in the same commit, add it to the plan, or conclude no action is needed.
  Record actions and rationale in `docs/learnings.md`. No-action findings
  leave no trace.

  Write a session checkpoint only at a handoff: session end, pause, or another
  agent continuing the work (Decision 7). Use
  `docs/sessions/YYYYMMDD-HHMMSS.md` (the actual date and time). Checkpoints
  are git-ignored and stay local (Decision 8).
  Checkpoint format:
  ```
  ---
  branch: <branch>
  commit: <HEAD short SHA>
  timestamp: <ISO datetime>
  ---
  ## Plan position
  - Phase: <current phase name>
  ## Skills used
  - <skill names invoked; flag any with `(correction)` or `(unhelpful)`>
  ## Remaining work
  - <one concrete next action>
  ```

  Reflection triggers: (a) session end after 3+ commits, (b) orchestrator
  completing a multi-skill chain, (c) a gate catching a project-rule
  violation that originated in a prior session, or (d) user request
  ("reflect", "stop and reflect"). Skills that coordinate multi-step work
  (orchestrator, project-commit, implementation-step-selector) should
  check trigger conditions and offer or auto-fire a reflection before
  producing their final output.

- At session start, check `docs/sessions/` for recent checkpoint files.
  If one exists, read the latest and orient context from it before routing
  any request.

## Skill Routing

Use these MiniMe target-reusable skills for development work on this repo.
Invoke by reading the skill file and following its procedure.

**Cross-skill delegation:** When a procedure step or gate lists another skill
by name (e.g. `minime-code-reviewer`), delegate to it — read that skill's file
and follow its full procedure, or invoke it through the host's skill mechanism
where the calling step says so (fresh-context skills, Decision 14). Do not approximate the skill's behavior from
memory or collapse its procedure into an inline summary. Each skill owns its
own procedure; delegation means executing it, not remembering it. If the
delegated gate, check, or workflow step requires no human input, execute it in
the same turn and continue through the chain until the next step genuinely
requires a user decision, external approval, or unavailable environment.

| Intent | Skill |
|---|---|
| Cold-start: enter a project with no context, identify state, pick next work | `minime-orient` |
| Bootstrap a new project from an idea: interview, guide, requirements, first milestone | `minime-project-inception` |
| Fresh-look reassessment of an inherited or drifted project: goals, docs, design, code, tests | `minime-project-reassessment` |
| Route a multi-step request or "what next" | `minime` |
| Full plan quality pass before a phase transition | `minime-plan-review` |
| Gate: enforce evidence before completion claims | `minime-verification-gate` |
| Surgical mid-project plan change | `minime-replan` |
| Pick the next implementation slice | `minime-implementation-step-selector` |
| Verify a specific factual claim (path, count, flag, behavior) | `minime-claim-verifier` |
| Sync docs with changes, check one doc, or sweep all docs (report-only/apply) | `minime-doc-sync` |
| Report docs a diff made stale, editing nothing (called by `minime-doc-sync`) | `minime-doc-check` |
| Detect over-engineering in plan/architecture | `minime-design-simplifier` |
| Check a diff stays in scope | `minime-scope-boundary` |
| Check phase readiness | `minime-phase-quality-guard` |
| Review code changes | `minime-code-reviewer` |
| Simplify implementation code | `minime-code-simplifier` |
| Record a technical decision | `minime-project-adr` |
| Update requirements | `minime-requirements-manager` |
| Update plan milestones | `minime-project-milestone` |
| Update architecture snapshot | `minime-system-updater` |
| Trace impact of a change | `minime-impact-analyzer` |
| Shape a commit (MiniMe repo) | `minime-self-commit` |
| Shape a commit (target project) | `minime-project-commit` |
| Intake gate: evaluate a feature request or course correction before code | `minime-course-correction-triage` |
| Handoff between sessions | `minime-context-handoff` |
| Write or refine a feature spec | `minime-project-spec` |
| Plan tests and release gates | `minime-validation-planner` |
| Audit an agent instruction file | `minime-agents-md-audit` |
| Prepare a repo for publishing: privacy sweep, doc coherence, README, history | `minime-publish-prep` |
| Systematic debugging (bugs, test failures, unexpected behavior) | `minime-systematic-debugging` |

## Verifiable Claims Index

Numeric facts that drift. Verify these against source before citing them.

| Claim | Source | Current value |
|---|---|---|
| Target-reusable skill count | `scripts/minime skills list --json` | 30 |
| Internal skill count | `scripts/minime skills list --json` | 2 |
| Test count | `python -m unittest discover -s tests` | Verify from the current run |
| Registered host skills (per surface) | `scripts/minime host-registration-audit --skills-root <surface> --json` | 30 |
| Installed surfaces | `scripts/minime skills install --json` | 4 (`~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`, `~/.copilot/skills`) |

## Key Invariants

- CLI write boundary: host/user-level installation only; no consuming-repo edits.
- `metadata.minime_kind: target-reusable` required for install-check.
- DRY: avoid duplicate skills, workflow bodies, tests, and docs unless the
  duplication is load-bearing for standalone consumption or a documented
  authority boundary.
- YAGNI: no speculative skills, abstractions, flags, schema fields, modes, or
  extension points without a current requirement, caller, test, or accepted
  decision.
- No names or paths of other local/target projects in any tracked file or
  commit message (Decision 8) - guarded by
  `test_tracked_files_have_no_local_home_paths` and
  `test_tracked_files_and_history_have_no_private_project_terms`, which reads
  the untracked `.minime-private-terms` denylist. Use neutral placeholders.
- `scripts/minime skills install-check <skill>` must pass before a new skill
  is considered complete.
