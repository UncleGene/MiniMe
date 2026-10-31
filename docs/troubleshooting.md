# Troubleshooting

## `MINIME_E_FRONTMATTER_MISSING`

Problem:
  A `SKILL.md` file does not start with a frontmatter delimiter.

Fix:

```md
---
name: minime-example
description: Short skill description.
metadata:
  minime_kind: target-reusable
---
```

## `MINIME_E_FRONTMATTER_MISSING_KIND`

Problem:
  A skill has no `metadata.minime_kind`.

Fix:

```md
metadata:
  minime_kind: internal
```

or:

```md
metadata:
  minime_kind: target-reusable
```

## `MINIME_E_FRONTMATTER_UNKNOWN_KIND`

Problem:
  A skill declares a kind MiniMe does not recognize.

Fix:
  Use exactly `internal` or `target-reusable`.

## `MINIME_E_INSTALL_WRONG_KIND`

Problem:
  `skills install-check` received an internal MiniMe skill.

Cause:
  Only `target-reusable` skills are eligible for install preflight.

Fix:

```sh
scripts/minime skills list --kind target-reusable
scripts/minime skills install-check skills/minime
```

## `MINIME_E_INSTALL_OUTSIDE_REPO`

Problem:
  The skill path resolves outside the MiniMe repo.

Cause:
  MiniMe blocks outside paths for local safety.

Fix:

```sh
scripts/minime skills install-check skills/minime
```

## `MINIME_E_INSTALL_SYMLINK`

Problem:
  The skill path or `SKILL.md` file is a symlink.

Cause:
  MiniMe rejects symlink escapes before reading installable skills.

Fix:
  Use a real `skills/<name>/SKILL.md` file inside this repo.

## Metadata admission errors

- `MINIME_E_FRONTMATTER_NAME`: provide a 1–64 character lowercase ASCII
  alphanumeric name with single separating hyphens.
- `MINIME_E_FRONTMATTER_NAME_MISMATCH`: make `name` match its skill directory.
- `MINIME_E_FRONTMATTER_DESCRIPTION`: provide a nonempty description of at most
  1024 characters. Quoted empty strings are also invalid.
- `MINIME_E_FRONTMATTER_DUPLICATE`: keep one value per field.
- `MINIME_E_FRONTMATTER_MALFORMED`: use supported flat scalar syntax;
  name/description may be plain, single-quoted or JSON double-quoted strings.

Catalog reports blocked source entries. Installation rejects the whole batch
until they are resolved; run `skills list --json` to locate them.

## `MINIME_E_INSTALL_CONTAMINATION`

A reusable source failed local-path/secret-pattern preflight. Run
`skills install-check <skill-path> --json` for redacted findings and clean the
source before retrying. No selected host surface is written when this fails.

## Blocked installer destinations

Symlinked metadata directories/files and incompatible path types are blocked
without writes. Restore ordinary `agents/` and `agents/openai.yaml` paths.
`--force` permits supported wrapper/SKILL.md link migration; it cannot bypass
unsafe metadata destinations. A blocked destination cancels the whole batch.

## Stale generated metadata

`host-skill-stale-openai-yaml` means `agents/openai.yaml` differs from MiniMe's
canonical generated output, including empty/malformed content or local edits.
Run `scripts/minime skills install --write` to regenerate it, then repeat the
audit. A dry-run reports the planned update; `--force` is unnecessary for
ordinary wrapper files. `host-skill-unsafe-openai-yaml` requires restoring
ordinary metadata paths first; the installer blocks links/nonfiles.

## Leftover skill wrappers

`host-skill-extra` means a host root still holds a `minime` or `minime-*` wrapper for a
skill that is no longer in the catalog, usually after a skill was merged or
retired. Hosts keep loading it until it is removed. `skills install` does not
delete wrappers. Confirm the wrapper holds only MiniMe-generated `SKILL.md` and
`agents/openai.yaml`, remove that directory from each host root, then repeat
the audit for every root.
