# Copyright (c) 2026 Hygon Information Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Exercise the Git clone/sparse-checkout path with a local upstream fixture."""

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_sources  # noqa: E402


class ExternalSyncTests(unittest.TestCase):
    def test_import_update_drift_and_failed_source_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            upstream = root / "upstream"
            catalog = root / "catalog"
            upstream.mkdir()
            (catalog / "components.d").mkdir(parents=True)
            name = "skillhub-contributor"
            source = upstream / "skills" / name
            shutil.copytree(Path(__file__).resolve().parents[1] / "skills" / name, source)
            card = source / "skill-card.md"
            card.write_text(card.read_text(encoding="utf-8").replace(
                "HYGON-AI/skillhub", "someone/tool-skills"), encoding="utf-8")
            registry = catalog / "components.d" / "external.yml"
            registration = (
                "name: External\nrepo: someone/tool-skills\nref: main\n"
                "description: External source fixture.\nskills:\n"
                f"  - path: skills/{name}\n    catalog_dir: {name}\n"
                "    category: Developer Tools\n"
            )
            registry.write_text(registration, encoding="utf-8")

            def git(*args):
                return subprocess.check_output(
                    ["git", "-C", str(upstream), *args], stderr=subprocess.STDOUT,
                    text=True,
                ).strip()

            git("init", "-b", "main")
            git("config", "user.name", "Fixture Author")
            git("config", "user.email", "fixture@example.com")
            git("config", "core.autocrlf", "false")
            git("add", ".")
            git("commit", "-m", "Initial skill")
            real_call = subprocess.check_call
            real_load = sync_sources.load_components

            def clone_from_fixture(command, *args, **kwargs):
                command = list(command)
                if command[:2] == ["git", "clone"]:
                    self.assertEqual(command[-2], "https://github.com/someone/tool-skills.git")
                    command[-2] = upstream.as_uri()
                return real_call(command, *args, **kwargs)

            with patch.object(sync_sources, "ROOT", catalog), \
                    patch.object(sync_sources, "load_components", lambda: real_load(catalog)), \
                    patch.object(sync_sources.subprocess, "check_call", clone_from_fixture):
                def sync(check=False):
                    with patch.object(sys, "argv", ["sync_sources.py"] + (["--check"] if check else [])), \
                            contextlib.redirect_stdout(io.StringIO()):
                        return sync_sources.main()

                self.assertEqual(sync(), 0)
                self.assertEqual(sync(True), 0)
                lock_path = catalog / ".skillhub-lock.json"
                first = json.loads(lock_path.read_text())["skills"][name]
                self.assertEqual(first["repo"], "someone/tool-skills")
                self.assertEqual(first["commit"], git("rev-parse", "HEAD"))
                (source / "references" / "update.md").write_text("Reviewed upstream update.\n")
                git("add", ".")
                git("commit", "-m", "Update skill")
                self.assertEqual(sync(True), 1)
                self.assertEqual(sync(), 0)
                self.assertEqual(sync(True), 0)
                updated = json.loads(lock_path.read_text())["skills"][name]
                self.assertNotEqual(first["content_digest"], updated["content_digest"])
                published = catalog / "skills" / name
                digest = sync_sources.file_tree_digest(published)
                lock_bytes = lock_path.read_bytes()

                registry.write_text(registration.replace("ref: main", "ref: missing-ref"))
                with self.assertRaises(subprocess.CalledProcessError):
                    sync()
                self.assertEqual(lock_path.read_bytes(), lock_bytes)
                self.assertEqual(sync_sources.file_tree_digest(published), digest)
                registry.write_text(registration)
                self.assertEqual(sync(True), 0)

                git("rm", f"skills/{name}/SKILL.md")
                git("commit", "-m", "Remove skill entrypoint")
                with self.assertRaisesRegex(sync_sources.CatalogError, "does not contain SKILL.md"):
                    sync()
                self.assertEqual(lock_path.read_bytes(), lock_bytes)
                self.assertEqual(sync_sources.file_tree_digest(published), digest)
