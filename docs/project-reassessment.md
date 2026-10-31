# Project reassessment

Date: 2026-10-30. Baseline commit: `fc75d38` (main, clean tree).
Status: assessment complete; both decisions resolved and applied (R1, R3
done; R2's detection baseline done with an accepted exception for Codex on
`gpt-6-luna`, its budget-plan cost measurement open under the routing
milestone).

## Conclusion

The project is viable and in unusually good health for a 15-day-old repo: all
gates pass, every component traces to an accepted decision or requirement, the
docs agree with the code and with each other, and the one roadmap reversal
(cross-host second opinion) was closed out cleanly as Decision 15. No
over-design was found — each abstraction has a current consumer, and the plan
explicitly marks temporary instrumentation for removal. The biggest risk is not
in the repo but in its evidence base: the quality bar is measured on the
maintainer's configuration (Opus 5.5 session model), while the stated audience
is budget users on the least expensive plans, whose session model is cheaper
and whose tolerance for ~$3–5 (list price) per gated commit is lower. The
newly stated goals (single-author vibe coding, budget audience, shareable
output, a self-complexity ceiling for MiniMe itself) are compatible with the
docs but not recorded in them.

## Decisions needed

Both raised via `minime-decision-prompt` and resolved on 2026-10-30:

1. **Record the restated goals, and confirm the cost ranking.** Accepted:
   amend Decisions 1/2 to record the vibe-coding audience, budget constraint,
   shareable-output motivation and MiniMe self-complexity guard, keeping
   quality > cost unchanged. Applied in `docs/decisions.md` (amendments to
   Decisions 1 and 2), the README intro and the `AGENTS.md` project section.
2. **Measure the bar on a cheapest-plan configuration.** Accepted: extend the
   open "Model and effort routing" milestone with a budget-configuration
   baseline (each verified host's cheapest-plan session model) rather than add
   a new milestone. Applied in `docs/implementation-plan.md`.

## Answers

1. **Goal clarity — adequate, with one unrecorded aspect.** From docs alone:
   MiniMe is a host-installed engineering skill library that holds AI coding
   agents to an anti-slop production-quality bar for one developer across
   projects, with cost second and portability third (Decision 1, Decision 2,
   `docs/requirements.md:3-8`). No conflicting goals across docs. Comparison
   with the user's stated goals:

   | Aspect | Docs | User | Relation |
   |---|---|---|---|
   | Primary goal | Anti-slop quality bar without the user catching defects (Decision 1) | Support single-author vibe coding with a quality bar | Match in substance; "vibe coding" framing unrecorded |
   | Why quality | Agent work the user need not audit (Decision 1 context) | Slop compounds cost/complexity; shared/open-sourced projects should not shame the author | Compatible; second motivation unrecorded |
   | Audience | Individual developer, cross-project (Decision 2) | Individuals on a budget, least expensive plans | Compatible; budget constraint unrecorded |
   | Cost rank | Strictly below quality; "cost never ranks above quality" (REQ-010) | "Find a balance … without taxing target projects' progress speed and expenses" | Possible tension — user decision 1 |
   | Hosts | Codex + Claude Code verified; OpenCode, Copilot supported (Decision 4) | Claude, ChatGPT, potentially other CLIs | Match |
   | MiniMe self-complexity | DRY/YAGNI invariants, design-simplifier, temporary-instrumentation table | Named as the main risk (fragility, dev cost) | Compatible; no explicit ceiling recorded |

2. **Goal viability — adequate, with an evidence gap for the audience.** The
   quality bar has real outcome evidence, not just presence checks:
   planted-defect review baseline 20/20 with 0/3 control false positives on
   both verified hosts (`docs/implementation-plan.md:34-66`); in live use, 27
   of 31 blocking verdicts held real defects, none noise
   (`docs/implementation-plan.md:105-107`); misfire counts dropped from 20/37
   turns to 1/27 after the Stop hook (`docs/implementation-plan.md:94-97`).
   External dependencies (host discovery, transcript formats, model prices)
   are named and bounded in README Known Limits and `docs/concepts.md`.
   Gap: no baseline run with a budget session model as the main context, and
   the cheaper Codex model already missed a hard-tier defect (5/6,
   `docs/implementation-plan.md:41-46`) — so "the bar holds on the least
   expensive plans" is asserted by extrapolation, not measured (finding F02;
   detection since measured on 2026-10-30, see F02).

