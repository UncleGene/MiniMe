---
name: minime-agents-md-audit
description: Audit and improve agent instruction files (AGENTS.md, CLAUDE.md, GEMINI.md). Use when instructions feel bloated, commands are stale, guidance is generic rather than execution-specific, or when asked to review or improve agent instruction quality.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-agents-md-audit

Agent instruction files are execution contracts, not knowledge bases.

**Litmus test for every line:** "Would removing this cause the agent to make a
mistake?" If no, cut it. Bloated instruction files cause agents to ignore rules.

## When to use

- Instructions feel too long or contain generic advice.
- Commands are stale or untested.
- Agents repeatedly miss rules that are technically present.
- Starting a project and need to write or validate initial instructions.

## Procedure

### Step 1 — Discover files

```sh
find . \( -name "AGENTS.md" -o -name "CLAUDE.md" -o -name "GEMINI.md" \) 2>/dev/null | sort
```

Check for a user-level file (`~/.claude/CLAUDE.md` or equivalent). Audit each
file independently. In monorepos, include workspace-level instruction files.

### Step 2 — Quick audit (10 checks)

Score each file. Target: ≥ 8/10. Automatic fail: commands are mostly broken, or
content is mostly generic template text.

| # | Check |
|---|---|
| 1 | Core run/test/build/lint commands exist when applicable |
| 2 | Commands appear runnable and match project scripts |
| 3 | Setup/bootstrap requirements are documented |
| 4 | At least one project-specific gotcha is documented |
| 5 | Gotchas include corrective action (what to do instead) |
| 6 | Conventions that change implementation choices are explicit |
| 7 | Every line passes the litmus test |
| 8 | File avoids framework doc dumps or generic template text |
| 9 | Linked paths and commands are current (not stale or dead) |
| 10 | Non-universal detail is linked out, not inlined |

### Step 3 — Report findings

Before editing, output a concise table:

```
| File | Score | Grade | Key issues |
|------|-------|-------|------------|
| AGENTS.md | 6/10 | Fail | Missing test command, stale path, generic advice |
```

### Step 4 — Propose minimal diffs

- Fix broken or stale commands first.
- Remove generic, duplicate, or obsolete guidance.
- Move deep detail into linked files.
- For a rule agents keep missing, propose enforcement at the highest level that
  works: a hook, script or CI check; then a lint or type check whose error names
  the fix; then a test. Keep it as prose only when it needs judgment, then add
  emphasis ("IMPORTANT", "NEVER") and one example of the failure. Unenforced
  emphasis decays; use it sparingly and only where evidence supports it.
- Keep rewrites incremental; preserve useful wording.

### Step 5 — Validate and apply

Smoke-check core commands after editing. Confirm linked paths resolve.
Do not apply edits until findings are reported to the user.

## Output

```
File: AGENTS.md
Score: 7/10 — borderline

Must fix:
- [stale] test command `npm run test` → script does not exist; correct is `npm test`
- [bloat] lines 22-31 are framework documentation; cut or link out

Should fix:
- [generic] "follow best practices" on line 14 — rewrite with a specific rule or remove

Pass:
- Commands, gotchas, and setup sections are present and correct
```

## Gotchas

- Do not rewrite the entire file when targeted edits pass audit — incremental fixes
  preserve useful wording and reduce review burden.
- Do not add gotchas not grounded in a real failure — hypothetical warnings become
  noise agents learn to ignore.
- Do not remove emphasis markers from rules agents consistently skip — they exist
  because the default phrasing was insufficient. Remove them only when a hook,
  check or test now enforces the rule.
- A high quick-audit score does not excuse skipping command validation — stale
  commands can hide behind passing checklists.

## Interaction rules

- End with `Recommended next action: <one concrete step>`. If that step is a
  check or gate that needs no user input, run it now instead of stopping.
- Before a feature or behavior change, check it against accepted requirements
  and decisions, name its impact, and confirm its value; route non-trivial
  cases through `minime-course-correction-triage`.
- Ask any question whose answer changes an artifact through
  `minime-decision-prompt`: one question per turn, named options with pros,
  cons and impact, in the host's choice UI when available.
- Never skip a failing test, lint, type or doc check because it pre-existed;
  fix it or escalate before committing.
- When a step names another skill, read that skill's file and follow its full
  procedure.
