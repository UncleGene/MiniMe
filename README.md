# MiniMe

MiniMe is a library of engineering skills for AI coding agents. You install it
once for your user account, and every project you open in Codex, Claude Code,
OpenCode or GitHub Copilot can use it. Your projects stay free of MiniMe files.

It is built for one developer directing agents on a budget plan: a strict
quality bar keeps agent-written slop from piling up cost and complexity, and
keeps a project you may later share or open-source fit to show.

## Goals

1. **Production quality without babysitting.** Agents meet an explicit
   anti-slop bar, so you are not the one catching invented APIs, stubbed
   code, weakened tests, swallowed errors or skipped checks.
2. **Cost-appropriate execution.** Spend tokens, model tier and effort where
   they matter, never at the expense of quality.
3. **Portability.** Codex and Claude Code are verified hosts, covered by
   review fixtures, transcript audits and commit hooks. OpenCode and GitHub
   Copilot are supported hosts that install the same skills.

## What you get

- **30 skills** covering the development loop: starting and orienting in a
  project, requirements and specs, planning and replanning, choosing the next
  step, debugging, review, simplification, keeping docs in sync, commits and
  pre-publish cleanup. Every skill follows the same interaction rules: it
  argues choices instead of guessing silently, shows evidence before calling
  work done, and ends each response with a recommended next action.
- **Layered code review.** The reviewer applies general slop checks plus a
  profile for each stack the change touches (currently Python, and agent
  skills and instructions). It warns you when a touched stack has no profile.
- **Optional enforcement hooks**, installed for your user account:
  - a **slop-scan pre-commit hook** that blocks TODO/FIXME markers, skipped
    or focused tests, blanket lint or type suppressions and debugger calls
    in staged code;
  - an **agent commit gate** for Claude Code and Codex that stops an agent's
    `git commit` until it has loaded the commit procedure and its checks. In
    Claude Code it also makes the agent end each MiniMe turn with a next
    action and ask choices through the choice dialog.
- **Audits** that check host installation, confirm a project carries no
  MiniMe trace, and scan your local agent transcripts for skipped steps.
  Nothing is collected or sent anywhere.

## Installation

You need Python 3.14+ (standard library only) and at least one agent host
whose user skills folder exists:

| Host | Skills folder |
|---|---|
| Codex | `~/.codex/skills` |
| Claude Code | `~/.claude/skills` |
| OpenCode | `~/.config/opencode/skills` |
| GitHub Copilot | `~/.copilot/skills` |

Clone MiniMe once, anywhere you like, and install from that clone:

```sh
git clone <repository-url> MiniMe
cd MiniMe

scripts/minime doctor                 # show version, Python and status
scripts/minime skills install         # dry run: list what would be written
scripts/minime skills install --write # install into every host folder that exists

# Confirm each host you use
scripts/minime host-registration-audit --skills-root ~/.claude/skills
scripts/minime host-registration-audit --skills-root ~/.codex/skills
```

Then start a new agent session so the host picks up the skills. Every command
is read-only unless you pass `--write`.

### Updating

The clone is the single source. To update, pull and reinstall:

```sh
git pull && scripts/minime skills install --write
```

The installer copies each skill into the host folders instead of linking to
the clone, for two reasons:

- **Codex** does not load a symlinked skill file, and it needs a generated
  `agents/openai.yaml` next to each skill.
- **Claude Code** gets a modified copy of two skills, `minime-code-reviewer`
  and `minime-doc-check`: the installer adds settings that run them as a
  subagent on a cheaper model.

The other Claude Code skills, and all OpenCode and GitHub Copilot skills, are
identical to the clone. Linking those instead of copying them is a candidate
in the plan, not yet available.

MiniMe installs only for your user account. There is no per-project install,
because MiniMe never writes into your projects.

### Optional hooks

```sh
scripts/minime git-hook install --write     # slop-scan pre-commit hook for all repos
scripts/minime claude-hook install --write  # Claude Code commit gate
scripts/minime codex-hook install --write   # Codex commit gate
```

- `git-hook` sets git's global `core.hooksPath` and refuses to replace one
  that already points elsewhere. It runs each repository's own pre-commit hook
  after its scan. Repositories that set their own `core.hooksPath` (husky,
  pre-commit) are not covered. Exempt paths with the `-slop-scan` git
  attribute; skip one commit with `SLOP_SCAN=off` or `--no-verify`.
- Codex runs a user-level hook only after you trust it in `/hooks`.
- `uninstall --write` removes a hook again.

## Using MiniMe in a project

Talk to your agent as usual. Hosts pick skills from their descriptions, and
you can name one explicitly: "use minime-replan", `/minime-replan` in Claude
Code or `$minime-replan` in Codex. Skills work from the project's own guide
(`AGENTS.md`, `CLAUDE.md`), requirements and plan; MiniMe never adds files of
its own to the project.

### Start here: `minime`

`minime` is the entry point for development work. Start with it when a task
spans more than one step, or when you just want to know what to do next:

- "What next?" or "use minime to add CSV export".
- It classifies the request, checks changes of direction before any code,
  picks the chain of skills (spec, decisions, plan, implementation, review,
  commit) and runs the quality gate between them.
- It keeps a checklist of required steps and does not report the work done
  while any step is still open.
- **Autopilot:** if you explicitly allow continued autonomous work, it repeats
  the select, plan, implement, validate and commit loop. It stops for
  unsettled product, architecture, safety or privacy decisions, destructive
  or paid actions, and failures outside the current step.

