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
- `transcript-audit` reports skill loads, token counts and observable contract
  misfires from local transcripts, excluding `review-eval` runs. Pricing and
  cost per gated commit are measured with the maintainer's local tooling, which
  is not published (Decision 10).
- Model and effort routing was accepted on 2026-11-01: review runs on the
  declared tier on both verified hosts, cost per gated change fell, fixture
  detection held, misfire rates fell, and cost per gated commit is measured per
  budget configuration (cost baseline below).
- Scale ceremony to risk was accepted on 2026-11-07 (measurements under Cost
  baseline): detection held on both hosts, cost per unit of work held or fell,
  and misfires showed no clear rise.
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

Budget configuration (Decision 2 amendment of 2026-10-30), 2026-10-30. The
budget audience spans two Claude Code session models: Opus 5.5, on the Pro
plan (which includes Opus but not Fable) and on the Max plan after its Fable
cap (currently half the plan quota) trips; and Fable, on the Max plan until
then. Cost and detection must hold on both. On Claude Code the reviewer forks
to Sonnet 5.5 whatever the session model, so the forked result below covers
both; the local cost tooling separates them by session model. On
Codex the reviewer runs on the session model, and the cheapest ChatGPT plan
with Codex includes `gpt-6.1-sol`, which passes (table above), so it is
Codex's budget configuration. `gpt-6-luna` is not: across three runs on all
fixtures it missed three different defects (`swallowed-error`,
`hard-vacuous-test`, `hard-buried-boundary`) and flagged the CSV
formula-injection control on both hard runs, failing the pass threshold. The
scattered misses suggest model capacity rather than a reviewer gap, so a luna
session weakens its own commit gate; README's Known Limits warns users.

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
plan records their aggregates. Compare runs of the same host over time; a
cheaper routing must not raise the misfire counts.

## Next implementation step

Make the question rules stick (chosen on 2026-11-07). Drop the six per-option
orchestration ratings the `minime` skill adds, which duplicate
`minime-decision-prompt`'s pros, cons, cost and lock-in. In Claude Code, have
the agent hooks block a choice-UI call that asks more than one question, and
send a MiniMe turn that ends on a prose question back to the choice UI. Of 187
choice-UI calls in 32 MiniMe sessions from 2026-11-01 to 2026-11-07, 11 asked
two or more questions and 80 came in a turn that had not loaded
`minime-decision-prompt` (an upper bound: an earlier turn's copy may still be
in context). Codex keeps the wording only.

## Cost baseline

The local cost tooling attributes each gated turn to its session model, the
main-context model that wrote most of its output. List price, subagents
included, through 2026-11-01:

| Session model | Window from | Gated turns | Median | Mean |
|---|---|---|---|---|
| Claude Code, Opus 5.5 (Pro; Max after the Fable cap) | 2026-10-25 | 113 | $1.19 | $1.88 |
| Claude Code, Fable 5.1 (Max) | 2026-10-25 | 19 | $4.69 | $5.27 |
| Codex, `gpt-6.1-sol` | 2026-10-01 | 69 | $0.78 | $1.21 |

Claude Code's window starts at the doc-check fork; Codex's is longer, because
that Claude-only fork does not affect it. One more Codex turn had no token data
and counts as `unknown`. The Codex row was recounted on 2026-11-07, once the
audit read the `.jsonl.zst` files Codex compresses older rollouts into; it
first showed 12 turns at $1.59 ($2.41). The Fable row merges 13 Fable 5.1 turns
from nine short single-model sessions with 6 earlier Fable 5 turns, repriced at
Fable 5.1's list price (the two differ only in cache-read price): the models
are of similar capability and Fable 5.1 is the current one. The merge used a
one-off run; the tooling itself still reports the two models apart. Fable 5.1
alone shows a $4.69 median over its 13 turns.

Scale ceremony to risk was measured from 2026-11-01 to 2026-11-07 and accepted.
Claude Code's raw cost per gated commit rose (Opus 5.5 median $1.18 to $2.27,
59 turns; Fable 5.1 fell to $3.86 over 14), but each turn ran about 2.5 times
the shell commands (median 9 to 24), and cost per command held: Opus median
$0.120 against $0.122 ($0.105 without a test-less content repo), and $0.111
against $0.102 in the one project with Opus turns in both windows. Codex fell
to a median $0.24 over 12 turns ($0.015 per command against $0.035), accepted
below the ~15-turn target because Codex use was paused.

Misfires: without the content repo, Claude Code `commit-unverified` was 14 in
127 MiniMe turns before and 10 in 65 after, and `no-next-action` 3 and 3,
within chance at these counts; the content repo added 26 `commit-unverified`
flags, none a commit of edited code without a check. Codex showed
`no-next-action` 1 and `commit-unverified` 0 in 55 MiniMe turns (18 of them
copies a resumed session writes again), against 2 and 0 in 21 before.

`review-eval` matched the review baseline on both hosts on 2026-11-07. Its
first Claude Code run left 12 of 23 replies unparsed: the installed `Stop` hook
made each review that ended on its JSON block add a next-action reply, which
`claude -p` printed in place of the review. Eval runs now disable installed
hooks.

The forked `minime-doc-check` was measured on 2026-10-31 (Claude Code, list
price, main context plus subagents, means, because the audit then reported
only totals; the reviewer-fork medians below are not directly comparable).
Before the fork (2026-10-01 to 10-25),
66 gated commit turns averaged $4.99. After it, 114 turns averaged $2.29.
Claude Code `no-next-action` misfires fell from 25 in 101 MiniMe turns to 3 in
135. The fork stays (Decision 14 amendment of 2026-10-25). The fall is not
the fork's alone: the `Stop` hook (Decision 13), the move to Opus 5.5's lower
price and Fable sessions all landed in the same window.

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
| Question rules stick | Drop the duplicate orchestration ratings; Claude Code hooks block multi-question choice-UI calls and bounce prose questions (next step above). | Hook tests pass; after install, `transcript-audit` shows no multi-question calls and fewer `prose-question` findings. |
| More stack profiles (lower priority) | Profiles and fixtures in order of recorded demand: sessions outside MiniMe and review-eval whose review reported the stack uncovered, counted on 2026-10-25. Ruby with Rails and ERB first (18 and 17 sessions), then Lua (16), then JavaScript (10). TypeScript (3), React and Vitest (0) wait until the warnings show demand; their marker rows in `stacks.md` stay so the warnings keep counting (Decision 11). | Each layer's fixtures meet the pass threshold on both verified hosts. |

## Plan maintenance

Update status, the next step and open milestones in the same commit as the
implementation. Remove a milestone when it is done; its result belongs in the
current-state list above. Change decisions in place in
[decisions](decisions.md). No separate state pin or traceability matrix is
used.

Costing and evaluation track the hosts' published models and must be
refreshed when they change: add a new model's published list price to the
maintainer's local cost tooling (its unpriced-models line is the signal; never
guess a price), and when a verified host's default or
budget model changes, rerun the review-eval baseline on it and update the
baseline tables above (Decision 15).
