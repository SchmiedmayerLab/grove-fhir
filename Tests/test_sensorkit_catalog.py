"""Validate the closed SensorKit adapter inventory and package contract."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SensorKitCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        cls.graph = json.loads(
            (ROOT / "catalog/package-graph.json").read_text(encoding="utf-8")
        )
        cls.claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )

    def test_release_package_and_profile_graph_are_exact(self) -> None:
        self.assertEqual(self.catalog["schemaVersion"], 1)
        self.assertEqual(self.catalog["fhirVersion"], "4.0.1")
        self.assertEqual(self.catalog["version"], "0.2.0")
        package = next(
            package for package in self.graph["packages"]
            if package["source"] == "sensorkit"
        )
        self.assertEqual(package["packageId"], self.catalog["packageId"])
        self.assertEqual(package["canonical"], self.catalog["canonical"])
        self.assertEqual(
            package["dependencies"],
            [
                "hl7.terminology.r4#7.3.0",
                "org.grovealliance.fhir.mobile#0.2.0",
                "org.grovealliance.fhir.sensor#0.2.0",
            ],
        )
        self.assertEqual(
            set(package["profiles"]),
            {
                "sensorkit-conversion-provenance",
                "sensorkit-device-usage-observation",
                "sensorkit-ecg-observation",
                "sensorkit-observation",
                "sensorkit-on-wrist-observation",
                "sensorkit-recording-document",
                "sensorkit-visit-observation",
            },
        )

    def test_current_platform_inventory_is_closed_and_scope_complete(self) -> None:
        entries = self.catalog["entries"]
        self.assertEqual(len(entries), 22)
        source_tokens = [entry["sourceToken"] for entry in entries]
        source_codes = [entry["sourceTypeCode"] for entry in entries]
        self.assertEqual(source_tokens, sorted(source_tokens))
        self.assertEqual(len(source_tokens), len(set(source_tokens)))
        self.assertEqual(len(source_codes), len(set(source_codes)))
        expected = {
            "SRSensor.accelerometer",
            "SRSensor.acousticSettings",
            "SRSensor.ambientLightSensor",
            "SRSensor.ambientPressure",
            "SRSensor.deviceUsageReport",
            "SRSensor.electrocardiogram",
            "SRSensor.faceMetrics",
            "SRSensor.heartRate",
            "SRSensor.keyboardMetrics",
            "SRSensor.mediaEvents",
            "SRSensor.messagesUsageReport",
            "SRSensor.odometer",
            "SRSensor.onWristState",
            "SRSensor.pedometerData",
            "SRSensor.phoneUsageReport",
            "SRSensor.photoplethysmogram",
            "SRSensor.rotationRate",
            "SRSensor.siriSpeechMetrics",
            "SRSensor.sleepSessions",
            "SRSensor.telephonySpeechMetrics",
            "SRSensor.visits",
            "SRSensor.wristTemperature",
        }
        self.assertEqual(set(source_tokens), expected)
        scopes = [entry["scope"] for entry in entries]
        self.assertEqual(scopes.count("catalog-baseline"), 20)
        self.assertEqual(scopes.count("stable-addition"), 2)
        self.assertEqual(
            set(self.catalog["inventoryScopes"]),
            {"catalog-baseline", "stable-addition"},
        )
        self.assertEqual(
            self.catalog["sourceEvidence"]["appleSensorInventory"],
            "https://developer.apple.com/documentation/sensorkit/srsensor",
        )
        self.assertEqual(
            self.catalog["sourceEvidence"]["sdkBaseline"],
            {
                "platform": "iPhoneOS",
                "version": "26.5",
                "xcodeVersion": "26.6",
                "xcodeBuild": "17F113",
            },
        )
        self.assertEqual(
            self.catalog["sourceEvidence"]["appleFrameworkDocumentation"],
            "https://developer.apple.com/documentation/sensorkit",
        )

    def test_platform_additions_are_honestly_deferred(self) -> None:
        by_token = {entry["sourceToken"]: entry for entry in self.catalog["entries"]}
        for token in ("SRSensor.acousticSettings", "SRSensor.sleepSessions"):
            self.assertEqual(by_token[token]["scope"], "stable-addition")
            self.assertEqual(by_token[token]["status"], "deferred")
            self.assertIn("stable platform symbol", by_token[token]["reason"])

    def test_every_row_has_one_definitive_status_and_admitted_contract(self) -> None:
        statuses = set(self.catalog["statusVocabulary"])
        self.assertEqual(statuses, set(self.catalog["statusDefinitions"]))
        for entry in self.catalog["entries"]:
            self.assertTrue(
                set(entry)
                <= {
                    "sourceToken",
                    "symbol",
                    "identifier",
                    "sourceTypeCode",
                    "title",
                    "documentation",
                    "minimumIOS",
                    "scope",
                    "status",
                    "structured",
                    "raw",
                    "reason",
                }
            )
            self.assertIn(entry["status"], statuses)
            self.assertRegex(entry["sourceTypeCode"], r"^[a-z][a-z0-9-]+$")
            if entry["status"] == "supported":
                structured = entry["structured"]
                self.assertIn("sourceNeutralProfile", structured)
                self.assertIn(
                    structured["adapterProfile"],
                    {
                        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                        "sensorkit-observation",
                        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                        "sensorkit-ecg-observation",
                    },
                )
            elif entry["status"] == "platform-exclusive":
                self.assertRegex(
                    entry["structured"]["profile"],
                    r"/StructureDefinition/sensorkit-(on-wrist|device-usage|visit)-observation$",
                )
            elif entry["status"] == "mapped-standard":
                self.assertTrue(
                    entry["raw"]["profile"].endswith("/sensorkit-recording-document")
                )
            elif entry["status"] in {"deferred", "intentionally-unsupported"}:
                self.assertTrue(entry["reason"])
            if "raw" in entry:
                raw = entry["raw"]
                self.assertTrue(
                    set(raw)
                    <= {
                        "status",
                        "profile",
                        "outputDiscriminator",
                        "encoding",
                        "requiredForFields",
                        "formats",
                        "formatsReason",
                    }
                )
                self.assertEqual(raw["status"], "mapped-standard")
                self.assertEqual(
                    raw["profile"],
                    "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                    "sensorkit-recording-document",
                )
                self.assertEqual(raw["outputDiscriminator"], "native-recording")
                self.assertEqual(raw["encoding"], "caller-supplied exact bytes")
                discriminators = {raw["outputDiscriminator"]}
                structured_discriminator = entry.get("structured", {}).get(
                    "outputDiscriminator"
                )
                if structured_discriminator is not None:
                    self.assertNotIn(structured_discriminator, discriminators)
                    discriminators.add(structured_discriminator)
                self.assertEqual(len(discriminators), len(set(discriminators)))

    def test_fail_closed_structured_boundaries_are_exact(self) -> None:
        by_token = {entry["sourceToken"]: entry for entry in self.catalog["entries"]}
        rotation = by_token["SRSensor.rotationRate"]["structured"]
        self.assertEqual(rotation["dimensions"], 3)
        self.assertEqual(rotation["ucumCode"], "rad/s")
        self.assertEqual(by_token["SRSensor.accelerometer"]["status"], "mapped-standard")
        self.assertIn("batch identifier", by_token["SRSensor.accelerometer"]["structured"]["reason"])
        self.assertEqual(by_token["SRSensor.heartRate"]["status"], "mapped-standard")
        self.assertIn("Confidence", by_token["SRSensor.heartRate"]["structured"]["reason"])
        ecg = by_token["SRSensor.electrocardiogram"]
        self.assertEqual(ecg["status"], "supported")
        self.assertIn("uniform series", ecg["structured"]["admissionRule"])
        self.assertTrue(
            any("signalInvalid" in field for field in ecg["raw"]["requiredForFields"])
        )
        self.assertEqual(by_token["SRSensor.photoplethysmogram"]["status"], "mapped-standard")
        self.assertEqual(by_token["SRSensor.pedometerData"]["status"], "mapped-standard")
        self.assertEqual(by_token["SRSensor.wristTemperature"]["status"], "mapped-standard")
        self.assertIn("must not bracket", by_token["SRSensor.onWristState"]["structured"]["rule"])
        self.assertIn("does not assert a clinical Encounter", by_token["SRSensor.visits"]["structured"]["rule"])
        graph = by_token["SRSensor.deviceUsageReport"]["structured"]["graphContract"]
        self.assertEqual(
            graph["requiredResources"],
            ["sensorkit-device-usage-observation", "sensorkit-recording-document"],
        )
        self.assertIn("same Grove Mobile collection Bundle", graph["relationship"])
        self.assertTrue(graph["sharedSourceIdentity"])
        ecg_graph = ecg["structured"]["graphContract"]
        self.assertEqual(
            ecg_graph["requiredResources"],
            ["sensorkit-ecg-observation", "sensorkit-recording-document"],
        )
        self.assertIn("same Grove Mobile collection Bundle", ecg_graph["relationship"])

    def test_ecg_profile_admits_both_exact_orientations_without_false_mdc_label(self) -> None:
        profile = (ROOT / "sensorkit/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        self.assertIn(
            "contains sensorKitECGLead 1..1 MS and mdcLead 0..1 MS",
            profile,
        )
        self.assertIn("code = 'leftArmMinusRightArm'", profile)
        self.assertIn("code = 'rightArmMinusLeftArm'", profile)
        self.assertIn("code = '131329').count() = 1", profile)
        self.assertIn("code = '131329').empty()", profile)

        examples = (ROOT / "sensorkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )
        self.assertRegex(
            examples,
            r"(?s)Instance: SensorKitECGExample.*?"
            r"leftArmMinusRightArm.*?coding\[mdcLead\].*?#131329",
        )
        inverse = re.search(
            r"(?s)Instance: SensorKitInverseECGExample(?P<body>.*?)"
            r"Instance: SensorKitInverseECGDocumentExample",
            examples,
        )
        self.assertIsNotNone(inverse)
        inverse_body = inverse.group("body")
        self.assertIn("rightArmMinusLeftArm", inverse_body)
        self.assertNotIn("coding[mdcLead]", inverse_body)
        self.assertNotIn("#131329", inverse_body)

    def test_business_identity_and_profile_claim_rules_are_closed(self) -> None:
        identity = self.catalog["identity"]
        self.assertEqual(
            identity["sourceRecord"]["system"],
            "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-record-id",
        )
        self.assertEqual(
            identity["output"]["system"],
            "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-output-id",
        )
        self.assertEqual(identity["output"]["namespace"], "c0b8814a-8178-5e92-996a-c4cf36cd640b")
        self.assertIsNotNone(re.fullmatch(identity["valuePattern"], "879d9ea2-21cb-4527-b59b-2831dc4c84ab"))
        self.assertIn("Resource.id is optional", identity["resourceIdPolicy"])
        self.assertIn("exactly two direct", self.catalog["profileClaims"]["sharedObservation"]["rule"])
        self.assertIn("exactly one direct", self.catalog["profileClaims"]["providerSpecificObservation"]["rule"])
        provenance = next(
            claim for claim in self.claims["adapterConversionProvenanceClaims"]
            if claim["adapter"] == "sensorkit"
        )
        self.assertEqual(
            provenance["profile"],
            self.catalog["profileClaims"]["conversionProvenance"]["profile"],
        )
        self.assertEqual(
            provenance["sourceIdentifierSystem"],
            identity["sourceRecord"]["system"],
        )
        self.assertIn(
            self.catalog["profileClaims"]["recordingDocument"]["adapterProfile"],
            provenance["targetAdapterProfiles"],
        )
        namespace = uuid.UUID(identity["output"]["namespace"])
        for vector in identity["output"]["vectors"]:
            self.assertEqual(
                str(uuid.uuid5(namespace, vector["canonicalPreimage"])),
                vector["identifierValue"],
            )
        edge = identity["output"]["vectors"][-1]
        self.assertFalse(edge["admitted"])
        self.assertIn("résumé", edge["canonicalPreimage"])
        self.assertIn("\\n\\\"\\\\", edge["canonicalPreimage"])

    def test_raw_payload_admission_is_explicit_and_fail_closed(self) -> None:
        admission = self.catalog["rawPayloadAdmission"]
        self.assertEqual(
            admission["allowedAssertions"],
            ["caller-authorized-opaque-payload", "verified-sanitized-input"],
        )
        self.assertIn("exactly one", admission["failureRule"])
        self.assertTrue(admission["notFHIRAuthorization"])


if __name__ == "__main__":
    unittest.main()
