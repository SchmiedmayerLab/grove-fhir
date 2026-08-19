"""Tests for immutable event ranges and the six-axis conformance path matrix."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SPECIFICATION = importlib.util.spec_from_file_location(
    "conformance_path_matrix", ROOT / "Scripts/conformance-path-matrix.py"
)
assert SPECIFICATION and SPECIFICATION.loader
MATRIX = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(MATRIX)


class ConformancePathMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = ROOT / "Conformance/evidence.json"
        self.matrix = MATRIX.load_path_matrix(self.manifest)
        self.ignored = MATRIX.load_ignored_paths(self.manifest)
        self.assertEqual(
            set(self.matrix),
            {
                "grove_questionnaire",
                "grove_mobile",
                "mhc_ios_study",
                "android",
                "firebase",
                "evidence_common",
            },
        )

    def test_pr_push_zero_and_dispatch_event_ranges_are_exact(self) -> None:
        base = "1" * 40
        head = "2" * 40
        self.assertEqual(
            MATRIX.event_range(
                "pull_request",
                {"pull_request": {"base": {"sha": base}, "head": {"sha": head}}},
            ),
            (base, head, False),
        )
        self.assertEqual(
            MATRIX.event_range("push", {"before": base, "after": head}),
            (base, head, False),
        )
        self.assertEqual(
            MATRIX.event_range("push", {"before": MATRIX.ZERO_COMMIT, "after": head}),
            (MATRIX.ZERO_COMMIT, head, True),
        )
        self.assertEqual(
            MATRIX.event_range("workflow_dispatch", {}),
            (MATRIX.ZERO_COMMIT, MATRIX.ZERO_COMMIT, True),
        )

    def test_common_unknown_and_sensor_only_have_safe_aggregate_behavior(self) -> None:
        common = MATRIX.classify_paths(
            self.matrix, ["Conformance/evidence.json"], self.ignored
        )
        unknown = MATRIX.classify_paths(
            self.matrix, ["new-top-level-input.txt"], self.ignored
        )
        sensor = MATRIX.classify_paths(
            self.matrix,
            ["Integration/Sources/GroveSensorKit/Sources/Sensor.swift"],
            self.ignored,
        )
        self.assertTrue(all(common.values()))
        self.assertTrue(all(unknown.values()))
        self.assertFalse(any(sensor.values()))

    def test_rename_from_relevant_to_ignored_and_deletion_remain_relevant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            self._git(repository, "init")
            self._git(repository, "config", "user.email", "test@example.org")
            self._git(repository, "config", "user.name", "Test")
            self._git(repository, "config", "commit.gpgsign", "false")
            relevant = repository / "mobile/input/fsh/example.fsh"
            relevant.parent.mkdir(parents=True)
            relevant.write_text("Profile: Example\n", encoding="utf-8")
            self._git(repository, "add", ".")
            self._git(repository, "commit", "-m", "base")
            base = self._git(repository, "rev-parse", "HEAD")

            ignored = repository / "Integration/Sources/GroveSensorKit/example.fsh"
            ignored.parent.mkdir(parents=True)
            relevant.rename(ignored)
            self._git(repository, "add", "-A")
            self._git(repository, "commit", "-m", "rename")
            renamed = self._git(repository, "rev-parse", "HEAD")
            changed = MATRIX.changed_paths_from_git(repository, base, renamed)
            self.assertEqual(
                changed,
                [
                    "Integration/Sources/GroveSensorKit/example.fsh",
                    "mobile/input/fsh/example.fsh",
                ],
            )
            result = MATRIX.classify_paths(self.matrix, changed, self.ignored)
            self.assertTrue(result["grove_mobile"])

            ignored.unlink()
            self._git(repository, "add", "-A")
            self._git(repository, "commit", "-m", "delete")
            deleted = self._git(repository, "rev-parse", "HEAD")
            self.assertEqual(
                MATRIX.changed_paths_from_git(repository, renamed, deleted),
                ["Integration/Sources/GroveSensorKit/example.fsh"],
            )

    def test_nonexistent_revision_is_rejected_before_diff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            self._git(repository, "init")
            with self.assertRaisesRegex(MATRIX.PathMatrixError, "exact base commit"):
                MATRIX.changed_paths_from_git(repository, "a" * 40, "b" * 40)

    @staticmethod
    def _git(repository: Path, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()


if __name__ == "__main__":
    unittest.main()
