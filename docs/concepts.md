# Concepts and current architecture

MiniMe is a host-level engineering skill library. Its goals are an anti-slop,
production-quality bar (REQ-003), cost-appropriate execution ranked below
quality (REQ-010), and host portability (REQ-004/011). Scope is governed by
[decisions](decisions.md) and [requirements](requirements.md).

## Components and data flow

1. `skills/minime*/SKILL.md` contains procedures and routing descriptions.
   `metadata.minime_kind` distinguishes target-reusable skills from internal
   generalization/commit procedures. Skills are single files, except that
   `minime-code-reviewer` ships a stack marker table and layer slop profiles in
   `references/`, loaded for each matching stack (Decision 11). Each reusable skill ends with an
   identical `## Interaction rules` section (Decision 6), so installed skills
   carry the shared contract into consumer sessions.
2. `scripts/minime` is a stdlib Python CLI for cataloging, preflight,
   host installation, user-level hooks and audits. Python 3.14+ is required.
   Read-only is the default; every write requires `--write`.
3. Host installation copies reusable `SKILL.md` files, and any flat
   `references/*.md`, into wrapper directories with generated
   `agents/openai.yaml`. Host roots are Codex
   `~/.codex/skills`, Claude Code `~/.claude/skills`, OpenCode
   `~/.config/opencode/skills` and GitHub Copilot `~/.copilot/skills`. Default
   installation uses existing roots; an explicit `--skills-root` selects one
   existing directory. Internal skills stay here. Into `~/.claude/skills`,
   a skill whose metadata declares `minime_context: fresh` is installed with
   `context: fork`, `background: false` and its tier's model, so Claude Code
   runs it in a subagent (Decision 14). One host-capability table in
   `scripts/minime` (`HOSTS`) holds each host's skills root, transcripts,
   choice UI, fork adapter, headless command and hooks; the installer, audits,
   `review-eval` and hook installers read it, so a new host is one entry
   (REQ-011).
4. Hosts discover descriptions, load procedures, and execute them against the
   consuming project's own requirements and guide. MiniMe does not provide a
   workflow engine or enforce natural-language compliance.
5. Tests exercise CLI behavior and instruction contracts. Filesystem registration
   checks do not prove fresh host discovery or correct engineering outcomes.

The CLI/catalog boundary is adequate for the current scale. Installation shares
source validation with the catalog and prevalidates all install destinations
before writing. Installation and registration audit compare generated metadata
with the same canonical source-derived output. Python is supporting tooling for
the Markdown skill library (Decision 5). No plugin framework, routing service,
telemetry system or module split is needed.
Links: REQ-001/004/007/008; Decisions 5/9.

## Consumption boundary

For any product repo consuming MiniMe skills:

- No repo-local MiniMe references.
- No pointer files or generated bootstrap files.
- No symlinks to MiniMe or copied MiniMe workflow bodies.
- No project-guide section whose purpose is MiniMe routing.

Product repositories retain product/domain behavior and local development
policy. Agents using host skills may make authorized product changes. This is
separate from MiniMe CLI writes: user-level installation of host skills, the
slop-scan git hook and the agent commit gate (Claude Code and Codex) are the
only write commands (Decisions 12/13).
Links: REQ-002/004; Decision 3.

## Artifact classification

These categories guide manual review; they are not a current CLI classifier.

| Class | Meaning | Action |
|---|---|---|
| `product-essential` | Product behavior, domain safety or business rules. | Keep in the product repo. |
| `repo-policy` | Local development policy. | Keep in the project guide. |
| `portable-process` | Reusable engineering workflow. | Consider improving the existing MiniMe owner. |
| `contaminated` | Workflow mixed with project assumptions. | Clean or split before reuse. |
| `obsolete` | Superseded behavior. | Retire through an accepted decision. |

## Validation limits

Catalog, preflight and installation share canonical source-path and metadata
validation: required safe name/directory agreement, nonempty bounded description,
no duplicate fields and supported kind. Preflight and installation also check
local-path/secret-looking-token patterns. Installer destination prevalidation
blocks unsafe nested symlinks/types across all selected surfaces before writes;
metadata replacement avoids overwriting hardlinked sibling files. Supported
symlink migrations remove the link itself. This is prevalidation, not a rollback
system for runtime I/O failures/concurrent changes.

Human review must assess product assumptions, business rules, external services
and side-file dependencies. The CLI's flat scalar parser is a limited subset
of YAML; it does not validate semantic portability or every standard field.

`transparent-audit` checks text references/skill names and MiniMe-pointing
symlinks in inspected files. It reads at most 512,001 bytes per regular file,
inspecting the first 512,000 bytes. Oversized text and access/traversal failures
produce blocking `inspection-incomplete` findings. Generated/vendor directories,
binary files (NUL in the first 2,048 bytes), non-regular files and symlink contents
are intentional exclusions. A pass covers these signals within this scope;
renamed copied bodies still require manual review of consumer instructions.
Links: REQ-002; TransparentAuditCoverageTests.

`host-registration-audit` checks wrapper presence, `SKILL.md` and
`references/` freshness and
canonical generated metadata content; linked/non-file metadata paths are blocked.
Generated metadata is MiniMe-owned, so local changes or alternate formatting
are stale and installation regenerates the file.
Audit each surface explicitly. Check fresh discovery when diagnosing host setup
or compatibility; registration alone does not prove execution.

`transcript-audit` parses local Claude Code and Codex transcripts on demand. It
reports token counts by host, context (main or subagent), model and effort,
skill and gated commit turn, priced from a dated list-price table, plus
slop-scan and blocking-review gate blocks (REQ-010). It excludes `review-eval`
runs. Its findings are heuristics about observable contract markers (next
action, choice UI, checks before commit, commit skill loaded); they cannot show
whether a skill's judgment was right. Unknown record shapes are skipped, so a
host format change shows up as falling counts rather than errors.
Links: REQ-009/010; Decision 10.

`review-eval` runs the installed reviewer, or `minime-doc-check`, headlessly on
planted-defect fixtures in temporary git repos. It scores detection, false
positives on controls, and uncovered-stack warnings; doc-check's planted
defects are stale document lines. Scoring is by file and line proximity, so a
finding reported at the wrong place counts as missed. The results measure the
skill on these fixtures, not on every project.
Links: REQ-003/010; Decisions 9/11/14.

Two user-level hooks enforce the mechanical part of the bar without touching
consuming repos. `scripts/slop-scan` runs as a global pre-commit hook through
`core.hooksPath` and then hands off to the repository's own hook.
`scripts/commit-gate` runs as a Claude Code or Codex `PreToolUse` hook and
blocks an agent's `git commit` until the commit skill is loaded in that turn;
in Claude Code it is also a `Stop` hook that keeps a MiniMe turn from ending
without a recommended next action.
Both are copied to `~/.config/minime/` so they run without the MiniMe repo.
Links: REQ-003; Decisions 12/13.

## Existing skill drift guards

The current `test_target_reusable_skills_are_token_conscious` check enforces a
15,000-byte file ceiling, body word count at most four times the catalog median,
and fewer than two transcript-like step headers, alongside emoji/filler checks.
Despite its name, its current file enumeration includes internal skills. The
median is calculated from the current catalog on each run, so a fixed numeric
word ceiling is not authoritative. Descriptor Jaccard overlap at or above 0.20
is a separate DRY review trigger, not proof that responsibilities are duplicates.
Review these policies using observed problems and user feedback.
Links: REQ-007/008; TokenConsciousSkillTests; CatalogDRYTests.

