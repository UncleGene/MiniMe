---
name: minime-self-commit
description: Shape atomic commits when working inside the MiniMe repo itself. Runs MiniMe-internal gates (skill reinstall, host-registration audit, distillation check) then chains to minime-project-commit for the shared commit rules and gate sequence.
metadata:
  minime_kind: internal
  model_tier: fast
  model_tier_strictness: preferred
---

# minime-self-commit

Commit gate for changes made to the MiniMe repo itself. Adds MiniMe-specific
checks that are not appropriate for target projects, then delegates to
`minime-project-commit` for the shared commit rules and gate sequence.

## MiniMe-internal pre-commit checks

Run these checks first, before invoking `minime-project-commit`.

- For diffs that add or modify any file under `skills/`: run
  `scripts/minime skills install --write` to reinstall to all surfaces, then
  verify with `scripts/minime host-registration-audit --json`. A skill update
  that is not reinstalled to all surfaces is a commit defect.

- For diffs that add or modify any skill file: run the distillation check —
  `python -m pytest tests/ -k test_target_reusable_skills_are_token_conscious`.
  A skill exceeding the 4× verbosity ceiling (computed from the current
  catalog median by the test) or containing 2+ transcript-like step headers
  (`### Now do/let/we/you` or `### Next, <word>`) must be distilled before the
  commit proceeds.

- Before stopping for any reason, report branch, HEAD short SHA, whether the
  working tree has uncommitted changes, changed file paths, verification status,
  whether the work is committed, commit-ready, or not commit-ready, and the next
  concrete action.

## Commit gate ledger

Before staging or committing, create a commit gate ledger and keep it current
until the commit is complete. Use `status: pending`, `status: pass`,
`status: blocked`, or `status: skipped (light tier)` for each row, with one
evidence sentence. Only the reviewer row may be skipped, and only when the
light tier in `AGENTS.md` applies.

Required rows:

- Repo state captured: branch, HEAD short SHA, changed file paths.
- MiniMe internal gate: skill reinstall to all surfaces when `skills/` changed.
- MiniMe internal gate: `host-registration-audit` after reinstall when
  `skills/` changed.
- MiniMe internal gate: distillation check when any skill file changed.
- Shared gate: `minime-doc-sync` against the staged diff.
- Shared gate: `minime-scope-boundary` against the staged diff.
- Shared gate: `minime-code-simplifier` against the staged diff.
- Shared gate: `minime-code-reviewer` against the staged diff.
- Shared gate: `minime-verification-gate` with the required project checks.
- Shared gate: reflection if the project guide's reflection trigger fires.
- Commit message: atomic conventional title and why-body.
- Commit action: commit created through this ledger and shared commit gate.
- Post-commit continuation: next step or decision prompt presented, or the
  next autopilot block started.

Direct git commit remains forbidden until every required ledger row is
`status: pass` or an allowed light-tier skip. Running some checks manually does
not authorize `git commit`; finish the ledger and the delegated `minime-project-commit` procedure first.

## Shared commit gate

After the MiniMe-internal checks above pass, delegate to minime-project-commit.
Read its skill file and follow its procedure. Do not commit directly —
`minime-project-commit` owns the shared commit rules, scope check, code
review, and post-commit prompt.