3. **Documentation — adequate** (doc-sync `all` scope, report-only). Verified:
   skill counts 29 reusable + 2 internal match `skills list --json`; all 10 CLI
   commands in `docs/cli.md` exist with matching flags (`scripts/minime
   --help`, `skills --help`); requirement→test links all resolve (every test
   class named in `docs/requirements.md` exists in `tests/test_minime.py`);
   REQ-011's acceptance test exists (`test_a_host_added_through_the_table_
   alone_is_installed_and_audited`, `tests/test_minime.py:2112`). No
   cross-doc contradictions found; statuses in the plan match the code. An
   agent reading only active docs gets one current direction — superseded
   directions live inside Decision 15 and the learnings log as context, not as
   live roadmap. 18 `DocumentationConsistencyTests` guard the structure
   mechanically. Only currency nit: `docs/development.md` repository layout
   omits the `CLAUDE.md`/`GEMINI.md` surface adapters it elsewhere tests
   (F04, low).

4. **Design fit — adequate; no over-design found** (design-simplifier pass,
   report-only). Inventory: 31 skills, 10 CLI commands in one 2,325-line
   stdlib file, 2 hook scripts, 2 eval fixture sets, the `HOSTS` table, a
   dated price table. Every item traces to a current consumer: each CLI
   command to a decision (9, 10, 12, 13) and test class; each skill to the
   AGENTS.md routing table (guarded by `RoutingTableCompletenessTests`);
   kept-but-unbuilt marker rows (TypeScript, React) are deliberate demand
   counters (Decision 11, plan milestone 3). The plan's "temporary
   instrumentation" table names removal conditions — the opposite of
   speculative accretion. No component serves a superseded goal; the dropped
   cross-host direction left no artifacts (Decision 15 records the reversal).
   Under-design: none observed; gates, hooks and audits cover the stated
   requirements. Watch item, not a finding: the single-file CLI and single
   test file (2,927 lines) are fine at this scale, and `docs/concepts.md:44-45`
   explicitly bounds the architecture ("no module split is needed").

5. **Code matches design — adequate** (doc-sync `document` scope on
   `docs/concepts.md` and `docs/requirements.md`). Spot-verified claims:
   skills-install surfaces and fork adapter metadata match `docs/cli.md`
   behavior text; `HOSTS` table exists and drives install/audits/review-eval
   (`scripts/minime:380`, `test_headless_commands_come_from_the_host_table`);
   `evals/review/{python,agent-skills,uncovered}` and `evals/doc-check/project`
   match the documented fixture layout; `doctor` output matches its doc. No
   drifted or removed claims found; nothing needed reproduction as a behavior
   gap. Full-suite execution (141 tests, OK) exercises the documented CLI
   behaviors end-to-end in temp dirs.

6. **Test adequacy — adequate.** 141 tests across 22 classes, all passing in
   52s. Insufficient coverage: none found at requirement level — each
   enforceable requirement names a passing test class, and the judgment-based
   parts (REQ-001/006, REQ-003's detection rate) are deliberately evidenced by
   `review-eval` fixtures and transcript audits rather than unit tests
   (Decision 9), which the docs state honestly. Implementation-coupled: the
   `DocumentationConsistencyTests` prose-wording guards (e.g.
   `test_intake_checks_the_premise_before_design_questions`) would break on a
   correct rewording — but for a prose skill library the wording is the
   shipped behavior, and `docs/concepts.md:139-145` already cautions these
   are drift guards, not outcome proof; acceptable. Excessive: none observed;
   no tests for retired behavior. Known cosmetic defect, already documented:
   `test_target_reusable_skills_are_token_conscious` also enumerates internal
   skills despite its name (`docs/concepts.md:142-143`) (F05, low).

## Evidence and limits

Gates run at `fc75d38`:

- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests` — 141 tests, OK.
- `ruff check --no-cache scripts/minime tests` — all checks passed.
- `mypy --python-version 3.14 --cache-dir /tmp/minime-check-mypy scripts/minime tests` — no issues.
- `scripts/minime doctor` — ok; `skills list --json` — 29 + 2.

