"""Bind published adapter source terminologies to the closed inventories."""

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


class AdapterSourceTerminologyTests(unittest.TestCase):
    def test_generated_source_terminologies_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, "Scripts/render-adapter-source-terminology.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
