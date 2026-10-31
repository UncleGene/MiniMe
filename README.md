# MiniMe

MiniMe is a library of engineering skills for AI coding agents. You install it
once at user level, and every project you open in Codex, Claude Code, OpenCode
or GitHub Copilot can use it. Your projects stay free of MiniMe files.

It is built for single-author, agent-driven development on a budget: the
quality bar keeps slop from compounding your cost and complexity, and keeps a
project you may later share or open-source fit to show.

## Goals

1. **Production quality without babysitting.** Agents meet an explicit
   anti-slop bar, so you are not the one catching invented APIs, stubbed
   code, weakened tests, swallowed errors or skipped checks.
2. **Cost-appropriate execution.** Spend tokens, model tier and effort where
   they matter, never at the expense of quality.
3. **Portability.** Codex and Claude Code are verified hosts with fixtures,
   transcript audits and commit hooks. OpenCode and GitHub Copilot are
   supported hosts that install the same skills.

## What you get

- **29 skills** covering the development loop: project inception and
  orientation, requirements and specs, planning and replanning, implementation
  step selection, debugging, review, simplification, documentation sync and
  commit shaping. Each skill carries the same interaction rules: argued choices
  instead of silent guesses, evidence before "done", and a recommended next
  action at the end of every response.
- **Layered code review.** The reviewer applies generic slop checks plus a
  profile for each stack layer the diff touches (currently Python and agent
  skills/instructions), and warns when a touched layer has no profile.
- **Optional enforcement hooks**, installed at user level:
  - a slop-scan pre-commit hook that blocks TODO/FIXME markers, skipped or
    focused tests, blanket lint/type suppressions and debugger calls in staged
    code, then runs the repository's own pre-commit hook;
  - an agent commit gate for Claude Code and Codex that blocks an agent's
    `git commit` until the commit procedure is loaded in that turn; in
    Claude Code it also keeps a MiniMe turn from ending without a
    recommended next action.
- **Audits**: check host registration, confirm a project carries no MiniMe
  trace, and scan your local agent transcripts for skill misfires and token
  cost. Nothing is collected or sent anywhere.

## Installation

Requirements: Python 3.14+ (standard library only) and at least one agent host
whose user skill directory exists:

| Host | Skills root |
|---|---|
| Codex | `~/.codex/skills` |
| Claude Code | `~/.claude/skills` |
| OpenCode | `~/.config/opencode/skills` |
| GitHub Copilot | `~/.copilot/skills` |

```sh
git clone <repository-url> MiniMe
cd MiniMe

scripts/minime doctor                 # print version, runtime and status
scripts/minime skills install         # dry run: shows what would be written
scripts/minime skills install --write # install into every existing host root

# Confirm each host you use
scripts/minime host-registration-audit --skills-root ~/.claude/skills
scripts/minime host-registration-audit --skills-root ~/.codex/skills
```

Every command is read-only unless you pass `--write`. Installation copies each
skill into a wrapper directory named for the skill, with a regular `SKILL.md` and generated
host metadata. Re-run `skills install --write` after `git pull` to refresh it.
Start a new agent session afterwards so the host discovers the skills.

### Optional hooks

```sh
scripts/minime git-hook install --write     # global slop-scan pre-commit hook
scripts/minime claude-hook install --write  # Claude Code commit gate
scripts/minime codex-hook install --write   # Codex commit gate
```

- `git-hook` sets the global `core.hooksPath` and refuses to replace one that
  points elsewhere. Exempt paths with the `-slop-scan` git attribute; bypass a
  single commit with `SLOP_SCAN=off` or `--no-verify`. Repositories that set
  their own `core.hooksPath` (husky, pre-commit) are not covered.
- Codex runs a user-level hook only after you trust it in `/hooks`.
- `uninstall --write` removes each hook again.

## Using MiniMe in a project

Talk to your agent as usual. Hosts pick skills from their descriptions, and you
can name one explicitly: "use minime-replan", `/minime-replan` in Claude Code
or `$minime-replan` in Codex. Skills work from the project's own guide
(`AGENTS.md`, `CLAUDE.md`), requirements and plan; MiniMe never adds files of
its own to the project.

### Start here: the orchestrator

`minime` is the root skill for development work. When a
task spans more than one step, or you just want to know what to do next, start
with it:

- "What next?" or "use minime to add CSV export"
- It classifies the request, runs intake triage on changes of direction, picks
  the skill chain (spec, decisions, plan, implementation, review, commit), and
  enforces the quality gate at each transition.
- It keeps a ledger of each required step and does not report the work
  complete while any step is still pending.
- **Autopilot:** if you explicitly authorize continued autonomous work, it
  repeats the select, plan, implement, validate, commit loop. It stops for
  unsettled product, architecture, safety or privacy decisions, destructive
  or paid actions, and failures outside the current slice.

Go to a specific skill directly only when the task clearly needs that one
skill, as in the table below.

### Common workflows

