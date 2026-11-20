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
import re
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
        self.assertIn("HealthKitAudiogramSensitivityTest named sensitivityTest 1..1", self.profile)

    def test_known_frequency_codes_cannot_disagree_with_the_source_coordinates(self):
        for component in self.row["components"]:
            ear, frequency = component["id"].split("-", 1)
            prefix = f"* component[{component['id']}].extension[sensitivityTest].extension"
            self.assertIn(f"{prefix}[frequency].valueQuantity.value = {frequency} (exactly)", self.profile)
            self.assertIn(f"{prefix}[ear].valueCode = #{ear} (exactly)", self.profile)

    def test_example_retains_source_facts_for_every_stated_sensitivity(self):
        lines = RENDERER.example_result_lines(self.row, ROOT)
        values = [line for line in lines if "].valueQuantity = " in line and ".extension[" not in line]
        details = [line for line in lines if "].extension[sensitivityTest].extension[frequency].valueQuantity = " in line]
        self.assertEqual(len(values), 2)
        self.assertEqual(len(details), len(values))
        self.assertEqual(sum("[masked].valueBoolean = false" in line for line in lines), len(values))

    def test_catalog_declares_the_required_component_extension(self):
        extension = self.row["componentExtension"]
        self.assertEqual(extension["url"], "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-audiogram-sensitivity-test")
        self.assertEqual(extension["cardinality"], "1..1")
        for component in self.row["components"]:
            ear, frequency = component["id"].split("-", 1)
            members = {member["member"]: member for member in component["extensionValues"]}
            self.assertEqual(members["ear"]["valueCode"], ear)
            self.assertEqual(members["frequency"]["valueQuantity"], {"value": int(frequency), "system": "http://unitsofmeasure.org", "code": "Hz"})
        renderer = (ROOT / "Scripts/render-measurement-profiles.py").read_text()
        self.assertNotIn('"audiogram-panel"', renderer)

    def test_panel_invariant_is_generated_from_the_catalog(self):
        extension = self.row["componentExtension"]
        self.assertIn(extension["invariant"], self.row["obeys"])
        generated = (ROOT / "healthkit/input/fsh/generated-measurement-profiles.fsh").read_text()
        expression = re.search(r"Invariant: healthkit-audiogram-panel-1\n.*?\nExpression: \"(.*?)\"\n", generated, re.S).group(1)
        self.assertEqual(RENDERER.component_invariant(self.row).splitlines()[-1], f'Expression: "{expression}"')
        self.assertNotIn("healthkit-audiogram-panel-1", (ROOT / "healthkit/input/fsh/audiogram.fsh").read_text())
        for component in self.row["components"]:
            ear, frequency = component["id"].split("-", 1)
            self.assertIn(f"'{component['code']}'", expression)
            self.assertIn(f"'{int(frequency) * 1000}@{ear}'", expression)
        # Both clauses use the same key, so frequency compares the same way in each.
        self.assertEqual(expression.count("* 1000).truncate()"), 2)
        self.assertIn(".isDistinct()", expression)

    def test_range_and_frequency_constraints_keep_the_source_domain(self):
        extension = (ROOT / "healthkit/input/fsh/audiogram.fsh").read_text()
        self.assertIn('Expression: "value > 0"', extension)
        self.assertIn("low.value < high.value", extension)
        self.assertIn("low.exists() or high.exists()", extension)
        self.assertIn("* extension[masked].valueBoolean 1..1", extension)
        self.assertIn("masked 0..1", extension)


if __name__ == "__main__":
    unittest.main()
