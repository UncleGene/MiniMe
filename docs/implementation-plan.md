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
- One host-capability table (`HOSTS` in `scripts/minime`) drives install,
  audits, `review-eval` and hooks; a test adds a hypothetical host through it
  alone (REQ-011).
- User-level enforcement: the slop-scan git hook and the agent commit gate for
  Claude Code and Codex. These and skill installation are the only CLI writes.
- `transcript-audit` reports skill loads, tokens and their list-price cost
  (also per gated commit turn, including its subagents), slop-scan and
  blocking-review gate blocks, and observable contract misfires from local
  transcripts, excluding `review-eval` runs.
- Full test, lint, type, documentation and review gates must pass before every
  commit. Commands are in [the developer guide](development.md).

## Review baseline

All fixtures (standard and hard tiers), each host's default model and effort:

| Host | Python defects | Agent-skills defects | Control false positives | Uncovered warning |
|---|---|---|---|---|
| Claude Code (Opus 5.5) | 13/13 | 7/7 | 0/3 | 1/1 |
| Codex (gpt-6.1-sol, medium) | 13/13 | 7/7 | 0/3 | 1/1 |

Hard tier on a cheaper model:

| Host / model | Defects | Control false positives |
|---|---|---|
| Claude Code / Sonnet 5.5 | 6/6 | 0/1 |
| Codex / gpt-6-luna | 5/6 (missed `hard-buried-boundary`) | 1/1 (CSV formula injection, debatable) |

Budget configuration (Decision 2 amendment of 2026-10-30), 2026-10-30. On
Claude Code the reviewer forks to Sonnet 5.5 whatever the session model, so
the forked result below covers a cheapest-plan session. On Codex the reviewer
runs on the session model. `gpt-6-luna` on all fixtures missed
`swallowed-error` and `hard-vacuous-test`; a standard-tier rerun, made for two
unparsed replies, found `swallowed-error`, which does not change the full
run's result. Across its three runs `luna` missed three different defects
(with `hard-buried-boundary` above) and flagged the CSV formula-injection
control on both hard runs. This fails the pass threshold. The user accepted it
as an exception on 2026-10-30, for Codex on `gpt-6-luna` only: the scattered
misses suggest model capacity rather than a reviewer gap a checklist would
close. Rerun it when the reviewer, a profile or the Codex budget model
changes; the exception ends when that run passes.

With the installed adapter, Claude Code's reviewer forked on Sonnet 5.5 found
20/20 defects across both tiers, with 0/3 control false positives and 1/1
uncovered warning. One run of `hard-two-defects` found only one of its two
defects; the rerun found both. Runs that hit a host limit exit non-zero and
count as `unparsed`; rerun those fixtures.

The report-only diff audit of `minime-doc-sync`, now `minime-doc-check`
(`--skill doc-check`, both tiers, 2026-10-25), found 8/8 planted stale lines
with 0/2 control false positives on the session model (Opus 5.5) and on Sonnet
5.5 alike, so these fixtures meet the fork bar but do not yet tell the tiers
apart.

The pass threshold is 100% detection, no false positives and every warning
shown. A defect the review finds anywhere blocks, so control projects must be
genuinely clean; repeat runs of one control can still differ between clean
and a borderline finding. The eval measures review misses on synthetic cases,
not how often agents write slop, so treat it as an instrument for cost
decisions: run it when the reviewer or a profile changes, or before a routing
change.

Cost and misfire baselines come from the maintainer's local transcripts; the
raw transcript and review reports are never committed (Decision 8), while the
plan records their aggregates. Compare `transcript-audit` runs of the same
host over time; a cheaper routing must not raise the misfire counts.

## Next implementation step

Measure the forked `minime-doc-check` as the reviewer fork was measured: after
enough gated commit turns, compare priced cost per gated commit turn, main
context plus subagents, and the misfire counts with the turns before the fork
(Decision 14 amendment of 2026-10-25). Keep the fork if cost falls and misfires
do not rise; otherwise fold the audit back into `minime-doc-sync`.

