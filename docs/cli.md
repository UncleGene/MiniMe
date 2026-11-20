# CLI reference

`scripts/minime` is the MiniMe command-line tool: a single Python 3.14+ script
with no dependencies. Run it from your MiniMe clone.

Every command is read-only unless you pass `--write`. Only four commands
write, all to your user account and never to a project:
`skills install --write`, `git-hook install|uninstall --write`,
`claude-hook install|uninstall --write` and
`codex-hook install|uninstall --write`. Before writing, the installer
validates every skill and every destination, and it writes nothing if any
check fails. Most commands accept `--json`; see [JSON reports](reports.md).

| Command | Use it to |
|---|---|
| `doctor` | Show the MiniMe version, Python runtime and status. |
| `skills install` | Install or update the skills in your host folders. |
| `git-hook`, `claude-hook`, `codex-hook` | Install or remove the optional hooks. |
| `host-registration-audit` | Check that a host folder holds current skills. |
| `transparent-audit` | Check that a project carries no MiniMe trace. |
| `transcript-audit` | Scan local agent transcripts for skipped steps. |
| `skills list`, `skills install-check`, `skills similar` | Work on MiniMe's own skills. |
| `review-eval` | Score the reviewer on planted-defect fixtures (spends plan quota). |

## Install and update

### `scripts/minime doctor`

Read-only status report; it does not validate the environment.

```sh
scripts/minime doctor
```

Prints the MiniMe version, Python runtime, repo path, write posture, and status.

### `scripts/minime skills install`

Installs or updates the skills in your host skills folders. Without `--write`
it is a dry run that lists what would be created, updated, skipped or blocked.

```sh
scripts/minime skills install                  # dry run
scripts/minime skills install --write          # install or update
scripts/minime skills install --write --force  # also migrate old symlinked installs
scripts/minime skills install --skills-root ~/.claude/skills --write  # one folder only
```

What it installs:

- Every `target-reusable` skill, into every host folder that exists:
  `~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills` and
  `~/.copilot/skills`. `--skills-root <path>` installs into that one folder
  instead. Point it only at a user-level host folder, never at a folder
  inside a project: MiniMe must leave no files in your projects, and the
  command does not check this for you. `~/.agents/skills` is left out on purpose: Codex reads it as well
  as `~/.codex/skills`, so installing there would show every skill twice.
- Each skill becomes a folder holding a regular copy of its `SKILL.md`, a
  generated `agents/openai.yaml` (Codex metadata) and a copy of its
  `references/` when it has one.
- In `~/.claude/skills`, a skill marked `minime_context: fresh` (currently
  `minime-code-reviewer` and `minime-doc-check`) gets `context: fork`,
  `background: false` and its model (`sonnet` for the `fast` tier, otherwise
  `inherit`) added to its frontmatter, so Claude Code runs it as a subagent.

Why copies, not symlinks: Codex does not load a symlinked `SKILL.md` and needs
`agents/openai.yaml`, and Claude Code needs the changed frontmatter above. All
other installed files are identical to the clone; linking them is a plan
candidate.
After `git pull`, re-run `skills install --write`.

Safety:

- Nothing is written unless every skill passes validation (name, description,
  metadata, and no local paths or secret-looking tokens) and every destination
  is a safe path. One rejected destination cancels the whole batch, including
  folders already checked. Unexpected I/O failures have no automatic rollback.
- Symlinked `agents/` or `agents/openai.yaml` paths and unexpected file types
  are blocked, even with `--force`.
- Installed files are owned by MiniMe: local edits, stale copies and extra
  reference files are replaced or removed on the next `--write`. Repeated runs
  change nothing.

Older installs:

- `--write` converts MiniMe's older symlinked `SKILL.md` wrappers to regular
  files, removing only the link.
- Older installs that linked a whole skill folder are reported as conflicts
  until you run `--write --force`.

