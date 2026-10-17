# MiniMe Implementation Plan

This plan owns current status and next steps. [Requirements](requirements.md)
define behavior, [concepts](concepts.md) describes the architecture and
[decisions](decisions.md) record accepted direction (goals: Decision 1).
Codex and Claude Code are verified hosts; OpenCode and GitHub Copilot are
supported (Decision 4). Python 3.14+ is required for the CLI and tests.

## Current state

- 28 reusable skills and 2 internal skills, installed at user level on all
  four host roots by `scripts/minime skills install --write`.
- Review applies generic slop checks plus layer profiles for Python and agent
  skills/instructions; `review-eval` scores the installed reviewer on
  planted-defect fixtures, with a standard and a hard tier.
- In Claude Code, `minime-code-reviewer` runs in a forked subagent on Sonnet
  5.5 (Decision 14); other hosts run it inline on the session model.
- User-level enforcement: the slop-scan git hook and the agent commit gate for
  Claude Code and Codex. These and skill installation are the only CLI writes.
- `transcript-audit` reports skill loads, token cost and observable contract
  misfires from local transcripts.
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

With the installed adapter, Claude Code's reviewer forked on Sonnet 5.5 found
20/20 defects across both tiers, with 0/3 control false positives and 1/1
uncovered warning. One run of `hard-two-defects` found only one of its two
defects; the rerun found both. Runs that hit a host limit exit non-zero and
count as `unparsed`; rerun those fixtures.

The pass threshold is 100% detection, no false positives and every warning
shown. A defect the review finds anywhere blocks, so control projects must be
genuinely clean; repeat runs of one control can still differ between clean
and a borderline finding. The eval measures review misses on synthetic cases,
not how often agents write slop, so treat it as an instrument for cost
decisions: run it when the reviewer or a profile changes, or before a routing
change.

Cost and misfire baselines come from the maintainer's local transcripts and
are not published (Decision 8). Compare `transcript-audit` runs of the same
host over time; a cheaper routing must not raise the misfire counts.

## Next implementation step

Measure the effect of the forked reviewer: compare main-context tokens per
gated commit in `transcript-audit` before and after it, on Claude Code. If they
fall and the misfire counts hold, move verification to a fresh context the same
way; otherwise revisit the fork.

## Open milestones

Run them in this order. Each milestone is accepted when its check passes, along
with the full project gates.

| Milestone | Goal | Acceptance |
|---|---|---|
| Model and effort routing | Have `transcript-audit` count slop-scan blocks and blocking review verdicts alongside framework misfires. Claude Code review already forks on the fast tier. Measure its token effect; run verification in a fresh fast-tier context; re-derive each skill's tier (REQ-010, Decision 14). | Transcripts show review running on the declared tier on each verified host; main-context tokens per gated change fall; fixture detection holds; misfire counts do not rise. |
| Scale ceremony to risk | Tier intake and question handling by risk; in `minime-decision-prompt`, explain any new mechanism or cost before showing the options; drop repeated chain text where a gate is delegated (REQ-010). | Token and detection measurements do not regress. |
| Host-capability table | One table gives each host's root, transcripts, choice UI, subagent, model and effort mechanism, headless command, read-only flags and hooks; the installer and audits read it (REQ-011). | A hypothetical host is added through the table alone in a test; all four roots still pass the audit. |
| Cross-agent second opinion | An optional second opinion from the other verified host, triggered by risk and spare quota, with a same-host or skip fallback (REQ-012, Decision 15). | On the fixtures, detection rises at an accepted cost; a test shows the fallback when the host is unavailable. |
| More stack profiles (lower priority) | Profiles and fixtures for Ruby, Rails, TypeScript/JavaScript, React and Vitest (Decision 11). | Each layer's fixtures meet the pass threshold on both verified hosts. |

## Plan maintenance

Update status, the next step and open milestones in the same commit as the
implementation. Remove a milestone when it is done; its result belongs in the
current-state list above. Change decisions in place in
[decisions](decisions.md). No separate state pin or traceability matrix is
used.
