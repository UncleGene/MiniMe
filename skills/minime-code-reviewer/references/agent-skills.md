# Agent skills and instructions slop profile

Applies to `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and their
references, in addition to the generic slop checks.

- Descriptions that restate the name, give no trigger, or trigger so broadly
  that they load for adjacent requests. A changed description without
  positive, negative and forbidden-load examples.
- Rules nobody can check, such as "be thorough" or "ensure quality", with no
  command, criterion or output field.
- Filler, greetings, emojis, and steps that read like a session transcript.
- Procedure copied from another skill instead of delegating to it by name, and
  rules that contradict another skill or the project guide.
- Host-specific syntax or paths in a skill meant to be portable, without a
  fallback for other hosts.
- References to skills, commands, flags or paths that do not exist.
- Bloat: material that only some runs need belongs in a reference loaded on
  demand. Each sentence must pass "would the agent get this wrong without it?"
- A step with no exit condition, or a pause that asks the user to approve a
  gate that is already mandatory.
- Instruction files with stale commands or claims the code no longer supports.
