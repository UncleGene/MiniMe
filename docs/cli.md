# CLI

`scripts/minime` is a dependency-free Python CLI for MiniMe's local skill
catalog, validation helpers, host installation and user-level hooks (Python
3.14+). All commands are read-only unless `--write` is passed explicitly.
`skills install --write`,
`git-hook install|uninstall --write` and `claude-hook|codex-hook install|uninstall --write`
are the only write commands, all at user level; consuming repositories are not edited. Installer metadata/path
admission and contamination preflight run before writes; nested destination
symlinks/non-file paths block the batch. Installation and registration audit
compare generated metadata against current source-derived output.

### `scripts/minime doctor`

Read-only status report; it does not validate the environment.

```sh
scripts/minime doctor
```

Prints the MiniMe version, Python runtime, repo path, write posture, and status.

### `scripts/minime transparent-audit --repo <path>`

Audits one or more product repos for transparent MiniMe consumption.

```sh
scripts/minime transparent-audit --repo /path/to/product-repo
scripts/minime transparent-audit --repo /path/to/repo-a --repo /path/to/repo-b --json
```

Behavior:

- Reads target repos without writing to them.
- Blocks textual MiniMe references.
- Blocks symlinks that point to MiniMe.
- Blocks known MiniMe skill names in inspected text; renamed copied bodies are not detected.
- Skips common generated/vendor directories such as `.git`, `node_modules`,
  `.venv`, `vendor`, `dist`, and `build`.
- Reads at most 512,001 bytes per regular file, inspecting the first 512,000
  bytes decoded as UTF-8 with replacement for invalid sequences.
- Excludes binary files (NUL in the first 2,048 bytes), non-regular files and
  symlink contents. Symlink targets are checked without following their contents.
- Oversized text, file/entry/symlink access failures and directory traversal
  errors produce `inspection-incomplete` findings and block the repo and overall
  result (exit 1). Detectable references in a truncated prefix are still reported.
- A pass means no findings within this inspection scope. It does not establish
  complete isolation; manually review instructions for renamed workflow copies.

### `scripts/minime host-registration-audit`

Audits host/user-level MiniMe skill registration without reading or writing any
product repo.

```sh
scripts/minime host-registration-audit
scripts/minime host-registration-audit --skills-root /path/to/host/skills --json
```

Behavior:

- Defaults to the first existing skills root in the host table
  (`~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`,
  `~/.copilot/skills`).
- Use `--skills-root` to audit a specific surface.
- Verifies every `target-reusable` skill has a host-level `minime-*` wrapper
  directory containing a regular installed `SKILL.md` file and
  `agents/openai.yaml`.
- Verifies installed `SKILL.md` content matches the matching MiniMe skill file,
  and that installed `references/` holds exactly the source references.
- Blocks symlinked `SKILL.md` wrappers because current Codex user-skill
  discovery does not load them.
- Blocks extra `minime-*` host entries that are not in the target-reusable
  manifest.
- Requires generated metadata to match MiniMe's canonical output, including
  display name, short description and default prompt. Metadata links/nonfiles
  are blocked. Empty, malformed or different content is reported stale.
- A filesystem pass does not prove fresh host discovery or workflow outcomes.
- Writes nothing.

### `scripts/minime transcript-audit`

On-demand, read-only scan of local Claude Code and Codex transcripts for MiniMe
skill use, token cost and observable contract misfires (Decision 10).

```sh
scripts/minime transcript-audit
scripts/minime transcript-audit --since 2026-10-07 --json
```

Behavior:

- Reads `~/.claude/projects` and `~/.codex/sessions` (override with
  `--claude-root` / `--codex-root`); OpenCode and Copilot are not parsed.
- Counts MiniMe skill loads per skill: slash commands, Skill-tool calls,
  injected `<skill>` blocks, `$minime-*` mentions and reads of a `SKILL.md`.
- Flags, once per turn: `no-next-action`, `next-action-unformatted`,
  `prose-question` (Claude only), `commit-unverified` (no test or check command
  before the commit in that turn) and `commit-without-commit-skill`.
