# Decisions

Accepted architecture and scope decisions. Current requirements live in
[requirements](requirements.md), architecture in [concepts](concepts.md) and
status in [the plan](implementation-plan.md). Change a decision by editing its
entry in the same commit as the change it governs; this file records only the
current position.

## Decision 1 — Project goals

- Status: accepted.
- Context: MiniMe exists so AI coding agents produce work the user does not
  have to audit line by line, without wasting tokens, across the agent hosts
  the user works in. The primary use is single-author vibe coding: the user
  directs and the agent writes nearly all of the code. Slop compounds the cost
  and complexity of later progress and maintenance, and a vibe-coded project,
  MiniMe included, may be shared or open-sourced.
- Decision: three ranked goals.
  - Primary: an explicit anti-slop, production-quality bar that an agent meets
    without the user catching its defects (REQ-003).
  - Secondary: token, model and effort cost (REQ-010). It ranks below quality:
    a cheaper model, a delegation or a lighter gate is accepted only if
    planted-defect detection (Decision 9) holds. Cost means tokens priced by
    model and token type, measured, not assumed: fewer tokens or a smaller
    model can still cost more.
  - Portability across hosts (Decision 4, REQ-011).
- Alternatives: a single "reliable delivery" goal leaves the quality bar
  undefined and cost unmanaged.
- Consequences: requirements, milestones and gate changes are judged against
  these goals in this order.

## Decision 2 — Individual cross-project use

- Status: accepted.
- Context: the skills serve one developer's work across many projects.
- Decision: optimize for an individual developer on a budget plan of each host,
  installing MiniMe at user level. Marketplace, enterprise and
  team-administration infrastructure is out of scope.
- Alternatives: team distribution adds onboarding, migration and support
  obligations without a current need.
- Consequences: validation targets the verified hosts and representative
  tasks; installation correctness and reproducible checks remain required.
  Quality evidence covers each host's budget configuration (plan, Review
  baseline): on Claude Code the Opus 5.5 and Fable session models (the Pro
  plan has Opus 5.5 only; the Max plan runs Fable until its cap, then Opus
  5.5); on Codex `gpt-6.1-sol`, which the cheapest ChatGPT plan with Codex
  includes (`gpt-6-luna` fails review detection and is not a budget
  configuration). MiniMe's own complexity is a standing risk to this audience:
  it must stay reliable and maintainable without taxing target-project progress
  or expense. The DRY/YAGNI invariants and `minime-design-simplifier` passes
  guard it.

## Decision 3 — Host-level consumption, no trace in consuming repos

- Status: accepted.
- Context: skills must reach every project without copying workflow text into
  each one.
- Decision: install shared skills at the host/user level. The MiniMe CLI never
  writes to consuming repositories, and no MiniMe reference, pointer, symlink
  or copied workflow body may land in one. Enforcement that leaves no MiniMe
  trace is acceptable: user-level hooks outside the repo, or neutral
  pre-commit/CI checks an agent adds as authorized project work.
- Alternatives: repo-local installation offers another adoption path but
  couples every project to MiniMe; prose-only enforcement stays probabilistic.
- Consequences: host discovery is an external dependency, and
  `transparent-audit` checks consuming repos for traces.

## Decision 4 — Verified and supported hosts

- Status: accepted.
- Context: hosts differ in skill roots, transcripts, hooks and headless modes,
  and verifying every host equally doubles the work.
- Decision: Codex and Claude Code are verified hosts, covered by fixtures,
  transcript audits and agent hooks. OpenCode, GitHub Copilot and new hosts are
  supported hosts: they install from the same wrappers and get registration
  checks only.
- Alternatives: four equally verified hosts (double the cost); two hosts only
  (drops hosts in active use).
- Consequences: regressions on supported hosts surface later. The
  host-capability table makes adding a host a table entry (REQ-011).

## Decision 5 — Python 3.14+ for tooling

- Status: accepted.
- Context: the skills are Markdown; Python only runs the supporting CLI and
  tests.
- Decision: the CLI and tests require Python 3.14+ and the standard library
  only. Particular-version enforcement is very low priority; no runtime guards
  or compatibility matrix.
- Alternatives: older minimums widen reach but add compatibility work with no
  current need.
- Consequences: the Markdown procedures work without Python.

## Decision 6 — Contract rules travel with skills

- Status: accepted.
- Context: installed wrappers carry only `SKILL.md`, references and metadata,
  and consuming repos may not carry MiniMe guidance (Decision 3). A contract
  kept only in MiniMe's `AGENTS.md` never reaches consumer sessions.
- Decision: every reusable skill ends with an identical `## Interaction rules`
  section carrying the consumer-facing contract.