Not inspected: host-registration audits of the four installed surfaces (they
check this machine's install state, not the repo); `review-eval --run`
(spends plan quota; baseline accepted from the plan's recorded runs);
`transcript-audit` (local-only data, Decision 8); skill bodies other than
doc-sync, design-simplifier, decision-prompt and reassessment were sampled
via their guard tests, not read in full.

## Findings

| ID | Title | Severity | Evidence | Owner skill | Status |
|---|---|---|---|---|---|
| F01 | Stated goals (vibe-coding audience, budget constraint, shareable-output motivation, self-complexity ceiling) were not recorded in Decisions 1/2 | High | Table in answer 1; `docs/decisions.md:9-39` | `minime-project-adr` | Resolved in this report's commit (R1) |
| F02 | Quality-bar evidence does not cover a cheapest-plan configuration (budget session model as main context; cost per gated commit on that plan) | Medium | `docs/implementation-plan.md:32-85,99-109`; cheaper Codex model already at 5/6 | `minime-project-milestone`, `minime-validation-planner` | Detection measured 2026-10-30: Claude Code passes; Codex on `gpt-6-luna` fails and is an accepted exception (plan review baseline, README Known Limits). Budget-plan cost per gated commit stays open as a routing-milestone acceptance item |
| F03 | Gated-commit cost (median $3.28, $5.18 when review blocks, list price) is accepted on quality-first grounds; unconfirmed against the budget framing | Medium | `docs/implementation-plan.md:99-109` | `minime-project-adr` | Resolved by decision 1: ranking confirmed |
| F04 | `docs/development.md` repo layout omitted the `CLAUDE.md`/`GEMINI.md` surface adapters | Low | `docs/development.md:7-22` | `minime-doc-sync` (apply) | Resolved in this report's commit (R3) |
| F05 | `test_target_reusable_skills_are_token_conscious` name does not match its enumeration (includes internal skills) — already documented as known | Low | `docs/concepts.md:142-143` | none | Accepted as recorded; fix only if touched |

## Repair sequence

IDs continue after the plan's three open milestones; none conflict with them.

| ID | Goal | Owners | Acceptance |
|---|---|---|---|
| R1 | Record the goal decisions: amend Decisions 1/2 (and README Goals if wording changes) with the vibe-coding audience, budget constraint, shareable-output motivation and MiniMe self-complexity ceiling, per the user's choice on decision 1 | `minime-project-adr`, `minime-doc-sync` | Decisions 1/2 carry the accepted wording; doc-sync `all` report clean; light-tier gates pass |
| R2 | Budget-configuration baseline: run `review-eval` (both tiers) with a budget session model on each verified host and record cost per gated commit there, per the user's choice on decision 2 | `minime-project-milestone`, `minime-validation-planner`, `minime-verification-gate` | Baseline table in the plan gains a budget-configuration row meeting the pass threshold, or a recorded accepted exception |
| R3 | Doc currency nit: add the surface adapters to `docs/development.md` layout | `minime-doc-sync` (apply), `minime-self-commit` | `test_surface_adapters_delegate_to_shared_agent_operating_guide` still passes; light-tier gates pass |

R1 restores a single authoritative baseline (docs carrying the real goals);
R2 and R3 follow. The existing plan milestones are unaffected and keep their
order.
