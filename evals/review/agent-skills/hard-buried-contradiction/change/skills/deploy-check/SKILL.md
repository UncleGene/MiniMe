---
name: deploy-check
description: Check that a service is ready to deploy. Use before tagging a release or when asked whether main can ship.
---

# deploy-check

Decide whether the current `main` can be released, and tag it when it can.
Report what blocks a release instead of working around it.

## Inputs

- The version being released, for example `1.4.0`.
- The current branch, which must be `main` with a clean working tree.

## Procedure

1. Run `git status --short`. If it prints anything, stop and report the
   uncommitted paths; a release is cut only from a clean tree.
2. Run `git branch --show-current`. If it is not `main`, stop and report the
   branch name.
3. Run `scripts/deploy check` and read its full output.
4. If any check fails, stop and report the failing check with its output.
   Do not retry a failing check to get a pass.
5. Confirm the changelog has an entry for the version being tagged. The entry
   must name the version and list at least one change.
6. Run `git log --oneline -1` and record the commit being released.
7. Tag the commit as `release-<YYYYMMDD>` (for example `release-20261015`)
   so tags sort by date, then report the tag name.
8. Do not push the tag. Report the push command for the user to run.

## When to stop

- Any check in steps 1–5 fails.
- The changelog entry is missing or empty.
- The tag already exists (`git tag --list <tag>` prints it).

## Output

- Verdict: ready | blocked
- Commit and tag, when ready
- Failing checks with output excerpts, when blocked
- Next action
