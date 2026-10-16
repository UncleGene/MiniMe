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
different paths. Do not resolve the question — stop and wait.

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

- **Question:** one sentence.
- **Why it matters:** reversibility, blast radius, what gets locked in.
- **Options:** minimum two, each with:
  - Name, pros, cons, cost, what it locks in.
- **Recommendation:** one option with confidence (low/medium/high).
- **Default if no reply:** stop or the recommended option.

## Rules

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
- Cite the artifacts each option affects (path:line or document section).
- Two options is the default; add a third only when it is materially
  different.
- After the user resolves a choice, record it as a durable decision.
- Render the question and options as a structured interactive choice through
  the host's choice UI when one is available (for example, `AskUserQuestion`
  in Claude Code; equivalents in other agentskills.io clients). Free-form
  bulleted text lists push the typing burden onto the user and obscure the
  recommended option. Fall back to numbered text options only when no choice
  UI exists in the current host.

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
