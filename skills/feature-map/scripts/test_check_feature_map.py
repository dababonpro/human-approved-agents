"""Tests for check_feature_map.py. Each test builds a throwaway git repo. Run: python -m unittest test_check_feature_map"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_feature_map as cfm  # noqa: E402

MAP = """
[settings]
mapped_paths = ["src/**"]
ignore = ["src/generated/**"]
test_paths = ["tests/**"]

[[feature]]
id = "contact"
owner = "owner"
must_stay_true = ["A sent form reaches the inbox"]
code = ["src/contact/**"]
proof = ["python tests/check_contact.py"]

[[feature]]
id = "billing"
must_stay_true = ["An invoice is charged once"]
code = ["src/billing.py"]
proof = ["python -c \\"raise SystemExit(3)\\""]
"""


def sh(*args):
    subprocess.run(args, check=True, capture_output=True)


class FeatureMapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp.name)
        sh("git", "init", "-q", "-b", "main")
        sh("git", "config", "user.email", "test@example.com")
        sh("git", "config", "user.name", "test")
        self.write("features.toml", MAP)
        self.write("src/contact/form.py", "x = 1\n")
        self.write("src/billing.py", "y = 1\n")
        self.write("src/other.py", "z = 1\n")
        self.write("tests/check_contact.py", "print('ok')\n")
        self.commit("base")
        sh("git", "checkout", "-q", "-b", "work")

    def write(self, path, text):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")

    def commit(self, message="change"):
        sh("git", "add", "-A")
        sh("git", "commit", "-q", "-m", message)

    def codes(self, **kwargs):
        return [f.split(":")[0] for f in cfm.check("main", "features.toml", **kwargs).failures]

    def test_change_inside_a_feature_passes_and_names_it(self):
        self.write("src/contact/form.py", "x = 2\n")
        self.commit()
        report = cfm.check("main", "features.toml")
        self.assertEqual(report.failures, [])
        self.assertEqual([f["id"] for f in report.touched], ["contact"])

    def test_unmapped_file_under_mapped_paths_fails(self):
        self.write("src/other.py", "z = 2\n")
        self.commit()
        self.assertEqual(self.codes(), ["UNMAPPED"])

    def test_new_unmapped_file_fails(self):
        self.write("src/brand_new.py", "n = 1\n")
        self.commit()
        self.assertEqual(self.codes(), ["UNMAPPED"])

    def test_ignored_and_out_of_scope_files_pass(self):
        self.write("src/generated/a.py", "g = 1\n")
        self.write("docs/note.md", "text\n")
        self.commit()
        self.assertEqual(self.codes(), [])

    def test_proof_runs_and_failure_is_reported(self):
        self.write("src/contact/form.py", "x = 2\n")
        self.write("src/billing.py", "y = 2\n")
        self.commit()
        report = cfm.check("main", "features.toml", run=True)
        self.assertEqual(len(report.proofs), 2)
        self.assertEqual([f.split(":")[0] for f in report.failures], ["PROOF-FAILED"])
        self.assertIn("billing", report.failures[0])

    def test_unrelated_proofs_do_not_run(self):
        self.write("src/contact/form.py", "x = 2\n")
        self.commit()
        report = cfm.check("main", "features.toml", run=True)
        self.assertEqual(report.proofs, ["PASS  python tests/check_contact.py"])

    def test_deleted_test_fails(self):
        self.write("tests/old_test.py", "ok = 1\n")
        self.commit("add test")
        sh("git", "checkout", "-q", "main")
        sh("git", "merge", "-q", "work")
        sh("git", "checkout", "-q", "work")
        Path("tests/old_test.py").unlink()
        self.commit()
        self.assertEqual(self.codes(), ["TEST-REMOVED"])

    def test_added_skip_marker_fails(self):
        self.write("tests/check_contact.py", "print('ok')\nit.skip('later', fn)\n")
        self.commit()
        self.assertEqual(self.codes(), ["TEST-WEAKENED"])

    def test_removed_promise_fails_until_approved(self):
        self.write("features.toml", MAP.replace('must_stay_true = ["A sent form reaches the inbox"]', 'must_stay_true = ["Something easier"]'))
        self.commit()
        self.assertEqual(self.codes(), ["MAP-WEAKENED"])
        self.assertEqual(self.codes(promises_approved=True), [])

    def test_narrowed_code_path_fails(self):
        self.write("features.toml", MAP.replace('code = ["src/contact/**"]', 'code = ["src/contact/form.py"]'))
        self.commit()
        self.assertEqual(self.codes(), ["MAP-WEAKENED"])

    def test_changed_proof_is_not_run(self):
        self.write("features.toml", MAP.replace("python tests/check_contact.py", "python -c pass"))
        self.write("src/contact/form.py", "x = 2\n")
        self.commit()
        report = cfm.check("main", "features.toml", run=True)
        self.assertEqual(report.proofs, [])
        self.assertIn("MAP-WEAKENED", report.failures[0])

    def test_added_promise_is_fine(self):
        self.write("features.toml", MAP.replace('["A sent form reaches the inbox"]', '["A sent form reaches the inbox", "It is logged"]'))
        self.commit()
        self.assertEqual(self.codes(), [])

    def test_stale_code_path_fails(self):
        Path("src/billing.py").unlink()
        self.commit()
        self.assertIn("STALE-MAP", self.codes())

    def test_worktree_mode_sees_uncommitted_and_untracked_files(self):
        self.write("src/fresh.py", "n = 1\n")
        self.assertEqual(self.codes(), [])
        self.assertEqual(self.codes(worktree=True), ["UNMAPPED"])

    def test_invalid_map_is_an_error_not_a_pass(self):
        self.write("features.toml", "[[feature\n")
        self.assertEqual(cfm.main(["--base", "main"]), 2)

    def test_no_proof_fails_for_a_touched_feature(self):
        self.write("features.toml", MAP + '\n[[feature]]\nid = "new"\nmust_stay_true = ["x"]\ncode = ["src/other.py"]\n')
        self.write("src/other.py", "z = 2\n")
        self.commit()
        self.assertEqual(self.codes(), ["NO-PROOF"])

    def test_emptying_test_paths_needs_a_person(self):
        self.write("features.toml", MAP.replace('test_paths = ["tests/**"]', "test_paths = []"))
        self.commit()
        self.assertEqual(self.codes(), ["MAP-WEAKENED"])

    def test_narrowing_mapped_paths_needs_a_person(self):
        self.write("features.toml", MAP.replace('mapped_paths = ["src/**"]', 'mapped_paths = ["src/contact/**"]'))
        self.commit()
        self.assertIn("MAP-WEAKENED", self.codes())

    def test_adding_to_ignore_needs_a_person(self):
        self.write("features.toml", MAP.replace('ignore = ["src/generated/**"]', 'ignore = ["src/generated/**", "src/**"]'))
        self.commit()
        self.assertIn("MAP-WEAKENED", self.codes())

    def test_replacing_skip_patterns_needs_a_person(self):
        self.write("features.toml", MAP.replace('test_paths = ["tests/**"]', 'test_paths = ["tests/**"]\nskip_patterns = []'))
        self.commit()
        self.assertIn("MAP-WEAKENED", self.codes())

    def test_string_promise_is_an_error(self):
        self.write("features.toml", MAP.replace('must_stay_true = ["A sent form reaches the inbox"]', 'must_stay_true = "A sent form reaches the inbox, unless busy"'))
        self.commit()
        self.assertEqual(cfm.main(["--base", "main"]), 2)

    def test_added_proof_needs_a_person_and_does_not_run(self):
        self.write("features.toml", MAP.replace('proof = ["python tests/check_contact.py"]', 'proof = ["python -c \\"open(1)\\"", "python tests/check_contact.py"]'))
        self.write("src/contact/form.py", "x = 2\n")
        self.commit()
        report = cfm.check("main", "features.toml", run=True)
        self.assertEqual(report.proofs, [])
        self.assertIn("MAP-WEAKENED", report.failures[0])

    def test_a_catch_all_feature_needs_a_person(self):
        self.write("features.toml", MAP + '\n[[feature]]\nid = "all"\nmust_stay_true = ["x"]\ncode = ["src/**"]\nproof = ["exit 0"]\n')
        self.write("src/other.py", "z = 2\n")
        self.commit()
        self.assertIn("MAP-WEAKENED", self.codes())

    def test_editing_a_test_needs_a_person(self):
        self.write("tests/check_contact.py", "print('changed')\n")
        self.commit()
        self.assertEqual(self.codes(), ["TEST-EDITED"])

    def test_commenting_out_a_test_needs_a_person(self):
        self.write("tests/check_contact.py", "# print('ok')\n")
        self.commit()
        self.assertEqual(self.codes(), ["TEST-EDITED"])

    def test_adding_a_test_is_fine(self):
        self.write("tests/check_contact.py", "print('ok')\nprint('another check')\n")
        self.commit()
        self.assertEqual(self.codes(), [])

    def test_removing_a_skip_marker_is_fine(self):
        self.write("tests/check_contact.py", "print('ok')\n@unittest.skip('later')\ndef test_x(): pass\n")
        self.commit("add skipped test")
        sh("git", "checkout", "-q", "main")
        sh("git", "merge", "-q", "work")
        sh("git", "checkout", "-q", "work")
        self.write("tests/check_contact.py", "print('ok')\ndef test_x(): pass\n")
        self.commit()
        self.assertEqual(self.codes(), [])

    def test_more_skip_markers_are_seen(self):
        for line in ("self.skipTest('x')", "raise unittest.SkipTest('x')", "pytestmark = 1", "fit('x', fn)", "t.SkipNow()"):
            self.write("tests/check_contact.py", f"print('ok')\n{line}\n")
            self.commit(line)
            self.assertEqual(self.codes(), ["TEST-WEAKENED"], line)
            sh("git", "reset", "-q", "--hard", "HEAD~1")

    def test_approval_covers_test_changes(self):
        self.write("tests/check_contact.py", "print('changed')\n")
        self.commit()
        self.assertEqual(self.codes(promises_approved=True), [])

    def test_unicode_paths_are_seen(self):
        self.write("src/caf\u00e9.py", "c = 1\n")
        self.commit()
        self.assertEqual(self.codes(), ["UNMAPPED"])

    def test_plain_directory_in_code_is_reported_as_stale(self):
        self.write("features.toml", MAP.replace('code = ["src/contact/**"]', 'code = ["src/contact/**", "src/contact"]'))
        self.commit()
        self.assertIn("STALE-MAP", self.codes())

    def test_changed_map_runs_its_proofs(self):
        self.write("features.toml", MAP.replace('must_stay_true = ["An invoice is charged once"]', 'must_stay_true = ["An invoice is charged once", "It is logged"]'))
        self.commit()
        report = cfm.check("main", "features.toml", run=True)
        self.assertEqual([f.split(":")[0] for f in report.failures], ["PROOF-FAILED"])

    def test_a_moved_base_gives_no_false_failure(self):
        sh("git", "checkout", "-q", "main")
        self.write("features.toml", MAP.replace('["A sent form reaches the inbox"]', '["A sent form reaches the inbox", "New on main"]'))
        self.commit("main moved")
        sh("git", "checkout", "-q", "work")
        self.write("src/contact/form.py", "x = 2\n")
        self.commit()
        self.assertEqual(self.codes(), [])

    def test_windows_style_map_path_still_finds_the_base_map(self):
        self.write("features.toml", MAP.replace("A sent form reaches the inbox", "Something easier"))
        self.commit()
        report = cfm.check("main", ".\\features.toml" if os.sep == "\\" else "./features.toml")
        self.assertIn("MAP-WEAKENED", [f.split(":")[0] for f in report.failures])


class GlobTest(unittest.TestCase):
    def test_globs(self):
        self.assertTrue(cfm.matches("src/a/b.py", ["src/**"]))
        self.assertTrue(cfm.matches("src/a/b.py", ["src/**/b.py"]))
        self.assertTrue(cfm.matches("src/b.py", ["src/**/b.py"]))
        self.assertTrue(cfm.matches("b.md", ["*.md"]))
        self.assertFalse(cfm.matches("src/b.md", ["*.md"]))
        self.assertTrue(cfm.matches("src/b.md", ["**/*.md"]))


if __name__ == "__main__":
    unittest.main()
