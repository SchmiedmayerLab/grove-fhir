"""Require published adapter status matrices to match their machine catalogs exactly."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
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

    def test_generated_matrix_headings_fit_the_ig_page_hierarchy(self) -> None:
        for path in ROOT.glob("*/input/pagecontent/status-matrix.md"):
            headings = re.findall(r"^(#+) ", path.read_text(encoding="utf-8"), re.MULTILINE)
            self.assertTrue(headings, path)
            self.assertEqual(headings[0], "###", path)
            self.assertTrue(all(len(heading) >= 3 for heading in headings), path)

    def test_healthkit_intro_classifies_every_contract_status(self) -> None:
        text = (
            ROOT / "healthkit/input/pagecontent/status-matrix.md"
        ).read_text(encoding="utf-8")
        for status in ("supported", "platform-exclusive", "mapped-standard"):
            self.assertIn(f"`{status}`", text)
        for status in ("unmodeled", "deferred", "intentionally-unsupported"):
            self.assertIn(f"`{status}`", text)
        self.assertIn("admit only the output contract(s) named in that row", text)
        self.assertIn("admit no output", text)

    def test_profile_claim_columns_contain_complete_claim_sets(self) -> None:
        healthkit = (
            ROOT / "healthkit/input/pagecontent/status-matrix.md"
        ).read_text(encoding="utf-8")
        recording_claims = (
            "grove-sensor-recording-document; healthkit-recording-document"
        )
        for source_type in (
            "HKDataTypeIdentifierHeartbeatSeries",
            "HKDocumentTypeIdentifierCDA",
            "HKWorkoutRouteTypeIdentifier",
        ):
            row = next(line for line in healthkit.splitlines() if source_type in line)
            self.assertIn(recording_claims, row)
        workout_row = next(
            line
            for line in healthkit.splitlines()
            if "HKWorkoutTypeIdentifier" in line
        )
        self.assertIn(
            "workout: grove-mobile-workout + healthkit-observation; "
            "workout-segment: grove-mobile-workout-segment + healthkit-observation",
            workout_row,
        )

        sensorkit = (
            ROOT / "sensorkit/input/pagecontent/status-matrix.md"
        ).read_text(encoding="utf-8")
        for line in sensorkit.splitlines():
            if line.startswith("| `SRSensor."):
                columns = [column.strip() for column in line.strip("|").split("|")]
                self.assertNotEqual(columns[5], "deferred", line)
                self.assertNotEqual(columns[6], "deferred", line)

        providers = (
            ROOT / "providers/input/pagecontent/status-matrix.md"
        ).read_text(encoding="utf-8")
        provider_recording_claims = (
            "grove-sensor-recording-document; providers-recording-document"
        )
        mapped_row = next(
            line for line in providers.splitlines() if "`oura` | `heartrate`" in line
        )
        self.assertIn(provider_recording_claims, mapped_row)

        withings = (
            ROOT / "withings/input/pagecontent/status-matrix.md"
        ).read_text(encoding="utf-8")
        for member in ("getmeas:9", "getmeas:10"):
            row = next(
                line
                for line in withings.splitlines()
                if line.startswith(f"| `{member}` |")
            )
            self.assertIn("required member of `getmeas:9+10`", row)
            self.assertIn("no standalone output", row)


if __name__ == "__main__":
    unittest.main()
