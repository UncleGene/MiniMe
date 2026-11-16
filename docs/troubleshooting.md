# Troubleshooting

MiniMe errors print a code such as `MINIME_E_INSTALL_BLOCKED`, a message and a
suggested fix. Find the code or the symptom below.

- [Installation](#installation)
- [Skill metadata errors](#skill-metadata-errors)
- [Registration audit findings](#registration-audit-findings)
- [Hooks](#hooks)

## Installation

**`MINIME_E_INSTALL_NO_SURFACES`: no host skills folder exists.**
`skills install` writes only into host folders that already exist. Create the
folder for each host you use, for example `mkdir -p ~/.claude/skills`, then
retry.

**`MINIME_E_INSTALL_HOST_ROOT_MISSING` or `MINIME_E_INSTALL_HOST_ROOT_NOT_DIR`.**
The folder given with `--skills-root` does not exist or is not a folder.
Create it or fix the path.

**`MINIME_E_INSTALL_BLOCKED`: blocked skill entries.**
At least one skill in the clone has invalid metadata, so nothing is installed.
Run `scripts/minime skills list` to see which skill and why, then fix it (see
[Skill metadata errors](#skill-metadata-errors)). In an unmodified clone this
points to a broken checkout; run `git status`.

**`MINIME_E_INSTALL_CONTAMINATION`: a skill failed the privacy check.**
A skill contains a local path or a secret-looking token. Run
`scripts/minime skills install-check skills/<name> --json` for the redacted
findings, clean the skill and retry. No host folder is written when this
fails.

**Blocked destinations.**
The installer refuses symlinked `agents/` folders or `agents/openai.yaml`
files and unexpected file types inside a host folder, even with `--force`.
Replace them with ordinary folders and files, then retry. One blocked
destination cancels the whole batch.

**`MINIME_E_REFERENCES_UNSAFE`.**
A skill's `references/` path is not a plain folder. Replace it with a folder
of regular `.md` files.

**`skills install-check` and `skills similar` errors.**

| Code | Meaning | Fix |
|---|---|---|
| `MINIME_E_INSTALL_WRONG_KIND` | The skill is `internal`; only `target-reusable` skills install. | Check with `scripts/minime skills list --kind target-reusable`. |
| `MINIME_E_INSTALL_OUTSIDE_REPO` | The path resolves outside the MiniMe clone. | Pass a path under `skills/`. |
| `MINIME_E_INSTALL_SYMLINK` | The skill folder, a parent or `SKILL.md` is a symlink. | Use a real `skills/<name>/SKILL.md` file. |
| `MINIME_E_INSTALL_SKILL_NOT_FOUND` | No `SKILL.md` at that path. | Pass `skills/<name>` or `skills/<name>/SKILL.md`. |
| `MINIME_E_INSTALL_INVALID_PATH` | The file is not at `skills/<name>/SKILL.md`. | Same as above. |
| `MINIME_E_SIMILAR_NOT_FOUND` | `skills similar` found no `SKILL.md` at that path. | Pass a skill folder or its `SKILL.md`. |

## Skill metadata errors

Every `SKILL.md` starts with a frontmatter block like this:

```md
---
name: minime-example
description: Short skill description.
metadata:
  minime_kind: target-reusable
---
```

MiniMe reads it with a deliberately small parser: flat `key: value` lines,
with indented lines only inside `metadata:`. `name` and `description` may be
plain, single-quoted or JSON double-quoted; multi-line YAML is not supported.

| Code | Fix |
|---|---|
| `MINIME_E_FRONTMATTER_MISSING` | Start the file with a `---` line. |
| `MINIME_E_FRONTMATTER_UNCLOSED` | Close the block with a `---` line. |
| `MINIME_E_FRONTMATTER_NESTED` | Indent lines only inside `metadata:`. |
| `MINIME_E_FRONTMATTER_MALFORMED` | Use one `key: value` per line with supported quoting. |
| `MINIME_E_FRONTMATTER_DUPLICATE` | Keep one value per field. |
| `MINIME_E_FRONTMATTER_NAME` | Use 1–64 lowercase letters and digits, separated by single hyphens. |
| `MINIME_E_FRONTMATTER_NAME_MISMATCH` | Make `name` match the skill's folder name. |
| `MINIME_E_FRONTMATTER_DESCRIPTION` | Give a non-empty description of at most 1024 characters (`""` is empty). |
| `MINIME_E_FRONTMATTER_MISSING_KIND`, `MINIME_E_FRONTMATTER_EMPTY_KIND`, `MINIME_E_FRONTMATTER_UNKNOWN_KIND` | Set `metadata.minime_kind` to exactly `internal` or `target-reusable`. |

## Registration audit findings

`host-registration-audit` compares a host folder with the clone. Most findings
are fixed by `scripts/minime skills install --write`, then re-running the
audit.

**`host-skill-missing`, `host-skill-stale-skill-md`, `host-skill-stale-references`.**
The host folder is missing a skill or holds an old copy, usually after a
`git pull` without reinstalling. Reinstall. The other `host-skill-missing-*`
findings (a wrapper without its `SKILL.md` or `agents/openai.yaml`) are fixed
the same way.

**`host-skill-stale-openai-yaml`.**
`agents/openai.yaml` differs from what MiniMe generates, including local edits
or empty files. Reinstall; `--force` is not needed.

**`host-skill-unsafe-openai-yaml`.**
`agents/` or `agents/openai.yaml` is a link or not a regular file. Replace it
with an ordinary folder or file first, then reinstall.

**`host-skill-symlink-skill-md`.**
The skill's `SKILL.md` is a link left by an older MiniMe install. Reinstall;
`--write` replaces the link with a copy.

**`host-skill-old-format`.**
The whole skill folder is a link left by an older MiniMe install. Run
`scripts/minime skills install --write --force` to convert it to a folder of
copies.

**`host-skill-not-dir`, `host-skill-md-not-file`, `host-skill-wrong-target`.**
The skill entry, or its `SKILL.md`, is not the ordinary folder or file MiniMe
installs, or is a link pointing somewhere other than the clone. Remove the
entry, then reinstall.

**`host-skill-unsafe-references`.**
The skill's `references/` is a link or not a plain folder. Replace it with a
plain folder, or remove it, then reinstall.

**`host-skill-extra`: a leftover skill.**
The host folder still holds a `minime` or `minime-*` skill that no longer
exists in the clone, usually after a skill was merged or retired. Hosts keep
loading it until you remove it, and `skills install` never deletes folders.
Check that the folder holds only `SKILL.md`, `agents/openai.yaml` and
`references/`, delete it from each host folder, then re-run the audit for
every folder.

## Hooks

**`MINIME_E_GIT_HOOKS_PATH_IN_USE`: `git-hook install` refuses.**
Your global git `core.hooksPath` already points to another hooks folder.
MiniMe will not replace it. Either unset it
(`git config --global --unset core.hooksPath`) and retry, or run the clone's
`scripts/slop-scan` from the pre-commit hook in your own hooks folder.

**The slop scan does not run in one repository.**
That repository sets its own `core.hooksPath` (husky, pre-commit and similar
tools do), which overrides the global one. Add the scan to that tool's hooks
if you want it there.

**The slop scan blocks a commit you want to keep.**
Fix the flagged line, exempt the path with the `-slop-scan` git attribute in
`.gitattributes`, or skip one commit with `SLOP_SCAN=off git commit ...` or
`git commit --no-verify`.

**The agent's commit is blocked by "MiniMe commit gate".**
This is the gate working. The agent must load the commit skill and its check
skills in the same turn as the commit, then retry; the message names what is
missing. Staging chained to a blocked commit (`git add ... && git commit`) did
not run either, so the agent stages in its own call.

**The agent recommends `/clear` after a commit or a long break.**
This is the fresh-session nudge. Once a MiniMe session's context passes 300k
tokens, every request re-reads it, so a handoff and a fresh session usually
cost less. Run `/clear` and `/minime-orient`, or ignore it to keep the
session; it comes back after the next commit or the next resume past an
hour idle.

**The Codex commit gate never fires.**
Codex runs a user-level hook only after you trust it in `/hooks`, and again
after the hook changes.

**`MINIME_E_HOOK_SETTINGS_UNREADABLE`.**
`~/.claude/settings.json` or `~/.codex/hooks.json` is not valid JSON or has an
unexpected `hooks` shape. Fix the file, then retry; MiniMe never overwrites a
file it cannot read.

**`MINIME_E_GIT_HOOKS_UNSAFE` or `MINIME_E_AGENT_HOOK_UNSAFE`.**
The hook folder or copied script under `~/.config/minime/` is not a regular
folder or file. Remove it, then retry.