- Reports token counts (`input`, `cache_read`, `cache_write`, `output`) and
  their list-price cost (`cost_usd_micros`, millionths of a dollar):
  - per host, split between the main context and subagent transcripts
    (Claude Code only; Codex sessions all count as main);
  - for MiniMe turns, by `model/effort`;
  - per skill, summed over the turns that loaded it;
  - per host, for gated commit turns (main-context turns that loaded a commit
    skill and ran `git commit`), by `model/effort`, including the Claude Code
    subagents each turn started (REQ-010).

  Cost prices each request from a dated table in `scripts/minime` of published
  API list prices, which stand in for plan quota. The table covers each token
  type, Claude Code's 5-minute and 1-hour cache writes, and the prompt-size
  tiers of Claude Haiku 5.5 (over 100K) and the OpenAI models (over 272K).
  Models missing from the table, and Claude fast mode or non-global routing,
  cost 0 and are listed per host as `unpriced_models`; update the table when
  prices or models change.

  A turn that loads several skills counts toward each one, so per-skill totals
  overlap. A turn is one user prompt and all the work that follows it, so the
  figures attribute cost coarsely. Claude Code turns and Codex tasks also differ
  in size, so compare a host with itself over time, not with the other host.
  Claude Code records that repeat a message's usage are counted once; Codex
  usage comes from increases in its cumulative totals.
- Counts gate blocks per host: slop-scan blocks in the output of a commit
  command, and turns with a blocking `Verdict: fix` or `Verdict: route` line; a
  forked review counts once, on the main turn that started it.
- Excludes `review-eval` runs, recognized by a prompt that starts with the
  review-eval prompt, and the subagents they fork; their count is reported per
  host.
- `--since` takes a date or a datetime; a datetime with an offset is converted
  to UTC, the time zone of transcript timestamps.
- Findings are heuristics; verify each one in the transcript before acting.
- Projects are reported as `project-N` and sessions as an 8-character id. No
  paths or message text are printed. Writes nothing.

### `scripts/minime review-eval`

Scores headless reviews of planted-defect fixtures (Decisions 9/11).

```sh
scripts/minime review-eval --host claude
scripts/minime review-eval --host claude --skill doc-check --run --model sonnet
scripts/minime review-eval --host codex --run --json
scripts/minime review-eval --host claude --run --model <model> --effort <level> --layer python
scripts/minime review-eval --host codex --run --tier hard --model <model>
```

Behavior:

- `--skill` picks the skill scored: `code-reviewer` (default) on
  `evals/review/`, or `doc-check` on `evals/doc-check/`, whose defects are
  stale lines, often in documents the change left untouched (Decision 14).
- Fixtures live in `evals/<skill root>/<layer>/`. Each layer has a `base/` project,
  and each fixture has a `change/` overlay plus an `expected.json` answer key.
  Defect keys locate the planted defect by a text snippet, or list several
  planted defects under `defects`. Controls carry no defect. An `uncovered` key
  expects the review to report the stack as having no profile. `"tier": "hard"`
  marks fixtures built to tell model tiers apart (larger diffs, several defects,
  plausible invented APIs, tests that pass without the change); `--tier` runs
  one tier only.
- Without `--run`, it lists the fixtures and invokes nothing. With `--run`, it
  copies each base and overlay into a temporary git repo, so the change is the
  uncommitted diff. It then runs one review per fixture, in parallel (`--jobs`,
  default 4):
  - Claude Code: `claude -p`, restricted to read, search, skill and `git diff`
    tools.
  - Codex: `codex exec -s read-only --ephemeral`.

  Every run spends host plan quota, and fixture files are never modified.
- The review must end with a JSON block of findings. A defect is found when a
  finding names its file within 3 lines of the snippet. A fixture is
  `detected` when every planted defect is found and `partial` when only some
  are; layer totals count defects, not fixtures. A control with
  any blocking finding is a `false-positive`; its `blocking` list gives each
  finding's file, line and summary so the cause can be checked. Unreadable replies are
  `unparsed`.
- The scored skill is the installed host skill, so run `skills install --write`
  first.

### `scripts/minime git-hook install|uninstall`

Installs or removes the user-level slop-scan pre-commit hook (Decision 12).

```sh
scripts/minime git-hook install
scripts/minime git-hook install --write
scripts/minime git-hook uninstall --write
```

Behavior:

- Install copies `scripts/slop-scan` to `~/.config/minime/git-hooks/pre-commit`,
  adds a pass-through for every other standard hook that runs the
  repository's own `.git/hooks/<name>`, and sets the global `core.hooksPath`.
  Nothing is written into any repository. It refuses to replace a global
  `core.hooksPath` that points elsewhere.
