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
