# Copyright (c) 2026 Hygon Information Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import yaml

from scripts import contribute
from scripts.new_skill import TEMPLATE_ROOT
from scripts.skillhub import ALLOWED_CATEGORIES, validate_catalog


class ContributionTests(unittest.TestCase):
    def invoke(self, argv, root=contribute.ROOT):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            result = contribute.main(argv, root=root)
        return result, output.getvalue()

    def fixture(self, path):
        root = Path(path)
        (root / "components.d").mkdir()
        shutil.copytree(TEMPLATE_ROOT, root / "templates" / "skill")
        (root / "LICENSE").write_text("Apache License\nVersion 2.0\n", encoding="utf-8")
        (root / "NOTICE").write_text("Original attribution\n", encoding="utf-8")
        return root

    def new_args(self, name="example-tool"):
        return [
            "new", name, "--owner", "Tool Team", "--description", "Analyze tool logs.",
            "--license", "Apache-2.0", "--category", "Developer Tools", "--non-interactive",
        ]

    def snapshot(self, root):
        return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def test_interactive_new_creates_local_registration_and_keeps_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            number = str(sorted(ALLOWED_CATEGORIES).index("Developer Tools") + 1)
            answers = ["", "Tool Team", "Analyze tool logs.", "Apache-2.0", "99", number]
            with mock.patch("builtins.input", side_effect=answers), mock.patch.object(contribute, "run") as run:
                code, output = self.invoke(["new", "example-tool", "--with-references"], root)
            self.assertEqual(code, 0, output)
            run.assert_not_called()
            directory = root / "skills" / "example-tool"
            card = (directory / "skill-card.md").read_text(encoding="utf-8")
            self.assertIn("lifecycle: staging", card)
            self.assertIn("TODO", card)
            self.assertIn("references/details.md", (directory / "SKILL.md").read_text(encoding="utf-8"))
            for name in ("LICENSE", "NOTICE"):
                self.assertEqual((directory / name).read_bytes(), (root / name).read_bytes())
            self.assertFalse((directory / "evals").exists())
            registry = yaml.safe_load((root / "components.d" / "skillhub.yml").read_text(encoding="utf-8"))
            self.assertTrue(registry["local"])
            self.assertNotIn("repo", registry)
            self.assertEqual(registry["skills"][0]["category"], "Developer Tools")
            self.assertIn("contribute.py check example-tool", output)
            errors, _, _, _ = validate_catalog(root)
            self.assertTrue(any("lifecycle must equal 'published'" in error for error in errors), errors)

    def test_noninteractive_new_reuses_generator_and_does_not_touch_git(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            (root / ".git").mkdir()
            (root / ".git" / "HEAD").write_text("ref: refs/heads/work\n", encoding="utf-8")
            (root / ".git" / "index").write_bytes(b"existing index")
            before = self.snapshot(root / ".git")
            with mock.patch("builtins.input", side_effect=AssertionError("must not prompt")):
                code, output = self.invoke(self.new_args() + ["--with-openai"], root)
            self.assertEqual(code, 0, output)
            self.assertEqual(before, self.snapshot(root / ".git"))
            self.assertTrue((root / "skills" / "example-tool" / "agents" / "openai.yaml").is_file())

    def test_cancelled_or_incomplete_prompts_leave_no_files(self):
        for failure, expected in ((EOFError(), 1), (KeyboardInterrupt(), 130)):
            with self.subTest(failure=type(failure).__name__), tempfile.TemporaryDirectory() as temp:
                root = self.fixture(temp)
                before = self.snapshot(root)
                with mock.patch("builtins.input", side_effect=["Tool Team", failure]):
                    code, _ = self.invoke(["new", "example-tool"], root)
                self.assertEqual(code, expected)
                self.assertEqual(before, self.snapshot(root))

    def test_noninteractive_missing_metadata_fails_without_prompting_or_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            before = self.snapshot(root)
            with mock.patch("builtins.input", side_effect=AssertionError("must not prompt")):
                code, output = self.invoke(["new", "example-tool", "--non-interactive"], root)
            self.assertEqual(code, 1)
            self.assertIn("--license", output)
            self.assertEqual(before, self.snapshot(root))

    def test_invalid_name_and_existing_destination_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            for name in ("profile", "../outside"):
                before = self.snapshot(root)
                code, _ = self.invoke(self.new_args(name), root)
                self.assertEqual(code, 1)
                self.assertEqual(before, self.snapshot(root))
            self.assertEqual(self.invoke(self.new_args(), root)[0], 0)
            before = self.snapshot(root)
            code, output = self.invoke(self.new_args(), root)
            self.assertEqual(code, 1)
            self.assertIn("refusing to overwrite", output)
            self.assertEqual(before, self.snapshot(root))

    def test_invalid_category_is_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            before = self.snapshot(root)
            argv = self.new_args()
            argv[argv.index("Developer Tools")] = "Made Up Category"
            with self.assertRaises(SystemExit) as failure:
                self.invoke(argv, root)
            self.assertEqual(failure.exception.code, 2)
            self.assertEqual(before, self.snapshot(root))

    def test_dry_run_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            before = self.snapshot(root)
            code, output = self.invoke(self.new_args() + ["--dry-run"], root)
            self.assertEqual(code, 0, output)
            self.assertEqual(before, self.snapshot(root))

    def test_license_and_notice_overrides_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.fixture(temp)
            (root / "LICENSE.other").write_text("Reviewed license text", encoding="utf-8")
            (root / "NOTICE.other").write_text("Required notice", encoding="utf-8")
            code, output = self.invoke(self.new_args() + [
                "--license-file", "LICENSE.other", "--notice-file", "NOTICE.other",
            ], root)
            self.assertEqual(code, 0, output)
            directory = root / "skills" / "example-tool"
            self.assertEqual((directory / "LICENSE").read_bytes(), (root / "LICENSE.other").read_bytes())
            self.assertEqual((directory / "NOTICE").read_bytes(), (root / "NOTICE.other").read_bytes())

    def test_help_works_without_site_packages(self):
        result = subprocess.run(
            [sys.executable, "-S", str(contribute.ROOT / "scripts" / "contribute.py"), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("{new,check}", result.stdout)

    def test_missing_import_has_install_hint(self):
        with mock.patch.object(contribute, "local_module", side_effect=ModuleNotFoundError("yaml")):
            code, output = self.invoke(self.new_args())
        self.assertEqual(code, 1)
        self.assertIn("pip install -r requirements-dev.txt", output)

    def test_missing_tools_or_modules_fail_before_generation(self):
        for missing in ("git", "node", "npx", "yaml", "skills_ref"):
            with self.subTest(missing=missing), \
                 mock.patch.object(contribute.shutil, "which", side_effect=lambda name: None if name == missing else name), \
                 mock.patch.object(contribute.importlib.util, "find_spec", side_effect=lambda name: None if name == missing else object()), \
                 mock.patch.object(contribute, "run") as run:
                code, output = self.invoke(["check"])
            self.assertEqual(code, 1)
            self.assertIn(missing, output)
            run.assert_not_called()

    def test_all_stages_and_cli_outputs_are_checked_without_submission(self):
        with mock.patch.object(contribute, "check_environment", return_value="npx.cmd"), \
             mock.patch.object(contribute, "run", return_value=subprocess.CompletedProcess([], 0, "CLI output")) as run:
            code, output = self.invoke(["check", "skillhub-contributor"])
        self.assertEqual(code, 0, output)
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(commands, [
            [sys.executable, "scripts/generate_catalog.py"],
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            [sys.executable, "scripts/validate_skills.py"],
            [sys.executable, "scripts/validate_agent_skills_spec.py"],
            [sys.executable, "scripts/generate_catalog.py", "--check"],
            [sys.executable, "scripts/sync_sources.py", "--check"],
            ["npx.cmd", "--yes", "skills@1.5.23", "add", ".", "--list"],
            [sys.executable, "scripts/validate_cli_discovery.py"],
            ["npx.cmd", "--yes", "skills@1.5.23", "add", ".", "--list", "--full-depth"],
            [sys.executable, "scripts/validate_cli_discovery.py"],
        ])
        for index in (7, 9):
            self.assertEqual(run.call_args_list[index].kwargs["input_text"], "CLI output")
        self.assertIn("all repository checks", output)
        self.assertIn("PR Quality Gate, DCO and maintainer review are still required", output)

    def test_each_failed_stage_stops_pipeline_and_never_reports_pass(self):
        # Includes the npx producer and its separate output validator in both modes.
        for failed in range(10):
            results = [subprocess.CompletedProcess([], 0, "output") for _ in range(failed)]
            results.append(subprocess.CompletedProcess([], 7, "failure detail"))
            with self.subTest(failed=failed), \
                 mock.patch.object(contribute, "check_environment", return_value="npx"), \
                 mock.patch.object(contribute, "run", side_effect=results) as run:
                code, output = self.invoke(["check"])
            self.assertEqual(code, 1)
            self.assertEqual(run.call_count, failed + 1)
            self.assertIn("exit 7", output)
            self.assertNotIn("PASS:", output)

    def test_unregistered_skill_fails_before_generation(self):
        with mock.patch.object(contribute, "check_environment", return_value="npx"), \
             mock.patch.object(contribute, "run") as run:
            code, output = self.invoke(["check", "not-a-registered-skill"])
        self.assertEqual(code, 1)
        self.assertIn("not registered", output)
        run.assert_not_called()

    def test_process_error_is_actionable(self):
        with mock.patch.object(contribute, "check_environment", return_value="npx"), \
             mock.patch.object(contribute, "run", side_effect=OSError("cannot launch tool")):
            code, output = self.invoke(["check"])
        self.assertEqual(code, 1)
        self.assertIn("cannot launch tool", output)
        self.assertNotIn("PASS:", output)

    def test_runner_uses_checkout_utf8_and_no_shell(self):
        with mock.patch.object(contribute.subprocess, "run") as run:
            contribute.run(["npx.cmd", "--yes", "skills@1.5.23", "add", ".", "--list"], contribute.ROOT, capture=True)
        self.assertEqual(run.call_args.kwargs["cwd"], contribute.ROOT)
        self.assertEqual(run.call_args.kwargs["env"]["PYTHONUTF8"], "1")
        self.assertNotIn("shell", run.call_args.kwargs)
        self.assertEqual(run.call_args.kwargs["stdout"], subprocess.PIPE)

    def test_submit_subcommand_is_not_available(self):
        with self.assertRaises(SystemExit) as failure:
            self.invoke(["submit"])
        self.assertEqual(failure.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
