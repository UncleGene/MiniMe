---
name: minime-decision-prompt
description: Standardized human checkpoint. When an ambiguity trigger fires, present the user with a clear, argued choice instead of silently picking. Required by other skills when routing on ambiguity.
metadata:
  minime_kind: target-reusable
  model_tier: fast
  model_tier_strictness: preferred
---

# minime-decision-prompt


Use when the agent would otherwise pick silently between materially
different paths. Do not resolve the question — stop and wait. The one
exception is a low-tier reversible choice with a conventional default (see
Rules), which is stated instead of asked.

## Ambiguity triggers

- Any question the agent is about to ask the user whose answer would change an
  artifact, implementation, validation, or handoff — including a clarifying
  question that surfaces mid-flow, outside every other trigger below. This
  trigger is the catch-all: a question does not escape the required shape by
  arising spontaneously rather than from a listed trigger.
- Spec gap that implementation would resolve by guessing.
- Two viable architectural paths with different long-term cost.
- Scope expansion beyond the user's request.
- Stack-freeze or constraint tension.
- A decision that meets the durability bar but no record exists.
- Conflicting prior decisions (memory vs. document, document vs. code).
- Any fix from a gate skill where the fix has multiple defensible shapes.

## Required output shape

- **Context first:** before the question, explain in plain terms any mechanism,
  cost or term the options depend on that the user has not seen this session;
  say whether a cost is one-time or recurring and where it falls.
- **Question:** one sentence.
- **Why it matters:** reversibility, blast radius, what gets locked in.
- **Options:** minimum two, each with:
  - Name, pros, cons, cost, what it locks in.
- **Recommendation:** one option with confidence (low/medium/high).
- **Default if no reply:** stop or the recommended option.

## Rules

- When a choice is low risk by the definition in
  `minime-course-correction-triage`, reversible and has a conventional default,
  state the default and proceed instead of asking.
- Before the first design question on a request, confirm its premise holds,
  or record it as unverified, never as failed (the premise check in
  `minime-course-correction-triage`); asking how to build something that may
  not work is premature.
- An external fact an option relies on (a law, a program rule, a vendor
  limit) needs a source checked this session, cited in the option; otherwise
  mark the option `unverified` and say what would check it. Never state such
  a fact from memory as settled.
- One question per turn. If multiple ambiguities exist, rank them by
  blocking priority — which one would halt implementation if left unresolved?
  Present the highest-priority question first. After the user answers, check
  whether any remaining ambiguities still need resolution before proceeding.
- Do not resolve the question. Stop and wait.
- Keep options materially different; do not pad with strawmen.
- Reject these question shapes outright — each drops the required structure and
  pushes the analysis back onto the user: a bare open question ("How would you
  like me to handle X?"), a yes/no with no stated consequence, and a prose
  paragraph that buries the choice in narrative. Every option carries pros,
  cons, and impact even when the answer looks obvious.
- If you cannot name a real con for an option, you have not understood it
  yet — restate.
- Write the context, question and every option so they read correctly with
  the dialog seen alone. Never cite a workflow item by number or code
  (decision, requirement, question, milestone, item, step or finding: "Decision
  13", "Q7", "M3", "item 6"); say in plain words what it is. Cite the artifacts
  each option affects only in its `Affects:`, as path:line.
- Two options is the default; add a third only when it is materially
  different.
- A terse free-text reply ("go", "ok") approves the recommended option
  only when that option is low-impact, in-repo and reversible. An option
  that creates a tracked doc, edits the project guide (`AGENTS.md`,
  `CLAUDE.md`, `GEMINI.md`) or reaches outside the repo needs an explicit
  pick by name; re-ask naming the options.
- After the user resolves a choice, record it as a durable decision.
- Render the question and options as a structured interactive choice through
  the host's choice UI when one is available (for example, `AskUserQuestion`
  in Claude Code; equivalents in other agentskills.io clients). Free-form
  bulleted text lists push the typing burden onto the user and obscure the
  recommended option. Fall back to numbered text options only when no choice
  UI exists in the current host.
- Map the shape onto the choice UI's fields; nothing may drop out. Put context
  and why-it-matters in the reply text before the call. The question field
  ends with `Default if no reply: <option or stop>`. Each option description
  carries `Pros:`, `Cons:` and `Locks in:`, plus `Affects:` with path:line
  when an artifact changes; the recommended option's label ends with
  `(Recommended)` and its description gives the confidence. Ask one question
  per call. In Claude Code an installed MiniMe hook rejects calls that miss
  these markers or cite a workflow item by number outside `Affects:`.

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
