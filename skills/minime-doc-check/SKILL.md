---
name: minime-doc-check
description: Report documentation a diff made stale, without editing anything. Returns each stale claim with its location and a proposed fix, classified as a factual auto-fix or an update for the user. Use as the report-only diff audit that minime-doc-sync's diff scope invokes; not for applying fixes or checking one document (use minime-doc-sync).
metadata:
  minime_kind: target-reusable
  model_tier: fast
  model_tier_strictness: preferred
  minime_context: fresh
---

# minime-doc-check

Find the documentation a diff made stale and report it. This skill edits
nothing and asks the user nothing: it returns findings to its caller, usually
`minime-doc-sync`, which applies the factual fixes and surfaces the rest.

## Inputs

- Diff or commit range (default: the staged diff, else the uncommitted diff).
- Project guide, README, requirements, decisions, architecture and plan.
- Code and tests the docs describe.

## Procedure

1. **Gather what changed.** List changed files; categorize as new capability,
   changed behavior, removed functionality, or internal. Enumerate doc files,
   including those the diff did not touch.
2. **Audit each doc against the changes.** Find load-bearing claims the diff may
   invalidate: paths, commands, flags, counts, defaults, limits, formats,
   feature descriptions, setup steps, expected output. README: capabilities,
   setup, examples. Architecture docs: only what the diff clearly contradicts.
   Project guide: commands, scripts, paths, test instructions, data contracts.
   A doc the diff updated can still be stale elsewhere; so can its siblings.
3. **Classify each finding.** `auto-fix`: a factual correction the diff clearly
   warrants (a path, a count, a new table row). `surface`: narrative changes,
   section removals, security-model changes, rewrites over ~10 lines, ambiguous
   relevance, new sections, positioning, design rationale and security
   descriptions.
4. **Check cross-references** touched by the diff: links, section names, tables
   of contents, counts.
5. **TODO cleanup** if a TODO file exists: flag items the diff completed or made
   stale; never mark them complete.

## Rules

- Report a finding at the stale line (`path:line`), not at the code that made
  it stale.
- Verify each proposed value against current code, tests or the diff.
- A doc claim the diff leaves true is not a finding; do not flag style.
- Edit no file and ask no question; the caller owns both.

## Output

```md
## Doc Check
- Diff: <range or staged>
- Docs reviewed:
- Findings: path:line, stale claim, actual state, proposed fix, auto-fix | surface
- Verdict: pass | fix
```

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
