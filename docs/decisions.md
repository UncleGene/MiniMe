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
  the user works in.
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
- Decision: optimize for an individual developer installing MiniMe at user
  level. Marketplace, enterprise and team-administration infrastructure is out
  of scope.
- Alternatives: team distribution adds onboarding, migration and support
  obligations without a current need.
- Consequences: validation targets the verified hosts and representative
  tasks; installation correctness and reproducible checks remain required.

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
- Consequences: regressions on supported hosts surface later. A
  host-capability table should make adding a host a table entry (REQ-011).

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
- Decision: a light tier (doc-sync, scope, full project verification) applies
  only when every changed file is documentation and no requirement, decision,
  acceptance or safety text changes. Everything else runs the full tier
  (doc-sync, scope, simplification, review, verification, commit). When in
  doubt, use the full tier. Reflection writes a learnings entry only when it
  produces an action; session checkpoints are written only at handoffs.
- Alternatives: any doc change qualifying (requirement edits skip review); a
  diff-size threshold (a one-line safety change skips review).
- Consequences: applies to MiniMe (`AGENTS.md`, `minime-self-commit`) and to
  consumers through `minime-project-commit`.

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
  Claude Code and Codex transcripts for MiniMe skill loads, token cost and
  observable contract misfires. Nothing is collected automatically, stored or
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
  nothing brings the commit procedure back several turns later, so most agent
  commits ran without it.
- Decision: `scripts/minime claude-hook|codex-hook install --write` copies
  `scripts/commit-gate` to a user-level directory and registers it as a
  `PreToolUse` hook for Bash in `~/.claude/settings.json` or
  `~/.codex/hooks.json`. It blocks a `git commit` when the session has loaded a
  MiniMe skill but the current turn has not loaded `minime-project-commit` or
  `minime-self-commit`. Sessions with no MiniMe skill are never blocked.
- Alternatives: a reminder from the slop-scan hook (cannot tell an agent from
  the user); skill wording only (relies on the instruction-following that
  fails).
- Consequences: one skill read per committing turn. The hooks edit host
  settings, adding or removing only their own entry. The installed hook
  duplicates a little transcript parsing so it runs without the MiniMe repo.
  Codex runs it only after the user trusts it in `/hooks`.
- Amendment (2026-10-20): in Claude Code the same script is also a `Stop`
  hook. A turn that loaded a MiniMe skill may not end without `Recommended
  next action:`, progress updates included; the hook blocks once and the agent
  adds the line. Transcripts showed late-session turns dropping the line.
  Codex is not covered until its stop-hook support is checked.

## Decision 14 — Installer-generated host adapters

- Status: accepted; implemented for Claude Code review and doc check.
- Context: skills declare `model_tier`, which no host reads yet. Model, effort
  and subagent mechanisms differ by host.
- Decision: skills name a tier and a context (fresh or main) for each step. The
  installer generates a host-specific adapter from the host-capability table,
  as it already generates `agents/openai.yaml`, mapping each tier to that
  host's subagent, model, effort and headless command.
- Alternatives: portable prose only (each session guesses the mapping); drop
  `model_tier` (leaves the cost goal without a lever).
- Consequences: the installer grows, and tier mappings, like the audit's
  list-price table, must keep pace with new models and prices. A fresh-context skill only forks when its caller invokes it through
  the host's skill mechanism; reading its file runs it inline.
- Current scope: `minime-code-reviewer` and `minime-doc-check` declare
  `model_tier: fast` and `minime_context: fresh`. Into `~/.claude/skills` the
  installer adds `context: fork`, `background: false` and `model: sonnet`;
  other hosts get the source unchanged, because the cheaper Codex model missed a hard-tier
  defect. A host-capability table replaces the inline mapping when a second
  host gains an adapter (REQ-011).
- Amendment (2026-10-20): a tier takes effect only for a fresh-context skill;
  an inline skill runs on the session model, so its tier records the work's
  difficulty for a later fork. A skill is a fork candidate when its input fits
  an argument, it returns a verdict without asking the user mid-procedure, it
  reads many files, and fixtures can measure it. The `diff` scope of
  `minime-doc-sync`, report-only with risky updates returned to the caller, is
  the next candidate; it becomes fresh-context on the fast tier only after
  planted stale-doc fixtures show detection holds there (done; see below).
- Amendment (2026-10-25): those fixtures passed on Sonnet 5.5 as on Opus 5.5.
  A fork covers a whole skill, and `minime-doc-sync`'s `document` and `all`
  scopes and apply mode surface updates to the user, so the report-only diff
  audit moves into `minime-doc-check` (fast tier, fresh context). The `diff`
  scope of `minime-doc-sync` invokes it through the host's skill mechanism and
  applies or surfaces its findings in the main session, so commit gates still
  name `minime-doc-sync`. Alternatives: fork all of `minime-doc-sync` (breaks
  the questions its other scopes ask); fork one scope through new installer
  metadata (a new adapter mechanism for one caller). Cost: one more skill to
  install and keep in step. Keep the fork only if priced cost per gated change
  falls and the misfire counts do not rise.

## Decision 15 — Cross-agent second opinion

- Status: accepted; not yet implemented.
- Context: every review runs in the same model family as the work it checks,
  so blind spots are correlated.
- Decision: add an optional second-opinion step to code review and decision
  challenges, triggered by risk tier and spare quota, that runs the other
  verified host read-only. If that host is unavailable, fall back to a fresh
  instance of the same host, or skip and report the skip. A project can opt
  out of sending code to a second provider.
- Alternatives: same-host fresh-context review only (cheaper, correlated blind
  spots); always-on cross review (cost on every change).
- Consequences: kept only if the fixtures show higher detection at an
  acceptable cost. Depends on the host-capability table.
