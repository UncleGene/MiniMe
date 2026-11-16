# MiniMe Implementation Plan

This plan owns current status and next steps. [Requirements](requirements.md)
define behavior, [concepts](concepts.md) describes the architecture and
[decisions](decisions.md) record accepted direction (goals: Decision 1).
Codex and Claude Code are verified hosts; OpenCode and GitHub Copilot are
supported (Decision 4). Python 3.14+ is required for the CLI and tests.

## Current state

- 30 reusable skills and 2 internal skills, installed at user level on all
  four host roots by `scripts/minime skills install --write`.
- Review applies generic slop checks plus layer profiles for Python and agent
  skills/instructions; `review-eval` scores the installed reviewer on
  planted-defect fixtures, with a standard and a hard tier, and
  `--skill doc-check` scores `minime-doc-check` on planted stale-doc fixtures.
- In Claude Code, `minime-code-reviewer` and `minime-doc-check` (the diff audit
  that `minime-doc-sync` calls) run in forked subagents on Sonnet 5.5
  (Decision 14); other hosts run them inline on the session model.
- Intake and questions scale with one risk scale (Decision 16).
- One host-capability table (`HOSTS` in `scripts/minime`) drives install,
  audits, `review-eval` and hooks; a test adds a hypothetical host through it
  alone (REQ-011).
- User-level enforcement: the slop-scan git hook and the agent commit gate for
  Claude Code and Codex. These and skill installation are the only CLI writes.
- Claude Code question hooks (Decision 13) accepted 2026-11-16: in the week
  after install, local transcripts show no multi-question choice-UI call
  reaching the user in a MiniMe session (baseline 11 of 187; the hook blocked
  2) and `prose-question` findings down from 3 to 0.
- `transcript-audit` reports skill loads, token counts and observable contract
  misfires from local transcripts, excluding `review-eval` runs. Pricing and
  cost per gated commit are measured with the maintainer's local tooling, which
  is not published (Decision 10).
- Full test, lint, type, documentation and review gates must pass before every
  commit. Commands are in [the developer guide](development.md).

## Review baseline

All fixtures (standard and hard tiers), each host's default model and effort,
last matched on 2026-11-07:

| Host | Python defects | Agent-skills defects | Control false positives | Uncovered warning |
|---|---|---|---|---|
| Claude Code (Opus 5.5) | 13/13 | 7/7 | 0/3 | 1/1 |
| Codex (gpt-6.1-sol, medium) | 13/13 | 7/7 | 0/3 | 1/1 |

Hard tier on a cheaper model:

| Host / model | Defects | Control false positives |
|---|---|---|
| Claude Code / Sonnet 5.5 | 6/6 | 0/1 |
| Codex / gpt-6-luna | 5/6 (missed `hard-buried-boundary`) | 1/1 (CSV formula injection, debatable) |

Budget configurations (Decision 2): on Claude Code the reviewer forks to Sonnet
5.5 whatever the session model, and found 20/20 defects across both tiers with
0/3 control false positives and 1/1 uncovered warning. On Codex the reviewer
runs on the session model; `gpt-6.1-sol` passes (table above), while
`gpt-6-luna` misses different defects from run to run and fails the pass
threshold, so a luna session weakens its own commit gate (README, Known
Limits).

`--skill doc-check` (both tiers) finds 8/8 planted stale lines with 0/2 control
false positives on Opus 5.5 and Sonnet 5.5 alike; these fixtures do not yet
tell the tiers apart.

The pass threshold is 100% detection, no false positives and every warning
shown. A defect the review finds anywhere blocks, so control projects must be
genuinely clean; repeat runs of one control can still differ between clean
and a borderline finding. Runs that hit a host limit exit non-zero and count
as `unparsed`; rerun those fixtures. The eval measures review misses on
synthetic cases, not how often agents write slop, so treat it as an instrument
for cost decisions: run it when the reviewer or a profile changes, or before a
routing change.

Cost and misfire baselines come from the maintainer's local transcripts; the
raw transcript and review reports are never committed (Decision 8), while the
plan records their aggregates. Compare runs of the same host over time; a
cheaper routing must not raise the misfire counts.

## Next implementation step

Measure the fresh-session nudge, installed on 2026-11-16: after 2026-11-23,
run the local cost audit and `transcript-audit` against its acceptance check.
Misfire baseline, 2026-11-10 to 2026-11-16 (turns cut off mid-tool are no
longer counted as `no-next-action`): Claude Code `no-next-action` 1,
`prose-question` 0, `commit-unverified` 119 (101 in one project); Codex
`no-next-action` 6, against 1 the week before (Codex has no Stop hook).

## Cost baseline

The local cost tooling attributes each gated turn to its session model, the
main-context model that wrote most of its output. List price, subagents
included, 2026-11-01 to 2026-11-07, excluding a test-less content repo:

| Session model | Gated turns | Median per turn | Median per shell command |
|---|---|---|---|
| Claude Code, Opus 5.5 (Pro; Max after the Fable cap) | 59 | $2.27 | $0.120 |
| Claude Code, Fable 5.1 (Max) | 14 | $3.86 | — |
| Codex, `gpt-6.1-sol` (below the ~15-turn target) | 12 | $0.24 | $0.015 |

Compare cost per command as well as per turn: a turn that runs more checks
costs more without costing more per unit of work.

