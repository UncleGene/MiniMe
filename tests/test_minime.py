"""MiniMe stdlib unittest harness."""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]

_minime_path = REPO_ROOT / "scripts" / "minime"
minime = types.ModuleType("minime")
minime.__file__ = str(_minime_path)
with open(_minime_path) as _f:
    exec(_f.read(), minime.__dict__)


def _make_skill_wrapper(skills_root: Path, name: str, source_skill_md: Path) -> None:
    """Create a proper wrapper directory: real dir + regular SKILL.md + agents/openai.yaml
    + the skill's references."""
    skill_dir = skills_root / name
    skill_dir.mkdir(exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(source_skill_md.read_text(encoding="utf-8"), encoding="utf-8")
    agents_dir = skill_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / "openai.yaml").write_text(
        minime._openai_yaml_content(name, minime.parse_skill_frontmatter(source_skill_md)["description"]),
        encoding="utf-8",
    )
    minime._write_references(skill_dir, minime._skill_references(source_skill_md.parent))


class FrontmatterParserTests(unittest.TestCase):
    def _write_and_parse(self, text: str) -> dict:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(text)
            f.flush()
            path = Path(f.name)
        try:
            return minime.parse_skill_frontmatter(path)
        finally:
            path.unlink()

    def _write_and_expect_error(self, text: str, code: str):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(text)
            f.flush()
            path = Path(f.name)
        try:
            with self.assertRaises(minime.MiniMeError) as ctx:
                minime.parse_skill_frontmatter(path)
            self.assertEqual(ctx.exception.code, code)
        finally:
            path.unlink()

    def test_parses_internal_kind(self):
        result = self._write_and_parse("""---
name: minime-foo
description: A test skill.
metadata:
  minime_kind: internal
---
# Body text
""")
        self.assertEqual(result["name"], "minime-foo")
        self.assertEqual(result["description"], "A test skill.")
        self.assertEqual(result["metadata"]["minime_kind"], "internal")

    def test_parses_target_reusable_kind(self):
        result = self._write_and_parse("""---
name: minime-bar
description: A reusable skill.
metadata:
  minime_kind: target-reusable
---
# Body text
""")
        self.assertEqual(result["metadata"]["minime_kind"], "target-reusable")

    def test_rejects_missing_frontmatter(self):
        self._write_and_expect_error(
            "# No frontmatter\nJust body text.\n",
            "MINIME_E_FRONTMATTER_MISSING",
        )

    def test_rejects_missing_closing_delimiter(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nmetadata:\n  minime_kind: internal\n# body\n",
            "MINIME_E_FRONTMATTER_UNCLOSED",
        )

    def test_rejects_empty_frontmatter(self):
        self._write_and_expect_error(
            "---\n---\n# body\n",
            "MINIME_E_FRONTMATTER_MISSING_KIND",
        )

    def test_rejects_unsupported_nested_block(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nfoo:\n  bar: baz\nmetadata:\n  minime_kind: internal\n---\nbody\n",
            "MINIME_E_FRONTMATTER_NESTED",
        )

    def test_rejects_indented_line_outside_metadata(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\n  bad: indented\nmetadata:\n  minime_kind: internal\n---\nbody\n",
            "MINIME_E_FRONTMATTER_NESTED",
        )

    def test_rejects_unknown_kind(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nmetadata:\n  minime_kind: experimental\n---\nbody\n",
            "MINIME_E_FRONTMATTER_UNKNOWN_KIND",
        )

    def test_rejects_empty_kind(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nmetadata:\n  minime_kind:\n---\nbody\n",
            "MINIME_E_FRONTMATTER_EMPTY_KIND",
        )

    def test_rejects_whitespace_only_kind(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nmetadata:\n  minime_kind:   \n---\nbody\n",
            "MINIME_E_FRONTMATTER_EMPTY_KIND",
        )

    def test_rejects_duplicate_metadata_block(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nmetadata:\n  minime_kind: internal\nmetadata:\n  minime_kind: target-reusable\n---\nbody\n",
            "MINIME_E_FRONTMATTER_DUPLICATE",
        )

    def test_rejects_duplicate_metadata_fields(self):
        for fields in ("  minime_kind: internal\n  minime_kind: target-reusable\n",
                       "  minime_kind: internal\n  model_tier: fast\n  model_tier: strong\n"):
            with self.subTest(fields=fields):
                self._write_and_expect_error(
                    f"---\nname: minime-foo\nmetadata:\n{fields}---\nbody\n",
                    "MINIME_E_FRONTMATTER_DUPLICATE",
                )

    def test_rejects_metadata_with_value(self):
        self._write_and_expect_error(
            "---\nname: minime-foo\nmetadata: some value\n  minime_kind: internal\n---\nbody\n",
            "MINIME_E_FRONTMATTER_MALFORMED",
        )

    def test_ignores_body_text(self):
        result = self._write_and_parse("""---
name: minime-foo
description: Parser fixture.
metadata:
  minime_kind: internal
---
# Body Heading

Body paragraph with **markdown**.

Another paragraph.
""")
        self.assertIn("# Body Heading", result["body"])
        self.assertIn("Body paragraph", result["body"])

    def test_body_starts_after_closing_delimiter(self):
        result = self._write_and_parse("""---
name: test
description: Parser fixture.
metadata:
  minime_kind: internal
---
The body is here.
""")
        self.assertEqual(result["body"].strip(), "The body is here.")

    def test_blank_lines_in_metadata_block(self):
        result = self._write_and_parse("""---
name: minime-foo
description: Parser fixture.
metadata:

  minime_kind: internal
  extra: allowed
---
body
""")
        self.assertEqual(result["metadata"]["minime_kind"], "internal")
        self.assertEqual(result["metadata"]["extra"], "allowed")


class ContaminationGateTests(unittest.TestCase):
    def test_blocks_local_paths(self):
        text = "# Plan Review\nReference docs at /Users/example/project/README.md"
        findings = minime.contamination_gate(text)
        self.assertTrue(any(f["type"] == "local-path" for f in findings))

    def test_blocks_secret_looking_token(self):
        text = "api_key: abcdef1234567890\nSome content."
        findings = minime.contamination_gate(text)
        self.assertTrue(any(f["type"] == "secret-looking-token" for f in findings))

    def test_clean_text_passes(self):
        text = "# Generic Code Review Skill\nReview the diff for common issues."
        findings = minime.contamination_gate(text)
        self.assertEqual(len(findings), 0)


class CollectSkillEntriesTests(unittest.TestCase):
    def test_returns_empty_for_no_skills_dir(self):
        with tempfile.TemporaryDirectory() as d:
            valid, blocked = minime.collect_skill_entries(Path(d))
        self.assertEqual(len(valid), 0)
        self.assertEqual(len(blocked), 0)

    def test_parses_internal_and_target_reusable(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            internal_dir = root / "skills" / "minime-internal-test"
            internal_dir.mkdir(parents=True)
            (internal_dir / "SKILL.md").write_text(
                "---\nname: minime-internal-test\ndescription: Internal helper.\nmetadata:\n  minime_kind: internal\n---\nbody\n"
            )
            reusable_dir = root / "skills" / "minime-reusable-test"
            reusable_dir.mkdir(parents=True)
            (reusable_dir / "SKILL.md").write_text(
                "---\nname: minime-reusable-test\ndescription: Reusable skill.\nmetadata:\n  minime_kind: target-reusable\n---\nbody\n"
            )
            valid, blocked = minime.collect_skill_entries(root)

        self.assertEqual(len(valid), 2)
        self.assertEqual(len(blocked), 0)
        kinds = {e["minime_kind"] for e in valid}
        self.assertIn("internal", kinds)
        self.assertIn("target-reusable", kinds)

    def test_blocks_invalid_skill(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bad_dir = root / "skills" / "minime-bad"
            bad_dir.mkdir(parents=True)
            (bad_dir / "SKILL.md").write_text("no frontmatter\n")
            valid, blocked = minime.collect_skill_entries(root)

        self.assertEqual(len(valid), 0)
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0]["error_code"], "MINIME_E_FRONTMATTER_MISSING")

    def test_skips_missing_skill_md(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            empty_dir = root / "skills" / "minime-empty"
            empty_dir.mkdir(parents=True)
            valid, blocked = minime.collect_skill_entries(root)

        self.assertEqual(len(valid), 0)
        self.assertEqual(len(blocked), 0)


class CatalogCLITests(unittest.TestCase):
    def test_skills_list_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "list"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_skills_list_internal_only(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "list", "--kind", "internal"],
            capture_output=True,
            text=True,
        )
        self.assertNotIn("target-reusable", result.stdout)
        self.assertIn("internal", result.stdout)

    def test_skills_list_target_reusable_only(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "list", "--kind", "target-reusable"],
            capture_output=True,
            text=True,
        )
        self.assertIn("target-reusable", result.stdout)
        self.assertNotIn("internal", result.stdout)

    def test_skills_list_json(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "list", "--json"],
            capture_output=True,
            text=True,
        )
        output = json.loads(result.stdout)
        self.assertIn("skills", output)
        self.assertIn("blocked_entries", output)

    def test_skills_list_human_shows_expected_sections(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "list"],
            capture_output=True,
            text=True,
        )
        self.assertIn("MiniMe skills catalog", result.stdout)
        self.assertIn("Skills directory:", result.stdout)


