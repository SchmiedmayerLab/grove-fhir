"""Require published adapter status matrices to match their machine catalogs exactly."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StatusMatrixTests(unittest.TestCase):
    def test_generated_matrices_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, "Scripts/render-status-matrices.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_published_matrices_do_not_reference_mutable_work_tracking(self) -> None:
        for path in ROOT.glob("*/input/pagecontent/*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("PR 60", text, path)
            self.assertNotIn("working document", text.lower(), path)
            self.assertNotIn("future published version", text.lower(), path)


if __name__ == "__main__":
    unittest.main()
