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
        self.assertEqual(self.catalog["version"], "0.6.0")
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
                "hl7.fhir.uv.extensions.r4#5.3.0",
                "org.grovealliance.fhir.mobile#0.6.0",
                "org.grovealliance.fhir.sensor#0.6.0",
            ],
        )
        self.assertEqual(
            set(package["profiles"]),
            {"sensorkit-accelerometer-observation", "sensorkit-conversion-provenance", "sensorkit-device-usage-observation", "sensorkit-ecg-observation", "sensorkit-keyboard-metrics-observation", "sensorkit-messages-usage-observation", "sensorkit-observation", "sensorkit-on-wrist-observation", "sensorkit-phone-usage-observation", "sensorkit-ppg-observation", "sensorkit-recording-document", "sensorkit-sleep-session-observation", "sensorkit-visit-observation",
                "sensorkit-wrist-temperature-observation"},
        )
        self.assertEqual(
            self.catalog["sourceTypeExtension"],
            {
                "url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type",
                "codeSystem": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-source-type",
                "r4Element": "Observation.extension.valueCode or DocumentReference.extension.valueCode",
                "cardinality": "exactly one",
                "rule": "Every admitted SensorKit output states the exact sourceTypeCode from its one catalog entry.",
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
        acoustic = by_token["SRSensor.acousticSettings"]
        self.assertEqual(acoustic["scope"], "stable-addition")
        self.assertEqual(acoustic["status"], "deferred")
        self.assertIn("stable platform symbol", acoustic["reason"])
        sleep = by_token["SRSensor.sleepSessions"]
        self.assertEqual(sleep["scope"], "stable-addition")
        self.assertEqual(sleep["status"], "platform-exclusive")
        self.assertTrue(
            sleep["structured"]["profile"].endswith(
                "sensorkit-sleep-session-observation"
            )
        )

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
                    r"/StructureDefinition/sensorkit-(on-wrist|device-usage|visit|messages-usage|phone-usage|keyboard-metrics|sleep-session|accelerometer|ppg|wrist-temperature)-observation$",
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
                        "jsonSchema",
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
        self.assertEqual(
            by_token["SRSensor.accelerometer"]["status"], "platform-exclusive"
        )
        self.assertTrue(
            by_token["SRSensor.accelerometer"]["structured"]["profile"].endswith(
                "sensorkit-accelerometer-observation"
            )
        )
        self.assertEqual(by_token["SRSensor.heartRate"]["status"], "mapped-standard")
        self.assertIn("Confidence", by_token["SRSensor.heartRate"]["structured"]["reason"])
        ecg = by_token["SRSensor.electrocardiogram"]
        self.assertEqual(ecg["status"], "supported")
        self.assertIn("uniform series", ecg["structured"]["admissionRule"])
        guidance = ecg["structured"]["nativeR4Mappings"][0]
        self.assertEqual(guidance["r4Element"], "Observation.method")
        self.assertEqual(guidance["allowedCodes"], ["guided", "unguided"])
        self.assertTrue(
            any("signalInvalid" in field for field in ecg["raw"]["requiredForFields"])
        )
        self.assertEqual(
            by_token["SRSensor.photoplethysmogram"]["status"], "platform-exclusive"
        )
        self.assertEqual(by_token["SRSensor.pedometerData"]["status"], "mapped-standard")
        # Wrist temperature gained a platform-scoped structured contract in 0.6.0, so its
        # top-level status matches its siblings rather than claiming a recording document only.
        self.assertEqual(
            by_token["SRSensor.wristTemperature"]["status"], "platform-exclusive"
        )
        self.assertIn("must not bracket", by_token["SRSensor.onWristState"]["structured"]["rule"])
        self.assertIn("does not assert a clinical Encounter", by_token["SRSensor.visits"]["structured"]["rule"])
        visit_location = by_token["SRSensor.visits"]["structured"]["nativeR4Mappings"][0]
        self.assertEqual(visit_location["valueKind"], "identifier-reference")
        self.assertEqual(visit_location["referenceType"], "Location")
        self.assertIn("source-store-scoped", visit_location["identifierSystemRule"])
        wrist_version = by_token["SRSensor.wristTemperature"]["structured"]["extensionMappings"][0]
        self.assertEqual(wrist_version["valueElement"], "valueString")
        self.assertIn("Coding.version", wrist_version["nativeR4Gap"])
        self.assertTrue(wrist_version["exactSourceValue"])
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
            identity["contract"],
            "catalog/exchange-protocol.json",
        )
        self.assertEqual(identity["protocolVersion"], 2)
        self.assertEqual(identity["adapterId"], "sensorkit")
        self.assertEqual(identity["sourceRecord"]["identityKind"], "source-record")
        self.assertEqual(
            identity["sourceRecord"]["components"],
            [
                "adapter-id",
                "source-type",
                "repository-scope-system",
                "repository-scope-value",
                "native-record-id",
            ],
        )
        self.assertIn("assigns and persists", identity["sourceRecord"]["nativeRecordRule"])
        self.assertIn("measured values", identity["sourceRecord"]["nativeRecordRule"])
        acquisition = identity["sourceRecord"]["acquisitionCoordinate"]
        self.assertIn("monotonic delivery ordinal", acquisition["record"])
        self.assertIn("pending start ordinal", acquisition["pendingBatch"])
        self.assertIn("splits or combines", acquisition["retry"])
        vectors = {vector["id"]: vector for vector in acquisition["vectors"]}
        self.assertEqual(
            vectors["equal-coordinate-cross-batch"]["expectedCoordinates"],
            [
                {"generation": 4, "deliveryOrdinal": 40},
                {"generation": 4, "deliveryOrdinal": 41},
            ],
        )
        rebatch = vectors["crash-retry-rebatch"]
        self.assertEqual(
            [attempt["resolvedOrdinals"] for attempt in rebatch["attempts"]],
            [[120, 121], [120], [121]],
        )
        self.assertEqual(identity["sourceOutput"]["identityKind"], "source-output")
        self.assertIn("length framing", identity["sourceOutput"]["outputDiscriminatorRule"])
        self.assertIn("there is no fallback", identity["sourceOutput"]["outputDiscriminatorRule"])
        self.assertEqual(identity["sourceArtifact"]["identityKind"], "source-artifact")
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
        self.assertEqual(provenance["sourceIdentifierRole"], "source-record")
        self.assertEqual(provenance["sourceIdentityKind"], "source-record")
        self.assertIn(
            self.catalog["profileClaims"]["recordingDocument"]["adapterProfile"],
            provenance["targetAdapterProfiles"],
        )
        recording_claim = self.claims["sensorKitRecordingDocumentClaim"]
        self.assertEqual(
            recording_claim["requiredIdentifierRoles"],
            ["source-record", "source-output", "source-artifact"],
        )

    def test_platform_summary_quantity_domains_are_closed_and_proportionate(self) -> None:
        domains = self.catalog["quantityValueDomains"]
        nonnegative = set(domains["nonNegativeProfiles"])
        integer_counts = set(domains["integerCountProfiles"])
        self.assertEqual(len(nonnegative), 9)
        self.assertEqual(len(integer_counts), 7)
        self.assertTrue(integer_counts < nonnegative)
        self.assertEqual(
            domains["countQuantity"],
            {"system": "http://unitsofmeasure.org", "code": "{count}"},
        )
        self.assertIn("no physiologic upper range", domains["rule"])
        source = (ROOT / "sensorkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            source.count("sensorkit-summary-quantity-nonnegative-1") - 1,
            len(nonnegative),
        )
        self.assertEqual(
            source.count("sensorkit-summary-count-integer-1") - 1,
            len(integer_counts),
        )

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