class InstallCheckCLITests(unittest.TestCase):
    def test_target_reusable_fixture_passes(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
             "skills/minime"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("approved-for-install", result.stdout)

    def test_internal_skill_blocked(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
             "skills/minime-generalize-skill"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MINIME_E_INSTALL_WRONG_KIND", result.stderr)

    def test_direct_skill_md_path_works(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
             "skills/minime/SKILL.md"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_outside_repo_path_blocked(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
             "/tmp/nonexistent"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MINIME_E_INSTALL_OUTSIDE_REPO", result.stderr)

    def test_json_output_includes_result(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
             "skills/minime", "--json"],
            capture_output=True,
            text=True,
        )
        output = json.loads(result.stdout)
        self.assertEqual(output["result"], "approved-for-install")
        self.assertEqual(output["mode"], "dry-run")

    def test_internal_skill_blocked_in_json(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
             "skills/minime-generalize-skill", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_symlink_skill_dir_blocked(self):
        skill_dir = REPO_ROOT / "skills" / "_test_target"
        symlink_path = REPO_ROOT / "skills" / "_test_symlink"
        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: test-symlink-target\nmetadata:\n  minime_kind: target-reusable\n---\nbody\n"
            )
            os.symlink(str(skill_dir), str(symlink_path))

            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
                 "skills/_test_symlink"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MINIME_E_INSTALL_SYMLINK", result.stderr)
        finally:
            if symlink_path.exists():
                symlink_path.unlink()
            if skill_dir.exists():
                (skill_dir / "SKILL.md").unlink(missing_ok=True)
                skill_dir.rmdir()

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_symlink_skill_md_blocked(self):
        skill_dir = REPO_ROOT / "skills" / "_test_target_md"
        symlink_dir = REPO_ROOT / "skills" / "_test_symlink_md"
        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            symlink_dir.mkdir(parents=True, exist_ok=True)
            real_file = skill_dir / "REAL_SKILL.md"
            real_file.write_text(
                "---\nname: test-real\nmetadata:\n  minime_kind: target-reusable\n---\nbody\n"
            )
            symlink_file = symlink_dir / "SKILL.md"
            os.symlink(str(real_file), str(symlink_file))

            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install-check",
                 "skills/_test_symlink_md"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MINIME_E_INSTALL_SYMLINK", result.stderr)
        finally:
            if symlink_dir.exists():
                (symlink_dir / "SKILL.md").unlink(missing_ok=True)
                symlink_dir.rmdir()
            if skill_dir.exists():
                (skill_dir / "REAL_SKILL.md").unlink(missing_ok=True)
                skill_dir.rmdir()


class SkillsSimilarCLITests(unittest.TestCase):
    def test_local_skill_top_match_is_self(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "similar",
             "skills/minime"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("MiniMe skills similar", result.stdout)
        self.assertIn("name: minime\n", result.stdout)
        self.assertIn("score 1.0", result.stdout)

    def test_json_output_shape(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "similar",
             "skills/minime-claim-verifier", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["command"], "skills similar")
        self.assertEqual(output["mode"], "read-only")
        self.assertIn("matches", output)
        self.assertIn("source", output)
        self.assertGreater(output["catalog_size"], 0)
        self.assertEqual(output["matches"][0]["name"], "minime-claim-verifier")
        self.assertEqual(output["matches"][0]["score"], 1.0)

    def test_path_outside_repo_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            skill_file = Path(d) / "SKILL.md"
            skill_file.write_text(
                "---\n"
                "name: debugger\n"
                "description: Investigate bugs by forming hypotheses, reproducing issues, and verifying root cause before fixing.\n"
                "---\n"
                "# Debugger\n"
            )
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "similar",
                 str(skill_file), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["source"]["name"], "debugger")
            match_names = [m["name"] for m in output["matches"]]
            self.assertIn("minime-systematic-debugging", match_names)

    def test_no_match_case_returns_empty_matches(self):
        with tempfile.TemporaryDirectory() as d:
            skill_file = Path(d) / "SKILL.md"
            skill_file.write_text(
                "---\n"
                "name: zzzunmatched\n"
                "description: xqzpf wlbvm yntrs jkdgh.\n"
                "---\n"
                "body\n"
            )
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "similar",
                 str(skill_file), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["matches"], [])

    def test_missing_file_errors(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "similar",
             "/tmp/this-path-should-not-exist-12345/SKILL.md"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MINIME_E_SIMILAR_NOT_FOUND", result.stderr)


class SecretRedactionTests(unittest.TestCase):
    def test_contamination_gate_redacts_secret(self):
        text = "api_key: abcdef1234567890\nSome content."
        findings = minime.contamination_gate(text)
        secret = [f for f in findings if f["type"] == "secret-looking-token"]
        self.assertEqual(len(secret), 1)
        self.assertEqual(secret[0]["detail"], "[REDACTED]")
        self.assertEqual(secret[0]["severity"], "blocked")

    def test_install_check_json_stays_redacted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill_dir = root / "skills" / "minime-secret-test"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: minime-secret\ndescription: Has secret.\nmetadata:\n  minime_kind: target-reusable\n---\napi_key: xyz123456789012345\n"
            )
            text = (skill_dir / "SKILL.md").read_text()
            findings = minime.contamination_gate(text)
        secret = [f for f in findings if f["type"] == "secret-looking-token"]
        self.assertEqual(len(secret), 1)
        self.assertEqual(secret[0]["detail"], "[REDACTED]")


class CLIDemoSmokeTests(unittest.TestCase):
    def test_doctor_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "doctor"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("status: ok", result.stdout)

    def test_skills_subcommand_without_subsubcommand_prints_help(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skills", result.stdout)


class TransparentConsumptionCLITests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_passes_for_registered_wrappers(self):
        with tempfile.TemporaryDirectory() as d:
            skills_root = Path(d)
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            for entry in target_skills:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["command"], "host-registration-audit")
        self.assertEqual(output["result"], "pass")
        self.assertFalse(output["target_repo_writes"])
        self.assertEqual(len(output["checked_skills"]), output["target_reusable_skills"])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_blocks_expected_skill_md_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            skills_root = Path(d)
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            first_skill = target_skills[0]
            first_dir = skills_root / first_skill["name"]
            first_dir.mkdir()
            source_skill_md = REPO_ROOT / "skills" / first_skill["name"] / "SKILL.md"
            os.symlink(str(source_skill_md.resolve()), str(first_dir / "SKILL.md"))
            (first_dir / "agents").mkdir()
            (first_dir / "agents" / "openai.yaml").write_text("interface:\n  display_name: x\n")
            for entry in target_skills[1:]:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["findings"]}
        self.assertIn("host-skill-symlink-skill-md", finding_types)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_blocks_missing_and_extra_entries(self):
        with tempfile.TemporaryDirectory() as d:
            skills_root = Path(d)
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            for entry in target_skills[1:]:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            # Extra unknown skill directory
            (skills_root / "minime-generalize-skill").mkdir()
            # Unrelated sibling sharing the name prefix; must not be flagged.
            (skills_root / "minimedia").mkdir()
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["findings"]}
        self.assertIn("host-skill-missing", finding_types)
        self.assertIn("host-skill-extra", finding_types)
        flagged_paths = {f["path"] for f in output["findings"]}
        self.assertFalse(any(p.endswith("minimedia") for p in flagged_paths))

    def test_host_registration_audit_blocks_missing_root(self):
        with tempfile.TemporaryDirectory() as d:
            missing_root = Path(d) / "missing-skills"
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(missing_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["findings"][0]["type"], "host-skills-root-missing")
        self.assertEqual(output["checked_skills"], [])

    def test_host_registration_audit_blocks_file_at_root_path(self):
        with tempfile.TemporaryDirectory() as d:
            file_root = Path(d) / "skills-is-a-file"
            file_root.write_text("not a directory\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(file_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["findings"][0]["type"], "host-skills-root-not-directory")
        self.assertEqual(output["checked_skills"], [])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_blocks_regular_file_at_expected_path(self):
        with tempfile.TemporaryDirectory() as d:
            skills_root = Path(d)
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            first_skill = target_skills[0]
            for entry in target_skills[1:]:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            (skills_root / first_skill["name"]).write_text("not a directory\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["findings"]}
        self.assertIn("host-skill-not-dir", finding_types)
        self.assertNotIn("host-skill-missing", finding_types)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_blocks_wrong_target_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            skills_root = base / "skills"
            skills_root.mkdir()
            wrong_dir = base / "wrong-target"
            wrong_dir.mkdir()
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            first_skill = target_skills[0]
            # First skill: wrapper dir with SKILL.md pointing to wrong path
            first_dir = skills_root / first_skill["name"]
            first_dir.mkdir()
            os.symlink(str(wrong_dir), str(first_dir / "SKILL.md"))
            (first_dir / "agents").mkdir()
            (first_dir / "agents" / "openai.yaml").write_text("interface:\n  display_name: x\n")
            for entry in target_skills[1:]:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["findings"]}
        self.assertIn("host-skill-wrong-target", finding_types)
        self.assertNotIn("host-skill-missing", finding_types)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_blocks_dangling_skill_md_link(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            skills_root = base / "skills"
            skills_root.mkdir()
            nonexistent_target = base / "deleted-skill-md"
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            first_skill = target_skills[0]
            # First skill: wrapper dir with SKILL.md pointing to nonexistent path
            first_dir = skills_root / first_skill["name"]
            first_dir.mkdir()
            os.symlink(str(nonexistent_target), str(first_dir / "SKILL.md"))
            (first_dir / "agents").mkdir()
            (first_dir / "agents" / "openai.yaml").write_text("interface:\n  display_name: x\n")
            for entry in target_skills[1:]:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["findings"]}
        # A dangling SKILL.md symlink resolves to a path != expected source → wrong-target
        self.assertIn("host-skill-wrong-target", finding_types)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_host_registration_audit_resolves_minime_to_repo_skill_dir(self):
        expected_skill = "minime"
        expected_source_md = (REPO_ROOT / "skills" / expected_skill / "SKILL.md").resolve()
        self.assertTrue(
            expected_source_md.exists(),
            f"Test fixture out of sync: {expected_source_md} does not exist",
        )
        with tempfile.TemporaryDirectory() as d:
            skills_root = Path(d)
            target_skills, _blocked = minime._target_reusable_skills(REPO_ROOT)
            for entry in target_skills:
                source_skill_md = REPO_ROOT / "skills" / entry["name"] / "SKILL.md"
                _make_skill_wrapper(skills_root, entry["name"], source_skill_md)
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "host-registration-audit",
                 "--skills-root", str(skills_root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        check = next(c for c in output["checked_skills"] if c["name"] == expected_skill)
        self.assertEqual(check["expected_skill_md"], expected_source_md.as_posix())
        self.assertEqual(check["result"], "pass")

    def test_transparent_audit_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("# Product repo\nNo external routing references.\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "transparent-audit",
                 "--repo", str(root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["command"], "transparent-audit")
        self.assertEqual(output["result"], "pass")
        self.assertEqual(output["repos"][0]["result"], "pass")

    def test_transparent_audit_blocks_minime_reference(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("Use MiniMe for development workflow.\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "transparent-audit",
                 "--repo", str(root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["result"], "blocked")
        self.assertEqual(output["repos"][0]["findings"][0]["type"], "minime-reference")

    def test_transparent_audit_blocks_copied_skill_name(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("Route through minime-code-reviewer.\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "transparent-audit",
                 "--repo", str(root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["repos"][0]["findings"]}
        self.assertIn("copied-minime-skill-body", finding_types)

    def test_transparent_audit_bare_minime_is_reference_only(self):
        """The bare `minime` skill name is covered by minime-reference alone."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("Route through minime.\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "transparent-audit",
                 "--repo", str(root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        finding_types = {f["type"] for f in output["repos"][0]["findings"]}
        self.assertIn("minime-reference", finding_types)
        self.assertNotIn("copied-minime-skill-body", finding_types)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink creation not available")
    def test_transparent_audit_blocks_minime_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            os.symlink(str(REPO_ROOT / "skills"), str(root / "skills"))
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "transparent-audit",
                 "--repo", str(root), "--json"],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["repos"][0]["findings"][0]["type"], "minime-symlink")


class TransparentAuditCoverageTests(unittest.TestCase):
    def test_large_text_blocks_even_when_reference_is_beyond_limit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            content = b"a" * minime.MAX_BYTES + b"MiniMe"
            path = root / "AGENTS.md"
            path.write_bytes(content)
            result = subprocess.run(
                [sys.executable, str(_minime_path), "transparent-audit",
                 "--repo", str(root), "--json"], capture_output=True, text=True,
            )
            self.assertEqual(path.read_bytes(), content)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], "blocked")
        self.assertEqual(report["repos"][0]["findings"][0]["type"], "inspection-incomplete")
        self.assertEqual(report["repos"][0]["findings"][0]["path"], "AGENTS.md")

    def test_byte_boundary_binary_exclusion_and_prefix_detection(self):
        cases = [
            (b"a" * minime.MAX_BYTES, "pass", set()),
            (b"a" * (minime.MAX_BYTES + 1), "blocked", {"inspection-incomplete"}),
            ("\u00e9".encode() * (minime.MAX_BYTES // 2 + 1), "blocked", {"inspection-incomplete"}),
            (b"MiniMe\n" + b"a" * minime.MAX_BYTES, "blocked",
             {"inspection-incomplete", "minime-reference"}),
            (b"\0MiniMe" + b"a" * minime.MAX_BYTES, "pass", set()),
        ]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for content, expected, finding_types in cases:
                with self.subTest(size=len(content), expected=expected, findings=finding_types):
                    (root / "content").write_bytes(content)
                    report = minime._transparent_audit_repo(root, REPO_ROOT)
                    self.assertEqual(report["result"], expected)
                    self.assertEqual({f["type"] for f in report["findings"]}, finding_types)

    def test_file_reads_have_a_byte_budget(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / "content"
            path.write_bytes(b"a" * (minime.MAX_BYTES * 3))
            original_open = io.open
            bytes_read = 0

            class BudgetedReader:
                def __init__(self, stream):
                    self.stream = stream

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    self.stream.close()

                def read(self, size=-1):
                    nonlocal bytes_read
                    if size < 0 or bytes_read + size > minime.MAX_BYTES + 1:
                        raise AssertionError("Audit exceeded the per-file read budget")
                    data = self.stream.read(size)
                    bytes_read += len(data)
                    return data

            def budgeted_open(candidate, *args, **kwargs):
                stream = original_open(candidate, *args, **kwargs)
                return BudgetedReader(stream) if Path(candidate).resolve() == path.resolve() else stream

            with patch.object(io, "open", budgeted_open):
                report = minime._transparent_audit_repo(root, REPO_ROOT)
            self.assertLessEqual(bytes_read, minime.MAX_BYTES + 1)
            self.assertEqual(report["result"], "blocked")

    def test_unreadable_file_blocks_and_other_files_are_inspected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            unreadable = root / "private.md"
            unreadable.write_text("ordinary instructions")
            (root / "AGENTS.md").write_text("MiniMe")
            original_open = Path.open

            def denied_open(candidate, *args, **kwargs):
                if candidate.resolve() == unreadable.resolve():
                    raise PermissionError("sensitive detail must not appear")
                return original_open(candidate, *args, **kwargs)

            with patch.object(Path, "open", denied_open):
                report = minime._transparent_audit_repo(root, REPO_ROOT)
        findings = report["findings"]
        self.assertEqual(report["result"], "blocked")
        incomplete = next(f for f in findings if f["type"] == "inspection-incomplete")
        self.assertEqual(incomplete["path"], "private.md")
        self.assertIn("minime-reference", {f["type"] for f in findings})
        self.assertNotIn("sensitive detail", json.dumps(report))

    def test_directory_traversal_error_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)

            def denied_walk(top, *, followlinks, onerror=None):
                if onerror is not None:
                    onerror(PermissionError(13, "Permission denied", str(Path(top) / "private")))
                return iter([])

            with patch.object(minime.os, "walk", denied_walk):
                report = minime._transparent_audit_repo(root, REPO_ROOT)
        self.assertEqual(report["result"], "blocked")
        self.assertEqual(report["findings"][0]["type"], "inspection-incomplete")
        self.assertEqual(report["findings"][0]["path"], "private")

    def test_entry_and_symlink_inspection_errors_block(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            path = root / "entry"
            path.write_text("ordinary instructions")
            original_lstat = Path.lstat

            def denied_lstat(candidate, *args, **kwargs):
                if candidate == path:
                    raise PermissionError("cannot stat")
                return original_lstat(candidate, *args, **kwargs)

            with patch.object(Path, "lstat", denied_lstat):
                report = minime._transparent_audit_repo(root, REPO_ROOT)
            self.assertEqual(report["result"], "blocked")
            self.assertEqual(report["findings"][0]["path"], "entry")
            self.assertEqual(report["findings"][0]["type"], "inspection-incomplete")
            path.unlink()
            path.symlink_to("missing-target")
            with patch.object(minime.os, "readlink", side_effect=PermissionError("cannot read link")):
                report = minime._transparent_audit_repo(root, REPO_ROOT)
            self.assertEqual(report["result"], "blocked")
            self.assertEqual(report["findings"][0]["type"], "inspection-incomplete")
            path.unlink()
            path.symlink_to("MiniMe-target")
            original_resolve = Path.resolve

            def denied_resolve(candidate, *args, **kwargs):
                if candidate == path:
                    raise PermissionError("cannot resolve link")
                return original_resolve(candidate, *args, **kwargs)

            with patch.object(Path, "resolve", denied_resolve):
                report = minime._transparent_audit_repo(root, REPO_ROOT)
            self.assertEqual(report["result"], "blocked")
            self.assertEqual({f["type"] for f in report["findings"]},
                             {"inspection-incomplete", "minime-symlink"})

    def test_intentional_exclusions_do_not_block(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "vendor").mkdir()
            (root / "vendor" / "AGENTS.md").write_text("MiniMe")
            (root / "ordinary-link").symlink_to("vendor", target_is_directory=True)
            report = minime._transparent_audit_repo(root, REPO_ROOT)
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["findings"], [])


class TranscriptAuditCLITests(unittest.TestCase):
    """Decision 10: on-demand, read-only, anonymized transcript audit."""

    PRIVATE = "/Users/example/secret-project"

    def _write(self, path: Path, records: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r) + "\n" for r in records) + "not json\n")

    def _claude_session(self, root: Path) -> None:
        def user(text, ts):
            return {"type": "user", "cwd": self.PRIVATE, "timestamp": ts,
                    "message": {"role": "user", "content": text}}

        def assistant(*blocks, usage=None):
            record = {"type": "assistant", "cwd": self.PRIVATE,
                      "message": {"role": "assistant", "content": list(blocks)}}
            if usage:
                message_id, model, effort, counts = usage
                record["message"].update(id=message_id, model=model, usage=dict(zip(
                    ("input_tokens", "cache_creation_input_tokens",
                     "cache_read_input_tokens", "output_tokens"), counts)))
                record["effort"] = effort
            return record

        def bash(command):
            return {"type": "tool_use", "name": "Bash", "input": {"command": command}}

        self._write(root / "proj" / "aaaaaaaa-1111.jsonl", [
            user("<command-name>/minime-code-reviewer</command-name> secret text", "2026-10-01T00:00:00Z"),
            {"type": "user", "isMeta": True, "message": {"role": "user", "content": [
                {"type": "text", "text": "Base directory for this skill: x"}]}},
            # One API message split across two records must be counted once.
            assistant(bash("git commit -m x"), usage=("m1", "claude-x", "high", (10, 100, 1000, 5))),
            assistant({"type": "text", "text": "Done. Shall I push?"},
                      usage=("m1", "claude-x", "high", (10, 100, 1000, 5))),
            user("next please", "2026-10-08T00:00:00Z"),
            assistant({"type": "tool_use", "name": "Read",
                       "input": {"file_path": "/h/.claude/skills/minime-scope-boundary/SKILL.md"}},
                      bash("cat /h/.claude/skills/minime-project-commit/SKILL.md"),
                      bash("python -m pytest && git commit -m y"),
                      usage=("m2", "claude-x", "high", (1, 0, 2000, 7))),
            assistant({"type": "text", "text": "Committed.\nRecommended next action: release."}),
        ])
        sidechain = assistant({"type": "text", "text": "secret result"},
                              usage=("m3", "claude-fast", None, (3, 0, 50, 2)))
        sidechain["isSidechain"] = True
        # Records without a message id cannot be deduplicated; count each one.
        no_id = assistant(usage=(None, "claude-fast", None, (1, 0, 10, 1)))
        self._write(root / "proj" / "aaaaaaaa-1111" / "subagents" / "agent-1.jsonl", [
            {**user("review this secret diff", "2026-10-08T00:00:00Z"), "isSidechain": True,
             "sessionId": "aaaaaaaa-1111"},
            sidechain, no_id, no_id,
        ])
        # A review-eval run and the reviewer subagent it forks are excluded.
        eval_prompt = ("Review the uncommitted changes in this repository (run `git diff`) "
                       "with the minime-code-reviewer skill")
        eval_reply = assistant({"type": "text", "text": "Verdict: fix"},
                               usage=("m4", "claude-x", "high", (9, 9, 9, 9)))
        self._write(root / "tmp-repo" / "cccccccc-3333.jsonl", [
            {**user(eval_prompt, "2026-10-08T00:00:00Z"), "sessionId": "cccccccc-3333"}, eval_reply])
        self._write(root / "tmp-repo" / "cccccccc-3333" / "subagents" / "agent-2.jsonl", [
            {**user("Base directory for this skill: x", "2026-10-08T00:00:00Z"),
             "isSidechain": True, "sessionId": "cccccccc-3333"}, eval_reply])
        # Quoting the eval prompt, or loading a commit skill without committing,
        # is ordinary work: not excluded, not a gated commit.
        self._write(root / "proj" / "dddddddd-4444.jsonl", [
            user(f"why does `{eval_prompt}` fail?", "2026-10-08T00:00:00Z"),
            assistant(bash("cat /h/.claude/skills/minime-project-commit/SKILL.md"),
                      {"type": "text", "text": "Recommended next action: rerun."})])

    def _codex_session(self, root: Path) -> None:
        def item(payload, ts="2026-10-08T00:00:00Z"):
            return {"type": "response_item", "timestamp": ts, "payload": payload}

        self._write(root / "2026" / "rollout-bbbbbbbb-2222.jsonl", [
            {"type": "session_meta", "payload": {"id": "bbbbbbbb-2222", "cwd": self.PRIVATE}},
            {"type": "event_msg", "timestamp": "2026-10-08T00:00:00Z",
             "payload": {"type": "task_started"}},
            {"type": "turn_context", "payload": {"model": "gpt-x", "effort": "medium"}},
            # Cumulative totals; a repeated total must not be counted twice.
            *[{"type": "event_msg", "payload": {"type": "token_count", "info": {
                "total_token_usage": {"input_tokens": i, "cached_input_tokens": c,
                                      "output_tokens": o}}}}
              for i, c, o in ((500, 300, 20), (500, 300, 20), (800, 600, 30))],
            item({"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": "<skill>\n<name>minime-doc-sync</name> secret"}]}),
            item({"type": "function_call", "name": "exec_command",
                  "arguments": json.dumps({"cmd": "sed -n 1,40p ~/.codex/skills/minime-replan/SKILL.md"})}),
            item({"type": "function_call", "name": "exec_command",
                  "arguments": json.dumps({"cmd": "python -m pytest && git commit -m z"})}),
            {"type": "event_msg", "payload": {"type": "task_complete",
                                              "last_agent_message": "Synced; next step is review."}},
        ])
        eval_prompt = ("Review the uncommitted changes in this repository (run `git diff`) "
                       "with the minime-code-reviewer skill")
        self._write(root / "2026" / "rollout-eeeeeeee-5555.jsonl", [
            {"type": "session_meta", "payload": {"id": "eeeeeeee-5555", "cwd": self.PRIVATE}},
            {"type": "event_msg", "timestamp": "2026-10-08T00:00:00Z", "payload": {"type": "task_started"}},
            item({"type": "message", "role": "user", "content": [{"type": "input_text", "text": eval_prompt}]}),
            {"type": "event_msg", "payload": {"type": "token_count", "info": {
                "total_token_usage": {"input_tokens": 9, "cached_input_tokens": 0, "output_tokens": 9}}}},
        ])

    def _run(self, *extra: str, compress_codex: bool = False) -> dict:
        with tempfile.TemporaryDirectory() as d:
            claude, codex = Path(d) / "claude", Path(d) / "codex"
            self._claude_session(claude)
            self._codex_session(codex)
            if compress_codex:
                from compression import zstd
                for path in list(codex.rglob("*.jsonl")):
                    path.with_name(path.name + ".zst").write_bytes(zstd.compress(path.read_bytes()))
                    path.unlink()
            before = {p: p.read_bytes() for p in Path(d).rglob("*.jsonl")}
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "transcript-audit",
                 "--claude-root", str(claude), "--codex-root", str(codex), "--json", *extra],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p: p.read_bytes() for p in Path(d).rglob("*.jsonl")}, before)
            self.assertNotIn("secret", result.stdout)
            self.assertNotIn("/Users/", result.stdout)
            return json.loads(result.stdout)

    def test_detects_skill_loads_and_misfires(self):
        report = self._run()
        self.assertEqual(report["skill_loads"], {
            "minime-code-reviewer": 1, "minime-doc-sync": 1,
            "minime-project-commit": 2, "minime-replan": 1, "minime-scope-boundary": 1})
        found = {(f["host"], f["turn"], f["type"]) for f in report["findings"]}
        self.assertEqual(found, {
            ("claude", 1, "commit-unverified"),
            ("claude", 1, "commit-without-commit-skill"),
            ("claude", 1, "no-next-action"),
            ("claude", 1, "prose-question"),
            ("codex", 1, "commit-without-commit-skill"),
            ("codex", 1, "next-action-unformatted"),
        })
        self.assertEqual({f["project"] for f in report["findings"]}, {"project-1"})

    def test_reads_compressed_codex_rollouts_like_plain_ones(self):
        # Codex compresses older rollouts in place; skipping them hid most of a month.
        self.assertEqual(self._run(compress_codex=True), self._run())

    def test_reports_token_counts_by_host_and_context_and_excludes_review_eval(self):
        def tokens(i, r, w, o):
            return {"input": i, "cache_read": r, "cache_write": w, "output": o}

        report = self._run()
        claude, codex = report["hosts"]["claude"], report["hosts"]["codex"]
        self.assertEqual(claude["tokens"], {"main": tokens(11, 3000, 100, 12), "subagent": tokens(5, 70, 0, 4)})
        self.assertEqual(codex["tokens"], {"main": tokens(200, 600, 0, 30), "subagent": tokens(0, 0, 0, 0)})
        self.assertEqual((claude["sessions"], claude["review_eval_sessions"]), (3, 1))
        self.assertEqual((codex["sessions"], codex["review_eval_sessions"]), (1, 1))

    def test_parsers_record_each_request_unpriced(self):
        with tempfile.TemporaryDirectory() as d:
            claude, codex = Path(d) / "c.jsonl", Path(d) / "rollout-x.jsonl"
            self._write(claude, [
                {"type": "user", "timestamp": "2026-10-08T00:00:00Z", "message": {"role": "user", "content": "go"}},
                {"type": "assistant", "effort": "high", "message": {
                    "id": "m1", "model": "claude-x", "role": "assistant", "content": [],
                    "usage": {"input_tokens": 1, "cache_read_input_tokens": 2, "cache_creation_input_tokens": 3,
                              "output_tokens": 4, "speed": "fast",
                              "cache_creation": {"ephemeral_1h_input_tokens": 2}}}}])
            totals = [{"input_tokens": 10, "cached_input_tokens": 4, "output_tokens": 1},
                      {"input_tokens": 15, "cached_input_tokens": 6, "output_tokens": 3}]
            self._write(codex, [
                {"type": "event_msg", "timestamp": "2026-10-08T00:00:00Z", "payload": {"type": "task_started"}},
                {"type": "turn_context", "payload": {"model": "gpt-x", "effort": "low"}},
                *[{"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": t}}}
                  for t in totals]])
            claude_requests = minime._parse_claude_transcript(claude)["turns"][0]["requests"]
            codex_requests = minime._parse_codex_transcript(codex)["turns"][0]["requests"]
        self.assertEqual(claude_requests, [{"key": "claude-x/high", "model": "claude-x (fast)", "input": 1,
                                            "cache_read": 2, "cache_write": 3, "cache_write_1h": 2, "output": 4}])
        # Codex totals are cumulative: the second request is the increase only.
        self.assertEqual(codex_requests, [
            {"key": "gpt-x/low", "model": "gpt-x", "input": 6, "cache_read": 4, "cache_write": 0, "output": 1},
            {"key": "gpt-x/low", "model": "gpt-x", "input": 3, "cache_read": 2, "cache_write": 0, "output": 2}])

    def test_commit_counts_checks_since_the_last_committing_turn(self):
        def turn(*commands, skills=("minime",)):
            return {"timestamp": "t", "skills": set(skills), "commands": list(commands),
                    "final": "Recommended next action: x", "asked_with_ui": True}

        def found(*turns):
            return [(f["turn"], f["type"]) for f in minime._transcript_findings({"turns": list(turns)})]

        self.assertEqual(found(
            turn("pytest", skills=()),
            turn("git commit -m z", skills=()),  # before MiniMe: not judged, uses the check
            turn("git commit -m y", skills=("minime-project-commit",)),
            turn("bin/rails test"),
            turn("git commit -m a"),  # checked in the turn before: verified
            turn("git commit -m b"),  # nothing checked since commit a
            turn("bin/ci > log &"),  # a background check
            turn("git status"),
            turn("git commit -m c", "git commit -m c"),  # checked two turns earlier; retry too
            turn("git commit -m d"),  # the check was used by commit c
            turn("git commit -m e", "pytest"),  # a check after the commit carries on
            turn("git commit -m f"),
        ), [(3, "commit-unverified"), (6, "commit-unverified"), (10, "commit-unverified"),
            (11, "commit-unverified")])
        self.assertEqual(found(turn("pytest && git commit -m x")),
                         [(1, "commit-without-commit-skill")])

    def test_since_compares_offset_times_in_utc(self):
        # 20:00-07:00 is 03:00Z on 10-08, after every 10-08T00:00Z turn.
        report = self._run("--since", "2026-10-07T20:00:00-07:00")
        self.assertEqual(report["hosts"]["claude"]["minime_turns"], 0)

    def test_since_skips_older_turns(self):
        report = self._run("--since", "2026-10-05")
        self.assertEqual({(f["host"], f["type"]) for f in report["findings"]},
                         {("codex", "commit-without-commit-skill"), ("codex", "next-action-unformatted")})
        self.assertEqual(report["hosts"]["claude"]["minime_turns"], 2)


class ReviewEvalCLITests(unittest.TestCase):
    """Decisions 9/11: planted-defect review fixtures and their runner."""

    FIXTURES = REPO_ROOT / "evals" / "review"
    # Fake host: reports a blocking finding at the first changed line of every
    # changed file, and Ruby as uncovered when a .rb file changed.
    FAKE_HOST = """#!/usr/bin/env python3
import json, re, subprocess
diff = subprocess.run(["git", "diff", "-U0"], capture_output=True, text=True).stdout
findings, uncovered, current = [], [], None
for line in diff.splitlines():
    if line.startswith("+++ b/"):
        current = line[6:]
        if current.endswith(".rb"):
            uncovered.append("Ruby")
    match = re.match(r"@@ -\\S+ \\+(\\d+)", line)
    if match and current and not any(f["file"] == current for f in findings):
        findings.append({"file": current, "line": int(match.group(1)), "severity": "blocking"})
print("Review done.\\n```json\\n" + json.dumps({"verdict": "fix", "findings": findings,
                                              "uncovered_stacks": uncovered}) + "\\n```")
"""

    def _fake_host(self, directory: Path) -> Path:
        fake = directory / "fake-host"
        fake.write_text(self.FAKE_HOST)
        fake.chmod(0o755)
        return fake

    def _layer(self, root: Path) -> None:
        base = root / "python" / "base"
        base.mkdir(parents=True)
        (base / "app.py").write_text("def a():\n    return 1\n")
        for name, text, expected in (
            ("planted", "def a():\n    return 1\n\n\ndef b():\n    pass  # TODO\n",
             {"kind": "defect", "type": "unfinished-code",
              "locations": [{"file": "app.py", "contains": "pass  # TODO"}]}),
            ("control", "def a():\n    return 2\n", {"kind": "control"}),
        ):
            (root / "python" / name / "change").mkdir(parents=True)
            (root / "python" / name / "change" / "app.py").write_text(text)
            (root / "python" / name / "expected.json").write_text(json.dumps(expected))
        ruby = root / "uncovered"
        (ruby / "base").mkdir(parents=True)
        (ruby / "base" / "x.rb").write_text("x = 1\n")
        (ruby / "rb" / "change").mkdir(parents=True)
        (ruby / "rb" / "change" / "x.rb").write_text("x = 2\n")
        (ruby / "rb" / "expected.json").write_text(json.dumps({"kind": "control", "uncovered": ["ruby"]}))

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "minime"), "review-eval", *args],
                              capture_output=True, text=True)

    def test_run_scores_detection_false_positives_and_uncovered_stacks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "fixtures"
            self._layer(root)
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = self._cli("--host", "claude", "--fixtures", str(root),
                               "--host-bin", str(self._fake_host(Path(d))), "--run", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p: p.read_bytes() for p in root.rglob("*") if p.is_file()}, before)
            report = json.loads(result.stdout)
            outcomes = {f["id"]: f["outcome"] for f in report["fixtures"]}
            self.assertEqual(outcomes, {"python/planted": "detected",
                                        "python/control": "false-positive",
                                        "uncovered/rb": "uncovered-reported"})
            self.assertEqual(report["summary"]["python"],
                             {"defects": 1, "detected": 1, "controls": 1, "false_positives": 1})
            control = next(f for f in report["fixtures"] if f["id"] == "python/control")
            self.assertEqual(control["blocking"], [{"file": "app.py", "line": 2}])
            self.assertNotIn("blocking", next(f for f in report["fixtures"]
                                              if f["id"] == "python/planted"))

    def test_multi_defect_fixture_scores_partial_and_counts_each_defect(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "fixtures"
            self._layer(root)
            two = root / "python" / "two"
            (two / "change").mkdir(parents=True)
            # The fake host reports only line 3, the first changed line: it finds
            # the defect on line 3 and misses the one on line 10.
            (two / "change" / "app.py").write_text(
                "def a():\n    return 1\nDEBUG = True\n\n\n\n\n\ndef c():\n    pass  # TODO\n")
            (two / "expected.json").write_text(json.dumps({"kind": "defect", "tier": "hard", "defects": [
                {"type": "debug-noise", "locations": [{"file": "app.py", "contains": "DEBUG = True"}]},
                {"type": "unfinished-code", "locations": [{"file": "app.py", "contains": "pass  # TODO"}]}]}))
            result = self._cli("--host", "claude", "--fixtures", str(root), "--tier", "hard",
                               "--host-bin", str(self._fake_host(Path(d))), "--run", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual([(f["id"], f["outcome"], f["found"]) for f in report["fixtures"]],
                             [("python/two", "partial", 1)])
            self.assertEqual(report["summary"], {"python": {
                "defects": 2, "detected": 1, "controls": 0, "false_positives": 0}})

    def test_doc_check_eval_prompts_doc_check_and_finds_stale_lines_in_unchanged_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "fixtures"
            base = root / "project" / "base"
            base.mkdir(parents=True)
            (base / "app.py").write_text("FLAG = '--out'\n")
            (base / "README.md").write_text("# app\n\nRun `app --out x`.\n")
            for name, expected in (
                ("stale", {"kind": "defect", "locations": [{"file": "README.md", "contains": "--out"}]}),
                ("control", {"kind": "control"}),
            ):
                (root / "project" / name / "change").mkdir(parents=True)
                (root / "project" / name / "change" / "app.py").write_text("FLAG = '--output'\n")
                (root / "project" / name / "expected.json").write_text(json.dumps(expected))
            # Fake host: blocks on README.md line 3 only when asked for doc-check.
            fake = Path(d) / "fake-host"
            fake.write_text("#!/usr/bin/env python3\nimport json, sys\n"
                            "findings = [{'file': 'README.md', 'line': 3, 'severity': 'blocking'}]\n"
                            "if 'minime-doc-check' not in ' '.join(sys.argv): findings = []\n"
                            "print('```json\\n' + json.dumps({'verdict': 'fix', 'findings': findings}) + '\\n```')\n")
            fake.chmod(0o755)
            result = self._cli("--host", "claude", "--skill", "doc-check", "--fixtures", str(root),
                               "--host-bin", str(fake), "--run", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["skill"], "doc-check")
            self.assertEqual({f["id"]: f["outcome"] for f in report["fixtures"]},
                             {"project/stale": "detected", "project/control": "false-positive"})

    def test_headless_commands_come_from_the_host_table(self):
        reply = Path("/tmp/reply.txt")
        for model, effort in (("", ""), ("m", "e")):
            claude = minime._review_command("claude", "claude", "code-reviewer", model, effort, reply)
            codex = minime._review_command("codex", "codex", "doc-check", model, effort, reply)
            with self.subTest(model=model):
                self.assertIn("minime-code-reviewer skill.", claude[2])
                self.assertEqual(claude[:2] + claude[3:], ["claude", "-p", *(["--model", "m", "--effort", "e"] if model else []),
                                                           "--settings", '{"disableAllHooks": true}',
                                                           "--allowedTools", "Read", "Grep", "Glob", "Skill",
                                                           "Bash(git diff:*)", "Bash(git status:*)"])
                self.assertIn("minime-doc-check skill ($minime-doc-check).", codex[-1])
                self.assertEqual(codex[:-1], ["codex", "exec", "-s", "read-only", "--skip-git-repo-check", "--ephemeral",
                                              "-o", str(reply),
                                              *(["-m", "m", "-c", "model_reasoning_effort=e"] if model else [])])

    def test_dry_run_lists_fixtures_without_invoking_the_host(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "fixtures"
            self._layer(root)
            missing = Path(d) / "no-such-host"
            result = self._cli("--host", "codex", "--fixtures", str(root), "--host-bin", str(missing))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("python/planted", result.stdout)
            self.assertIn("dry run", result.stdout)

    def test_shipped_doc_check_fixtures_are_well_formed(self):
        """Each stale snippet is base text the change left in place, and every change passes its tests."""
        project = REPO_ROOT / "evals" / "doc-check" / "project"
        fixtures = [p for p in project.iterdir() if p.is_dir() and p.name != "base"]
        self.assertTrue(fixtures)
        for fixture in fixtures:
            with self.subTest(fixture=fixture.name), tempfile.TemporaryDirectory() as d:
                expected = json.loads((fixture / "expected.json").read_text())
                self.assertIn(expected["kind"], ("defect", "control"))
                self.assertIn(expected.get("tier", "standard"), ("standard", "hard"))
                shutil.copytree(project / "base", d, dirs_exist_ok=True)
                shutil.copytree(fixture / "change", d, dirs_exist_ok=True)
                defects = expected.get("defects") or (
                    [{"locations": expected["locations"]}] if expected["kind"] == "defect" else [])
                for defect in defects:
                    for location in defect["locations"]:
                        self.assertIn(location["contains"], (project / "base" / location["file"]).read_text())
                        self.assertIn(location["contains"], (Path(d) / location["file"]).read_text())
                run = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=d,
                                     capture_output=True, text=True,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                self.assertEqual(run.returncode, 0, run.stderr)

    def test_shipped_fixtures_are_well_formed(self):
        """Every answer key points at a changed line, and Python bases pass their tests."""
        layers = [p for p in self.FIXTURES.iterdir() if p.is_dir()]
        self.assertTrue(layers)
        for layer in layers:
            base = layer / "base"
            self.assertTrue(base.is_dir(), layer)
            for fixture in (p for p in layer.iterdir() if p.is_dir() and p.name != "base"):
                with self.subTest(fixture=f"{layer.name}/{fixture.name}"):
                    expected = json.loads((fixture / "expected.json").read_text())
                    self.assertIn(expected["kind"], ("defect", "control"))
                    self.assertIn(expected.get("tier", "standard"), ("standard", "hard"))
                    defects = expected.get("defects") or (
                        [{"locations": expected["locations"]}] if expected["kind"] == "defect" else [])
                    for defect in defects:
                        self.assertTrue(defect["locations"])
                        for location in defect["locations"]:
                            changed = (fixture / "change" / location["file"]).read_text()
                            self.assertIn(location["contains"], changed)
                            original = base / location["file"]
                            if original.exists():
                                self.assertNotIn(location["contains"], original.read_text())
        python = self.FIXTURES / "python"
        controls = [p for p in python.iterdir()
                    if (p / "expected.json").exists()
                    and json.loads((p / "expected.json").read_text())["kind"] == "control"]
        for change in [None, *controls]:
            with self.subTest(python_tests=change.name if change else "base"), \
                    tempfile.TemporaryDirectory() as d:
                shutil.copytree(python / "base", d, dirs_exist_ok=True)
                if change:
                    shutil.copytree(change / "change", d, dirs_exist_ok=True)
                run = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=d,
                                     capture_output=True, text=True,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                self.assertEqual(run.returncode, 0, run.stderr)


class AgentHookCLITests(unittest.TestCase):
    """Decision 13: user-level Claude Code and Codex hooks that gate agent commits."""

    GATE = REPO_ROOT / "scripts" / "commit-gate"
    # The light-tier checks first, then the reviewer, which only the full tier needs.
    CHECKS = ("minime-doc-sync", "minime-scope-boundary", "minime-code-simplifier", "minime-code-reviewer")
    HOSTS = {"claude": ".claude/settings.json", "codex": ".codex/hooks.json"}

    def _minime(self, home: Path, host: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "minime"), f"{host}-hook", *args],
                              capture_output=True, text=True, env={**os.environ, "HOME": str(home)})

    def test_install_keeps_other_settings_and_uninstall_removes_only_its_entry(self):
        for host, relative in self.HOSTS.items():
            with self.subTest(host=host):
                self._check_install(host, relative)

    def _check_install(self, host: str, relative: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            settings = home / relative
            settings.parent.mkdir()
            other = {"matcher": "Bash", "hooks": [{"type": "command", "command": "/bin/true"}]}
            other_stop = {"hooks": [{"type": "command", "command": "/bin/true"}]}
            original = {"model": "x", "hooks": {"PreToolUse": [other], "Stop": [other_stop]}}
            settings.write_text(json.dumps(original))
            self.assertEqual(self._minime(home, host, "install").returncode, 0)
            self.assertEqual(json.loads(settings.read_text()), original, "dry run must not write")
            for _ in range(2):
                result = self._minime(home, host, "install", "--write")
                self.assertEqual(result.returncode, 0, result.stderr)
            gate = home / ".config" / "minime" / f"{host}-hooks" / "commit-gate"
            self.assertTrue(os.access(gate, os.X_OK))
            installed = json.loads(settings.read_text())
            self.assertEqual(installed["model"], "x")
            ours = [{"type": "command", "command": str(gate)}]
            matcher = "Bash|AskUserQuestion" if host == "claude" else "Bash"
            self.assertEqual(installed["hooks"]["PreToolUse"], [other, {"matcher": matcher, "hooks": ours}])
            self.assertEqual(installed["hooks"]["Stop"],
                             [other_stop, {"hooks": ours}] if host == "claude" else [other_stop])
            result = self._minime(home, host, "uninstall", "--write")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(settings.read_text()), original)
            self.assertFalse(gate.parent.exists())

    def test_reinstall_upgrades_an_earlier_install(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            settings = home / ".claude" / "settings.json"
            settings.parent.mkdir()
            gate = home / ".config" / "minime" / "claude-hooks" / "commit-gate"
            ours = [{"type": "command", "command": str(gate)}]
            settings.write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": ours}]}}))
            result = self._minime(home, "claude", "install", "--write")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(settings.read_text())["hooks"], {
                "PreToolUse": [{"matcher": "Bash|AskUserQuestion", "hooks": ours}], "Stop": [{"hooks": ours}],
                "SessionStart": [{"matcher": "compact", "hooks": ours}]})

    def test_reinstall_keeps_a_customized_or_shared_matcher(self):
        other = {"type": "command", "command": "/bin/true"}
        for name, entry in (("customized", {"matcher": "Bash|Edit", "hooks": None}),
                            ("shared", {"matcher": "Bash", "hooks": [other]})):
            with self.subTest(name), tempfile.TemporaryDirectory() as d:
                home = Path(d)
                settings = home / ".claude" / "settings.json"
                settings.parent.mkdir()
                gate = home / ".config" / "minime" / "claude-hooks" / "commit-gate"
                entry = {**entry, "hooks": [{"type": "command", "command": str(gate)}, *(entry["hooks"] or [])]}
                settings.write_text(json.dumps({"hooks": {"PreToolUse": [entry]}}))
                result = self._minime(home, "claude", "install", "--write")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("kept the customized PreToolUse matcher", result.stdout)
                self.assertEqual(json.loads(settings.read_text())["hooks"]["PreToolUse"], [entry])

    def test_refuses_unreadable_settings(self):
        for content in ("{not json", '{"hooks": {"Stop": {}}}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as d:
                settings = Path(d) / ".claude" / "settings.json"
                settings.parent.mkdir()
                settings.write_text(content)
                result = self._minime(Path(d), "claude", "install", "--write")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("MINIME_E_HOOK_SETTINGS_UNREADABLE", result.stdout + result.stderr)
                self.assertEqual(settings.read_text(), content)

    def _gate(self, directory: Path, records: list[dict], command: str) -> subprocess.CompletedProcess:
        transcript = directory / "t.jsonl"
        transcript.write_text("".join(json.dumps(r) + "\n" for r in records))
        event = {"tool_name": "Bash", "tool_input": {"command": command}, "transcript_path": str(transcript)}
        return subprocess.run([sys.executable, str(self.GATE)], input=json.dumps(event),
                              capture_output=True, text=True)

    def test_stop_gate_requires_a_next_action_after_a_minime_turn(self):
        def user(text):
            return {"type": "user", "message": {"role": "user", "content": text}}

        def reply(text, sidechain=False):
            return {"type": "assistant", "isSidechain": sidechain,
                    "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}

        skill = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "minime-project-commit"}}]}}
        done = "Committed.\n\nRecommended next action: run the audit."
        asked = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "AskUserQuestion", "input": {"questions": []}}]}}
        ask = "Should I push?\n\nRecommended next action: push after review."
        question = "choice UI"
        not_last = [
            "> Should I push?", "### Why?", "| a | b? |", "a | b?", "~~~\nwhy?\n~~~",
            "Is it fine? Yes, the tests cover it.", "Should I push?\n\nNo: the remote is protected."]
        cases = [
            ("no MiniMe skill in the turn", [user("go"), reply("Done.")], False, 0),
            ("ends on a prose question", [user("go"), skill, reply(ask)], False, 2, question),
            ("prose question after the choice UI", [user("go"), skill, asked, reply(ask)], False, 0),
            ("bold question line", [user("go"), skill, reply("**Ship it?**\n\nRecommended next action: ship it.")], False, 2, question),
            *[(f"not a closing prose question: {text!r}", [user("go"), skill, reply(f"{text}\n\n{done}")], False, 0)
              for text in not_last],
            ("question while continuing from this hook", [user("go"), skill, reply(ask)], True, 0),
            ("skill only in an earlier turn", [user("go"), skill, reply(done), user("thanks"), reply("Sure.")],
             False, 0),
            ("turn ends with a next action", [user("go"), skill, reply(done)], False, 0),
            ("turn ends without one", [user("go"), skill, reply(done), reply("Tests pass; not pushed.")], False, 2,
             "Recommended next action:"),
            ("only a subagent wrote it", [user("go"), skill, reply("Summary."), reply(done, sidechain=True)],
             False, 2, "Recommended next action:"),
            ("already continuing from this hook", [user("go"), skill, reply("Summary.")], True, 0),
        ]
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "t.jsonl"
            for name, records, active, code, *named in cases:
                with self.subTest(name):
                    transcript.write_text("".join(json.dumps(r) + "\n" for r in records))
                    event = {"hook_event_name": "Stop", "stop_hook_active": active,
                             "transcript_path": str(transcript)}
                    result = subprocess.run([sys.executable, str(self.GATE)], input=json.dumps(event),
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, code, result.stderr)
                    for text in named:
                        self.assertIn(text, result.stderr)

    def test_compaction_reminds_and_requires_a_ledger(self):
        def user(text):
            return {"type": "user", "message": {"role": "user", "content": text}}

        def reply(text):
            return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}

        skill = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "minime"}}]}}
        compact = [{"type": "system", "subtype": "compact_boundary", "content": "Conversation compacted"},
                   {"type": "user", "isCompactSummary": True, "message": {"content": "This session is continued"}}]
        done = "Recommended next action: run the tests."
        ledger = "**Ledger:**\n- triage: pass, checked.\n\n" + done
        cases = [
            ("no compaction", [user("go"), skill, reply(done)], 0),
            ("compacted, no MiniMe skill", [user("go"), *compact, user("go on"), reply(done)], 0),
            ("compacted, no ledger yet", [user("go"), skill, reply(done), *compact, user("go on"), reply(done)], 2),
            ("compacted, ledger written", [user("go"), skill, *compact, user("go on"), reply(ledger)], 0),
            ("ledger in an earlier post-compaction turn", [user("go"), skill, *compact, reply(ledger),
                                                           user("next"), reply("Done.")], 0),
            ("ledger only mentioned mid-sentence", [user("go"), skill, *compact,
                                                    reply("I will write the ledger later.\n" + done)], 2),
            *[(f"not a ledger marker: {text!r}", [user("go"), skill, *compact, reply(f"{text}\n{done}")], 2)
              for text in ("Ledger entries are stale.", "## Ledger", "- **Ledger**")],
            *[(f"a ledger marker: {text!r}", [user("go"), skill, *compact, reply(f"{text}\n- x: pass\n{done}")], 0)
              for text in ("  - **Ledger:**", "### Orchestration ledger:", "ledger: (post-compaction)")],
        ]
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "t.jsonl"
            for name, records, code in cases:
                with self.subTest(name):
                    transcript.write_text("".join(json.dumps(r) + "\n" for r in records))
                    event = {"hook_event_name": "Stop", "transcript_path": str(transcript)}
                    result = subprocess.run([sys.executable, str(self.GATE)], input=json.dumps(event),
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, code, result.stderr)
                    if code:
                        self.assertIn("Ledger:", result.stderr)
            with self.subTest("ledger and next action both missing"):
                transcript.write_text("".join(json.dumps(r) + "\n" for r in
                                              [user("go"), skill, *compact, user("go on"), skill, reply("Done.")]))
                result = subprocess.run([sys.executable, str(self.GATE)], capture_output=True, text=True,
                                        input=json.dumps({"hook_event_name": "Stop", "transcript_path": str(transcript)}))
                self.assertEqual(result.returncode, 2)
                self.assertIn("Ledger:", result.stderr)
                self.assertIn("Recommended next action:", result.stderr)
                result = subprocess.run([sys.executable, str(self.GATE)], capture_output=True, text=True,
                                        input=json.dumps({"hook_event_name": "Stop", "stop_hook_active": True,
                                                          "transcript_path": str(transcript)}))
                self.assertEqual(result.returncode, 0, result.stderr)
            for name, records, source, expected in (
                    ("MiniMe session compacted", [user("go"), skill, *compact], "compact", "minime"),
                    ("plain session compacted", [user("go"), *compact], "compact", ""),
                    ("MiniMe session resumed", [user("go"), skill], "resume", "")):
                with self.subTest(name):
                    transcript.write_text("".join(json.dumps(r) + "\n" for r in records))
                    event = {"hook_event_name": "SessionStart", "source": source,
                             "transcript_path": str(transcript)}
                    result = subprocess.run([sys.executable, str(self.GATE)], input=json.dumps(event),
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if expected:
                        self.assertIn("still in force", result.stdout)
                        self.assertIn(expected, result.stdout)
                    else:
                        self.assertEqual(result.stdout, "")

    def test_choice_gate_requires_the_decision_prompt_shape(self):
        minime = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "minime"}}]}}

        def option(label, description="Pros: a. Cons: b. Locks in: nothing."):
            return {"label": label, "description": description}

        def question(text="Pick one? Default if no reply: stop.", options=None):
            return {"question": text, "header": "Pick", "multiSelect": False,
                    "options": [option("A (Recommended)"), option("B")] if options is None else options}

        cases = [
            ("the full shape", [minime], [question()], 0, ""),
            ("no MiniMe skill in the session", [], [question("Pick one?")], 0, ""),
            ("two questions", [minime], [question(), question()], 2, "exactly one question"),
            ("no default", [minime], [question("Pick one?")], 2, "Default if no reply"),
            ("an option without lock-in", [minime], [question(options=[option("A"), option("B", "Pros: x. Cons: y.")])],
             2, "'B' lacks Locks in:"),
            ("no options", [minime], [question(options=[])], 2, "at least two options"),
            ("one option", [minime], [question(options=[option("A")])], 2, "at least two options"),
            ("a non-dict question", [minime], ["Pick?"], 2, "exactly one question"),
            ("lower-case markers", [minime], [question("pick? default if no reply: A", [
                option("A", "pros: x; cons: y; locks in: z"), option("B")])], 0, ""),
        ]
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "t.jsonl"
            for name, records, questions, code, named in cases:
                with self.subTest(name):
                    transcript.write_text("".join(json.dumps(r) + "\n" for r in
                                                  [{"type": "user", "message": {"content": "go"}}, *records]))
                    event = {"hook_event_name": "PreToolUse", "tool_name": "AskUserQuestion",
                             "tool_input": {"questions": questions}, "transcript_path": str(transcript)}
                    result = subprocess.run([sys.executable, str(self.GATE)], input=json.dumps(event),
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, code, result.stderr)
                    self.assertIn(named, result.stderr)

    def test_one_read_command_counts_every_skill_file_it_names(self):
        """A shared `cat a b c` loads all three skills, in the gate and in the audit."""
        names = ("minime-doc-sync", "minime-scope-boundary", "minime-code-simplifier")
        command = "cat " + " ".join(f"~/.claude/skills/{name}/SKILL.md" for name in names) + " | head"
        self.assertEqual(minime._read_skills(minime.SKILL_READ_RE, command), set(names))
        # The installed gate keeps its own copy of the read patterns (Decision 13).
        def read_lines(path: Path) -> list[str]:
            return [line for line in path.read_text().splitlines()
                    if line.startswith(("SKILL_NAME =", "SKILL_FILE_RE =", "_SKILL_READ =", "SKILL_READ_RE =",
                                        "CODEX_SKILL_READ_RE ="))]
        self.assertEqual(read_lines(self.GATE), read_lines(REPO_ROOT / "scripts" / "minime"))
        codex = json.dumps({"cmd": "cat ~/.codex/skills/minime-doc-sync/SKILL.md README.md\n"
                                   "echo ~/.codex/skills/minime-code-reviewer/SKILL.md"})
        self.assertEqual(minime._read_skills(minime.CODEX_SKILL_READ_RE, codex), {"minime-doc-sync"})
        record = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": command}}]}}
        transcript_records = [{"type": "user", "message": {"content": "go"}},
                              {"type": "assistant", "message": {"role": "assistant", "content": [
                                  {"type": "tool_use", "name": "Skill", "input": {"skill": name}}
                                  for name in ("minime-project-commit", "minime-code-reviewer")]}},
                              record]
        with tempfile.TemporaryDirectory() as d:
            result = self._gate(Path(d), transcript_records, "git commit -m x")
            self.assertEqual(result.returncode, 0, result.stderr)
            blocked = self._gate(Path(d), transcript_records[:2], "git add -A && git commit -m x")
            self.assertEqual(blocked.returncode, 2)
            self.assertIn("stage in its own call", blocked.stderr)

    def test_gate_reads_codex_transcripts(self):
        def task():
            return {"type": "event_msg", "payload": {"type": "task_started"}}

        def user(text):
            return {"type": "response_item", "payload": {"type": "message", "role": "user",
                                                         "content": [{"type": "input_text", "text": text}]}}

        def call(code):
            return {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "input": code}}

        def reply(text):
            return {"type": "response_item", "payload": {"type": "message", "role": "assistant",
                                                         "content": [{"type": "output_text", "text": text}]}}

        checks = [call(f'tools.exec_command({{cmd:"cat ~/.codex/skills/{name}/SKILL.md"}})')
                  for name in self.CHECKS]
        earlier = [{"type": "session_meta", "payload": {"id": "s"}}, task(), user("$minime go"),
                   user("<skill>\n<name>minime-project-commit</name>\nbody</skill>"), task(), user("continue")]
        cases = [
            ("no MiniMe skill in the session", [task(), user("fix it")], 0),
            ("commit skill loaded in an earlier task", earlier, 2),
            ("commit skill injected in this task", [*earlier, user("<skill>\n<name>minime-project-commit</name>"),
                                                    *checks], 0),
            ("commit skill read in this task", [*earlier, call(
                'tools.exec_command({cmd:"sed -n 1,80p ~/.codex/skills/minime-project-commit/SKILL.md"})'),
                *checks], 0),
            ("commit skill without the checks", [*earlier, user("<skill>\n<name>minime-project-commit</name>")], 2),
            ("light tier stated in this task", [*earlier, user("<skill>\n<name>minime-project-commit</name>"),
                                                *checks[:3], reply("Commit tier: light. Status notes only.")], 0),
            ("light tier only quoted in this task", [*earlier, user("<skill>\n<name>minime-project-commit</name>"),
                                                     *checks[:3], reply("Per the rule, `Commit tier: light` skips it.")],
             2),
        ]
        with tempfile.TemporaryDirectory() as d:
            for name, records, code in cases:
                with self.subTest(name):
                    self.assertEqual(self._gate(Path(d), records, "git commit -m x").returncode, code)

    def test_gate_waits_for_a_commit_skill_read_still_being_written(self):
        """Parallel tool calls can reach the hook before their reads are on disk."""
        user = {"type": "user", "message": {"role": "user", "content": "go"}}
        loaded = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "minime"}}]}}
        read = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": f"/s/skills/{name}/SKILL.md"}}
            for name in ("minime-self-commit", *self.CHECKS)]}}
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "t.jsonl"
            transcript.write_text(json.dumps(user) + "\n" + json.dumps(loaded) + "\n")
            event = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"},
                     "transcript_path": str(transcript)}
            gate = subprocess.Popen([sys.executable, str(self.GATE)], stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, text=True)
            assert gate.stdin is not None
            gate.stdin.write(json.dumps(event))
            gate.stdin.close()
            time.sleep(0.5)
            with transcript.open("a") as handle:
                handle.write(json.dumps(read) + "\n")
            self.assertEqual(gate.wait(timeout=10), 0)

    def test_gate_blocks_commits_without_a_commit_skill_in_the_turn(self):
        def user(text, meta=False):
            return {"type": "user", "isMeta": meta, "message": {"role": "user", "content": text}}

        def tool(name, **data):
            return {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": name, "input": data}]}}

        def reply(text):
            return {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "text", "text": text}]}}

        orchestrated = [user("<command-name>/minime</command-name>"),
                        tool("Skill", skill="minime-project-commit"), user("continue")]
        checks = [tool("Skill", skill=name) for name in self.CHECKS]
        committing = [*orchestrated, tool("Skill", skill="minime-project-commit")]
        queued = {"type": "attachment", "attachment": {"type": "queued_command", "prompt": "also note X"}}
        check_cases = [
            ("commit skill without the checks", committing, 2, "minime-doc-sync"),
            ("full tier missing the reviewer", [*committing, *checks[:3]], 2, "minime-code-reviewer"),
            ("full tier with every check", [*committing, *checks], 0, ""),
            ("doc-check stands in for doc-sync", [*committing, tool("Skill", skill="minime-doc-check"),
                                                  *checks[1:]], 0, ""),
            ("checks from an earlier turn", [*committing[:-2], *checks, user("continue"), committing[-1]], 2,
             "minime-doc-sync"),
            ("a queued mid-turn message keeps the turn", [*committing, *checks[:2], queued, *checks[2:]], 0, ""),
            ("light tier stated", [*committing, reply("**Commit tier:** light. Plan status only."),
                                   *checks[:3]], 0, ""),
            ("light tier without the simplifier", [*committing, reply("Commit tier: light"), *checks[:2]], 2,
             "minime-code-simplifier"),
            *[(f"tier text that does not choose light: {text!r}", [*committing, reply(text), *checks[:3]], 2,
               "minime-code-reviewer") for text in (
                "The rule: a turn stating `Commit tier: light` may skip review.", "Commit tier: light-ish",
                "Commit tier: lighter", "- Commit tier: light\n\nCommit tier: full, a code file changed.")],
            ("light tier in an earlier text block", [*committing, {"type": "assistant", "message": {
                "role": "assistant", "content": [{"type": "text", "text": "Commit tier: light — status only"},
                                                 {"type": "text", "text": "Running checks."}]}}, *checks[:3]],
             0, ""),
            ("light tier stated in an earlier turn", [*orchestrated[:2], reply("Commit tier: light"),
                                                      user("continue"), committing[-1], *checks[:3]], 2,
             "minime-code-reviewer"),
        ]
        with tempfile.TemporaryDirectory() as d:
            for name, records, code, named in check_cases:
                with self.subTest(name):
                    result = self._gate(Path(d), records, "git commit -m x")
                    self.assertEqual(result.returncode, code, result.stderr)
                    self.assertIn(named, result.stderr)
        cases = [
            ("no MiniMe skill in the session", [user("fix it")], "git commit -m x", 0),
            ("commit skill loaded in an earlier turn", orchestrated, "git add -A && git commit -m x", 2),
            ("commit skill loaded by the Skill tool", [*orchestrated, tool("Skill", skill="minime-self-commit"),
                                                       user("Base directory for this skill: /h/x", meta=True), *checks],
             "git commit -m x", 0),
            ("commit skill read through Bash", [*orchestrated, tool(
                "Bash", command="cat ~/.claude/skills/minime-project-commit/SKILL.md"), *checks], "git commit -m x", 0),
            ("commit skill loaded by a skill base-directory message", [*orchestrated, user(
                "Base directory for this skill: /h/.claude/skills/minime-project-commit", meta=True), *checks],
             "git commit -m x", 0),
            ("text that only mentions a skill read", [*orchestrated, tool("Bash", command=(
                "python3 - <<EOF\n    call('tools.exec_command({cmd:\"sed -n 1p "
                "~/.codex/skills/minime-project-commit/SKILL.md\"})')\nEOF"))], "git commit -m x", 2),
            ("a command that only mentions git commit", orchestrated, 'grep -n "git commit" notes.md', 0),
            ("a piped commit", orchestrated, "printf msg | git commit -F -", 2),
            ("a commit only mentioned in a heredoc body", orchestrated,
             "python3 - <<'EOF'\nrun('pytest && git commit -m y')\ndoc = 'ran `git commit`'\nEOF", 0),
            *[(f"a commit in a heredoc fed to a shell: {feed}", orchestrated,
               feed.replace("BODY", "\ngit commit -m x\nEOF"), 2) for feed in (
                "bash <<EOFBODY", "tcsh <<EOFBODY", "cat <<EOF | fishBODY", "cat <<EOF | sh -sBODY", "eval \"$(cat <<'EOF'BODY\n)\"",
                "source /dev/stdin <<EOFBODY", ". /dev/stdin <<EOFBODY")],
            ("a commit in an unterminated heredoc", orchestrated, "python3 - <<EOF\ngit commit -m x", 2),
            ("a commit message from a heredoc", orchestrated,
             'git commit -m "$(cat <<\'EOF\'\nmsg\nEOF\n)"', 2),
            ("a commit after a heredoc", orchestrated, "cat > f <<EOF\nx\nEOF\ngit commit -m x", 2),
        ]
        with tempfile.TemporaryDirectory() as d:
            for name, records, command, code in cases:
                with self.subTest(name):
                    result = self._gate(Path(d), records, command)
                    self.assertEqual(result.returncode, code, result.stderr)
                    if code:
                        self.assertIn("minime-project-commit", result.stderr)
            for transcript in (str(Path(d) / "missing.jsonl"), None):
                with self.subTest(transcript=transcript):
                    event = {"tool_name": "Bash", "tool_input": {"command": "git commit"},
                             "transcript_path": transcript}
                    missing = subprocess.run([sys.executable, str(self.GATE)], input=json.dumps(event),
                                             capture_output=True, text=True)
                    self.assertEqual(missing.returncode, 0, missing.stderr)


class GitHookCLITests(unittest.TestCase):
    """Decision 12: user-level pre-commit slop scan that leaves no repo trace."""

    def _env(self, home: Path) -> dict[str, str]:
        return {**os.environ, "HOME": str(home), "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}

    def _minime(self, env: dict[str, str], *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "minime"), "git-hook", *args],
                              capture_output=True, text=True, env=env)

    def _repo(self, base: Path, env: dict[str, str]) -> Path:
        repo = base / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, env=env, check=True)
        return repo

    def _commit(self, repo: Path, env: dict[str, str], files: dict[str, str]) -> subprocess.CompletedProcess:
        for name, text in files.items():
            (repo / name).parent.mkdir(parents=True, exist_ok=True)
            (repo / name).write_text(text)
        subprocess.run(["git", "add", "-A"], cwd=repo, env=env, check=True)
        return subprocess.run(["git", "commit", "-qm", "change"], cwd=repo, env=env,
                              capture_output=True, text=True)

    def test_installed_hook_blocks_slop_and_chains_repo_hooks(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d).resolve()
            env = self._env(home)
            dry = self._minime(env, "install")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse((home / ".gitconfig").exists(), "dry run must not write")
            result = self._minime(env, "install", "--write")
            self.assertEqual(result.returncode, 0, result.stderr)
            repo = self._repo(home, env)
            self.assertEqual(list(repo.rglob("*minime*")), [], "no MiniMe trace in the repo")
            ran = home / "repo-hooks-ran"
            for name in ("pre-commit", "commit-msg"):
                hook = repo / ".git" / "hooks" / name
                hook.write_text(f"#!/bin/sh\necho {name} >> '{ran}'\n")
                hook.chmod(0o755)

            self.assertEqual(self._commit(repo, env, {"app.py": "def a():\n    return 1\n"}).returncode, 0)
            self.assertEqual(ran.read_text().split(), ["pre-commit", "commit-msg"])

            cases = {
                "todo.py": "def b():\n    pass  # TODO finish\n",
                "skip.py": "import unittest\n\n\n@unittest.skip('later')\ndef test_x():\n    pass\n",
                "ignore.py": "x: int = 'a'  # type: ignore\n",
                "only.test.ts": "it.only('runs', () => {});\n",
                "debug.rb": "binding.pry\n",
            }
            for name, text in cases.items():
                with self.subTest(file=name):
                    blocked = self._commit(repo, env, {name: text})
                    self.assertNotEqual(blocked.returncode, 0, blocked.stdout)
                    self.assertIn(name, blocked.stderr)
                    subprocess.run(["git", "reset", "-q"], cwd=repo, env=env, check=True)
                    (repo / name).unlink()

            allowed = {"notes.md": "TODO: write docs\n",
                       "typed.py": "x: int = 'a'  # type: ignore[assignment]\n",
                       "lint.ts": "// eslint-disable-next-line no-console -- CLI output\n"}
            self.assertEqual(self._commit(repo, env, allowed).returncode, 0)

            (repo / ".gitattributes").write_text("fixtures/** -slop-scan\n")
            exempt = self._commit(repo, env, {"fixtures/stub.py": "raise NotImplementedError\n"})
            self.assertEqual(exempt.returncode, 0, exempt.stderr)
            bypass_env = {**env, "SLOP_SCAN": "off"}
            self.assertEqual(self._commit(repo, bypass_env, {"later.py": "# FIXME\n"}).returncode, 0)

            removed = self._minime(env, "uninstall", "--write")
            self.assertEqual(removed.returncode, 0, removed.stderr)
            config = subprocess.run(["git", "config", "--global", "--get", "core.hooksPath"],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(config.stdout, "")

    def test_install_refuses_to_replace_a_foreign_hooks_path(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d).resolve()
            env = self._env(home)
            subprocess.run(["git", "config", "--global", "core.hooksPath", "/opt/other-hooks"],
                           env=env, check=True)
            result = self._minime(env, "install", "--write")
            self.assertNotEqual(result.returncode, 0)
            config = subprocess.run(["git", "config", "--global", "--get", "core.hooksPath"],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(config.stdout.strip(), "/opt/other-hooks")


class MiniMeErrorTests(unittest.TestCase):
    def test_has_code_message_fix(self):
        exc = minime.MiniMeError("MINIME_E_TEST", "something wrong", "run doctor")
        self.assertEqual(exc.code, "MINIME_E_TEST")
        self.assertEqual(exc.message, "something wrong")
        self.assertEqual(exc.fix, "run doctor")


class DocumentationConsistencyTests(unittest.TestCase):
    def test_transparent_consumption_template_separates_registration_and_execution(self):
        """Evidence records must distinguish filesystem checks from host execution."""
        template = (REPO_ROOT / "docs" / "templates" /
                    "transparent-consumption-verification.md").read_text()
        sections = set(re.findall(r"^## (.+)$", template, re.MULTILINE))
        self.assertTrue({"Host registration", "Fresh session", "Task outcomes",
                         "Product repo isolation"}.issubset(sections))
        self.assertIn("--skills-root", template)
        for root in minime._surface_roots():
            with self.subTest(root=root):
                self.assertIn(root, template)

    def test_requirements_are_contiguous_and_docs_state_supported_environment(self):
        """Check requirement IDs and the supported environment without locking prose."""
        requirements = (REPO_ROOT / "docs" / "requirements.md").read_text()
        ids = re.findall(r"^## (REQ-\d+) —", requirements, re.MULTILINE)
        self.assertEqual(ids, [f"REQ-{i:03}" for i in range(1, len(ids) + 1)])
        self.assertNotIn("Status: deprecated", requirements)

        for relative in ("AGENTS.md", "README.md", "docs/requirements.md",
                         "docs/concepts.md", "docs/implementation-plan.md"):
            text = (REPO_ROOT / relative).read_text()
            with self.subTest(document=relative):
                self.assertIn("Python 3.14+", text)
                for host in ("Codex", "Claude Code", "OpenCode", "GitHub Copilot"):
                    self.assertIn(host, text)

    @staticmethod
    def _tracked_text_files() -> dict[str, str]:
        listed = subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.split("\0")
        texts = {}
        for name in filter(None, listed):
            try:
                texts[name] = (REPO_ROOT / name).read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        return texts

    def test_cli_reference_documents_every_command(self):
        """Each CLI command and skills subcommand has its own docs/cli.md section."""
        parser = minime.build_parser()
        commands = parser._subparsers._group_actions[0].choices  # type: ignore[union-attr]  # argparse has no public accessor
        names = [name for name in commands if name != "skills"]
        names += [f"skills {name}" for name in
                  commands["skills"]._subparsers._group_actions[0].choices]  # type: ignore[union-attr]
        reference = (REPO_ROOT / "docs" / "cli.md").read_text()
        undocumented = [name for name in names if not re.search(
            rf"^### `scripts/minime {re.escape(name)}[ `]", reference, re.MULTILINE)]
        self.assertEqual(undocumented, [])

    def test_tracked_files_have_no_local_home_paths(self):
        """Decision 8: no tracked file may reveal a local home directory."""
        home_path = re.compile(r"(/Users|/home)/(?!example/)[A-Za-z0-9._-]+/")
        offenders = [
            f"{name}:{text.count(chr(10), 0, match.start()) + 1}"
            for name, text in self._tracked_text_files().items()
            for match in home_path.finditer(text)
        ]
        self.assertEqual(offenders, [])

    def test_tracked_files_and_history_have_no_private_project_terms(self):
        """Decision 8: other local/target project names stay out of the repo.

        Terms live in the untracked `.minime-private-terms` (one per line) so
        the guard never commits the names it protects.
        """
        terms_file = REPO_ROOT / ".minime-private-terms"
        if not terms_file.is_file():
            self.skipTest(".minime-private-terms not present on this machine")
        terms = [t.strip().lower() for t in terms_file.read_text().splitlines()
                 if t.strip() and not t.startswith("#")]
        sources = dict(self._tracked_text_files())
        sources["<commit messages>"] = subprocess.run(
            ["git", "log", "--all", "--format=%B"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
        ).stdout
        paths = "\n".join(sources)
        offenders = sorted(
            f"{name}: term #{index}"
            for name, text in {**sources, "<paths>": paths}.items()
            for index, term in enumerate(terms, start=1)
            if term in text.lower()
        )
        self.assertEqual(offenders, [])

    def test_reusable_skills_carry_identical_interaction_rules(self):
        """Decision 6: installed skills carry the contract without consumer files.

        Each target-reusable skill ends with the same `## Interaction rules`
        section, so the copies cannot drift apart.
        """
        sections = {}
        for skill_path in sorted((REPO_ROOT / "skills").glob("minime*/SKILL.md")):
            text = skill_path.read_text(encoding="utf-8")
            if "minime_kind: target-reusable" not in text:
                continue
            _, marker, section = text.partition("\n## Interaction rules\n")
            with self.subTest(skill=skill_path.parent.name):
                self.assertTrue(marker, "missing ## Interaction rules section")
                self.assertNotIn("\n## ", section, "Interaction rules must be the last section")
            sections[skill_path.parent.name] = section
        self.assertGreater(len(sections), 0)
        self.assertEqual(len(set(sections.values())), 1,
                         "Interaction rules sections differ between skills")

    def test_surface_adapters_delegate_to_shared_agent_operating_guide(self):
        for adapter_name in ["CLAUDE.md", "GEMINI.md"]:
            adapter = (REPO_ROOT / adapter_name).read_text()
            with self.subTest(adapter=adapter_name):
                self.assertIn("AGENTS.md", adapter)
                self.assertNotIn("## Completion Gates", adapter)
                self.assertNotIn("## Skill Routing", adapter)
                self.assertLess(adapter.count("\n"), 8)

    SKILL_REFERENCE = re.compile(r"(?<![\w/.-])minime(?:-[a-z]+)*(?![\w*<-])")

    def test_skill_references_resolve(self):
        """Every `minime*` skill named in a skill, guide or README exists."""
        names = {p.parent.name for p in (REPO_ROOT / "skills").glob("*/SKILL.md")}
        reference = self.SKILL_REFERENCE
        sources = [REPO_ROOT / "AGENTS.md", REPO_ROOT / "README.md",
                   *sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))]
        dangling = sorted(
            f"{path.relative_to(REPO_ROOT)}: {name}"
            for path in sources
            for name in set(reference.findall(path.read_text(encoding="utf-8")))
            if name not in names
        )
        self.assertEqual(dangling, [])

    REQUIRED_COLLABORATORS = {
        "minime": ["minime-course-correction-triage", "minime-project-adr",
                   "minime-plan-review", "minime-decision-prompt",
                   "minime-implementation-step-selector"],
        "minime-implementation-step-selector": ["minime-decision-prompt", "minime-project-commit"],
        "minime-code-reviewer": ["minime-decision-prompt", "minime-project-commit"],
        "minime-project-commit": ["minime-doc-sync", "minime-scope-boundary",
                                  "minime-code-simplifier", "minime-code-reviewer"],
        "minime-orient": ["minime-decision-prompt", "minime-project-inception",
                          "minime-project-milestone"],
        "minime-project-inception": ["minime-decision-prompt", "minime-requirements-manager",
                                     "minime-project-milestone", "minime-phase-quality-guard"],
        "minime-replan": ["minime-decision-prompt", "minime-project-milestone",
                          "minime-doc-sync"],
        "minime-doc-sync": ["minime-doc-check"],
        "minime-course-correction-triage": ["minime-impact-analyzer"],
        "minime-project-reassessment": ["minime-doc-sync", "minime-design-simplifier",
                                        "minime-decision-prompt"],
    }

    def test_skills_reference_their_required_collaborators(self):
        """Routing edges that past failures depended on stay in place.

        Checks references outside the shared Interaction rules section, not
        wording, so a correct rephrase still passes.
        """
        for skill, collaborators in self.REQUIRED_COLLABORATORS.items():
            text = (REPO_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            body = text.split("\n## Interaction rules\n", 1)[0]
            referenced = set(self.SKILL_REFERENCE.findall(body))
            with self.subTest(skill=skill):
                self.assertEqual([c for c in collaborators if c not in referenced], [])

    NO_PLAN_GUARDS = {
        "minime-orient": ["a missing plan or checkpoint is an observation, not a gap",
                          "no plan, on purpose"],
        "minime-project-inception": ["never use this skill to add a plan to an established project",
                                     "an inferred brief is a proposal, not consent"],
        "minime-decision-prompt": ["needs an explicit pick"],
        "minime": ["never route it to `minime-project-inception`"],
    }

    def test_established_project_without_plan_is_not_bootstrapped(self):
        """Regression: an agent added a plan to an established project that has
        none on purpose, after a biased bootstrap question and a bare "go".
        The guards that stop each step of that chain stay in place. This pins
        wording: rephrasing a guard means updating its phrase here on purpose.
        """
        for skill, phrases in self.NO_PLAN_GUARDS.items():
            text = (REPO_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            text = " ".join(text.lower().split())
            with self.subTest(skill=skill):
                self.assertEqual([p for p in phrases if p not in text], [])

    RISK_TIER_GUARDS = {
        "skills/minime-course-correction-triage/SKILL.md": [
            "## risk tier (pick first)", "contradicts no accepted requirement, decision or invariant",
            "`intake: low — contradicts nothing accepted; <why>; improvement: <classification>`",
            "when in doubt, pick the higher tier", "commit gate tiers (light or full) are chosen separately"],
        "skills/minime-decision-prompt/SKILL.md": [
            "explain in plain terms any mechanism, cost or term",
            "when a choice is low risk by the definition in `minime-course-correction-triage`, reversible and has a conventional default, state the default and proceed"],
        "AGENTS.md": ["scale it to the change's risk tier", "a low-risk change states one intake line",
                      "in the low risk tier, a reversible choice with a conventional default is stated, not asked"],
    }

    PREMISE_GUARDS = {
        "skills/minime-course-correction-triage/SKILL.md": [
            "**premise check** — can the request work as stated",
            "premise check (holds | fails — <evidence> | unverified — <what would check it>)"],
        "skills/minime-decision-prompt/SKILL.md": [
            "before the first design question on a request, confirm its premise holds"],
        "AGENTS.md": ["**premise check** — can the request work as stated"],
    }

    def test_intake_checks_the_premise_before_design_questions(self):
        """Regression: three design questions were asked for a cross-host
        second opinion before anyone asked whether a reviewer without the
        session's context could work, and an offload premise turned out false.
        This pins wording: rephrasing a rule means updating its phrase here.
        """
        for path, phrases in self.PREMISE_GUARDS.items():
            text = " ".join((REPO_ROOT / path).read_text(encoding="utf-8").lower().split())
            with self.subTest(path=path):
                self.assertEqual([p for p in phrases if p not in text], [])

    def test_ceremony_scales_with_risk_tier(self):
        """Decision 16: intake and questions scale with one risk scale, and the
        user sees a mechanism explained before options that depend on it.
        This pins wording: rephrasing a rule means updating its phrase here.
        """
        for path, phrases in self.RISK_TIER_GUARDS.items():
            text = " ".join((REPO_ROOT / path).read_text(encoding="utf-8").lower().split())
            with self.subTest(path=path):
                self.assertEqual([p for p in phrases if p not in text], [])

    def test_step_selector_delegates_the_gate_chain_instead_of_restating_it(self):
        """Regression: the selector's copy of the commit gate chain drifted and
        dropped doc-sync and scope; `minime-project-commit` owns the chain."""
        text = (REPO_ROOT / "skills" / "minime-implementation-step-selector" / "SKILL.md").read_text()
        body = text.split("\n## Interaction rules\n", 1)[0]
        self.assertIn("minime-project-commit", body)
        self.assertIn("same turn", body)
        for gate in ("minime-code-simplifier", "minime-code-reviewer", "minime-doc-sync"):
            with self.subTest(gate=gate):
                self.assertNotIn(gate, body)

    GATE_ORDER = ["minime-doc-sync", "minime-scope-boundary", "minime-code-simplifier",
                  "minime-code-reviewer", "minime-verification-gate"]

    def test_gate_chains_keep_canonical_order(self):
        """Completion gates run doc-sync, scope, simplify, review, verify in order."""
        chains = [
            (REPO_ROOT / "AGENTS.md", "## Completion Gates"),
            (REPO_ROOT / "skills" / "minime-project-commit" / "SKILL.md", "## Pre-commit checks"),
            (REPO_ROOT / "skills" / "minime-self-commit" / "SKILL.md", "## Commit gate ledger"),
        ]
        for path, heading in chains:
            section = path.read_text(encoding="utf-8").split(heading, 1)[1].split("\n## ", 1)[0]
            positions = [section.find(gate) for gate in self.GATE_ORDER]
            with self.subTest(chain=f"{path.name} {heading}"):
                self.assertNotIn(-1, positions[:4], "gate chain lost a required gate")
                present = [pos for pos in positions if pos >= 0]
                self.assertEqual(present, sorted(present), "gates out of order")

    def test_no_skill_labels_mandatory_routing_as_suggested(self):
        """Catalog-wide guard for the miss above: "Suggested" in a routing or
        next-action heading reads as optional and undercuts mandatory routing.
        """
        for skill_dir in sorted((REPO_ROOT / "skills").iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            with self.subTest(skill=skill_dir.name):
                for line in skill_md.read_text(encoding="utf-8").splitlines():
                    if line.startswith("#"):
                        self.assertNotIn(
                            "Suggested",
                            line,
                            msg=f"{skill_dir.name}: heading labels routing as suggested: {line!r}",
                        )

    def test_no_skill_tells_agent_to_wait_for_go_after_completed_gates(self):
        """After gates complete, a skill must not strand the workflow by
        asking the user to type go/continue when no real decision remains.
        """
        forbidden = [
            "user proceeds by typing \"go\"",
            "user proceeds by typing go",
            "typing \"go\"",
            "typing go",
        ]
        for skill_file in sorted((REPO_ROOT / "skills").glob("minime*/SKILL.md")):
            text = " ".join(skill_file.read_text(encoding="utf-8").lower().split())
            with self.subTest(skill=skill_file.relative_to(REPO_ROOT)):
                for phrase in forbidden:
                    self.assertNotIn(
                        phrase,
                        text,
                        msg=(
                            f"{skill_file.relative_to(REPO_ROOT)} strands an "
                            "automatable workflow behind a manual go/continue prompt"
                        ),
                    )

    def test_all_skills_satisfy_agentskills_io_minimum(self):
        """Every SKILL.md must declare name and description in frontmatter.

        agentskills.io open standard minimum: name + description.
        MiniMe SKILL.md format must remain compatible with the ecosystem.
        """
        skills_dir = REPO_ROOT / "skills"
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue
            with self.subTest(skill=skill_dir.name):
                text = skill_file.read_text(encoding="utf-8")
                lines = text.splitlines()
                self.assertTrue(lines and lines[0].strip() == "---",
                                msg=f"{skill_dir.name}: missing frontmatter delimiter")
                end_idx = next((i for i, line in enumerate(lines[1:], start=1)
                                if line.strip() == "---"), None)
                self.assertIsNotNone(end_idx,
                                     msg=f"{skill_dir.name}: missing closing frontmatter delimiter")
                fm_block = "\n".join(lines[1:end_idx])
                self.assertRegex(fm_block, r"(?m)^name:\s*\S+",
                                 msg=f"{skill_dir.name}: missing non-empty name in frontmatter")
                self.assertRegex(fm_block, r"(?m)^description:\s*\S+",
                                 msg=f"{skill_dir.name}: missing non-empty description in frontmatter")

    def test_no_skill_uses_host_specific_call_syntax(self):
        """SKILL.md files must not use Skill("name") notation for cross-skill
        delegation. This is Claude Code-specific function-call syntax that fails
        on Codex, OpenCode, and other non-Claude hosts. Skills must use
        host-agnostic delegation: read the named skill's file and follow its
        procedure."""
        import re
        pattern = re.compile(r'Skill\("[^"]+"\)')
        for skill_dir in (REPO_ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            text = skill_file.read_text(encoding="utf-8")
            matches = pattern.findall(text)
            self.assertEqual(
                [], matches,
                msg=f"{skill_file.relative_to(REPO_ROOT)} contains host-specific "
                    f"Skill(\"name\") syntax: {matches}. Use host-agnostic "
                    f"delegation instead (read the skill file and follow its "
                    f"procedure).",
            )


class SkillsInstallCLITests(unittest.TestCase):
    def test_default_install_surfaces_exclude_agents_root_to_avoid_codex_duplicates(self):
        self.assertNotIn(
            "~/.agents/skills",
            minime._surface_roots(),
            "Codex scans ~/.agents/skills in addition to ~/.codex/skills, causing duplicate skills",
        )

    def test_default_install_surfaces_use_copilot_personal_skills_root(self):
        self.assertIn("~/.copilot/skills", minime._surface_roots())
        self.assertNotIn(
            "~/.config/github-copilot/skills",
            minime._surface_roots(),
            "GitHub Copilot personal skills are loaded from ~/.copilot/skills",
        )

    def test_install_dry_run_lists_create_for_new_wrappers(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                 "--skills-root", d],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("created", result.stdout)
            self.assertIn("Summary:", result.stdout)

    def test_a_host_added_through_the_table_alone_is_installed_and_audited(self):
        """REQ-011: one host-table entry is enough for install and the audit,
        and a fork adapter declared there reaches that host's root only."""
        from contextlib import redirect_stdout
        from io import StringIO
        acme = {"name": "Acme", "skills_root": "~/.acme/skills",
                "fork": {"frontmatter": "acme-fork: {}\n", "models": {"fast": "acme-small"}}}
        with tempfile.TemporaryDirectory() as d, \
                patch.dict(os.environ, {"HOME": d}), patch.dict(minime.HOSTS, {"acme": acme}):
            for spec in minime.HOSTS.values():
                Path(spec["skills_root"]).expanduser().mkdir(parents=True)
            with redirect_stdout(StringIO()):
                self.assertEqual(minime.main(["skills", "install", "--write"]), 0)
            for spec in minime.HOSTS.values():
                root = Path(spec["skills_root"]).expanduser()
                with self.subTest(root=spec["skills_root"]), redirect_stdout(StringIO()) as output:
                    self.assertEqual(minime.main(["host-registration-audit", "--skills-root", str(root),
                                                  "--json"]), 0, output.getvalue())
            for host, spec in minime.HOSTS.items():
                installed = (Path(spec["skills_root"]).expanduser() / "minime-code-reviewer" / "SKILL.md").read_text()
                with self.subTest(host=host):
                    self.assertEqual("\nacme-fork: acme-small\n" in installed, host == "acme")

    def test_every_transcript_parser_has_a_transcripts_root_in_the_host_table(self):
        for host in minime.TRANSCRIPT_PARSERS:
            with self.subTest(host=host):
                self.assertIn("transcripts", minime.HOSTS[host])

    def test_claude_root_runs_fresh_context_skills_in_a_forked_subagent(self):
        """Decision 14: Claude Code forks fresh-context skills; other hosts get the source."""
        cli = [sys.executable, str(REPO_ROOT / "scripts" / "minime")]
        with tempfile.TemporaryDirectory() as d:
            claude, codex = Path(d) / ".claude" / "skills", Path(d) / ".codex" / "skills"
            for root in (claude, codex):
                root.mkdir(parents=True)
                install = subprocess.run([*cli, "skills", "install", "--skills-root", str(root), "--write"],
                                         capture_output=True, text=True)
                self.assertEqual(install.returncode, 0, install.stderr)
                audit = subprocess.run([*cli, "host-registration-audit", "--skills-root", str(root), "--json"],
                                       capture_output=True, text=True)
                self.assertEqual(json.loads(audit.stdout)["result"], "pass", audit.stdout)
            for skill in ("minime-code-reviewer", "minime-doc-check"):
                source = (REPO_ROOT / "skills" / skill / "SKILL.md").read_text()
                installed = (claude / skill / "SKILL.md").read_text()
                _, frontmatter, body = installed.split("---\n", 2)
                for line in ("context: fork", "background: false", "model: sonnet"):
                    self.assertIn(f"\n{line}\n", f"\n{frontmatter}")
                self.assertEqual(body, source.split("---\n", 2)[2])
                self.assertEqual((codex / skill / "SKILL.md").read_text(), source)
            self.assertEqual((claude / "minime-doc-sync" / "SKILL.md").read_text(),
                             (REPO_ROOT / "skills" / "minime-doc-sync" / "SKILL.md").read_text())

    def test_install_write_creates_regular_skill_files(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                 "--skills-root", d, "--write"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Result: written", result.stdout)
            skill_dir = Path(d) / "minime"
            self.assertTrue(skill_dir.is_dir(), "wrapper dir should exist")
            self.assertFalse(skill_dir.is_symlink(), "wrapper dir must not be a symlink")
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(skill_md.is_file(), "SKILL.md inside wrapper must be a file")
            self.assertFalse(skill_md.is_symlink(), "Codex does not discover symlinked SKILL.md files")
            openai_yaml = skill_dir / "agents" / "openai.yaml"
            self.assertTrue(openai_yaml.exists(), "agents/openai.yaml must exist")

    def test_install_write_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            args = [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                    "--skills-root", d, "--write"]
            subprocess.run(args, capture_output=True, text=True, check=True)
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn(" = ", result.stdout, "existing wrappers should show 'exists'")

    def test_install_write_updates_expected_skill_md_symlink_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            host = Path(d)
            source_skill_md = REPO_ROOT / "skills" / "minime" / "SKILL.md"
            skill_dir = host / "minime"
            skill_dir.mkdir()
            os.symlink(str(source_skill_md.resolve()), str(skill_dir / "SKILL.md"))
            (skill_dir / "agents").mkdir()
            (skill_dir / "agents" / "openai.yaml").write_text("interface:\n  display_name: x\n")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                 "--skills-root", d, "--write"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(skill_md.is_file())
            self.assertFalse(skill_md.is_symlink())

    def test_install_conflicts_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            host = Path(d)
            wrong = host / "minime"
            os.symlink("/tmp/nowhere", str(wrong))
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                 "--skills-root", d],
                capture_output=True, text=True,
            )
            self.assertIn("conflicts", result.stdout)

    def test_install_force_overwrites_conflicting_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            host = Path(d)
            wrong = host / "minime"
            os.symlink("/tmp/nowhere", str(wrong))
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                 "--skills-root", d, "--write", "--force"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("updated", result.stdout)

    def test_install_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
                 "--skills-root", d, "--json"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertEqual(output["command"], "skills-install")
            self.assertIn("surface_results", output)
            self.assertIn("actions", output["surface_results"][0])
            self.assertIn("created", output)
            self.assertGreater(output["total_skills"], 0)

    def test_install_rejects_missing_host_root(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install",
             "--skills-root", "/tmp/nonexistent-minime-install-test"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MINIME_E_INSTALL_HOST_ROOT_MISSING", result.stderr)

    def test_install_no_surfaces_guidance_mentions_copilot_root(self):
        with tempfile.TemporaryDirectory() as d:
            env = os.environ.copy()
            env["HOME"] = d
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"), "skills", "install"],
                capture_output=True, text=True, env=env,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MINIME_E_INSTALL_NO_SURFACES", result.stderr)
        self.assertIn("~/.copilot/skills", result.stderr)


class InstallerSafetyTests(unittest.TestCase):
    def _source(self, base: Path) -> Path:
        source = base / "source"
        (source / "scripts").mkdir(parents=True)
        (source / "scripts" / "minime").write_bytes((REPO_ROOT / "scripts" / "minime").read_bytes())
        self._skill(source, "aaa-valid")
        return source

    def _skill(self, source: Path, directory: str, fields: str | None = None,
               body: str = "# Fixture\n") -> Path:
        skill = source / "skills" / directory
        skill.mkdir(parents=True, exist_ok=True)
        if fields is None:
            fields = f"name: {directory}\ndescription: Exercise an isolated installer fixture.\n"
        (skill / "SKILL.md").write_text(
            f"---\n{fields}metadata:\n  minime_kind: target-reusable\n---\n{body}")
        return skill

    def _cli(self, source: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(source / "scripts" / "minime"), *args],
                              capture_output=True, text=True)

    def _audit_types(self, source: Path, host: Path) -> set[str]:
        audit = self._cli(source, "host-registration-audit", "--skills-root", str(host), "--json")
        return {f["type"] for f in json.loads(audit.stdout)["findings"]}

    def test_references_are_installed_audited_and_kept_current(self):
        """Decision 11: profiles ship as skill references and stay current."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source = self._source(base)
            references = source / "skills" / "aaa-valid" / "references"
            references.mkdir()
            (references / "python.md").write_text("# Python profile\n")
            host = base / "host"
            host.mkdir()

            def install() -> None:
                result = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            install()
            installed = host / "aaa-valid" / "references"
            self.assertEqual((installed / "python.md").read_text(), "# Python profile\n")
            self.assertEqual(self._audit_types(source, host), set())

            (installed / "python.md").write_text("edited")
            (installed / "extra.md").write_text("extra")
            self.assertEqual(self._audit_types(source, host), {"host-skill-stale-references"})
            install()
            self.assertEqual(sorted(p.name for p in installed.iterdir()), ["python.md"])
            self.assertEqual(self._audit_types(source, host), set())

            shutil.rmtree(references)
            install()
            self.assertFalse(installed.exists())
            self.assertEqual(self._audit_types(source, host), set())

    def test_install_check_scans_references_for_contamination(self):
        with tempfile.TemporaryDirectory() as d:
            source = self._source(Path(d).resolve())
            references = source / "skills" / "aaa-valid" / "references"
            references.mkdir()
            (references / "profile.md").write_text("See /Users/example/private/notes.\n")
            result = self._cli(source, "skills", "install-check", str(source / "skills" / "aaa-valid"))
            self.assertIn("Result: blocked", result.stdout, result.stderr)

    def test_unsafe_references_are_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source = self._source(base)
            references = source / "skills" / "aaa-valid" / "references"
            references.mkdir()
            outside = base / "outside.md"
            outside.write_text("outside")
            (references / "linked.md").symlink_to(outside)
            host = base / "host"
            host.mkdir()
            result = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(host.iterdir()), [])

            (references / "linked.md").unlink()
            (references / "python.md").write_text("# Python profile\n")
            wrapper = host / "aaa-valid"
            wrapper.mkdir()
            target = base / "elsewhere"
            target.mkdir()
            (wrapper / "references").symlink_to(target)
            result = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(target.iterdir()), [])
            self.assertIn("host-skill-unsafe-references", self._audit_types(source, host))

    def test_metadata_only_drift_is_audited_and_repaired_idempotently(self):
        for drift in ("empty", "malformed", "binary", "display_name", "short_description", "default_prompt"):
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                host = base / "host"
                host.mkdir()
                install = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
                self.assertEqual(install.returncode, 0, install.stderr)
                wrapper = host / "aaa-valid"
                skill_bytes = (wrapper / "SKILL.md").read_bytes()
                metadata = wrapper / "agents" / "openai.yaml"
                expected = metadata.read_text()
                if drift == "empty":
                    metadata.write_text("")
                elif drift == "malformed":
                    metadata.write_text("interface: [\n")
                elif drift == "binary":
                    metadata.write_bytes(b"\xff\xfe")
                else:
                    metadata.write_text(re.sub(rf"(?m)^(  {drift}:).*$", r'\1 "stale"', expected))
                dry = self._cli(source, "skills", "install", "--skills-root", str(host), "--json")
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertEqual(json.loads(dry.stdout)["updated"], 1)
                self.assertNotEqual(metadata.read_bytes(), expected.encode("utf-8"))
                audit = self._cli(source, "host-registration-audit", "--skills-root", str(host), "--json")
                self.assertNotEqual(audit.returncode, 0, audit.stdout)
                report = json.loads(audit.stdout)
                self.assertIn("host-skill-stale-openai-yaml", {f["type"] for f in report["findings"]})
                self.assertNotIn('"stale"', audit.stdout)
                repair = self._cli(source, "skills", "install", "--skills-root", str(host), "--write", "--json")
                self.assertEqual(repair.returncode, 0, repair.stderr)
                self.assertEqual(json.loads(repair.stdout)["updated"], 1)
                self.assertEqual(metadata.read_text(), expected)
                self.assertEqual((wrapper / "SKILL.md").read_bytes(), skill_bytes)
                audit = self._cli(source, "host-registration-audit", "--skills-root", str(host), "--json")
                self.assertEqual(audit.returncode, 0, audit.stdout)
                repeated = self._cli(source, "skills", "install", "--skills-root", str(host), "--write", "--json")
                self.assertEqual(repeated.returncode, 0, repeated.stderr)
                self.assertEqual(json.loads(repeated.stdout)["updated"], 0)

    def test_audit_rejects_metadata_symlinks_and_nonfiles(self):
        for invalid in ("agents-link", "yaml-link", "yaml-directory"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                host = base / "host"
                host.mkdir()
                self.assertEqual(self._cli(source, "skills", "install", "--skills-root", str(host),
                                           "--write").returncode, 0)
                agents = host / "aaa-valid" / "agents"
                metadata = agents / "openai.yaml"
                outside = base / "outside"
                outside.mkdir()
                target = outside / "openai.yaml"
                target.write_bytes(metadata.read_bytes())
                metadata.unlink()
                if invalid == "agents-link":
                    agents.rmdir()
                    agents.symlink_to(outside, target_is_directory=True)
                elif invalid == "yaml-link":
                    metadata.symlink_to(target)
                else:
                    metadata.mkdir()
                audit = self._cli(source, "host-registration-audit", "--skills-root", str(host), "--json")
                self.assertNotEqual(audit.returncode, 0, audit.stdout)
                self.assertIn("host-skill-unsafe-openai-yaml",
                              {f["type"] for f in json.loads(audit.stdout)["findings"]})

    def test_invalid_metadata_blocks_catalog_preflight_and_install_without_writes(self):
        invalid = [
            "description: Missing name.\n",
            "name: zzz-invalid\n",
            *[f"name: zzz-invalid\ndescription: {empty}\n" for empty in ("''", '\"\"', '\"   \"')],
            "name: ../outside\ndescription: Unsafe name.\n",
            "name: different\ndescription: Directory mismatch.\n",
            "name: zzz-invalid\nname: other\ndescription: Duplicate name.\n",
            "name: zzz-invalid\ndescription: One.\ndescription: Two.\n",
            *[f"name: {name}\ndescription: Invalid name.\n" for name in
              ("-bad", "bad-", "bad--name", "BAD", "bad_name", "x" * 65)],
            "name: zzz-invalid\ndescription: " + "x" * 1025 + "\n",
        ]
        for fields in invalid:
            with self.subTest(fields=fields[:80]), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                skill = self._skill(source, "zzz-invalid", fields)
                host = base / "host"
                host.mkdir()
                marker = host / "keep.txt"
                marker.write_text("untouched")
                catalog = json.loads(self._cli(source, "skills", "list", "--json").stdout)
                self.assertEqual(len(catalog["blocked_entries"]), 1)
                self.assertEqual([item["name"] for item in catalog["skills"]], ["aaa-valid"])
                preflight = self._cli(source, "skills", "install-check", str(skill))
                self.assertNotEqual(preflight.returncode, 0)
                for flags in ([], ["--write", "--force"]):
                    install = self._cli(source, "skills", "install", "--skills-root", str(host), *flags)
                    self.assertNotEqual(install.returncode, 0, install.stdout + install.stderr)
                    self.assertEqual(list(host.iterdir()), [marker])
                    self.assertEqual(marker.read_text(), "untouched")

    def test_contamination_is_rejected_before_installing_any_skill(self):
        for body in ("Fixture path /Users/example/private-doc.md", "token=syntheticFixtureToken123"):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                skill = self._skill(source, "zzz-invalid", body=body)
                host = base / "host"
                host.mkdir()
                preflight = self._cli(source, "skills", "install-check", str(skill), "--json")
                self.assertNotEqual(preflight.returncode, 0)
                for flags in ([], ["--write", "--force"]):
                    install = self._cli(source, "skills", "install", "--skills-root", str(host), *flags)
                    self.assertNotEqual(install.returncode, 0)
                    self.assertEqual(list(host.iterdir()), [])
                    self.assertNotIn("syntheticFixtureToken123", install.stdout + install.stderr)

    def test_source_symlink_is_rejected_before_installing_other_skills(self):
        for linked in ("directory", "SKILL.md"):
            with self.subTest(linked=linked), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                outside = base / "outside"
                outside.mkdir()
                text = "---\nname: zzz-linked\ndescription: Fixture.\nmetadata:\n  minime_kind: target-reusable\n---\n"
                (outside / "SKILL.md").write_text(text)
                skill = source / "skills" / "zzz-linked"
                if linked == "directory":
                    skill.symlink_to(outside, target_is_directory=True)
                else:
                    skill.mkdir()
                    (skill / "SKILL.md").symlink_to(outside / "SKILL.md")
                host = base / "host"
                host.mkdir()
                install = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
                self.assertNotEqual(install.returncode, 0)
                self.assertEqual(list(host.iterdir()), [])
                self.assertEqual((outside / "SKILL.md").read_text(), text)

    def test_nested_destination_symlinks_never_modify_wrapper_or_sibling(self):
        for linked in ("agents", "openai.yaml"):
            for flags in ([], ["--write"], ["--write", "--force"]):
                with self.subTest(linked=linked, flags=flags), tempfile.TemporaryDirectory() as d:
                    base = Path(d).resolve()
                    source = self._source(base)
                    self._skill(source, "zzz-valid")
                    host = base / "host"
                    wrapper = host / "zzz-valid"
                    wrapper.mkdir(parents=True)
                    (wrapper / "SKILL.md").write_text("stale skill")
                    victim = base / "sibling"
                    victim.mkdir()
                    (victim / "openai.yaml").write_text("keep sibling")
                    if linked == "agents":
                        (wrapper / "agents").symlink_to(victim, target_is_directory=True)
                    else:
                        (wrapper / "agents").mkdir()
                        (wrapper / "agents" / "openai.yaml").symlink_to(victim / "openai.yaml")
                    install = self._cli(source, "skills", "install", "--skills-root", str(host), *flags)
                    self.assertNotEqual(install.returncode, 0)
                    self.assertEqual((victim / "openai.yaml").read_text(), "keep sibling")
                    self.assertEqual((wrapper / "SKILL.md").read_text(), "stale skill")
                    self.assertFalse((host / "aaa-valid").exists())
                    self.assertTrue((wrapper / "agents" if linked == "agents" else
                                     wrapper / "agents" / "openai.yaml").is_symlink())

    def test_invalid_destination_types_block_the_entire_install(self):
        for invalid in ("SKILL.md", "agents", "openai.yaml"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                self._skill(source, "zzz-valid")
                host = base / "host"
                wrapper = host / "zzz-valid"
                wrapper.mkdir(parents=True)
                if invalid == "SKILL.md":
                    (wrapper / "SKILL.md").mkdir()
                else:
                    (wrapper / "SKILL.md").write_text("stale skill")
                    if invalid == "agents":
                        (wrapper / "agents").write_text("keep file")
                    else:
                        (wrapper / "agents" / "openai.yaml").mkdir(parents=True)
                install = self._cli(source, "skills", "install", "--skills-root", str(host),
                                    "--write", "--force")
                self.assertNotEqual(install.returncode, 0)
                self.assertFalse((host / "aaa-valid").exists())
                if invalid != "SKILL.md":
                    self.assertEqual((wrapper / "SKILL.md").read_text(), "stale skill")
                if invalid == "agents":
                    self.assertEqual((wrapper / "agents").read_text(), "keep file")

    def test_metadata_limits_accept_the_valid_boundary(self):
        for name in ("a", "x" * 64):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                skill = self._skill(source, name, f"name: {name}\ndescription: {'x' * 1024}\n")
                host = base / "host"
                host.mkdir()
                preflight = self._cli(source, "skills", "install-check", str(skill))
                self.assertEqual(preflight.returncode, 0, preflight.stderr)
                install = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
                self.assertEqual(install.returncode, 0, install.stderr)
                repeated = self._cli(source, "skills", "install", "--skills-root", str(host), "--write", "--json")
                self.assertEqual(repeated.returncode, 0, repeated.stderr)
                self.assertEqual(json.loads(repeated.stdout)["updated"], 0)
                self.assertEqual((host / name / "SKILL.md").read_bytes(), (skill / "SKILL.md").read_bytes())

    def test_quoted_metadata_is_normalized_before_admission(self):
        for description in ("A quoted fixture.", 'Line one.\nLine two "quote" and \\ path.'):
            with self.subTest(description=description), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                scalar = "'A quoted fixture.'" if description == "A quoted fixture." else json.dumps(description)
                skill = self._skill(source, "quoted-skill",
                                    f'name: "quoted-skill"\ndescription: {scalar}\n')
                host = base / "host"
                host.mkdir()
                preflight = self._cli(source, "skills", "install-check", str(skill), "--json")
                self.assertEqual(preflight.returncode, 0, preflight.stderr)
                self.assertEqual(json.loads(preflight.stdout)["skill_name"], "quoted-skill")
                install = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
                self.assertEqual(install.returncode, 0, install.stderr)
                self.assertEqual((host / "quoted-skill" / "SKILL.md").read_bytes(),
                                 (skill / "SKILL.md").read_bytes())
                yaml = (host / "quoted-skill" / "agents" / "openai.yaml").read_text()
                prompt_line = next(line for line in yaml.splitlines() if "default_prompt:" in line)
                self.assertEqual(json.loads(prompt_line.split(":", 1)[1]), description)

    def test_rejection_on_later_surface_prevents_writes_to_earlier_surface(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source = self._source(base)
            first, second = base / "first", base / "second"
            first.mkdir()
            wrapper = second / "aaa-valid"
            wrapper.mkdir(parents=True)
            (wrapper / "SKILL.md").write_text("keep skill")
            victim = base / "sibling"
            victim.mkdir()
            (victim / "openai.yaml").write_text("keep sibling")
            (wrapper / "agents").symlink_to(victim, target_is_directory=True)
            output = StringIO()
            with patch.object(minime, "repo_root", return_value=source), \
                    patch.object(minime, "_surface_roots", return_value=[str(first), str(second)]), \
                    redirect_stdout(output):
                result = minime.main(["skills", "install", "--write", "--force", "--json"])
            self.assertNotEqual(result, 0)
            self.assertEqual(list(first.iterdir()), [])
            self.assertEqual((wrapper / "SKILL.md").read_text(), "keep skill")
            self.assertEqual((victim / "openai.yaml").read_text(), "keep sibling")
            self.assertEqual(json.loads(output.getvalue())["created"], 0)

    def test_rejected_inputs_do_not_expose_secret_patterns_in_diagnostics(self):
        token = "syntheticFixtureToken123"
        for malformed in (False, True):
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as d:
                base = Path(d).resolve()
                source = self._source(base)
                skill = self._skill(source, "zzz-invalid",
                                    body=f"Path /Users/example/private token={token}")
                if malformed:
                    path = skill / "SKILL.md"
                    path.write_text(path.read_text().replace("target-reusable", f"token={token}"))
                host = base / "host"
                host.mkdir()
                for args in (("skills", "list", "--json"),
                             ("skills", "install-check", str(skill), "--json"),
                             ("skills", "install", "--skills-root", str(host), "--write")):
                    result = self._cli(source, *args)
                    self.assertNotIn(token, result.stdout + result.stderr)
                self.assertEqual(list(host.iterdir()), [])

    def test_metadata_update_does_not_overwrite_a_hardlinked_sibling(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source = self._source(base)
            host = base / "host"
            wrapper = host / "aaa-valid"
            (wrapper / "agents").mkdir(parents=True)
            (wrapper / "SKILL.md").write_text("stale skill")
            victim = base / "sibling.yaml"
            victim.write_text("keep sibling")
            os.link(victim, wrapper / "agents" / "openai.yaml")
            result = self._cli(source, "skills", "install", "--skills-root", str(host), "--write")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(victim.read_text(), "keep sibling")
            self.assertNotEqual((wrapper / "agents" / "openai.yaml").read_text(), "keep sibling")

    def test_preflight_rejects_other_filenames(self):
        with tempfile.TemporaryDirectory() as d:
            source = self._source(Path(d).resolve())
            other = source / "skills" / "aaa-valid" / "OTHER.md"
            other.write_bytes((other.parent / "SKILL.md").read_bytes())
            result = self._cli(source, "skills", "install-check", str(other))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MINIME_E_INSTALL_INVALID_PATH", result.stderr)



class TokenConsciousSkillTests(unittest.TestCase):
    def test_target_reusable_skills_are_token_conscious(self):
        skills_root = REPO_ROOT / "skills"
        emoji_pattern = re.compile(
            r'[\U0001F300-\U0001F9FF]'
            r'|[\U0001FA00-\U0001FA6F]'
            r'|[\U00002702-\U000027B0]'
            r'|[\U0001F600-\U0001F64F]'
            r'|[\U0001F680-\U0001F6FF]'
            r'|[\U00002600-\U000026FF]'
            r'|[\U0001F1E0-\U0001F1FF]',
        )
        filler_phrases = re.compile(
            r'(?i)('
            r'let me (help|guide|walk|show|assist) you'
            r'|I hope this (helps|is useful|is helpful)'
            r'|feel free to (reach out|ask|contact)'
            r'|let me know if you (need|have|want)'
            r'|don.t hesitate to'
            r'|happy to (help|assist|answer|clarify)'
            r'|please (let me know|feel free|don.t hesitate)'
            r'|good luck'
            r')',
        )
        # Transcript-like structural signatures: conversational step headers
        # that indicate a transcribed session rather than a distilled procedure.
        # "Now do X" / "Next, Y" as section headers are transcript markers;
        # "Step N — <name>" and "Next Step" are legitimate procedure structure.
        transcript_step = re.compile(
            r'(?m)^#{1,4}\s+(Now\s+(do|let|we|you)\b|Next,\s+\w)',
        )
        TRANSCRIPT_STEP_LIMIT = 2
        MAX_BYTES = 15_000
        VERBOSITY_RATIO = 4.0

        skill_bodies = []
        for skill_dir in sorted(skills_root.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue

            text = skill_file.read_text(encoding="utf-8")
            body = text.split("---", 2)[-1] if text.startswith("---") else text
            byte_count = len(text.encode("utf-8"))
            word_count = len(body.split())
            skill_bodies.append((skill_dir.name, byte_count, word_count, body))

        med_word = sorted(wc for _, _, wc, _ in skill_bodies)[len(skill_bodies) // 2]

        for name, byte_count, word_count, body in skill_bodies:
            with self.subTest(skill=name):
                emoji_match = emoji_pattern.search(body)
                if emoji_match is not None:
                    self.fail(f"emoji found in {name} body: {emoji_match.group()!r}")

                filler_match = filler_phrases.search(body)
                if filler_match is not None:
                    self.fail(f"conversational filler found in {name} body: {filler_match.group()!r}")

                transcript_matches = transcript_step.findall(body)
                if len(transcript_matches) >= TRANSCRIPT_STEP_LIMIT:
                    self.fail(
                        f"{name} has {len(transcript_matches)} transcript-like step headers "
                        f"(matched: '### Now do/let/we/you' or '### Next, <word>'). "
                        f"Distill to a procedure: replace conversational headers with a named section "
                        f"and prose rules."
                    )

                if byte_count > MAX_BYTES:
                    self.fail(
                        f"{name} is {byte_count} bytes, exceeds {MAX_BYTES} cap. "
                        f"Compress or split before committing."
                    )

                if med_word > 0 and word_count > med_word * VERBOSITY_RATIO:
                    self.fail(
                        f"{name} is {word_count} words ({VERBOSITY_RATIO:.0f}x the median of {med_word}). "
                        f"Distill before committing: trim conversational patterns and redundant restatement."
                    )


    def test_target_reusable_skills_have_no_internal_references(self):
        target_skills, _ = minime._target_reusable_skills(REPO_ROOT)
        forbidden = "scripts/minime"
        for entry in target_skills:
            skill_file = REPO_ROOT / entry["path"]
            text = skill_file.read_text(encoding="utf-8")
            if forbidden in text:
                self.fail(
                    f"{entry['name']} contains '{forbidden}' — "
                    f"MiniMe-internal tooling must not appear in target-reusable skills."
                )

class CatalogDRYTests(unittest.TestCase):
    """Drift-guard: no two target-reusable skills should overlap enough to merge.

    Threshold 0.20 calibrated from the first DRY sweep (2026-05-22).
    Top observed pair was minime-code-reviewer / minime-code-simplifier at 0.179.
    """

    _STOPWORDS = frozenset({
        "the", "and", "for", "with", "use", "when", "that", "this", "are", "from",
        "into", "have", "not", "any", "but", "all", "its", "you", "your", "via",
        "skill", "skills", "minime", "user", "users", "agent", "agents",
        "before", "after", "during", "each",
    })
    SIMILARITY_THRESHOLD = 0.20

    @classmethod
    def _tokenize(cls, text: str) -> set:
        import re
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        return {t for t in tokens if len(t) >= 3 and t not in cls._STOPWORDS}

    @classmethod
    def _descriptor(cls, skill_file: Path) -> dict:
        text = skill_file.read_text(encoding="utf-8")
        lines = text.splitlines()
        name = description = ""
        if lines and lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                if line.startswith(("  ", "\t")):
                    continue
                if line.startswith("name:"):
                    name = line[len("name:"):].strip()
                elif line.startswith("description:"):
                    description = line[len("description:"):].strip()
        return {"name": name, "description": description}

    def test_no_skill_pair_exceeds_similarity_threshold(self):
        skills_root = REPO_ROOT / "skills"
        skill_files = sorted(
            p / "SKILL.md"
            for p in skills_root.iterdir()
            if (p / "SKILL.md").is_file()
        )
        descriptors = {
            f.parent.name: self._tokenize(
                f"{self._descriptor(f)['name']} {self._descriptor(f)['description']}"
            )
            for f in skill_files
        }
        names = sorted(descriptors)
        violations = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                ta, tb = descriptors[a], descriptors[b]
                union = ta | tb
                if not union:
                    continue
                score = len(ta & tb) / len(union)
                if score >= self.SIMILARITY_THRESHOLD:
                    violations.append((score, a, b))

        if violations:
            lines = "\n".join(
                f"  {s:.3f}  {a}  <->  {b}"
                for s, a, b in sorted(violations, reverse=True)
            )
            self.fail(
                f"Skill pairs exceed similarity threshold {self.SIMILARITY_THRESHOLD}.\n"
                f"Assess for DRY merge:\n"
                f"{lines}"
            )


class KnownLimitsDriftGuardTests(unittest.TestCase):
    def test_known_limits_write_commands_match_actual_cli(self):
        """The Known Limits claim about which commands accept --write must
        match what the CLI actually exposes. When a new --write flag is added,
        both the Known Limits text and this test must be updated together.
        """
        # Discover which skills subcommands actually have --write
        actual_write_commands = []
        for cmd in ["apply", "unapply", "install", "install-check", "list"]:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"),
                 "skills", cmd, "--help"],
                capture_output=True, text=True,
            )
            if "--write" in result.stdout:
                actual_write_commands.append(cmd)

        actual_write_commands.sort()

        # Read the Known Limits claim from README
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        limits_section = readme.split("## Known Limits")[1].split("##")[0]
        # Join markdown continuation lines (lines indented under a bullet)
        lines = limits_section.split("\n")
        joined = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("- ") or not joined:
                joined.append(line)
            else:
                joined[-1] = joined[-1] + " " + line.strip()
        write_line = [line for line in joined if "--write" in line]
        self.assertTrue(write_line, "Known Limits must contain a line about --write commands")
        write_text = write_line[0]

        # Verify the claim names exactly the right commands
        for cmd in actual_write_commands:
            self.assertIn(cmd, write_text,
                          f"Known Limits must mention 'skills {cmd}' as a write command")

        # Verify no rollback/cleanup subcommand exists (Known Limits claims none)
        for cmd in ["rollback", "cleanup"]:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "minime"),
                 "skills", cmd],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0,
                                f"'skills {cmd}' should not exist per Known Limits")


class RoutingTableCompletenessTests(unittest.TestCase):
    """Every user-invokable target-reusable skill must appear in the
    AGENTS.md routing table. Inter-skill plumbing skills (invoked only by
    other skills, never directly by the user) are explicitly excluded.
    """

    INTER_SKILL_PLUMBING = {
        "minime-decision-prompt",
    }

    def test_routing_table_lists_all_user_invokable_target_reusable_skills(self):
        result = subprocess.run(
            [str(REPO_ROOT / "scripts" / "minime"), "skills", "list", "--json"],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        target_reusable = {
            s["name"] for s in data["skills"]
            if s["minime_kind"] == "target-reusable"
        }

        expected = target_reusable - self.INTER_SKILL_PLUMBING
        guide = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        missing = sorted(name for name in expected if f"`{name}`" not in guide)
        self.assertFalse(
            missing,
            msg=(
                f"AGENTS.md routing table missing user-invokable skills: {missing}. "
                "Add a row to the routing table or, if the skill is inter-skill "
                "plumbing, add it to RoutingTableCompletenessTests.INTER_SKILL_PLUMBING."
            ),
        )


if __name__ == "__main__":
    unittest.main()
