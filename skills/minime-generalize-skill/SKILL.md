---
name: minime-generalize-skill
description: Improve an existing MiniMe skill by identifying a gap or quality issue through self-dogfood, finding the closest skill in the catalog, and distilling the improvement. Use when self-dogfood reveals a missing workflow step, a contract gap, or quality drift in an existing skill.
metadata:
  minime_kind: internal
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-generalize-skill

Catalog improvement through self-dogfood. When MiniMe development exposes a
workflow gap, contract gap, or quality issue in an existing skill, this skill
guides the improvement path: identify the closest existing skill, distill the
fix, validate, and update.

Do not create a new skill speculatively. Only act when a concrete gap or
quality issue was observed during self-dogfood.

## Inputs

- **Gap or quality issue** — what went wrong or was missing during the session.
  One sentence. Cite the session or commit where it was observed. Describe
  evidence from other projects generically: no names, paths, or their commits.
- **Candidate skill** — the MiniMe skill closest to the observed gap. If
  unsure, use `scripts/minime skills similar <source>` to find it.

## Workflow

### Step 0 — Define routing evidence

Before changing any skill, write the route evidence that will prove the change:

- Positive examples: user requests or session failures where this skill should
  load or the changed rule should fire.
- Negative examples: adjacent requests where another skill should load or no
  skill change should happen.
- Forbidden loads: cases where a broader description would cause off-target
  activation.

If the change touches frontmatter `description:`, treat that line as the routing
trigger, not documentation. Use user-intent language, keep it terse, and verify
the positive and negative examples before editing the body. Description changes
without route evidence are blocked.

### Step 1 — Confirm the gap is real

Re-read the session or commit where the gap was observed. Verify:

- The workflow role was missing from the existing skill, not just overlooked.
- The gap recurred or has a clear mechanism to recur — not a one-off slip.
- No existing skill already covers it (check `scripts/minime skills list`).

If any item fails, do not proceed. Record why in `docs/learnings.md` and stop.

### Step 2 — Find the closest existing skill

Run the catalog similarity search:

```sh
scripts/minime skills similar <source-skill-directory-or-SKILL.md-path>
```

Read the top-ranked result. If it already covers the gap fully, the issue is
enforcement, not the skill. Escalate to an AGENTS.md rule or a gate position
instead of modifying the skill.

### Step 3 — Distill the improvement

Draft the minimal change to the candidate skill that closes the gap:

- Add the missing rule, step, or gate at the position where it would have fired.
- Do not expand scope beyond the gap.
- Do not introduce a new skill for a gap that fits inside an existing one.
- Keep the skill within its size ceiling (see `docs/concepts.md`).
- Every new sentence must pass: "Would the agent get this wrong without this?"
- Prefer grounded gotchas and negative examples over longer generic procedure.
- Move conditional, bulky, or deterministic support into `scripts/`,
  `references/`, or `assets/` instead of expanding `SKILL.md`.

### Step 4 — Validate

```sh
scripts/minime skills install-check skills/minime-<target-reusable-name>
```

Run `install-check` for changed target-reusable skills. Internal skills are not
installable; for internal skill changes, run the relevant drift-guard tests
plus the full test suite. Fix any contamination or frontmatter errors before
proceeding. If the description changed, run or add routing tests that cover
positive examples, negative examples, and forbidden loads.

### Step 5 — Record

- Update `docs/learnings.md` with the gap finding and action taken.
- If the gap reveals a structural enforcement hole (rule exists but agent
  bypassed it), also add a drift-guard test or gate position.

## Constraints

- Do not create a new skill without two distinct observed use cases.
- Do not improve a skill based on a hypothetical gap — self-dogfood evidence
  is required.
- Keep changes small. Prefer inserting one rule at the right gate position
  over a multi-section rewrite.

## Output

Updated `skills/minime-<name>/SKILL.md` that passes the validation gate for its
kind, plus a one-entry addition to `docs/learnings.md` recording the gap and
the fix.
