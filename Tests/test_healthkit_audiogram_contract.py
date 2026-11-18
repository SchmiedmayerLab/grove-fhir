#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

"""Audiogram source facts survive profile and example projection without review bypasses."""

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("audiogram_renderer", ROOT / "Scripts/render-measurement-profiles.py")
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


class AudiogramContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "catalog/measurement-catalog.json").read_text())
        cls.by_id = {row["id"]: row for row in cls.catalog["measurements"]}
        cls.row = cls.by_id["audiogram-panel"]
        cls.profile = RENDERER.render_profile(cls.row, RENDERER.alias_map(RENDERER.Layout(ROOT)), cls.by_id)

    def test_preserves_intervals_and_source_ear_frequency_cardinality(self):
        self.assertIn("* effective[x] only dateTime or Period", self.profile)
        self.assertTrue(all(row["cardinality"] == "0..1" for row in self.row["components"]))
        self.assertIn("* component ^slicing.rules = #open", self.profile)
        self.assertIn("HealthKitAudiogramTestDetails named sourceTest 1..1", self.profile)

    def test_known_frequency_codes_cannot_disagree_with_the_source_coordinates(self):
        for component in self.row["components"]:
            ear, frequency = component["id"].split("-", 1)
            prefix = f"* component[{component['id']}].extension[sourceTest].extension"
            self.assertIn(f"{prefix}[frequency].valueQuantity.value = {frequency} (exactly)", self.profile)
            self.assertIn(f"{prefix}[ear].valueCode = #{ear} (exactly)", self.profile)

    def test_example_retains_source_facts_for_every_stated_sensitivity(self):
        lines = RENDERER.example_result_lines(self.row, ROOT)
        values = [line for line in lines if "].valueQuantity = " in line and ".extension[" not in line]
        details = [line for line in lines if "].extension[sourceTest].extension[frequency].valueQuantity = " in line]
        self.assertEqual(len(values), 2)
        self.assertEqual(len(details), len(values))
        self.assertEqual(sum("[masked].valueBoolean = false" in line for line in lines), len(values))

    def test_range_and_frequency_constraints_keep_the_source_domain(self):
        extension = (ROOT / "healthkit/input/fsh/audiogram.fsh").read_text()
        self.assertIn('Expression: "value > 0"', extension)
        self.assertIn("low.value < high.value", extension)
        self.assertIn("low.exists() or high.exists()", extension)
        self.assertIn("* extension[masked].valueBoolean 1..1", extension)
        self.assertIn("masked 0..1", extension)


if __name__ == "__main__":
    unittest.main()