`no-next-action` misfires on Claude Code rose from 3 in the 31 MiniMe turns
before the reviewer fork to 20 in the 37 after it. With the `Stop` hook
installed (Decision 13), audits from 2026-10-21 to 2026-10-25 show 1 in 27.
Codex has no such hook and showed 18 in 67 turns in the same period.

The forked reviewer was measured on 2026-10-20 (Claude Code, list price, main
context plus subagents, MiniMe counted as a target project). Before the fork,
15 gated commit turns in three projects cost a median $1.52 (mean $2.51); after
it, 28 turns in four projects cost a median $3.28 (mean $6.14). Turns whose
review passed stayed flat at a median $1.50. The rise sits in the 17 turns with
a blocking review (median $5.18), as fix work and re-review; the reviewer
subagent averaged $0.28 per turn. Of 31 blocking verdicts since the fork, 27
held real defects, 4 were borderline and none was noise. The fork stays,
because its blocks are real defects and quality ranks above cost (Decision 1).
Verification does not move to a fresh context, because the fork showed no
saving to copy.

## Open milestones

Run them in this order. Each milestone is accepted when its check passes, along
with the full project gates.

| Milestone | Goal | Acceptance |
|---|---|---|
| Model and effort routing | Claude Code review forks on the fast tier and stays (measured above). Tiers were re-derived on 2026-10-20 (Decision 14 amendment); stale-doc fixtures passed on the fast tier and `minime-doc-check` now forks, on probation until its cost is measured; next, measure it (REQ-010, Decision 14). Every routing change, including a cheaper model or effort level, needs a feasibility and benefit check first: what it saves, measured, against the detection it risks (Decision 15). Budget-configuration detection is measured (above): Claude Code passes; Codex on `gpt-6-luna` is an accepted exception. Cost per gated commit on a cheapest-plan session is not yet measured. | Transcripts show review running on the declared tier on each verified host; priced cost per gated change, main context plus subagents, falls; fixture detection holds; misfire counts do not rise; cost per gated commit is reported for a cheapest-plan session on each verified host. |
| Scale ceremony to risk | Implemented: intake and questions scale with one risk scale, `minime-decision-prompt` explains new mechanisms and costs before the options (Decision 16), and `minime-implementation-step-selector` delegates the gate chain to `minime-project-commit` instead of restating it (REQ-010). Next, measure. | Cost and detection measurements do not regress. |
| More stack profiles (lower priority) | Profiles and fixtures in order of recorded demand: sessions outside MiniMe and review-eval whose review reported the stack uncovered, counted on 2026-10-25. Ruby with Rails and ERB first (18 and 17 sessions), then Lua (16), then JavaScript (10). TypeScript (3), React and Vitest (0) wait until the warnings show demand; their marker rows in `stacks.md` stay so the warnings keep counting (Decision 11). | Each layer's fixtures meet the pass threshold on both verified hosts. |

## Temporary instrumentation

These `transcript-audit` outputs gather evidence for open milestones and are
removed, with their tests and docs, when the condition holds. The agent hooks,
`review-eval` and the misfire findings are lasting functionality and stay.

| Output | Serves | Remove when |
|---|---|---|
| Cost per gated commit turn, main context plus subagents | Model and effort routing | That milestone is accepted |
| Slop-scan and blocking-review gate-block counts | Judging the reviewer fork by its blocks | Model and effort routing is accepted |
| Tokens and list-price cost per skill and per model/effort | Model and effort routing; Scale ceremony to risk | Both milestones are accepted |

## Plan maintenance

Update status, the next step and open milestones in the same commit as the
implementation. Remove a milestone when it is done; its result belongs in the
current-state list above. Change decisions in place in
[decisions](decisions.md). No separate state pin or traceability matrix is
used.
