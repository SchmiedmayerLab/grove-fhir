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
RELEASE_VERSION = json.loads(
    (ROOT / "catalog/release-manifest.json").read_text(encoding="utf-8")
)["releaseVersion"]


class SensorCatalogTests(unittest.TestCase):
    def test_sensor_catalog_matches_package_graph_and_profile_claims(self) -> None:
        catalog = json.loads((ROOT / "catalog/sensor-catalog.json").read_text(encoding="utf-8"))
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        claims = json.loads((ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8"))
        package = next(item for item in graph["packages"] if item["source"] == "sensor")
        self.assertEqual(catalog["fhirVersion"], "4.0.1")
        self.assertEqual(catalog["version"], RELEASE_VERSION)
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
        self.assertIn("declared registry grammar", admission["scope"])
        self.assertIn("derives grammar-defined summary counts", admission["scope"])
        self.assertIn("required Attachment metadata only", admission["scope"])
        self.assertIn("does not fetch or verify the bytes", admission["scope"])
        self.assertIn("size/hash integrity", admission["scope"])
        self.assertIn("strict JSON envelope", admission["scope"])
        self.assertIn("registered CSV grammars", admission["scope"])
        self.assertIn("structural and lexical", admission["scope"])
        self.assertIn("do not enforce per-column source-domain ranges", admission["scope"])
        self.assertIn("parse every binary grammar", admission["scope"])
        self.assertIn("recompute summaries", admission["scope"])
        self.assertIn("semantically reinterpret", admission["scope"])
        self.assertIn("sanitize, rewrite, or reserialize", admission["scope"])
        self.assertIn("does not prove", admission["scope"])

    def test_recording_attachment_title_is_optional_presentation_text(self) -> None:
        sensor_profiles = (ROOT / "sensor/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn("* content.attachment.title 0..1 MS", sensor_profiles)
        self.assertNotIn("* content.attachment.title 1..1 MS", sensor_profiles)

        healthkit_profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        clinical_profile = healthkit_profiles.split(
            "Profile: HealthKitClinicalRecordDocument", 1
        )[1].split("Profile: HealthKitVisionPrescription", 1)[0]
        self.assertNotIn("content.attachment.title", clinical_profile)

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

    def test_ecg_channel_identity_is_complete_unique_and_ignores_display_text(self) -> None:
        catalog = json.loads((ROOT / "catalog/sensor-catalog.json").read_text(encoding="utf-8"))
        ecg = next(item for item in catalog["contracts"] if item["id"] == "ecg")
        rule = ecg["channelIdentityRule"]
        self.assertIn("Coding.system", rule)
        self.assertIn("Coding.code", rule)
        self.assertIn("unordered set", rule)
        self.assertIn("duplicate pairs", rule)
        self.assertIn("duplicate identity sets", rule)
        self.assertIn("display", rule)
        profiles = (ROOT / "sensor/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        self.assertIn("* component.code.coding 1..* MS", profiles)
        self.assertIn("* component.code.coding.system 1..1 MS", profiles)
        self.assertIn("* component.code.coding.code 1..1 MS", profiles)

    def test_sensor_pins_mobile_and_terminology_dependencies(self) -> None:
        configuration = (ROOT / "sensor/sushi-config.yaml").read_text(encoding="utf-8")
        self.assertIn(
            f"org.grovealliance.fhir.mobile:\n    version: {RELEASE_VERSION}",
            configuration,
        )
        self.assertIn("hl7.terminology.r4: 7.3.0", configuration)
        # PHD is an alignment described in prose, not a package dependency.
        self.assertNotIn("hl7.fhir.uv.phd", configuration)


if __name__ == "__main__":
    unittest.main()
