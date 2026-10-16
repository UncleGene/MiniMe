# Transparent Consumption Verification Report

Date:
Agent:
Host/model/version:
Verdict: `PASS` / `FAIL` / `BLOCKED`

Optional diagnostic record for host setup or compatibility issues. A registration
pass does not imply fresh discovery or task completion. This template records
technical behavior; usefulness is judged by continued use (Decision 9).

## Product repo

Repo/commit:
Worktree status before/after:
Diagnostic scope:

## Host registration

Selected surface and command/result:

```sh
scripts/minime host-registration-audit --skills-root <host-skills-root> --json
```

Required surfaces: Codex `~/.codex/skills`, Claude Code `~/.claude/skills`,
OpenCode `~/.config/opencode/skills`, GitHub Copilot `~/.copilot/skills`.
Record checked skills and findings; do not infer other surfaces from the default.

## Fresh session

Fresh-session command or host action:
Observed skills and discovery evidence:
Skills activated and procedure execution evidence:
Missing workflow roles or host-specific blockers:

## Task outcomes

Optional observed task and expected behavior:
Observed result and verification output:
Host-specific execution failures or limitations:

## Product repo isolation

Transparent audit command/result:

```sh
scripts/minime transparent-audit --repo <product-repo> --json
```

Manually reviewed instruction files and renamed-copy check:
Skipped/unreadable/large-file coverage limits:
Repo-local MiniMe references, pointers, symlinks or copied workflow bodies:
Files changed by the authorized task versus discovery/isolation verification:

## Decision

Can this host discover and consume skills transparently for the diagnostic scope?
Result/rationale:
Remaining evidence gaps and next action:
