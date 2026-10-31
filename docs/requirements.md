# Requirements

MiniMe serves cross-project engineering work through host-installed skills
that hold AI coding agents to an anti-slop, production-quality bar (REQ-003).
Token, model and effort cost is secondary and ranks below quality (REQ-010).
Skills are portable across agent hosts (REQ-004/011). [Decisions](decisions.md)
govern scope, [concepts](concepts.md) describes the architecture, and
[the plan](implementation-plan.md) tracks delivery. Active means required, not
necessarily implemented; each status line says which.

## REQ-001 — Improve skills from observed gaps

Status: active. Type: core. Priority: high.

When an engineering session reveals a workflow gap, identify the closest
existing skill, distill the minimal fix, validate and reinstall it. Do not add
speculative skills or run automated repo-wide source scanning.

Acceptance: cite the observed gap; prefer the existing owner; keep the repair
bounded; updated reusable skills pass `skills install-check`; record the action
and rationale in `docs/learnings.md`. If no skill change is justified, route the
local issue to its existing document/code owner.

Links: Decisions 2/9; `skills/minime-generalize-skill/SKILL.md`.

## REQ-002 — Product repo boundary

Status: active; enforced. Type: safety. Priority: high.

Generic MiniMe workflow bodies and registration belong outside consuming repos.
Product/domain behavior and local development policy remain in their project.
The MiniMe CLI never writes to consuming repos, and no MiniMe trace may land in
one (Decision 3). Neutral enforcement, such as project-owned pre-commit or CI
checks with no MiniMe reference that the agent adds as authorized product
work, is compatible with it.

Acceptance: consuming repos need no MiniMe pointers, symlinks, bootstrap files,
copied workflow bodies or routing sections. Agents may perform authorized
product work using host skills. User-level installation of host skills, the
slop-scan git hook and the agent commit gate (Claude Code and Codex) are the
only opt-in write commands (Decisions 12/13); none writes to a consuming repo.
Transparency audit results are limited to inspected signals, not proof of
absence of renamed copies or intentionally excluded content. Each regular file
read is bounded to 512,001 bytes; text beyond the 512,000-byte inspection limit
or an access/traversal failure must block with an explicit coverage finding.
References detected in inspected prefixes must still be reported. Binary files,
generated/vendor directories, non-regular files and symlink contents are
excluded; symlink targets are checked. Renamed workflow copies require manual
review.

Links: Decision 3; concepts Consumption boundary;
TransparentConsumptionCLITests; TransparentAuditCoverageTests.

## REQ-003 — Anti-slop production-quality bar

Status: active; review checks, implementation discipline, planted-defect
fixtures, the slop-scan git hook and the agent commit gate are implemented.
Type: core. Priority: high.

MiniMe skills must hold an agent to a production-quality bar across planning,
implementation, validation, review, documentation and handoff. The agent must
meet the bar without the user catching its defects (Decision 1). Slop
includes, at minimum:
- invented APIs or dependencies;
- stubs, placeholders or TODOs in shipped paths;
- tests that are weakened, skipped or assert only mocks;
- swallowed errors;
- comments that narrate code;
- leftover debug or dead code;
- unchecked new input paths;
- edits that diverge from the surrounding code's idiom;
- skipping the skill framework's rules: gates, the commit skill, the
  decision-prompt shape and the next-action line. Transcript audits show this
  is the most common slop in practice.

Natural-language instructions do not guarantee compliance, so mechanical parts
of the bar may be enforced deterministically within REQ-002. Review adds a
profile for each layer it detects along the diff's paths, such as a language,
a framework, or agent skills and instructions. It warns in the session when a
touched layer has no profile (Decision 11). Code is never committed in a
broken state: a defect the review finds blocks the commit wherever it is,
whether or not the change introduced it.

Acceptance: review on the planted-defect fixtures reports a detection rate on
each verified host (Decision 9). The pass threshold is: every planted defect
detected, no blocking finding on a control, and every uncovered-stack warning
shown. The rate must not fall between runs without an accepted reason. Quality
is applied while code is written, not only after it. Functional correctness
and project completion gates remain required.

Links: Decisions 1/9/11/12/13; REQ-001/006/010; ReviewEvalCLITests;
GitHookCLITests; AgentHookCLITests.

## REQ-004 — Host-level transparent consumption

Status: active; installation safety and metadata freshness implemented.
Type: core. Priority: high.

Codex and Claude Code are verified hosts. OpenCode and GitHub Copilot are
supported hosts (Decision 4). All four use host/user-level registration on
Python 3.14+. Installed wrappers and fresh agent discovery are separate checks.

Acceptance: explicitly audit each of the four skill roots. Planted-defect
fixtures and agent hooks cover the verified hosts; installed regular `SKILL.md`
content, references and generated metadata must be current. Invalid metadata,
contamination and destination escapes must be rejected without changing
existing files; valid installs are idempotent. Validate tooling on the
available supported interpreter (Decision 5). Fresh discovery can be checked
when diagnosing host setup or compatibility; registration alone does not prove
it.

Links: Decisions 3/4/5; InstallerSafetyTests; SkillsInstallCLITests;
TransparentConsumptionCLITests. Metadata constraints follow the
[Agent Skills name/description contract](https://agentskills.io/specification#frontmatter)
within MiniMe's documented narrow parser.

## REQ-005 — Current, consistent and private documentation

Status: active. Type: core. Priority: high.

Documentation describes the current product: one scope, one set of accepted
decisions, and the open plan, without obsolete roadmap items or superseded
decisions. No tracked file or commit message may name or path other
local/target projects or carry personal data (Decision 8); use neutral
placeholders such as `ProductA`. Public research sources may be attributed.

Acceptance: active references resolve; no two documents contradict each other;
`test_tracked_files_have_no_local_home_paths` and
`test_tracked_files_and_history_have_no_private_project_terms` pass, the latter
using the untracked `.minime-private-terms` denylist.

Links: Decision 8; DocumentationConsistencyTests.

## REQ-006 — User feedback improvement loop

Status: active. Type: AI. Priority: high.

Every user input and user-identified problem must be examined for a durable
improvement opportunity: local project improvement, a reusable skill improvement
candidate, both, or no durable action. Record actionable findings and rationale
through their existing owner. In consumer projects, hand reusable candidates to
host-level MiniMe work; do not add MiniMe-specific guidance there.

Acceptance: triage names the classification and rationale; reflection produces
an action in `docs/learnings.md`; avoid speculative workflow additions.

Links: Decisions 6/7; `skills/minime-course-correction-triage/SKILL.md`.

## REQ-007 — Token-conscious reusable skills

Status: active. Type: core. Priority: high.

Reusable skill bodies contain no emojis, social filler, greetings or sign-offs.
Descriptions must not redundantly restate names. Verbosity and descriptor
heuristics are drift guards, not evidence of utility or semantic duplication.

Acceptance: `test_target_reusable_skills_are_token_conscious` passes; evaluate
policy changes explicitly using observed failures and user feedback, rather than
suppressing a failure.

Links: TokenConsciousSkillTests; CatalogDRYTests.

## REQ-008 — Routing evidence and progressive disclosure

Status: active. Type: core. Priority: high.

Descriptions serve as routing triggers. Before new skills or description
changes, record positive, negative and forbidden-load cases. Keep body text to
instructions needed for correct execution; move conditional/bulky material to
progressively loaded references, scripts or assets when the need is concrete.

Acceptance: changed routes have evidence before body edits; descriptions use
user intent; observed failures drive gotchas; affected drift guards pass.

Links: Decision 6; `skills/minime-generalize-skill/SKILL.md`;
DocumentationConsistencyTests.

## REQ-009 — Detectable skill misfires

Status: active; implemented. Type: AI. Priority: medium.

Misfires must be detectable without relying on the user to notice them. An
on-demand, read-only command scans local host transcripts for MiniMe skill loads
and observable contract misfires, reporting placeholders only.

Acceptance: `TranscriptAuditCLITests` pass: skill loads are counted for each
load path; each finding type fires on a synthetic transcript; slop-scan and
blocking-review gate blocks are counted; review-eval runs are excluded;
`--since` filters; transcripts are unchanged; no path or message text appears
in the report.

Links: Decisions 8/10; REQ-001/003/006.

## REQ-010 — Cost-appropriate execution

Status: active; token measurement, including per-model usage of each gated
commit turn and its subagents, and list-price cost implemented; Claude Code
review runs forked on the fast tier; other routing pending.
Type: core. Priority: high.

Skills run each step at the lowest-cost model, effort level and context that
keeps the REQ-003 bar. Cost is tokens priced by model and token type, not raw
token counts: fewer tokens or a smaller model is not cheaper by default, since
a fresh context pays to rebuild its cache and a weaker model may need more
work. Gates that need no main-session context run in a fresh context where the
host allows it and it costs less. Ceremony scales with the risk of the change.
Cost never ranks above quality (Decision 1).

Acceptance: an on-demand transcript report gives the tokens and model for each
MiniMe skill flow on each verified host, with counts only and no message text
(Decision 8). Each skill's declared tier reaches the host through a generated
adapter (Decision 14). A routing change is accepted only if the priced cost per
gated change, main context plus the subagents it starts, falls and fixture
detection holds.

Links: Decisions 1/9/10/14; REQ-003/007/009; TranscriptAuditCLITests.

## REQ-011 — Host adoptability

Status: active; not yet implemented. Type: core. Priority: medium.

Host differences are recorded in one host-capability table. The table gives
each host's skills root, transcript location, choice UI, subagent, model and
effort mechanism, headless command, read-only flags and hooks. The installer
and audits read the table. Skills contain no host-specific call syntax.

Acceptance: a test adds a hypothetical host through the table alone; all
existing roots still pass the registration audit;
`test_no_skill_uses_host_specific_call_syntax` passes.

Links: Decisions 4/14; REQ-004.

## REQ-012 — Cross-agent second opinion

Status: active; not yet implemented. Type: AI. Priority: medium.

Code review and decision challenges can get a second opinion from the other
verified host. It triggers by risk tier and spare quota and runs read-only. If
the other host is unavailable or out of quota, it falls back to a fresh instance
of the same host, or skips and reports the skip. A project can opt out of
sending code to a second provider.

Acceptance: on the fixtures, the second opinion raises the detection rate at a
token cost the user accepts. A test with an unavailable host shows the fallback
running. With neither host available, the flow completes and reports the skip.

Links: Decisions 9/14/15; REQ-003/010/011.