Misfires in MiniMe turns over the same window, excluding the content repo:
Claude Code `commit-unverified` 10 and `no-next-action` 3 in 65; Codex
`no-next-action` 1 and `commit-unverified` 0 in 55, 18 of them copies a resumed
session writes again.

Opus 5.5 cost by context size per request, Claude Code, 2026-11-07 to
2026-11-14, all projects: under 300k tokens 33.5%, 300k–600k 36.5%, over 600k
30.1%. Resumes after more than an hour idle re-cached 10.2M tokens, about 5%
of Opus cost. Median cost per gated Opus 5.5 commit turn in the same window:
$3.59 over 218 turns, content repo included, so not comparable with the
table above; the nudge's acceptance compares against this figure
(Decision 17).

## Open milestones

Run them in this order. Each milestone is accepted when its check passes, along
with the full project gates.

| Milestone | Goal | Acceptance |
|---|---|---|
| Fresh-session nudge | In Claude Code, an agent hook recommends a handoff, `/clear` and `minime-orient` when the last request's context exceeds about 300k tokens after a commit (the Stop hook, shared with the post-commit menu, returns the turn once per commit) or on the first prompt after more than an hour idle (a new `UserPromptSubmit` hook adds context); it never blocks a tool call or a commit (Decision 17). Installed 2026-11-16. | Hook tests cover both triggers, the threshold boundary, silence below it and one Stop return per commit with no loop; after a week installed, the local cost audit shows the share of Opus cost above 300k context below the 67% baseline (Cost baseline), and neither the median cost per gated turn nor the misfire counts rise. |
| Post-commit menu and prose choices | Commits in a compacted session ended without the post-commit "what next?" menu that `minime-project-commit` requires, and options came as prose ("type X to choose") instead of the choice UI. Decide (open, for `minime-decision-prompt`): whether a hook enforces the menu and how autopilot's commit-and-continue loop is exempted; whether the menu offers "Stop and reflect" after N commits since the last reflection, and the value of N. The menu-enforcement and prose-choice checks both judge how a MiniMe turn ends, so they share the Stop hook. In scope: `transcript-audit` finding kinds for a post-commit turn without a menu and for a prose choice. | The new finding kinds exist with tests, prose-choice false-positive samples pass, and hook cases cover the enforcement, if any, and the exemption the decision chose; after install, `transcript-audit` shows neither finding kind. |
| More stack profiles (lower priority) | Profiles and fixtures in order of recorded demand: sessions outside MiniMe and review-eval whose review reported the stack uncovered, counted on 2026-10-25. Ruby with Rails and ERB first (18 and 17 sessions), then Lua (16), then JavaScript (10). TypeScript (3), React and Vitest (0) wait until the warnings show demand; their marker rows in `stacks.md` stay so the warnings keep counting (Decision 11). | Each layer's fixtures meet the pass threshold on both verified hosts. |

## Candidate skill changes

Ideas from the public `compound-engineering-plugin` (`ce-plan`, `ce-brainstorm`)
that were not adopted with the inception interview rules. Each goes through
`minime-course-correction-triage` before any edit, must add no lookup or
subagent, and has no evidence yet that it improves quality.

- Considered-and-not-built record (check first): build an unrequested guard
  only when its absence causes harm nobody would catch in time or adding it
  later is expensive; list each rejected concern as a one-line non-goal. Check
  overlap with `minime-design-simplifier` and `minime-code-reviewer`; at most
  three lines.
- Open-ended fact-finding questions: ask facts only the user knows without
  invented options. Conflicts with Decision 13; needs a user decision.
- Two "you decide" answers in a row: state the default and record it as an
  assumption. Likely covered by `minime-decision-prompt` "Default if no reply";
  confirm before adding.
- Duplicate-tool check in inception: ask what existing tools the user knows
  of and mark the answer unverified.

## Candidate install changes

User requests, not scheduled. Each goes through
`minime-course-correction-triage` before any edit.

- Link instead of copy where no host needs a copy: Codex needs regular files
  and `agents/openai.yaml` (code comment in `HOSTS`; not re-tested since), and
  Claude Code needs the fork frontmatter on `minime_context: fresh` skills.
  Every other installed `SKILL.md` is byte-identical to its source (checked
  2026-11-10), so Claude Code's other skills and all OpenCode and GitHub
  Copilot skills could be symlinks into the clone, letting `git pull` update
  them. First verify that each of those hosts loads symlinked skills; then the
  installer must link them and `host-registration-audit` must accept the
  links, which it now blocks on every root. New, renamed or forked skills
  still need `skills install --write`.
- Per-project install (for example `<project>/.claude/skills`): not supported.
  It puts MiniMe files in a consuming repo, which Decision 3 and REQ-002
  forbid, so it needs that decision changed first. Today
  `skills install --skills-root` accepts any existing folder, including one
  inside a project, and maps it to a host by path suffix; nothing refuses it.

## Plan maintenance

Update status, the next step and open milestones in the same commit as the
implementation. Remove a milestone when it is done; its result belongs in the
current-state list above. Keep only what continuing work needs: a newer
measurement replaces its baseline, and git history holds achieved items and
past measurements. Change decisions in place in
[decisions](decisions.md). No separate state pin or traceability matrix is
used.

Costing and evaluation track the hosts' published models and must be
refreshed when they change: add a new model's published list price to the
maintainer's local cost tooling (its unpriced-models line is the signal; never
guess a price), and when a verified host's default or
budget model changes, rerun the review-eval baseline on it and update the
baseline tables above (Decisions 9 and 14).