- Alternatives: a dedicated contract skill keeps one source, but loading it in
  consumer sessions is unverified and adds a hop.
- Consequences: bounded duplication is load-bearing for standalone use; a test
  keeps all copies identical.

## Decision 7 — Gates scale to change size

- Status: accepted.
- Context: running the full gate chain on every commit costs time and tokens
  without catching more on non-normative doc edits.
- Decision: a light tier (doc-sync, scope, simplification, full project
  verification) applies only when every changed file is documentation and no
  requirement, decision, acceptance or safety text changes. Everything else
  runs the full tier (doc-sync, scope, simplification, review, verification,
  commit). When in doubt, use the full tier. The strictest applicable rule
  wins: a user, memory or project-guide rule that requires a check the tier
  skips overrides the tier. Files whose path has the neutral `commit-data` git
  attribute set (records a repository marks, not code or docs) are outside
  the doc, scope, simplifier and review checks, which run on the rest of the
  diff, and the tier is picked from that rest; a commit of data files only
  takes the data tier, which runs only the project's full check. Reflection
  writes a learnings entry only when it produces an action; session
  checkpoints are written only at handoffs.
- Alternatives: any doc change qualifying (requirement edits skip review); a
  diff-size threshold (a one-line safety change skips review). For data: a
  MiniMe-named attribute or config file (leaves a MiniMe trace in the
  consuming repo, Decision 3); detection by file extension (CSV fixtures and
  generated code look like data).
- Consequences: applies to MiniMe (`AGENTS.md`, `minime-self-commit`) and to
  consumers through `minime-project-commit`. The data tier exists only where
  a repository sets `commit-data`; MiniMe sets it nowhere. Data content gets
  no review, only the project's own checks.

## Decision 8 — No personal data or other-project references

- Status: accepted.
- Context: MiniMe is developed by dogfooding on other projects, and records of
  that work can leak names, paths and people.
- Decision: no tracked file or commit message may name or path other local or
  target projects, or carry personal data. Use neutral placeholders
  (`ProductA`, `~/`). Public research sources may be attributed by project,
  not by personal contact. Transcript and review reports are never committed.
- Alternatives: cleaning only current files leaves the data in history.
- Consequences: guard tests check tracked files for home paths and, with the
  untracked `.minime-private-terms` denylist, check files and commit messages
  for private names. Session checkpoints stay local (`docs/sessions/` is
  ignored).

## Decision 9 — Quality evidence from planted-defect fixtures

- Status: accepted.
- Context: registration and structural tests prove only presence; a checkable
  quality bar needs evidence that the skills catch defects.
- Decision: keep a set of diffs with planted defects and controls, organized by
  stack layer. Run review on them headlessly, on demand, on each verified host,
  and report a detection rate. Cost reductions must not lower it. Adoption is
  judged by continued use; matched-task trials, usefulness scorecards and
  automatic telemetry are out of scope.
- Alternatives: transcript heuristics only (cost cuts go unguarded); the
  user's judgment only (makes the user the detector, contradicting Decision 1).
- Consequences: each run spends plan quota; fixtures need upkeep and can be
  overfitted, so they run only before reviewer, profile or routing changes.

## Decision 10 — On-demand transcript audit

- Status: accepted.
- Context: misfires are hard to see: a skill can load and skip a step, or not
  load at all, without visible failure.
- Decision: an on-demand, read-only `transcript-audit` command parses local
  Claude Code and Codex transcripts for MiniMe skill loads, token counts and
  observable contract misfires. Pricing and cost per gated change are
  maintainer-local tooling, not published: they serve
  only MiniMe's own development. Nothing is collected automatically, stored or
  sent; reports use placeholders (Decision 8).
- Alternatives: scripted scenario runs on a sample repo (costly and
  artificial).
- Consequences: findings are heuristics that need verification; host
  transcript formats may change without notice.

## Decision 11 — Layered slop profiles with stateless stack detection

- Status: accepted.
- Context: slop depends on language and framework, and projects mix stacks
  that change over time.
- Decision:
  - Review applies the generic REQ-003 checks plus a profile for each detected
    layer: language, framework, or agent skills and instructions.
  - A marker table in `minime-code-reviewer/references/` maps each layer to its
    marker files and profile; the reviewer and the CLI both read it.
  - The reviewer re-detects layers along the paths the diff touches and stores
    nothing, so no trace is left (Decision 3).
  - A touched layer with no profile produces an in-session warning that only
    generic checks applied.
  - Fixtures follow the same layers. Python and agent skills are covered first.
