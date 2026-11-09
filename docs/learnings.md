# MiniMe Learnings

This file records actions taken on reflection findings and on observed skill
gaps (REQ-001, REQ-006), with the rationale. Findings that need no action
leave no trace. Remove an entry once the skill, test or document it changed
fully carries the lesson.

## Entry shape

```text
## YYYY-MM-DD — Title

Context: <one sentence on session scope>

Action taken:
- Finding → what was done + why.
```

Follow-up trigger: if two entries show the same failure class, route the fix
through `minime-generalize-skill` for reusable skill changes or through the
relevant project-guide/plan skill for local workflow changes.

Entries must follow Decision 8: no names or paths of other projects, no
personal data, no transcript excerpts.

## 2026-10-20 — Commit gate blocked a skill read made in the commit's command

Context: plan, hook and routing commits in the MiniMe repo.

Action taken:
- The commit gate blocked a commit whose Bash command also read the commit
  skill, because the hook checks the transcript before the command runs, and
  its message did not say so → the message now says the read must be its own
  earlier tool call, so the retry succeeds first time.

## 2026-10-16 — Orchestrator routing depended on a forbidden project section

Context: README review promoted `minime` as the root skill.

Action taken:
- The orchestrator, `minime-orient` and `minime-replan` required a
  skill routing table in the project guide, which Decision 3 forbids in
  consuming repos, so routing was unconfigured outside MiniMe. The
  orchestrator now ships a default routing table naming the installed skills;
  a project guide may add rows, gates or a delegating repo-local skill but
  cannot remove a row or weaken a default gate, and orient and replan defer
  to that default.

## 2026-10-16 — Control fixtures carried real defects

Context: hard-tier review eval on default and cheaper models.

Action taken:
- Codex blocked every control on defects older than the change (unvalidated
  quantities, duplicate SKUs, a deploy check with zero tests, a missing
  changelog), while Claude passed them. The user ruled that code is never
  committed broken, so any defect a review finds blocks.
  `minime-code-reviewer` now says so explicitly, and the fixture projects
  were fixed until both hosts pass every control.
- `review-eval` dropped reviewer replies, so explaining a false positive took
  extra paid reviews. A false-positive result now lists its blocking
  findings.
- The agent commit gate also blocks setup commits in throwaway scratch repos.
  Worked around by staging instead of committing; follow-up trigger: a
  second occurrence.
- The gate then blocked a commit sent in the same parallel batch as the
  commit-skill read: replayed on the final transcript it passed, so the read
  was not yet written when the hook ran. The gate now re-reads the
  transcript for up to 2 seconds before blocking.

## 2026-10-17 — Cost is priced tokens; the commit gate over-matches

Context: checking whether enough target-project data exists to measure the
forked reviewer.

Action taken:
- The audit had no per-commit metric and mixed review-eval runs into host
  totals. It now reports gated commit turns by model, with their subagents,
  and excludes review-eval runs.
- The user ruled that cost, not raw tokens, is the target: fewer tokens or a
  smaller model can cost more. Recorded in Decision 1 and REQ-010; pricing is
  the next plan step.
- `--since` compared offset datetimes as strings and widened the window by
  the offset; it now converts to UTC.
- The agent commit gate blocked plain edit commands whose text mentioned a
  commit, a second over-match after the scratch-repo case. Follow-up trigger
  met: the gate now ignores heredoc bodies that do not feed a shell.

## 2026-10-25 — Intake took request premises at face value

Context: planning a cross-host second opinion and offload to Codex.

Action taken:
- Three design questions were asked for the second opinion before anyone
  asked whether a reviewer without the session's goal and in-chat decisions
  could work; the user raised it. The offload requirement assumed Claude Code
  ran out of quota first, but local transcripts showed Codex at 96-100% of its
  5-hour window on three of eight days. Both features were withdrawn
  (Decision 15). Intake now has a premise check in
  `minime-course-correction-triage` and `AGENTS.md`, and
  `minime-decision-prompt` confirms the premise before the first design
  question; a guard test pins both.

## 2026-11-09 — Hook copies drifted; the reviewer fork touched the index

Context: acting on two target-project reports about skipped gates and question
shape, with the agent commit gate as the main fix.

Action taken:
- The installed gate keeps its own copy of the transcript patterns (Decision
  13), and two had drifted from the audit's: the gate ignored the bare `minime`
  skill, and both read only the first `SKILL.md` in a shared `cat`. A test now
  pins the skill-name and read-pattern lines as identical in both files.
- The forked reviewer ran `git stash` and `git stash pop` mid-review, briefly
  unstaging the commit under review. `minime-code-reviewer` now forbids
  changing the working tree or index.
