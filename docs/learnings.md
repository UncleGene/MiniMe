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

## 2026-10-16 — Commit gate blocks commits in scratch repos

Context: setup commits in throwaway scratch repos during review-eval work.

Action taken:
- The agent commit gate also blocks setup commits in throwaway scratch repos.
  Worked around by staging instead of committing; follow-up trigger: a
  second occurrence.
