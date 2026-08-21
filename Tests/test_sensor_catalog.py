"""Validate the source-neutral Sensor and Waveform machine contract."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SensorCatalogTests(unittest.TestCase):
    def test_sensor_catalog_matches_package_graph_and_profile_claims(self) -> None:
        catalog = json.loads((ROOT / "catalog/sensor-catalog.json").read_text(encoding="utf-8"))
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        claims = json.loads((ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8"))
        package = next(item for item in graph["packages"] if item["source"] == "sensor")
        self.assertEqual(catalog["fhirVersion"], "4.0.1")
        self.assertEqual(catalog["version"], "0.2.0")
        self.assertEqual(catalog["packageId"], package["packageId"])
        profile_ids = {item["profile"].rsplit("/", 1)[-1] for item in catalog["contracts"]}
        self.assertEqual(profile_ids, set(package["profiles"]))
        observation_profiles = {
            item["profile"]
            for item in catalog["contracts"]
            if item["resourceType"] == "Observation"
        }
        self.assertEqual(
            observation_profiles,
            set(claims["observationAdapterClaim"]["sharedSensorProfiles"]),
        )

    def test_recording_document_has_no_normative_capacity_threshold(self) -> None:
        catalog = json.loads((ROOT / "catalog/sensor-catalog.json").read_text(encoding="utf-8"))
        document = next(item for item in catalog["contracts"] if item["id"] == "recording-document")
        self.assertIsNone(document["sizeThreshold"])
        self.assertEqual(document["sizeThresholdPolicy"], "deployment-specific")
        self.assertTrue(document["integrity"]["sizeRequired"])
        self.assertTrue(document["integrity"]["hashRequired"])
        self.assertIn("immutable", document["integrity"]["urlRule"])
        self.assertIn("never a signature", document["integrity"]["securityRule"])
        admission = document["payloadAdmission"]
        self.assertEqual(
            admission["allowedAssertions"],
            ["caller-authorized-opaque-payload", "verified-sanitized-input"],
        )
        self.assertIn("exactly one", admission["requiredProducerInput"])
        self.assertIn("fail closed", admission["failureRule"])
        self.assertIn("does not inspect", admission["scope"])

    def test_sampled_data_timing_contract_is_exact(self) -> None:
        catalog = json.loads((ROOT / "catalog/sensor-catalog.json").read_text(encoding="utf-8"))
        sampled = next(item for item in catalog["contracts"] if item["id"] == "sampled-data")
        timing = sampled["timing"]
        self.assertEqual(timing["effectiveType"], "Period")
        self.assertIn("at least 2", timing["frameCountRule"])
        self.assertEqual(timing["exceptionalTokensAdmitted"], [])
        self.assertFalse(timing["factorAdmitted"])
        self.assertEqual(len(timing["vectors"]), 3)
        self.assertGreater(
            len(timing["vectors"][-1]["start"].split(".")[1].rstrip("Z")), 6
        )

    def test_sensor_pins_mobile_and_terminology_dependencies(self) -> None:
        configuration = (ROOT / "sensor/sushi-config.yaml").read_text(encoding="utf-8")
        self.assertIn("org.grovealliance.fhir.mobile:\n    version: 0.2.0", configuration)
        self.assertIn("hl7.terminology.r4: 7.3.0", configuration)
        # PHD is an alignment described in prose, not a package dependency.
        self.assertNotIn("hl7.fhir.uv.phd", configuration)


if __name__ == "__main__":
    unittest.main()
