# Reports

Commands that take `--json` print a structured report.

## Skill Catalog Report

Produced by:

```sh
scripts/minime skills list --json
```

Important fields:

- `schema_version`
- `skills_directory`
- `skills`
- `blocked_entries`

Each skill includes:

- `name`
- `path`
- `minime_kind`
- `description`

Each blocked entry includes:

- `path`
- `error_code`
- `error`

## Transparent Audit Report

Produced by:

```sh
scripts/minime transparent-audit --repo /path/to/product-repo --json
```

Important fields:

- `schema_version`
- `command`
- `mode`
- `routing`
- `target_repo_writes`
- `product_repo_references_required`
- `target_reusable_skills`
- `blocked_entries`
- `repos`
- `result`

Each repo includes:

- `repo`
- `result`
- `findings`

Each finding includes:

- `type`
- `path`
- `detail`
- `severity`
- `line` when available

`inspection-incomplete` findings identify oversized text or an entry, file,
directory or symlink that could not be inspected. Their `path` and `detail`
identify the coverage gap without echoing file contents or exception messages.
They use `severity: blocked` and set both repo and overall `result` to `blocked`
(exit 1), using the existing report fields. Findings from inspected prefixes
remain present. `pass` covers only the scope described in [the CLI reference](cli.md#scriptsminime-transparent-audit---repo-path);
intentional exclusions and renamed workflow copies are not isolation proof.

## Host Registration Audit Report

Produced by:

```sh
scripts/minime host-registration-audit --json
```

Important fields:

- `schema_version`
- `command`
- `mode`
- `routing`
- `host_skills_root`
- `target_repo_writes`
- `product_repo_references_required`
- `target_reusable_skills`
- `checked_skills`
- `blocked_entries`
- `findings`
- `result`
- `minime_root`

Each checked skill includes:

- `name`
- `host_path`
- `expected_skill_md`
- `result`

Each finding includes:

- `type`
- `path`
- `detail`
- `severity`

Registration findings include `host-skill-stale-openai-yaml` for generated
metadata differing from canonical output, and `host-skill-unsafe-openai-yaml`
for metadata links/non-file paths. Details do not echo installed content.

## Host Install Report

Produced by `scripts/minime skills install --json` (dry-run) or with `--write`.
`mode` records the requested mode. `surfaces` and `surface_results` list selected
roots and per-skill `actions`; summary counts are `created`, `updated`, `exists`
and `conflicts`. `updated` includes supported migrations.

Dry-run actions describe planned changes. A write request with a rejected
source fails before installation; a rejected destination cancels the batch and
marks other planned changes `blocked`, with no created/updated count. Existing
unchanged wrappers can still report `exists`. Block details explain the rejection.

## Install-Check Report

Produced by:

```sh
scripts/minime skills install-check skills/minime --json
```

Important fields:

- `schema_version`
- `command`
- `mode`
- `skill_name`
- `minime_kind`
- `skill_path`
- `contamination_findings`
- `result`

## Transcript Audit Report

Produced by:

```sh
scripts/minime transcript-audit --json
```

Important fields:

- `schema_version`, `command`, `mode`, `since`
- `hosts`: per host `sessions`, `sessions_with_minime`, `minime_turns`
- `skill_loads`: loads per MiniMe skill
- `finding_counts`: findings per type
- `findings`: `type`, `host`, `project` (placeholder), `session` (short id),
  `turn`, `timestamp`, `detail`

Reports must not be committed (Decision 8); placeholders are stable only
within one run.
