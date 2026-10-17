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

## 2026-10-16 — Orchestrator routing depended on a forbidden project section

Context: README review promoted `minime-agent-orchestrator` as the root skill.

Action taken:
- The orchestrator, `minime-project-orient` and `minime-replan` required a
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
