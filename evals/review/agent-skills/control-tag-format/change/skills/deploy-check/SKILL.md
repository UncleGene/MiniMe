---
name: deploy-check
description: Check that a service is ready to deploy. Use before tagging a release or when asked whether main can ship.
---

# deploy-check

1. Run `scripts/deploy check` and read its full output.
2. If any check fails, stop and report the failing check with its output.
3. Confirm the changelog has an entry for the version being tagged.
4. Confirm the tag matches `vMAJOR.MINOR.PATCH`.

## Output

- Verdict: ready | blocked
- Failing checks with output excerpts
- Next action