- Alternatives: one language-agnostic fixture set (misses framework slop); a
  stack list stored per project (leaves a trace and goes stale); automatic
  profile generation (unreviewed drafts could corrupt the detection rate).
- Consequences: the installer ships and audits `references/`. Each review loads
  about 0.5–1k tokens of profiles.

## Decision 12 — User-level slop-scan git hook

- Status: accepted.
- Context: mechanical slop (unfinished markers, skipped or focused tests,
  blanket suppressions, debugger calls) can be caught without judgment, but
  prose rules can be skipped.
- Decision: `scripts/minime git-hook install --write` installs a user-level
  hooks directory and sets the global `core.hooksPath`. Its pre-commit hook
  scans added lines of staged source files by layer, then runs the
  repository's own pre-commit hook; every other standard hook passes through.
  Exemptions use the neutral `-slop-scan` git attribute; single commits bypass
  with `SLOP_SCAN=off` or `--no-verify`. Installing refuses to replace a
  foreign global `core.hooksPath`.
- Alternatives: per-project checks (need setup in each project and drift);
  host hooks only (host-specific, miss manual commits).
- Consequences: works for every host and for manual commits; repositories that
  set their own `core.hooksPath` (husky, pre-commit) are not covered.

## Decision 13 — Agent commit gate on Claude Code and Codex

- Status: accepted.
- Context: transcript audits showed that skipped framework rules are the main
  real-world slop. Agents follow a skill in the turn that loads it, and
  nothing brings it back several turns later: commits ran without the commit
  procedure or its checks, turns dropped the next action, questions lost their
  shape, and a compacted session kept only the hook-checked rules.
- Decision: `scripts/minime claude-hook|codex-hook install --write` copies
  `scripts/commit-gate` to a user-level directory and registers it in
  `~/.claude/settings.json` or `~/.codex/hooks.json`. Sessions that have not
  loaded a MiniMe skill are never blocked. In the others:
  - `PreToolUse` on Bash blocks a `git commit` unless the current turn loaded
    `minime-project-commit` or `minime-self-commit` and the check skills:
    doc-sync (or doc-check), scope-boundary, simplifier and reviewer. A turn
    whose latest line-leading `Commit tier:` statement since its last
    successful commit (in Codex, the turn) says `light` may skip the reviewer. A commit needs no
    skill and no statement when `git check-attr` reports `commit-data` set
    for every staged path other than a `.gitattributes` and the command is
    one of a few exact `git [-C <dir>] commit -m`/`-F` shapes alone in its
    call, so it can only commit the index. The data tier needs no statement
    because the hook often runs before one in the same reply is recorded.
    Messages queued mid-turn are attachments, not new turns, so checks run
    before one still count.
  - Claude Code only: `PreToolUse` on `AskUserQuestion` requires one question
    per call, `Default if no reply:` in the question, `Pros:`, `Cons:` and
    `Locks in:` in each option, and no workflow item cited by number or code
    ("Decision 13", "Q7", "M3") outside an option's `Affects:`.
  - Claude Code only: the `Stop` hook blocks once when a turn that loaded a
    MiniMe skill ends without `Recommended next action:` (progress updates
    included), or when it ends, without having used the choice UI, on a
    question or on a text option list (Decision 19). After a compaction it also blocks each
    stop once until a reply starts a line with `Ledger:`.
  - Claude Code only: on `SessionStart` with the `compact` matcher it reminds
    the agent that the loaded MiniMe skills are still in force.
- Alternatives: a reminder from the slop-scan hook (cannot tell an agent from
  the user); skill wording only (relies on the instruction-following that
  fails); receipt files keyed to the staged tree (the agent writes them
  itself, so they prove no more than the transcript and add a write step to
  every check skill).
- Consequences: one skill read per committing turn. The hooks edit host
  settings, adding or removing only their own entry. The installed hook
  duplicates a little transcript parsing so it runs without the MiniMe repo.
  It proves a skill was loaded and markers are present, not that the skill was
  followed or the content is sound, and it trusts a light or full tier
  statement because it cannot judge a diff; only the data tier is checked
  against the repository. Codex runs it only after the user trusts it in
  `/hooks`, and has no stop, choice-UI or compaction coverage.

## Decision 14 — Installer-generated host adapters

- Status: accepted; implemented for Claude Code review and doc check.
- Context: skills declare `model_tier`; no host reads it directly. Model, effort
  and subagent mechanisms differ by host.
