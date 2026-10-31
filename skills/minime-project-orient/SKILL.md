---
name: minime-project-orient
description: Cold-start orientation for an agent entering an existing project. Reads the project guide, plan, latest session checkpoint, and git state to produce a verified current-state briefing and next-action options. Use as the entry point when an agent has no prior session context.
metadata:
  minime_kind: target-reusable
  schema_version: 1
  model_tier: reasoning
  model_tier_strictness: preferred
---

# minime-project-orient


Read the project's persistent state and produce a briefing that lets an
agent pick up work without chat-transcript archaeology. The skill is
read-only — it does not modify any artifact. It is the main entry point
when an agent encounters a project cold.

## When to use

- A new agent or session starts with no prior context.
- The user opens with an open-ended request ("where were we", "what's
  going on", "let's continue", "pick this up") without naming a task.
- A different agent role is taking over from another's work.

Do not use when:

- The user has already named a specific task; route directly via
  `minime-agent-orchestrator`.
- The current session already has an active context from the prior turn.
- A reflection or checkpoint is the right next step instead of a full
  orientation pass.

## Inputs

- Working directory (defaults to repo root).
- Optional overrides for project-guide path and plan path.

## Procedure

1. **Locate the project guide.** Read `AGENTS.md` if present; otherwise
   `CLAUDE.md` or `GEMINI.md` (these may be thin adapters pointing back to
   `AGENTS.md`). Extract the project name, quick commands, completion
   gates, any skill routing or gate rules, and the verifiable claims index
   if they exist.

2. **Locate the plan or state pin.** Find the plan file named by the
   project guide. Common locations: `docs/implementation-plan.md`,
   `docs/current-state.md`, or `PLAN.md` at root. Extract: the active
   phase name and status, the next concrete action, and any open
   questions. If there is no plan file, find where the project tracks
   status instead: open-items, "not yet" or to-do sections in the guide or
   development docs, or an issue tracker the guide names. Use that as the
   current state.

3. **Read the latest session checkpoint.** If a `docs/sessions/` directory
   exists, list entries and read the most recent one. Extract: branch and
   commit at checkpoint, recorded phase position, and the listed
   remaining-work item.

4. **Inspect git state.** Run:

   ```sh
   git status --short
   git log --oneline -n 10
   git branch --show-current
   ```

   Note: current branch, count of uncommitted changes, count of untracked
   files, and the last 5–10 commit subjects.

5. **Verify claims against current state.** For every numeric or
   referential claim in the verifiable claims index, run the listed source
   command and compare with the documented value. Record each as `ok` or
   `drift: claimed=<X> actual=<Y>`. Do not auto-fix — this skill is
   read-only.

6. **Synthesise the briefing.** Compose a single coherent summary covering:
   project name and one-line description, current phase and status,
   branch and HEAD, verified facts versus claimed values, recent activity,
   the remaining-work item from the latest checkpoint, open questions
   from the plan, and any conflicts between sources.

7. **Offer next-action options via `minime-decision-prompt`.** Build the
   option list from what was found:

   - Continue the remaining-work item from the latest checkpoint (if any).
   - Start the next concrete action from the plan, or the next open item
     from wherever the project tracks status.
   - Run `minime-doc-sync` with `all` scope (if Step 5 detected drift).
   - Run `minime-plan-review` (if phase status is ambiguous).
   - Ask the user for direction (if state is unclear or sources conflict).

   After presenting the choice, state explicitly: all subsequent
   implementation, documentation, review, and quality work in this session
   must route through `minime-agent-orchestrator`'s default routing, plus any
   rows or gates the project guide adds to it (Step 1).
   Do not use ad-hoc approaches for any intent covered by a routed skill.

## Skeptic pass

- Plan claims are not self-verifying; run the source commands in Step 5
  and prefer current state over the document when they disagree.
- If the latest checkpoint disagrees with the plan on phase position,
  surface the conflict — do not pick a side silently.
- A missing plan or checkpoint is an observation, not a gap. A project
  with a guide, requirements or commit history may have none on purpose;
  report the status location from Step 2 and offer next work from it. Ask
  about bootstrapping a plan only when no such location exists, through
  `minime-decision-prompt`. Include a "No plan, on purpose" option, and do
  not recommend bootstrapping unless the user asked for a plan. Do not
  invent state.
- If the project guide names skills that are not registered (e.g.
  `host-registration-audit` would fail), record the gap; do not assume
  the catalog is available.
- An agent reading this briefing should be able to act without re-reading
  the plan, so include enough specifics (paths, counts, IDs) that the
  briefing stands alone.

## Output

```md
## Project Orientation Briefing

**Project:** <name and one-line description>
**Current phase:** <name> — <status>
**Branch:** <branch> at <short SHA>
**Working tree:** <clean | N modified, M untracked>

### Verified state
- <claim>: <documented value> | actual: <actual value> | <ok | drift>
- ...

### Recent activity
- <subject of last commit>
- ...

### Latest session checkpoint
- Path: <path>
- Phase position recorded: <phase>
- Remaining work recorded: <items>

### Open questions
- <items from plan, or "none">

### Conflicts and gaps
- <plan vs checkpoint disagreements, drift items, missing artefacts>

### Next actions (route each through its owner skill)
1. <continue remaining-work item, if any>
2. <next plan slice>
3. <run coherence sweep | plan review | clarify with user>

Recommended next action: <one concrete next step>

**Routing reminder:** All subsequent implementation, documentation, review,
and quality work routes through `minime-agent-orchestrator`'s default routing.
```

When the briefing ends with two or more viable next actions, delegate to
`minime-decision-prompt` — read its skill file and follow its procedure. The
numbered list above is the briefing's content, not the question; rendering it
as the question leaves the user a prose menu to type against.

## Hand-off

Each entry names an owner skill. Delegate to the listed skill — read its file and
follow its full procedure. Do not approximate from memory.

- "Continue remaining work" → owner skill named in the checkpoint's
  remaining-work line.
- "Next plan slice" → `minime-implementation-step-selector`.
- "Run doc sweep" → `minime-doc-sync` (`all` scope, apply mode).
- "Run plan review" → `minime-plan-review`.
- Plan vs checkpoint conflict → `minime-course-correction-triage`.
- Drift in verified claims → `minime-doc-sync`.
- Established project with no status location, and the user explicitly
  picks a plan → `minime-project-milestone`.
- No guide, requirements or substantial code (an empty or notes-only repo)
  → `minime-project-inception`.

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
