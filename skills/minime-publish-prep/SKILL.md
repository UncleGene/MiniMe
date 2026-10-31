---
name: minime-publish-prep
description: Prepare a repository for publishing. Sweep personal data and other-project references out of tracked files, make the docs coherent for outside readers, shape the README for onboarding, and limit how much development history the public commit log exposes. Use before making a repo public or pushing substantial private history to a public remote.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-publish-prep

Make a repository fit to publish: no private data, no contradictory docs, a
README that onboards a new user, and a commit history that shows milestones
rather than internal churn. This skill is invoked explicitly, never as a push
gate: squashing commits and rewriting docs are deliberate, occasional acts, and
a gate would force them at the wrong cadence. Continuous protection stays with
the project's own privacy tests and commit gates.

## Inputs

- Repository root; the public remote, if one exists.
- The project's privacy checks (denylist tests, path scans) when present.
- Project guide, README, docs, and decision records.

## Procedure

1. **Baseline and backup.** Classify commits from evidence: `git fetch
   <remote>`, then `git rev-list <remote>/<branch>..HEAD` lists the local-only
   commits; everything below that range is published. With no remote, or no
   such branch on it yet, treat every commit as local-only. Back up with a git
   bundle of the current branch (`git bundle create <file> <branch>`), not a
   new branch; it covers the starting state. All later steps work on the same
   branch.
2. **Privacy sweep.** Search every tracked file — including diff summaries and
   change narratives recorded inside docs — for personal data (names, emails,
   home paths, machine names, credentials) and for names or paths of other
   local projects. Run the project's own privacy tests first when they exist;
   add grep passes for what they do not cover. Replace findings with neutral
   placeholders. Where removing a leaking diff summary leaves a hole in the
   record, write a retroactive backfill: a neutral summary derived from the
   original change itself (`git show <commit>`), never from memory, so the
   documentation stays complete without the leak. The sweep report uses
   placeholders too — never reproduce a found value in it.
3. **Doc coherence.** Delegate to `minime-doc-sync` (`all` scope, apply mode).
   Then remove obsolete roadmap items and superseded decisions — those the
   record marks replaced or overridden — rather than preserving them as
   history: a decision record keeps only the current decision and its
   rationale. Confirm each removal through `minime-decision-prompt` (it is a
   content deletion) and route decision edits through `minime-project-adr`.
   Docs must not contradict each other or expose abandoned roadmap
   generations.
4. **README onboarding pass.** The README serves a new user of the project,
   not its maintainers: goals, installation and initialization, user-facing
   features, and suggested usage workflows for the main use cases. Move
   internal detail to a developers document (or a clearly separated developers
   section when the project is small) and link it from the README.
5. **Commit and verify.** Run the privacy checks and the project's full test,
   lint and type gates, then commit the content changes through the project's
   commit gate skill when it has one, otherwise plainly. Confirm the remaining
   tracked set reads as if written for publication.
6. **History shaping.** The last mutating step; it rewrites only finished,
   committed work. Limit what the public log exposes, especially complete
   roadmap reversals: squash the local-only commits (re-run the step-1
   classification first) into milestone-grained commits with clean messages.
   Take a fresh bundle of the pre-rewrite state, then present the squash plan
   — ranges and resulting messages — through `minime-decision-prompt` and get
   approval before rewriting anything; the bundle is a safety net, not a gate.
   Never rewrite published commits without an explicit user decision made the
   same way — force-pushing published history is not a default. After the
   rewrite, re-run the privacy checks and the project gates, and confirm the
   new commit messages leak nothing; if any check fails, restore from the
   fresh bundle and replan.

## Skeptic pass

- A denylist only catches what it names. Sweep for patterns even when the
  denylist passes, e.g. `git ls-files -z | xargs -0 grep -nEi
  "<home-dir>|<git config user.name>|@"` for user directories, the author's
  name and email addresses.
- Untracked files are not safe to ignore: confirm private artifacts
  (checkpoints, denylists, local notes) are ignored by git, not merely
  uncommitted.
- Squashing cannot hide what the remote already serves. Check the remote's
  actual history before claiming exposure is limited.
- A README section that explains internals is not onboarding content, however
  well written; move it rather than trimming it.

## Output

- Remote baseline: published commits vs local-only commits; backup bundle path
- Privacy findings and resolutions, including backfilled summaries
- Doc coherence findings (from `minime-doc-sync`) and decision-record edits
- History plan: squash ranges and resulting commits; any force-push decision
- README and developers-doc changes
- Verification results
- Verdict: ready-to-publish | fixes-applied-recheck | blocked (with owner)

## Hand-off

Delegate by reading the named skill's file and following its full procedure.

- Doc sweep → `minime-doc-sync` (`all` scope, apply mode)
- Decision-record edits → `minime-project-adr`
- Squash-plan, force-push or content-deletion choices → `minime-decision-prompt`
- Content commit (step 5) → the project's commit gate skill

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