- The scan blocks a commit when added lines in staged Python, JS/TS or Ruby
  files contain any of:
  - `TODO`, `FIXME` or `XXX`, or `NotImplementedError`;
  - skipped or focused tests;
  - blanket suppressions (`# type: ignore` or `# noqa` without a code,
    `@ts-ignore`, `@ts-nocheck`, and `eslint-disable` or `rubocop:disable`
    without a `-- reason`);
  - debugger calls.

  After a clean scan, it runs the repository's own pre-commit hook.
- Exempt paths with the `-slop-scan` git attribute. Bypass a single commit
  with `SLOP_SCAN=off` or `git commit --no-verify`.
- A repository that sets its own `core.hooksPath`, such as husky or
  pre-commit, overrides the global setting, so the scan does not run there.
- Uninstall unsets `core.hooksPath` only if it points to this directory.

### `scripts/minime claude-hook install|uninstall`

Installs or removes the user-level Claude Code commit gate (Decision 13).

```sh
scripts/minime claude-hook install
scripts/minime claude-hook install --write
scripts/minime claude-hook uninstall --write
```

Behavior:

- Install copies `scripts/commit-gate` to
  `~/.config/minime/claude-hooks/commit-gate` and adds a `PreToolUse` hook
  for `Bash` and a `Stop` hook to `~/.claude/settings.json`. Other settings
  and hooks are kept, reinstalling does not add second entries, and an
  unreadable settings file is refused. Uninstall removes only those entries
  and the copied script.
- Before each Bash call, the gate checks for a `git commit` command. It blocks
  the commit (exit 2, with a message to the agent) when the session has loaded
  a MiniMe skill but the current turn has not loaded `minime-project-commit` or
  `minime-self-commit`. Loads count through the Skill tool, a slash command, an
  injected `<skill>` block or `$minime-*` mention (Codex), or a Read or
  `cat`/`sed`-style read of the skill's `SKILL.md` that starts a shell segment.
  A Codex turn starts at its `task_started` event. Detection is textual: a
  command that contains a complete read command as data, such as a heredoc,
  can still count as a load.
- Sessions that never loaded a MiniMe skill, commands that only mention
  `git commit` (including in a heredoc body, unless a shell, `eval`, `source`
  or `.` on the `<<` line may run it), and unreadable transcripts pass.
- Before blocking, the gate re-reads the transcript for up to 2 seconds,
  because a skill read sent in the same parallel batch as the commit can reach
  the transcript after the hook starts.
- When a turn ends, the `Stop` hook blocks once (exit 2, with a message to the
  agent) if the turn loaded a MiniMe skill and its last main-thread reply does
  not contain `Recommended next action`. It does not block again while the
  agent is continuing from that block (`stop_hook_active`).

### `scripts/minime codex-hook install|uninstall`

Installs or removes the same commit gate for Codex (Decision 13).

```sh
scripts/minime codex-hook install --write
scripts/minime codex-hook uninstall --write
```

Behavior:

- Same as `claude-hook` without the `Stop` hook, with the script in
  `~/.config/minime/codex-hooks/commit-gate` and the entry in
  `~/.codex/hooks.json`.
- Codex runs a user-level hook only after you trust it in `/hooks`, and again
  after its definition changes.

### `scripts/minime skills list`

Lists local MiniMe skills from `skills/*/SKILL.md`.

```sh
scripts/minime skills list
scripts/minime skills list --kind internal
scripts/minime skills list --kind target-reusable
scripts/minime skills list --json
```

Shows `name`, `minime_kind`, `path`, and `description` for each skill. Human
output includes a `Blocked entries` section for skills with invalid or missing
frontmatter metadata. `--json` includes both valid `skills` and
`blocked_entries` with stable error codes.

### `scripts/minime skills install`

Install MiniMe skills as wrapper directories for universal host-level routing.
Dry-run by default; `--write` required to apply changes.

```sh
scripts/minime skills install
scripts/minime skills install --write
scripts/minime skills install --write --force
scripts/minime skills install --json
```

Behavior:

- Discovers all `target-reusable` skills via the catalog.
- Without `--skills-root`: installs to every known surface that exists —
  `~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`,
  `~/.copilot/skills`. `~/.agents/skills` is intentionally
  excluded because current Codex scans it in addition to `~/.codex/skills`,
  which duplicates every MiniMe skill in Codex.
