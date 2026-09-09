# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "check_content_files", Path(__file__).resolve().parents[1] / "Scripts/check-content.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ContentFileTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git("init", "--quiet")
        (self.root / ".gitignore").write_text("ignored/\n__pycache__/\n", encoding="utf-8")
        (self.root / "catalog").mkdir()
        (self.root / "publication").mkdir()
        (self.root / "publication/config.json").write_text(json.dumps({
            "releaseMode": "ci-build-only", "canonicalBaseUrl": "https://example.org/fhir", "guides": []
        }), encoding="utf-8")
        # Only the source-file boundary is under test; guide-specific checks have their own suites.
        overrides = patch.multiple(
            CHECK, ROOT=self.root, CATALOGS=self.root / "catalog", GUIDES=(), EXPECTED_GUIDE_SOURCES=()
        )
        overrides.start()
        self.addCleanup(overrides.stop)

    def git(self, *arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=self.root, check=True, capture_output=True)

    def test_inventory_includes_new_files_and_excludes_ignored_or_deleted_files(self) -> None:
        for name in ("tracked.json", "deleted.json", "new.json"):
            (self.root / name).write_text("{}", encoding="utf-8")
        self.git("add", "tracked.json", "deleted.json")
        (self.root / "deleted.json").unlink()
        (self.root / "ignored").mkdir()
        (self.root / "ignored/broken.json").write_text("{", encoding="utf-8")
        files = {path.relative_to(self.root).as_posix() for path in CHECK.source_files()}
        self.assertEqual(files, {".gitignore", "publication/config.json", "tracked.json", "new.json"})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(CHECK.main(), 0)

    def test_unstaged_invalid_json_and_python_fail_the_content_check(self) -> None:
        for name, content, diagnostic in (
            ("new.json", "{", "invalid JSON in new.json"),
            ("new.py", "def invalid(\n", "invalid Python in new.py"),
        ):
            with self.subTest(name=name):
                candidate = self.root / name
                candidate.write_text(content, encoding="utf-8")
                output = io.StringIO()
                try:
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(CHECK.main(), 1)
                    self.assertIn(diagnostic, output.getvalue())
                finally:
                    candidate.unlink()

    def test_git_inventory_failure_is_not_an_empty_passing_check(self) -> None:
        outside = self.root / "not-a-repository"
        outside.mkdir()
        with patch.object(CHECK, "ROOT", outside), patch.dict("os.environ", {"GIT_CEILING_DIRECTORIES": str(self.root)}):
            with self.assertRaises(subprocess.CalledProcessError):
                CHECK.source_files()