Go to a specific skill directly only when the task clearly needs just that
skill, as in the table below.

### Common workflows

| Situation | Start with | What happens |
|---|---|---|
| Multi-step work, or "what next?" | `minime` | Routes the request through the right skills, with checks between phases. |
| New project from an idea | `minime-project-inception` | Interviews you on purpose, users, scope and success criteria; creates the project guide, requirements and first milestone. |
| Entering an existing project cold | `minime-orient` | Reads the guide, plan, latest checkpoint and git state; returns a verified briefing and next-step options. |
| Inherited or drifted project | `minime-project-reassessment` | Judges goals, docs, design, code and tests; produces a prioritized repair plan. |
| "What should I work on next?" | `minime-implementation-step-selector` | Picks the next concrete step from the docs and repo state. |
| New feature or change of direction | `minime-course-correction-triage` | Before any code, checks the request against earlier decisions, traces its impact, questions its value and tests whether it can work. Scaled to risk: one line for a low-risk change. |
| Priorities shifted mid-project | `minime-replan` | Updates only the affected plan documents and picks the next step. |
| Bug or failing test | `minime-systematic-debugging` | Root cause first, fix second. |
| Change is ready | `minime-project-commit` | Runs doc sync, scope check, simplification, review and verification, then writes the commit. |
| Docs drifted from code | `minime-doc-sync` | Syncs docs with recent changes, checks one document, or sweeps them all. |
| Making a repo public | `minime-publish-prep` | Removes personal data, makes docs coherent, shapes the README and tidies history. |

A typical feature loop, which `minime` runs for you: triage the request, pick
the step, implement, then commit through `minime-project-commit`, which runs
the checks. Documentation-only changes that touch no requirement, decision or
safety text get a lighter set of checks.

### All skills

**Skills you call directly:**

| Area | Skills |
|---|---|
| Entry point | `minime` |
| Start and orient | `minime-project-inception`, `minime-orient`, `minime-project-reassessment` |
| Define | `minime-requirements-manager`, `minime-project-spec` |
| Plan and route | `minime-implementation-step-selector`, `minime-replan`, `minime-course-correction-triage`, `minime-plan-review` |
| Build and fix | `minime-systematic-debugging`, `minime-code-reviewer` |
| Keep docs true | `minime-doc-sync`, `minime-agents-md-audit`, `minime-design-simplifier` |
| Ship | `minime-project-commit`, `minime-publish-prep` |

**Skills other skills call.** You rarely need these by name, though each can
run on its own:

| Skill | Used for |
|---|---|
| `minime-decision-prompt` | Every question to you: named options with pros, cons and impact. |
| `minime-scope-boundary`, `minime-code-simplifier`, `minime-verification-gate` | Commit checks. |
| `minime-doc-check` | Reports docs a change made stale, without editing; runs as a cheaper subagent in Claude Code. |
| `minime-claim-verifier`, `minime-phase-quality-guard` | Plan review and phase transitions. |
| `minime-impact-analyzer` | Tracing a change across docs and code during triage and replanning. |
| `minime-project-adr`, `minime-project-milestone`, `minime-system-updater`, `minime-validation-planner` | Writing decisions, milestones, architecture and test plans. |
| `minime-context-handoff` | Handing work between sessions or agents. |

## Audits

```sh
# Is MiniMe installed and current on a host?
scripts/minime host-registration-audit --skills-root ~/.codex/skills

# Does a project carry any MiniMe trace?
scripts/minime transparent-audit --repo /path/to/project

# Did agents skip skill steps?
scripts/minime transcript-audit --since 2026-01-01
```

`transcript-audit` reads your local Claude Code and Codex transcripts and
prints counts only: projects appear as `project-N`, and no paths or message
text are shown. Its findings are heuristics; check one before acting on it.
Add `--json` to any audit for a machine-readable report.

## Known Limits

- Skills are natural-language procedures. Hooks and audits make the important
  rules checkable, but no host guarantees an agent follows every step.
- Installation checks prove the files are in place, not that a fresh host
  session found and used them.
- Review strength follows the model that runs it. With MiniMe installed,
  Claude Code runs the reviewer on Sonnet whatever your session model. Codex
  runs it on your session model: on the cheaper `gpt-6-luna`, review missed
  one or two planted defects in twenty per run, where the default model
  missed none, so a commit gate on that model can pass a defect. Even the
  cheapest ChatGPT plan with Codex includes `gpt-6.1-sol`; use it for
  MiniMe work.
- `transparent-audit` detects MiniMe references, skill names and symlinks; it
  does not detect renamed copies of skill text.
- `skills install --write`, `git-hook install|uninstall --write` and
  `claude-hook|codex-hook install|uninstall --write` are the only write
  commands, all at user level; everything else is read-only. Installation
  checks every destination before writing, but there is no automated
  rollback.

## Documentation

- [CLI reference](docs/cli.md): every command and option.
- [Troubleshooting](docs/troubleshooting.md): error codes and hook problems.
- [JSON reports](docs/reports.md): fields of each `--json` report.
- [Developer guide](docs/development.md): working on MiniMe itself.
- Project records: [requirements](docs/requirements.md),
  [architecture](docs/concepts.md), [decisions](docs/decisions.md) and
  [plan](docs/implementation-plan.md).
