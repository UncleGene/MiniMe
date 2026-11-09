# Developer Guide

How to work on MiniMe itself. Agents follow [`AGENTS.md`](../AGENTS.md), which
holds the completion gates, skill routing and interaction contract; this guide
covers the same ground for people.

## Repository layout

- `skills/minime*/SKILL.md` — skills. `metadata.minime_kind: target-reusable`
  skills are installed on hosts; `internal` skills (`minime-generalize-skill`,
  `minime-self-commit`) are used only inside this repo.
- `skills/minime-code-reviewer/references/` — stack marker table and layer
  slop profiles, installed with the skill.
- `scripts/minime` — stdlib CLI: catalog, install, audits, `review-eval` and
  hook installers.
- `scripts/slop-scan`, `scripts/commit-gate` — hook bodies copied to
  `~/.config/minime/` on install.
- `evals/review/<layer>/` — planted-defect review fixtures;
  `evals/doc-check/<layer>/` — planted stale-doc fixtures for `minime-doc-check`.
- `tests/` — stdlib unittest suite.
- `docs/` — CLI reference, reports, troubleshooting, requirements,
  architecture, decisions, plan, learnings and dated reassessment reports.
- `CLAUDE.md`, `GEMINI.md` — surface adapters that delegate to `AGENTS.md`.

## Environment

The CLI needs only Python 3.14+. Development checks use Ruff 0.15.12, mypy
1.20.2 and, for the distillation check, pytest 9.0.3:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install ruff==0.15.12 mypy==1.20.2 pytest==9.0.3
```

## Checks

Run the full set before every commit; a failing check blocks the commit even
when the failure predates your change. Run unittest before the catalog and host
checks, because test fixtures temporarily modify `skills/`. Include the
extensionless CLI explicitly in lint and type scope.

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
ruff check --no-cache scripts/minime tests
mypy --python-version 3.14 --cache-dir /tmp/minime-check-mypy scripts/minime tests
scripts/minime doctor
scripts/minime skills list --json
scripts/minime host-registration-audit --skills-root ~/.codex/skills --json
scripts/minime host-registration-audit --skills-root ~/.claude/skills --json
scripts/minime host-registration-audit --skills-root ~/.config/opencode/skills --json
scripts/minime host-registration-audit --skills-root ~/.copilot/skills --json
```

Mypy uses its default checks. Host audits need the installed surfaces.

## Changing a skill

1. Start from an observed gap, not a speculative improvement (REQ-001). Find
   the closest owner with `scripts/minime skills similar skills/<skill>`.
2. Keep the fix minimal. Every reusable skill ends with an identical
   `## Interaction rules` section; edit all copies together (Decision 6).
3. Validate and reinstall:

   ```sh
   scripts/minime skills install-check skills/<name>
   python -m pytest tests/ -k test_target_reusable_skills_are_token_conscious
   scripts/minime skills install --write
   ```

4. If the reviewer or a slop profile changed, run the fixtures (this spends
   host plan quota): `scripts/minime review-eval --host <claude|codex> --run`.
   If `minime-doc-check` changed, add `--skill doc-check`.
5. Record the action and rationale in `docs/learnings.md`.

`minime-generalize-skill` walks an agent through these steps.

## Commits

Commits go through `minime-self-commit`, which picks the gate tier
(Decision 7): documentation-only changes that touch no requirement, decision,
acceptance or safety text run doc-sync, scope, simplification and
verification; everything else also runs review. Update docs, plan status and
decisions in the same commit as the change they describe.

## Privacy

No tracked file or commit message may name or path other local projects or
carry personal data (Decision 8). Two tests guard this. One rejects home
directory paths. The other reads an untracked `.minime-private-terms` file
(one term per line) and checks tracked files, paths and commit messages for
those terms; it skips when the file is absent. Session checkpoints in
`docs/sessions/` are git-ignored, and transcript or review reports are never
committed.
