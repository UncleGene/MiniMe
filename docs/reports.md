# JSON reports

Commands run with `--json` print one JSON report to standard output, for
scripts and agents. Two exceptions: `review-eval` without `--run` prints its
fixture list as text, and any error (invalid arguments or a `MINIME_E_*`
code) prints text to standard error with exit 2 and no JSON. Each report
carries a `schema_version`; this page lists the fields you can rely on.
Commands are described in the
[CLI reference](cli.md).

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

## Similar Skills Report

Produced by `scripts/minime skills similar <skill-path> --json`.

- `schema_version`, `command`, `mode`, `minime_version`
- `source`: `path`, `name`, `description`
- `scoring`, `catalog_size`
- `matches`: up to five skills with a positive `score`

## Review Eval Report

Produced by `scripts/minime review-eval --run --json`.

- `schema_version`, `command`, `skill`, `host`, `model`, `effort`, `tier`
- `summary`: per layer, `defects` and `detected`, `controls` and
  `false_positives`, and for stack-warning fixtures `uncovered` and `reported`
- `fixtures`: one entry per fixture with its `id` and `outcome`

The command exits 0 whenever the runs complete, even when fixtures were missed
or a host run failed; read `summary` and each fixture's `outcome`.

## Transcript Audit Report

Produced by:

```sh
scripts/minime transcript-audit --json
```

Important fields:

- `schema_version`, `command`, `mode`, `since`
- `hosts`: per host `sessions`, `sessions_with_minime`, `minime_turns`,
  `review_eval_sessions` and `tokens`
- `skill_loads`: loads per MiniMe skill
- `finding_counts`: findings per type
- `findings`: `type`, `host`, `project` (placeholder), `session` (short id),
  `turn`, `timestamp`, `detail`

Do not commit reports: they describe your local projects and sessions.
Placeholders such as `project-1` are stable only within one run.
