"""Bind published adapter source terminologies to the closed inventories."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
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

    def test_sensorkit_definitions_name_every_admitted_output(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        terminology = (
            ROOT / "sensorkit/input/fsh/generated-source-types.fsh"
        ).read_text(encoding="utf-8")
        recording_document = catalog["profileClaims"]["recordingDocument"]
        recording_claims = (
            recording_document["sourceNeutralProfile"].rsplit("/", 1)[-1],
            recording_document["adapterProfile"].rsplit("/", 1)[-1],
        )

        for entry in catalog["entries"]:
            code = entry["sourceTypeCode"]
            line = next(
                line for line in terminology.splitlines() if line.startswith(f"* #{code} ")
            )
            structured = entry.get("structured") or {}
            structured_profiles = [
                profile.rsplit("/", 1)[-1]
                for profile in (
                    structured.get("sourceNeutralProfile"),
                    structured.get("profile"),
                    structured.get("adapterProfile"),
                )
                if profile
            ]
            if structured_profiles:
                self.assertIn("a structured Observation", line)
                for profile in structured_profiles:
                    self.assertIn(profile, line)
            if entry.get("raw"):
                self.assertIn("a Recording Document", line)
                for profile in recording_claims:
                    self.assertIn(profile, line)
            if structured_profiles or entry.get("raw"):
                self.assertIn("Grove admits", line)
                self.assertNotIn("Grove admits no output", line)

    def test_sensorkit_definitions_keep_resource_claim_sets_separate(self) -> None:
        terminology = (
            ROOT / "sensorkit/input/fsh/generated-source-types.fsh"
        ).read_text(encoding="utf-8")
        for code in ("ecg", "rotation-rate"):
            line = next(
                line for line in terminology.splitlines() if line.startswith(f"* #{code} ")
            )
            structured_index = line.index("a structured Observation")
            recording_index = line.index("a Recording Document")
            self.assertLess(structured_index, recording_index)
            self.assertLess(
                line.index("grove-sensor-recording-document"),
                line.index("sensorkit-recording-document"),
            )
            self.assertGreater(
                line.index("grove-sensor-recording-document"), recording_index
            )


if __name__ == "__main__":
    unittest.main()