- Decision: skills name a tier and a context (fresh or main) for each step. The
  installer generates a host-specific adapter from the host-capability table,
  as it already generates `agents/openai.yaml`, mapping each tier to that
  host's subagent, model, effort and headless command. A tier takes effect
  only for a fresh-context skill; an inline skill runs on the session model,
  so its tier records the work's difficulty for a later fork. A skill is a
  fork candidate when its input fits an argument, it returns a verdict without
  asking the user mid-procedure, it reads many files, and fixtures show
  detection holds on the fork's tier. A fork stays only while priced cost per
  gated change falls and the misfire counts do not rise (plan, Cost baseline).
- Alternatives: portable prose only (each session guesses the mapping); drop
  `model_tier` (leaves the cost goal without a lever). For the doc audit:
  fork all of `minime-doc-sync` (breaks the questions its other scopes ask);
  fork one scope through new installer metadata (a new adapter mechanism for
  one caller).
- Consequences: the installer grows, and tier mappings, like the
  maintainer's local list-price table, must keep pace with new models and
  prices. A fresh-context skill only forks when its caller invokes it through
  the host's skill mechanism; reading its file runs it inline.
- Current scope: `minime-code-reviewer` and `minime-doc-check` declare
  `model_tier: fast` and `minime_context: fresh`. Into `~/.claude/skills` the
  installer adds `context: fork`, `background: false` and `model: sonnet`;
  other hosts get the source unchanged, because the cheaper Codex model missed
  a hard-tier defect. `minime-doc-check` is the report-only diff audit split
  out of `minime-doc-sync`, whose `diff` scope invokes it through the host's
  skill mechanism and applies or surfaces its findings in the main session, so
  commit gates still name `minime-doc-sync`. Verification stays inline: the
  reviewer fork showed no saving to copy. The mapping lives in the
  host-capability table (REQ-011), so another host gains an adapter by
  declaring its fork entry there.

## Decision 15 — One CLI or agent per session

- Status: accepted.
- Context: MiniMe aims for quality first and cost second (Decision 1). Asking a
  second CLI to review or take over work looked like a way to catch correlated
  blind spots and to spare quota.
- Decision: MiniMe works within the single CLI or agent the session runs in. It
  delegates no work to another host's CLI: no cross-host second opinion or
  offload. Handing a session to a later session or agent
  (`minime-context-handoff`) is unaffected. Cost reduction comes from choosing
  model and effort levels within that host (Decision 14), and each such change
  must first show a measured benefit (REQ-010).
- Alternatives: a cross-host second opinion (the other CLI lacks the session's
  goal and in-chat decisions, so its findings skew to noise the main session
  must argue down); offload to the other CLI when it has quota (local
  transcripts showed Codex, not Claude Code, near its limits, so the premise
  failed).
- Consequences: blind spots stay correlated within one model family; the forked
  reviewer and fixtures are the guard. Codex, Claude Code and the supported
  hosts each still run MiniMe on their own (Decision 4).

## Decision 16 — One risk scale for intake and questions

- Status: accepted; implemented for intake and questions.
- Context: every request paid the full written intake and most choices became
  questions, so a typo fix cost as much ceremony as a requirement change
  (REQ-010).
- Decision: `minime-course-correction-triage` defines three tiers by what a
  change touches, not its size. Low (reversible, local, contradicting nothing
  accepted, and changing no requirement, decision, acceptance, safety,
  security, data-format or public-interface text or behavior) states one intake
  line that says so and records the improvement classification, and a
  reversible choice with a conventional default is stated, not asked. Standard
  states the four intake checks, including a premise check. High runs full
  triage and impact analysis. At any tier, a choice that only places or names
  code (reversible, local, and touching no public interface, data format,
  module boundary or accepted decision) is stated, not asked, and every
  question frames its options by their effect on the user's goals; the rule
  lives in `minime-decision-prompt`.
  When in doubt, the higher tier. `minime-decision-prompt` explains any new
  mechanism or cost before the options. Commit gate tiers (Decision 7) are
  unchanged.
- Alternatives: reuse Decision 7's gate tiers (little saving: small code fixes
  keep full intake); a diff-size
  threshold (a one-line safety change would pass as low).
- Consequences: an agent that misjudges a change as low gives it less intake
  scrutiny; commit gates still review it. Kept only if cost per turn falls and
  fixture detection and the misfire counts do not regress.

## Decision 17 — Nudge toward a fresh session when context grows large

- Status: accepted; implemented in the Claude Code hook.
- Context: every request re-reads the whole conversation from the prompt
  cache, so cost per turn grows with context size (REQ-010). From 2026-11-07
  to 2026-11-14, Claude Code Opus 5.5 requests carrying over 300k context
  tokens drew 67% of Opus list-price cost (over 600k alone: 30%). Resumes after
  more than an hour idle, past Claude Code's one-hour cache lifetime, re-cached
  10.2M tokens, about 5% of Opus cost. A restart pays only if it costs less
  than the reads it saves: a handoff (median $2.34) plus `minime-orient`
  ($0.35 to $1.17, ending at 54k to 130k context) is recovered after 25 to 103
  further requests, depending on context size. Sessions stayed above 300k for
  a median of 139 requests, and 23 to 33 of those 39 stretches ran past
  break-even. The agent cannot see its own context size; the transcript
  records it for each request.
