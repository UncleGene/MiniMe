---
name: minime-doc-sync
description: Keep project documentation true to the code and to itself, scoped to recent changes, one document, or the whole doc set in report-only or apply mode. Use after commits or a release, when a document may be stale, or for a full documentation health check.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-doc-sync

Bring documentation back in line with the code and with itself. Pick one scope
per invocation:

- `diff` (default): docs affected by a diff or commit range. Use as the commit
  gate and after each implementation step or release.
- `document`: one named document checked claim by claim against the code. Use
  when a single doc may have gone stale.
- `all`: every doc, for cross-doc consistency, authority, status truthfulness,
  procedure executability and traceability. Run `report-only` for a health
  check ("what is wrong") and `apply` to fix ("bring docs up to date").

## Inputs

- Diff or commit range (`diff`), document path (`document`), or the doc root.
- Project guide, requirements, decisions, architecture, plan, README.
- Code and tests the docs describe.

## Procedure — `diff`

1. **Gather what changed.** List changed files; categorize as new capability,
   changed behavior, removed functionality, or internal. Enumerate doc files.
2. **Audit each doc against the changes.** Find load-bearing claims the diff may
   invalidate: paths, commands, flags, counts, feature descriptions, setup
   steps, expected output. README: capabilities, setup, examples. Architecture
   docs: only what the diff clearly contradicts. Project guide: commands,
   scripts, paths, test instructions.
3. **Classify each update.** Auto-fix factual corrections the diff clearly
   warrants (a path, a count, a new table row). Surface narrative changes,
   section removals, security-model changes, rewrites over ~10 lines, ambiguous
   relevance and new sections. Never auto-fix positioning, design rationale or
   security descriptions.
4. **Apply auto-fixes**, one specific summary line per file.
5. **Surface risky updates one at a time**; apply approved ones immediately.
6. **Check cross-references** touched by the diff: links, section names, tables
   of contents, counts.
7. **TODO cleanup** if a TODO file exists: flag items the diff completed or made
   stale; never silently mark them complete.

## Procedure — `document`

Read the document in full. Extract concrete claims: identifiers, paths,
behaviors, contracts, error cases. Verify each against the code. Group them as
still-true, drifted, removed or ambiguous. Do not reverse-engineer documents
from code or propose new behavior; if a claim cannot be confirmed, report it as
ambiguous rather than guessing.

## Procedure — `all`

1. **Enumerate** every doc the project guide names, plus README and guide files.
   Skip vendored docs.
2. **Currency:** verify load-bearing claims (paths, commands, flags, counts,
   statuses) against code and tests. Replace stale precise numbers with
   non-drifting descriptions or current values.
3. **References:** every requirement, decision, milestone, section, path, skill
   and command reference resolves.
4. **Authority:** load-bearing rules agree across guide, core docs and README.
   Conflicts are blocking; do not pick a winner.
5. **Status truthfulness:** "complete" items meet acceptance; "planned" items
   are not already shipped. Route status changes to `minime-project-milestone`.
6. **Clarity:** ambiguous or contradictory claims, TODO/FIXME, duplicated or
   orphaned sections, dead links.
7. **Procedure executability:** referenced scripts exist and flags and outputs
   match the current tooling.
8. **Decisions and traceability:** superseded decisions name successors; new
   behavior is backed by a decision; every active requirement links to a
   decision, architecture section, milestone, test or code. Record missing
   links; never fabricate a requirement or decision to close one.
9. **Classify** findings as blocking (contradiction, false claim, broken
   authority, missing decision), consistency, clarity or currency.
10. In `apply` mode, fix consistency, clarity and currency findings; surface
    blocking ones. Then re-walk references and rules to confirm no fix broke
    anything. In `report-only` mode, edit nothing.

## Rules

- Never change a number, path, flag, status or claim without verifying the new
  value against current code, tests or the diff. Cite `path:line`.
- Never remove content that may still be accurate, or a whole section, without
  approval.
- When docs conflict, surface the question; do not silently pick a side.
- Never silently rewrite a superseded decision or load-bearing rule; route to
  `minime-project-adr`.
- Never collapse two docs with real audiences (human-facing README, agent-facing
  guide); reduce duplication by linking.
- A broken reference may mean the target moved; read the target before editing.
- Do not paraphrase a load-bearing rule for clarity unless it is ambiguous.

## Output

```md
## Doc Sync
- Scope: diff | document | all (report-only | apply)
- Docs reviewed:
- Findings: location (path:line), claim, actual state, kind, resolution
  (applied | surfaced | routed)
- Edits applied (paths, one-line summaries):
- Surfaced to user, with decisions:
- Blocking findings and owner skills:
- Verdict: pass | fix | route
- Next action:
```

## Hand-off

Delegate by reading the named skill's file and following its full procedure.

- Blocking contradiction or authority conflict → `minime-course-correction-triage`,
  then the owner skill
- Plan status change → `minime-project-milestone`
- Architecture statement change → `minime-system-updater`
- Decision gap or conflict → `minime-project-adr`
- Requirement gap → `minime-requirements-manager`
- Code-doc divergence needing a code change → `minime-implementation-step-selector`
- Repeated drift in one area → `minime-design-simplifier`

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