- `--skills-root <path>` restricts installation to a single explicit surface.
- Blocks the entire batch when any catalog entry has invalid metadata/source
  paths, or a reusable source fails local-path/secret-pattern contamination checks.
- Catalog and preflight require a 1–64 character lowercase ASCII alphanumeric
  name with single separating hyphens, matching its directory; description must
  be nonempty and at most 1024 characters. Duplicate fields are rejected.
- The narrow parser supports plain scalars, single-quoted name/description and
  JSON double-quoted name/description; general YAML/multiline blocks are not
  supported. Quoted empty descriptions remain invalid.
- Validates all selected surface roots and wrapper destinations before writing.
  A destination rejection cancels all writes, including earlier surfaces.
- Blocks symlinked `agents/` or `agents/openai.yaml` and incompatible path types,
  even with `--force`. Metadata updates replace the file so hardlinked sibling
  files are not overwritten. Supported wrapper/SKILL.md link migrations unlink
  the link itself, preserving its target.
- Prevalidation covers known invalid inputs; unexpected I/O failures/concurrent
  filesystem mutation do not have a transactional rollback guarantee.
- Without `--write`: prints what would be created, updated, skipped, or blocked.
- With `--write`: creates wrapper directories in each surface root. Each wrapper
  contains a regular installed `SKILL.md` file, a generated
  `agents/openai.yaml` for agent compatibility, and a copy of the skill's
  `references/` when it has one. In a `.claude/skills` root, a skill whose
  metadata declares `minime_context: fresh` gets `context: fork`,
  `background: false` and `model: sonnet` (tier `fast`) or `inherit` added to
  its frontmatter, so Claude Code runs it in a subagent; the registration audit
  expects the same text. References must be regular `.md` files in a
  flat directory. Installed references are MiniMe-owned: stale or extra files
  are replaced or removed.
- Metadata-only drift is refreshed without `--force`. Generated metadata is
  MiniMe-owned: byte differences, including local edits or alternate formatting,
  are stale. Dry-run reports an update; repeated writes are idempotent.
- Re-running with `--write` updates stale installed `SKILL.md` files and
  converts MiniMe's older symlinked `SKILL.md` wrappers to regular files.
- `--force`: migrate old-format directory symlinks and overwrite stale entries.
- Old-format directory symlinks (pre-wrapper-dir) are reported as conflicts
  until migrated with `--write --force`.

### `scripts/minime skills install-check <skill-path>`

Dry-run preflight check for skill installation. Accepts a skill directory or a
direct `SKILL.md` path:

```sh
scripts/minime skills install-check skills/minime-agent-orchestrator
scripts/minime skills install-check skills/minime-agent-orchestrator/SKILL.md
scripts/minime skills install-check skills/minime-agent-orchestrator --json
```

Behavior:

- Blocks `metadata.minime_kind: internal` skills; only `target-reusable` is
  eligible.
- Requires the canonical `skills/<name>/SKILL.md` path, matching validated name
  and nonempty description; rejects outside paths and source symlinks.
- Runs contamination checks for local paths and secret-looking tokens on
  `SKILL.md` and every file in `references/`.
- Redacts secret-looking token details, including local-path snippets and metadata errors.
- Writes nothing.

### `scripts/minime skills similar <skill-path>`

Read-only analog search. Ranks local target-reusable skills by token overlap
against a source `SKILL.md`. Used during the generalization workflow to surface
existing analogs before adapting an external skill.

```sh
scripts/minime skills similar skills/minime-agent-orchestrator
scripts/minime skills similar /path/to/other/skills/debugger/SKILL.md
scripts/minime skills similar /path/to/other/skills/debugger --json
```

Behavior:

- Accepts a directory containing `SKILL.md` or a direct `SKILL.md` path.
- Accepts paths outside the MiniMe repo (unlike `install-check`); no
  contamination gate runs because nothing is installed or copied.
- Loose frontmatter parse: extracts `name:` and `description:` only — does not
  require `minime_kind` so external skills are accepted.
- Scoring: Jaccard similarity on lowercased alphanumeric tokens (length >= 3)
  drawn from name + description; common English and skill-vocabulary stopwords
  filtered.
- Prints up to five matches with `score > 0`; prints "No similar skills found."
  when none qualify. `--json` includes the full ranked list under `matches` and
  the full source descriptor under `source`.
- Writes nothing.

## Test Suite

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
```