- Decision: in Claude Code, a MiniMe agent hook reads the last request's
  context size from the transcript. When context exceeds about 300k tokens it
  has the agent recommend a handoff (`minime-context-handoff`), then `/clear`
  and `minime-orient`: after a commit, the Stop hook returns the turn once per
  commit with that recommendation; on the first prompt after more than an hour
  idle, a `UserPromptSubmit` hook adds it as context. It never blocks a tool
  call or a commit, and the user runs `/clear`. The 300k threshold and the
  one-hour idle trigger are the defaults the user accepted. Codex is out of
  scope until its transcripts show the same cost pattern.
- Alternatives: habit only (long sessions go unnoticed);
  skill wording only (the agent cannot see its context size); forking
  `minime-project-commit` to a cheaper model (it asks the user after the
  commit and needs main-session context, failing the fork criteria
  in Decision 14).
- Consequences: one more hook to maintain. A fresh session loses working
  memory the handoff does not capture. Kept only if the share of Opus cost
  above 300k context falls and the median cost per gated turn and the misfire
  counts do not rise in the local cost audit; the threshold is revisited with
  that data.

## Decision 18 — "Go" starts autopilot

- Status: accepted.
- Context: in long runs the user answers each recommended next action or
  post-commit menu with "Go" and expects the agent to commit each finished
  block and keep going. The post-commit "what next?" menu stopped every
  commit, and each new turn reloaded the commit skill and its checks.
- Decision: a reply of "go", "go on", "continue" or "proceed" to a
  recommended next action that continues work, or one that selects a
  continue-work option in a next-step choice, authorizes `minime` autopilot
  for the current work list (the plan's or the request's remaining blocks, or
  the list the agent last stated): each finished block is committed and the
  agent continues without stopping until the list is done, an
  autopilot stop condition applies, or the user gives a new direction. Every
  turn still ends with a next action. As an answer to a pending choice, "go"
  approves the recommended option only when it is low-impact, in-repo and
  reversible (`minime-decision-prompt`); a "go" that selects a stop option,
  answers an unsettled decision or needs an explicit pick starts no
  autopilot.
- Alternatives: a menu after every commit (stops runs the user already
  authorized); a dedicated autopilot command (one more thing to type for what
  "Go" already says).
- Consequences: one "go" can produce many commits without review by the user
  between them; the commit gates, the autopilot stop conditions and the
  fresh-session nudge (Decision 17) still apply to each. Guard: "go" never
  approves an option that creates a tracked doc,
  edits the project guide or reaches outside the repo.

## Decision 19 — Choices in the choice UI, no mandatory post-commit menu

- Status: accepted; implemented in the Claude Code Stop hook and
  `transcript-audit`.
- Context: from 2026-11-10 to 2026-11-20, 74% of commit turns outside "go"
  runs in MiniMe sessions ended without the post-commit "what next?" menu
  `minime-project-commit` required, and 33 of those ended on options written
  as a text list the user had to type back; a consuming project's owner
  flagged such lists twice.
- Decision: after a commit the agent ends with a recommended next action;
  only when two or more materially different next steps remain does it ask,
  through `minime-decision-prompt` in the choice UI. The Stop hook blocks
  once a MiniMe turn that, without using the choice UI, ends on a text option
  list: two or more closing list items whose lead-in or closing line asks the
  user to choose ("Options:", "pick one", "which option", "reply with").
  `transcript-audit` reports such turns as `prose-choice`. The
  design-simplifier's approval asks one multi-select question instead of a
  list of ids. Reflection keeps its triggers and is offered as a next action.
- Alternatives: enforce the menu after every commit outside "go" runs (would
  return about three in four commit turns and ask even when one next step is
  obvious); report only (text lists keep reaching the user).
- Consequences: no guaranteed reflect prompt after each commit. The detector
  needs an explicit choice phrase, so a list that only implies a choice
  passes; a numbered summary or instructions list does not trigger it. On
  replies from 2026-11-01 to 2026-11-20 it flagged 8 of 11,738 text blocks,
  at least 5 of them real offers, so a wrong block costs about one extra
  round-trip a week. The audit loads the detector from the repo's gate
  script and the hook runs the installed copy, so they agree after a
  reinstall.