| Situation | Start with | What happens |
|---|---|---|
| Multi-step work, or "what next?" | `minime` | Routes the request through the right skill chain with gates between phases. |
| New project from an idea | `minime-project-inception` | Interview on purpose, users, scope and success criteria; creates the project guide, requirements and first milestone. |
| Entering an existing project cold | `minime-orient` | Reads guide, plan, latest checkpoint and git state; returns a verified briefing and next-action options. |
| Inherited or drifted project | `minime-project-reassessment` | Judges goals, docs, design, code and tests; produces a prioritized repair plan. |
| "What should I work on next?" | `minime-implementation-step-selector` | Picks the next concrete slice from the docs and repo state. |
| New feature or a change of direction | `minime-course-correction-triage` | Checks the request against accepted decisions, traces impact, challenges value and tests whether it can work as stated before any code, scaled to risk: one line for a low-risk change. |
| Priorities shifted mid-project | `minime-replan` | Updates only the affected plan artifacts and selects the next slice. |
| Bug or failing test | `minime-systematic-debugging` | Root cause first, fix second. |
| Change is ready | `minime-project-commit` | Runs doc sync, scope check, simplification, review and verification, then shapes the commit. |
| Docs drifted from code | `minime-doc-sync` | Syncs the latest changes, checks one document, or sweeps the whole doc set. |

Typical loop for a feature, which the orchestrator runs for you: triage the
request, select the step, implement, then commit through
`minime-project-commit`, which runs the gates.
Documentation-only changes that touch no requirement, decision or safety text
get a lighter gate tier automatically.

### Core skills

You invoke these directly.

| Area | Skills |
|---|---|
| Root entry point | **`minime`** |
| Start and orient | `minime-project-inception`, `minime-orient`, `minime-project-reassessment` |
| Define | `minime-requirements-manager`, `minime-project-spec` |
| Plan and route | `minime-implementation-step-selector`, `minime-replan`, `minime-course-correction-triage`, `minime-plan-review` |
| Build and fix | `minime-systematic-debugging`, `minime-code-reviewer` |
| Keep docs true | `minime-doc-sync`, `minime-agents-md-audit`, `minime-design-simplifier` |
| Ship | `minime-project-commit` |

### Workflow skills

Other skills and gates call these, so you rarely need them by name. Each can
still be invoked on its own.

| Skill | Called by / used for |
|---|---|
| `minime-decision-prompt` | Every skill that needs your choice: named options with pros, cons and impact. Only called by other skills. |
| `minime-scope-boundary`, `minime-code-simplifier`, `minime-verification-gate` | Commit gates. |
| `minime-doc-check` | `minime-doc-sync`'s diff scope: reports stale docs without editing; forked on a cheaper model in Claude Code. |
| `minime-claim-verifier`, `minime-phase-quality-guard` | Plan review and phase transitions. |
| `minime-impact-analyzer` | Triage and replanning, to trace a change across docs and code. |
| `minime-project-adr`, `minime-project-milestone`, `minime-system-updater`, `minime-validation-planner` | Writing decisions, milestones, architecture and test plans during inception and replanning. |
| `minime-context-handoff` | Handoffs between sessions or agents. |

## Audits

```sh
# Is MiniMe installed and current on a host?
scripts/minime host-registration-audit --skills-root ~/.codex/skills --json

# Does a project carry any MiniMe trace?
scripts/minime transparent-audit --repo /path/to/project --json

# Did agents skip skill steps, and what did MiniMe turns cost?
scripts/minime transcript-audit --since 2026-01-01
```

`transcript-audit` reads local Claude Code and Codex transcripts, prints
counts with `project-N` placeholders, and never prints paths or message text.
Its findings are heuristics; verify one before acting on it.

## Known Limits

- Skills are natural-language procedures. Hooks and audits make the important
  rules checkable, but no host guarantees an agent follows every step.
- Registration checks prove the files are in place, not that a fresh host
  session discovered and used them.
- Review strength follows the model that runs it. With MiniMe installed,
  Claude Code runs the reviewer on Sonnet whatever your session model. Codex
  runs it on your session model: on the cheaper `gpt-6-luna`, review missed
  one or two planted defects in twenty per run, where the default model
  missed none, so a commit gate on that model can pass a defect.
- `transparent-audit` detects MiniMe references, skill names and symlinks; it
  does not detect renamed copies of skill text.
- `skills install --write`, `git-hook install|uninstall --write` and
  `claude-hook|codex-hook install|uninstall --write` are the only write
  commands, all at user level; everything else is read-only. Installation
  prevalidates every destination, but there is no automated rollback.

## Documentation

- [CLI reference](docs/cli.md), [JSON reports](docs/reports.md) and
  [troubleshooting](docs/troubleshooting.md)
- [Developer guide](docs/development.md) for working on MiniMe itself
- [Requirements](docs/requirements.md), [architecture](docs/concepts.md),
  [decisions](docs/decisions.md) and [plan](docs/implementation-plan.md)