The name and description rules the validator applies are listed under
[metadata errors](troubleshooting.md#skill-metadata-errors).

## Hooks

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
  for `Bash` and `AskUserQuestion`, a `Stop` hook, a `SessionStart` hook
  for `compact` and a `UserPromptSubmit` hook to `~/.claude/settings.json`.
  Other settings and hooks are kept, reinstalling does not add second entries
  and widens an earlier `Bash`-only matcher, and an unreadable settings file
  is refused. Uninstall removes only those entries and the copied script.
- Before each Bash call, the gate checks for a `git commit` command. It blocks
  the commit (exit 2, with a message to the agent) when the session has loaded
  a MiniMe skill but the current turn has not loaded `minime-project-commit` or
  `minime-self-commit`. Loads count through the Skill tool, a slash command, an
  injected `<skill>` block or `$minime*` mention (Codex), or a Read or
  `cat`/`sed`-style read that starts a shell segment, counting every `SKILL.md`
  the segment names. A block message reminds the agent that a blocked
  command runs none of its parts, so staging chained to the commit is lost.
  A Codex turn starts at its `task_started` event. Detection is textual: a
  command that contains a complete read command as data, such as a heredoc,
  can still count as a load.
- The same turn must also load the check skills: `minime-doc-sync` (or
  `minime-doc-check`), `minime-scope-boundary`, `minime-code-simplifier` and
  `minime-code-reviewer`. A turn whose latest line starting with
  `Commit tier:` since its last successful commit says `light` may skip the
  reviewer; a quote mid-sentence does not count, a later `Commit tier: full`
  withdraws it, and each commit needs its own line (Claude Code only; a Codex
  `light` line lasts the turn). The gate trusts the
  statement and cannot judge the diff. It may run before a line written in the
  commit call's own reply reaches the transcript, so the agent states the tier
  when it stages.
  A message queued mid-turn does not start a new turn.
- A commit needs no skill and no tier line (the data tier) when every path in
  `git diff --cached --name-only` has the `commit-data` git attribute set
  (`git check-attr --cached`, run from the top level of the repository at the
  hook event's working directory, or at `-C <dir>` resolved from it) and the
  command is exactly `git [-C <dir>] commit [-q|-s|-v|--no-edit] -m <message>`
  or `-F <file>`,
  alone in its call. The message is one plain word, a single-quoted string
  (several lines allowed) or a double-quoted string without `$`, backtick,
  backslash or `!`, so the shell cannot run anything before the commit; a
  heredoc in `$(...)` is refused because macOS bash 3.2 can run text from its
  body. A staged `.gitattributes` is never data. Otherwise the usual checks
  apply; after a `Commit tier: data` line the block message names the
  unmarked paths. Staging sent in the same parallel batch
  as the commit can still change the index after the check.
- Any skill named `minime` or `minime-*` counts as a MiniMe skill, the
  `minime` orchestrator included.
- Sessions that never loaded a MiniMe skill, commands that only mention
  `git commit` (including in a heredoc body, unless a shell, `eval`, `source`
  or `.` on the `<<` line may run it), and unreadable transcripts pass.
- Before blocking, the gate re-reads the transcript for up to 2 seconds,
  because a skill read sent in the same parallel batch as the commit can reach
  the transcript after the hook starts.
- In a session that loaded a MiniMe skill, an `AskUserQuestion` call is
  blocked (exit 2) unless it asks exactly one question with at least two
  options, the question contains `Default if no reply:`, and every option
  description contains `Pros:`, `Cons:` and `Locks in:` (case-insensitive),
  and no text outside an option's `Affects:` cites a workflow item by number
  or code (such as `Decision 13`, `item 6`, `Q7`, `M3`, `REQ-005`), the
  `minime-decision-prompt` shape. Install widens an earlier `Bash`-only
  matcher in place, but keeps a customized or shared one and prints a note.
- When a turn ends, the `Stop` hook blocks once (exit 2, with a message to the
  agent) if the turn loaded a MiniMe skill and its last main-thread reply does
  not contain `Recommended next action`, or its last prose line before that
  line (not code, a quote, a heading or a table row) ends in `?` while the
  turn made no `AskUserQuestion` call. It does not
  block again while the agent is continuing from that block
  (`stop_hook_active`).
- After a compaction in a session that loaded a MiniMe skill, the
  `SessionStart` hook prints a reminder, added as context, that those skills
  are still in force and the step-0 ledger is due. Until a main-thread reply
  starts a line with `Ledger:` (or `Orchestration ledger:`), the `Stop` hook
  blocks each stop once.
- Fresh-session nudge (Decision 17), in a session that loaded a MiniMe skill
  when the last main-thread request carried more than 300k context tokens:
  the `Stop` hook blocks once at the end of a turn that ran a `git commit`
  whose result was not an error, unless its last reply already mentions `/clear`; the
  `UserPromptSubmit` hook adds context to a prompt sent more than an hour
  after the last reply. Both ask the agent to recommend a handoff with
  `minime-context-handoff`, then `/clear` and `/minime-orient`. Neither
  blocks a tool call or a commit.

### `scripts/minime codex-hook install|uninstall`

Installs or removes the same commit gate for Codex (Decision 13).

```sh
scripts/minime codex-hook install --write
scripts/minime codex-hook uninstall --write
```

Behavior:

- Same as `claude-hook` without the `Stop`, `SessionStart` and
  `UserPromptSubmit` hooks and the `AskUserQuestion` gate, with the script in
  `~/.config/minime/codex-hooks/commit-gate` and the entry in
  `~/.codex/hooks.json`.
- Codex runs a user-level hook only after you trust it in `/hooks`, and again
  after its definition changes.

## Audits

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
- Verifies every `target-reusable` skill has a host-level wrapper
  directory containing a regular installed `SKILL.md` file and
  `agents/openai.yaml`.
- Verifies installed `SKILL.md` content matches the matching MiniMe skill file,
  and that installed `references/` holds exactly the source references.
- Blocks symlinked `SKILL.md` wrappers because current Codex user-skill
  discovery does not load them.
- Blocks extra `minime` or `minime-*` host entries that are not in the target-reusable
  manifest.
- Requires generated metadata to match MiniMe's canonical output, including
  display name, short description and default prompt. Metadata links/nonfiles
  are blocked. Empty, malformed or different content is reported stale.
- A filesystem pass does not prove fresh host discovery or workflow outcomes.
- Writes nothing.

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

### `scripts/minime transcript-audit`

On-demand, read-only scan of local Claude Code and Codex transcripts for MiniMe
skill use, token counts and observable contract misfires (Decision 10).

```sh
scripts/minime transcript-audit
scripts/minime transcript-audit --since 2026-10-07 --json
```

Behavior:

- Reads `~/.claude/projects` and `~/.codex/sessions` (override with
  `--claude-root` / `--codex-root`), including the `.jsonl.zst` files Codex
  compresses older rollouts into; OpenCode and Copilot are not parsed.
- Counts MiniMe skill loads per skill: slash commands, Skill-tool calls,
  injected `<skill>` blocks, `$minime*` mentions and reads of a `SKILL.md`.
- Flags, once per turn: `no-next-action`, `next-action-unformatted`,
  `prose-question` (Claude only), `commit-unverified` (no test or check command
  earlier in the turn or since the previous commit) and
  `commit-without-commit-skill`. A Claude Code turn cut off during a tool call
  has no ending reply, so it is not judged for a next action or a question.
- Reports token counts (`input`, `cache_read`, `cache_write`, `output`) per
  host, split between the main context and subagent transcripts (Claude Code
  only; Codex sessions all count as main). Claude Code records that repeat a
  message's usage are counted once; Codex usage comes from increases in its
  cumulative totals. Pricing, and cost per gated change, are measured with the
  maintainer's local tooling, which is not published (REQ-010).
- Excludes `review-eval` runs, recognized by a prompt that starts with the
  review-eval prompt, and the subagents they fork; their count is reported per
  host.
- `--since` takes a date or a datetime; a datetime with an offset is converted
  to UTC, the time zone of transcript timestamps.
- Findings are heuristics; verify each one in the transcript before acting.
- Projects are reported as `project-N` and sessions as an 8-character id. No
  paths or message text are printed. Writes nothing.

## Developing skills

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

### `scripts/minime skills install-check <skill-path>`

Dry-run preflight check for skill installation. Accepts a skill directory or a
direct `SKILL.md` path:

```sh
scripts/minime skills install-check skills/minime
scripts/minime skills install-check skills/minime/SKILL.md
scripts/minime skills install-check skills/minime --json
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
scripts/minime skills similar skills/minime
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
  - Claude Code: `claude -p` with installed hooks disabled, restricted to read,
    search, skill and `git diff` tools. A `Stop` hook's added reply would
    otherwise replace the review as the printed result.
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
