"""Test dependency-closed draft guide selection."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "select_draft_guides", ROOT / "Scripts/select-draft-guides.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DraftGuideSelectionTests(unittest.TestCase):
    def test_mobile_change_builds_every_reverse_dependency(self) -> None:
        self.assertEqual(
            MODULE.select(["mobile/input/fsh/profiles.fsh"]),
            [
                "mobile",
                "sensor",
                "sensorkit",
                "healthkit",
                "health-connect",
                "providers",
            ],
        )

    def test_sensor_change_builds_sensor_consumers_only(self) -> None:
        self.assertEqual(
            MODULE.select(["sensor/input/fsh/profiles.fsh"]),
            ["sensor", "sensorkit", "healthkit", "providers"],
        )

    def test_adapter_and_questionnaire_changes_remain_scoped(self) -> None:
        self.assertEqual(
            MODULE.select(["catalog/health-connect-adapter.json"]),
            ["health-connect"],
        )
        self.assertEqual(
            MODULE.select(["questionnaire/input/fsh/profiles.fsh"]),
            ["questionnaire"],
        )

    def test_shared_build_or_unknown_catalog_change_builds_all(self) -> None:
        all_guides = [
            "mobile",
            "questionnaire",
            "sensor",
            "sensorkit",
            "healthkit",
            "health-connect",
            "providers",
        ]
        self.assertEqual(MODULE.select(["Scripts/build-guides.sh"]), all_guides)
        self.assertEqual(MODULE.select(["catalog/profile-claims.json"]), all_guides)

    def test_non_guide_change_selects_no_guide(self) -> None:
        self.assertEqual(MODULE.select(["Tests/test_content.py"]), [])

    def test_changed_paths_includes_deletions_and_both_rename_paths(self) -> None:
        completed = mock.Mock(
            stdout="mobile/input/fsh/removed.fsh\nsensor/input/fsh/moved.fsh\n"
        )
        with mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run:
            self.assertEqual(
                MODULE.changed_paths("0" * 40, "1" * 40),
                [
                    "mobile/input/fsh/removed.fsh",
                    "sensor/input/fsh/moved.fsh",
                ],
            )

        command = run.call_args.args[0]
        self.assertIn("--no-renames", command)
        self.assertIn("--diff-filter=ACDMRTUXB", command)


if __name__ == "__main__":
    unittest.main()
