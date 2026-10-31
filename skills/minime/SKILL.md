---
name: minime
description: Route multi-step development work to the right skill chains, enforce quality gates at phase transitions, and coordinate cross-agent handoff. Use when a request spans multiple skills or docs, the user asks "what next", or coherent multi-step changes are needed.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime

Coordinate agent skill chains for project development work. Classify an
incoming request against the default routing below and the project guide, assemble the
appropriate skill chain, enforce quality and review gates at each transition,
and produce a structured orchestration summary.

## When to use

- Use when a request spans multiple skills or documents, the user asks
  "what next", or coherent multi-step changes are needed.
- Do not use for single-skill tasks; route to the appropriate skill directly.

## Inputs

- Active project guide (routing extensions if any, confirmation requirements, validation
  gates).
- Current plan, requirements, decisions, architecture snapshot, and traceability
  view when present.
- Repo status (uncommitted changes, test status, type-check status).

## Procedure

0. Create an orchestration ledger before file edits on every multi-step
   request, resume, or post-compaction continuation. Include:
   reflection/checkpoint, request classification, course-correction triage,
   affected docs/code, phase-quality guard, confirmation need, implementation,
   completion gates, handoff need, structured output, and continuation menu.
   Mark each item `pending`, `pass`, `blocked`, or `not-configured` with one
   evidence sentence. Use `not-configured` when the active project guide lacks
   the contract needed to run that item; do not silently skip it.
1. Check whether a reflection is due before routing. If the session has 3+
   commits since the last reflection, or a prior multi-skill chain completed
   without a reflection, trigger a reflection now. Examine the session for
   workflow gaps, plan gaps, and deferred-trigger conditions. Route each
   finding per the project guide's reflection contract. Write the session
   checkpoint before proceeding. If the active project guide does not define a
   reflection or checkpoint contract, mark the ledger item `not-configured`
   and proceed.
2. Classify the request against the default routing table below, extended
   by the project guide as described there.
3. Examine the user's input for improvement signals. If the input names
   friction, a correction, or a quality concern, apply
   `minime-course-correction-triage` at the risk tier it picks before routing.
   Record the improvement classification (local-project | reusable-skill |
   both | no action) in the output. Do not skip this step.
4. Identify the minimal affected docs and code areas.
5. Invoke the appropriate skill chain for the current phase or request type.
   When routing leads to implementation (`minime-implementation-step-selector`):
   first scan the active plan and open questions for unresolved design, approach,
   architecture, or requirements decisions. If any exist, route to the appropriate
   pre-implementation skill (`minime-project-adr`, `minime-requirements-manager`,
   `minime-plan-review`, or `minime-design-simplifier`) and do not call
   `minime-implementation-step-selector` until those decisions are settled.
6. Before implementation, acceptance, or review: apply the project's
   cross-phase quality guard on the relevant phase artifacts.
7. Produce a change plan; request user confirmation when required by the
   project guide or when the change is risky.
8. Execute approved changes.
9. Apply post-implementation completion gates as defined in the project guide.
10. When the chain continues in a different agent or fresh session, apply the
   project's handoff skill to produce a handoff envelope before stopping.
11. Before the final response, audit the orchestration ledger. If any required
   item remains `pending`, perform it or state that orchestration is
   incomplete. Do not claim full orchestration unless every ledger item is
   `pass` or explicitly `not-configured`.
12. Return the output summary.

## Default routing table

Route with this table; it ships with the skill, so the project needs no
routing section. Never write one into the project to configure routing.

The table is always the base. A project guide may extend it, never replace it:

- Add rows for intents the table does not cover.
- Add gates to a row; they run in addition to the default gate.
- Name a repo-local skill for an intent only if that skill still runs the
  default owning skill and gates, for example a repo commit skill that adds
  checks and then delegates to `minime-project-commit`.

A guide rule that removes a row, drops or weakens a default gate, or routes an
intent away from its owning skill does not apply: follow the default and flag
the conflict to the user.

