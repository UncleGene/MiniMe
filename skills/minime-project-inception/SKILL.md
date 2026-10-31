---
name: minime-project-inception
description: Turn a new project idea into a development-ready project. Interview the user about purpose, users, scope, constraints and success criteria, then create the project guide, requirements and first milestone. Use when starting a new project, or when a repo holds only notes or a code sketch and no guide or requirements.
metadata:
  minime_kind: target-reusable
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-inception


Convert an idea into a project that an agent can start developing without
guesswork. The skill owns the discovery interview and the readiness bar; each
artifact is written by its existing owner skill. It creates generic project
files only: no references to MiniMe, its skills, or a skill-routing section.

## When to use

- The user describes a new project, product or tool idea and wants to start.
- A repo holds only notes or a code sketch, with no project guide or
  requirements.

Do not use when:

- A project guide, requirements or decisions, or a non-trivial source tree
  exist: use `minime-orient`, even when no plan exists.
- An existing project has drifted or was inherited: use
  `minime-project-reassessment`.
- The user wants one feature added to an existing project: use
  `minime-course-correction-triage`.

## Procedure

1. **Check the starting state.** Look for `AGENTS.md`, `CLAUDE.md`,
   `GEMINI.md`, `docs/requirements.md`, `docs/implementation-plan.md`, a
   README and source code. If a project guide, requirements or decisions,
   or a non-trivial source tree exist, stop and route to
   `minime-orient` (or `minime-project-reassessment` for a drifted
   project); a README or notes alone do not stop it. Never use this skill
   to add a plan to an established project. Never overwrite an existing
   file. Read existing code and notes before asking anything they answer.

2. **Take the idea.** Ask the user to describe the idea in their own words
   (plain prose; there are no options yet). Restate it as one paragraph:
   whose problem, what pain, what changes when it is solved.

3. **Find the gaps.** Score the idea against the readiness checklist. Mark
   each item answered, inferred (an assumption to confirm) or missing:

   - Problem and value: who has the pain, how they cope today, why now.
   - Users and context, including who is explicitly not served.
   - First-release capabilities and explicit non-goals.
   - Constraints: platform, language or stack, integrations, data, privacy
     and security, cost, deadline.
   - Success criteria the user can observe or a test can verify.
   - Delivery: where it runs, who operates it, required quality checks.
   - Risks and open questions.

4. **Interview.** Ask one question per turn, the most blocking gap first,
   through `minime-decision-prompt`: propose two to four concrete answers
   derived from the idea, each with pros, cons and impact, recommended one
   first; the user may answer freely instead. Do not ask what the repo or
   earlier answers settle. Stop when every item is answered, recorded as an
   assumption, or deferred as an open question that does not block the first
   milestone.

5. **Confirm the brief.** Present a compact brief in chat: problem, users,
   scope, non-goals, constraints, success criteria, assumptions, open
   questions. Ask for approval or the item to revise. Do not write files
   before approval. This holds when the brief is inferred from notes or
   code: an inferred brief is a proposal, not consent.

6. **Write the artifacts.** Create only these, each through its owner:

   - `AGENTS.md` (written directly): purpose in two or three lines, where
     requirements, plan and decisions live, quick commands for build, test and
     lint (mark planned commands as not yet runnable), completion checks and
     key invariants taken from the constraints. If the user's host reads only
     its own guide file, add a one-line adapter pointing to `AGENTS.md`.
   - `docs/requirements.md` through `minime-requirements-manager`: one
     requirement per first-release capability with verifiable acceptance, and
     the non-goals.
   - `docs/decisions.md` through `minime-project-adr`, only for hard-to-reverse
     choices settled in the interview, such as stack, platform or storage.
   - `docs/implementation-plan.md` through `minime-project-milestone`: goal,
     the first milestone as the smallest end-to-end useful slice, its
     acceptance, open questions and the next concrete step.

7. **Check readiness.** Run `minime-phase-quality-guard` on the new artifacts.
   Ready means: each active requirement has verifiable acceptance; the first
   milestone has acceptance and a next step; no open question blocks it; the
   guide says how work is verified. Fix gaps before declaring readiness.

8. **Hand off.** If the directory is not a git repository, offer to initialise
   one. Commit through `minime-project-commit`, then route to
   `minime-implementation-step-selector` for the first slice.

## Skeptic pass

- A solution-shaped idea ("build an app that...") hides the problem; ask
  whose pain it solves before accepting features.
- Do not record an inferred answer as a requirement; it stays an assumption
  until the user confirms it.
- Challenge first-release scope: anything not needed for the first useful
  slice becomes a later milestone or a non-goal.
- Do not let stack choice precede the constraints that decide it.

## Output

- Approved project brief (in chat).
- Created files and the owner skill used for each.
- Readiness verdict with any remaining open questions.
- First milestone and its next concrete step.

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