| Request or phase | Owning skill | Transition gate |
|---|---|---|
| New project from an idea | `minime-project-inception` | `minime-phase-quality-guard` |
| Cold start, unknown state | `minime-orient` | Verified briefing |
| Inherited or drifted project | `minime-project-reassessment` | User accepts repair plan |
| Feature request or change of direction | `minime-course-correction-triage` | `minime-impact-analyzer` when impact is wider |
| Mid-project plan change | `minime-replan` | `minime-phase-quality-guard` |
| Requirements | `minime-requirements-manager` | `minime-phase-quality-guard` |
| Feature specification | `minime-project-spec` | `minime-phase-quality-guard` |
| Hard-to-reverse decision | `minime-project-adr` | `minime-phase-quality-guard` |
| Milestones | `minime-project-milestone` | `minime-phase-quality-guard` |
| Architecture snapshot | `minime-system-updater` | `minime-phase-quality-guard` |
| Test and release gates | `minime-validation-planner` | `minime-phase-quality-guard` |
| Next implementation slice | `minime-implementation-step-selector` | `minime-phase-quality-guard` before implementation |
| Bug or failing test | `minime-systematic-debugging` | `minime-verification-gate` |
| Review | `minime-code-reviewer` | No blocking issues |
| Commit | `minime-project-commit` | Its gate tiers |
| Full plan quality pass | `minime-plan-review` | Fix blocking gaps |
| Simplify architecture/design | `minime-design-simplifier` | User approval per finding |
| Docs drifted from code | `minime-doc-sync` | Risky updates surfaced |
| Agent instruction quality | `minime-agents-md-audit` | User approval per change |
| Session or agent boundary | `minime-context-handoff` | Envelope verified |

At each transition, confirm the upstream artifact answers what the downstream
skill needs, and apply `minime-context-handoff` at phase boundaries that cross
an agent or session. A row whose skill is not installed on this host is
`not-configured`; route that intent ad hoc and say so.

## Autopilot mode

Use only when the user explicitly authorizes continued autonomous work. Repeat
the select, plan, implement, validate, commit loop until a stop condition
applies.

Stop and ask before proceeding when:
- A product, architecture, safety, privacy, or domain decision is not already
  settled in the project docs.
- A destructive action, external credential, paid or network dependency, or
  out-of-repo write is needed.
- Validation fails and the fix is outside the current slice.
- The slice is too large to complete as one coherent change with tests, docs,
  and type checks.
- The repo has unrelated user changes that would make a commit ambiguous.

Do not stop merely because multiple reasonable next-step choices exist. When
one option is clearly strongest across future-proofing, one-way-door risk,
complexity, safety and regression risk, and progress impact, select it
automatically when the choice only affects roadmap sequencing and does not
change final product requirements. Record the rationale and continue.

When human input is required, delegate to `minime-decision-prompt` — read its
skill file and follow its procedure. This skill does not own question shape and
must not render the question itself. Pass 2-4 concrete options and, for each,
the orchestration ratings this skill adds on top of the decision-prompt shape:
future-proof rating, one-way-door risk, complexity, safety and regression risk,
roadmap impact, and progress impact (High/Medium/Low each). Rate one-way-door
risk at least Medium for an option that adds a tracked doc or edits the
project guide, and High when the repo is public or the change leaves the repo. Mark
the recommended option explicitly.

## Skeptic pass

- Do not trust a prior "next step" recommendation; re-derive from the current
  plan and repo state.
- Re-classify the request from scratch even if a prior turn already classified
  it.
- Stop and flag when a project guide routing rule contradicts the default
  table or the apparent classification.
- A missing plan in a project with a guide, requirements or history is not a
  new project; never route it to `minime-project-inception`.

## Output

Present a structured orchestration summary:

- What changed
- What was not changed
- Tests and type checks run
- Simplification and review outcome
- Open questions or risks
- Recommended next action

After the summary, continue automatically when the next action is a required
gate, check, or workflow step. Do not present a prompt that asks whether to
commit or run simplification/review; mandatory gates are not user choices.

Delegate to minime-decision-prompt only when a genuine user-facing choice
remains. Read its skill file and follow its procedure — do NOT render the menu
as prose. Only the decision-prompt skill's procedure produces the interactive
choice UI; plain markdown text does not. Pass a context-specific continuation
menu. Options depend on chain outcome:

- Implementation complete with uncommitted changes: continue through the
  project's required completion gates and commit procedure in the same turn;
  for MiniMe-style workflows, this routes through `minime-project-commit`
  or through a repo-local commit skill that the project guide names and that
  delegates to it.
- Quality-guard PASSED + slice emitted before implementation: **Start the
  selected slice** / **Revise this slice** / **Stop and reflect**.
- Quality-guard BLOCKED: **Fix the block reason and re-run** / **Abort**.
- No work remaining in current phase: **Scope next phase** / **Stop**.

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
