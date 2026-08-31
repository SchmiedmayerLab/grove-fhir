"""Lock the complete HealthKit source inventory and shared-coverage claims."""

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
OLD_MOBILE = {
    "grove-mobile-bmi",
    "grove-mobile-blood-glucose",
    "grove-mobile-capillary-blood-glucose",
    "grove-mobile-serum-plasma-glucose",
    "grove-mobile-interstitial-glucose",
}


class HealthKitCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )
        cls.mobile = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        cls.protocol = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        cls.claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )

    def test_every_active_output_and_direct_claim_is_machine_closed(self) -> None:
        prefix = "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
        generic = prefix + "healthkit-observation"
        ecg = prefix + "healthkit-ecg-observation"
        active_rows = [
            row for row in self.catalog["rows"]
            if row["status"] in {"supported", "platform-exclusive"}
        ]
        active_healthkit_profiles = {
            profile
            for row in active_rows
            for profile in row["profiles"]
            if profile.startswith(prefix)
        }
        ecg_output_profiles = {
            profile
            for output in self.catalog["sensorAdapterClaims"]["electrocardiogram"]["outputs"]
            for profile in output["profiles"]
            if profile.startswith(prefix)
        }
        active_healthkit_profiles.update(ecg_output_profiles)
        provenance = next(
            claim for claim in self.claims["adapterConversionProvenanceClaims"]
            if claim["adapter"] == "healthkit"
        )
        self.assertEqual(
            provenance["targetAdapterProfiles"], sorted(active_healthkit_profiles)
        )
        self.assertEqual(len(active_healthkit_profiles), 119)

        single_profiles = {
            profile
            for row in self.catalog["rows"]
            if row["status"] == "supported"
            for profile in row["profiles"]
            if profile.startswith(prefix) and profile not in {generic, ecg}
        }
        single_claim = self.claims["healthKitSingleProfileObservationClaims"]
        self.assertEqual(single_claim["cardinality"], 1)
        self.assertFalse(single_claim["otherProfilesAllowed"])
        self.assertEqual(single_claim["profiles"], sorted(single_profiles))
        self.assertEqual(len(single_profiles), 111)

        self.assertEqual(
            self.claims["healthKitRecordingDocumentClaim"]["profiles"],
            [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-recording-document",
                prefix + "healthkit-recording-document",
            ],
        )
        self.assertEqual(
            self.claims["healthKitClinicalRecordDocumentClaim"]["profiles"],
            [prefix + "healthkit-clinical-record-document"],
        )
        self.assertEqual(
            {
                (claim["resourceType"], claim["profile"])
                for claim in self.claims["healthKitPlatformExclusiveResourceClaims"]
            },
            {
                ("VisionPrescription", prefix + "healthkit-vision-prescription"),
                ("MedicationAdministration", prefix + "healthkit-medication-dose-event"),
                ("MedicationStatement", prefix + "healthkit-user-annotated-medication"),
            },
        )

    def test_health_concept_links_use_the_shared_opaque_context_identity(self) -> None:
        kinds = {
            row["kind"]: row for row in self.protocol["opaqueIdentity"]["identityKinds"]
        }
        context = self.catalog["identity"]["sourceContext"]
        self.assertEqual(context["identityKind"], "source-context")
        self.assertEqual(context["identifierRole"], "source-context")
        self.assertEqual(context["components"], kinds["source-context"]["components"])
        self.assertIn("HKHealthConceptIdentifier", context["rule"])
        self.assertIn("HMAC", context["rule"])

    def test_clinical_release_representation_uses_standard_mime_parameters(self) -> None:
        representation = self.catalog["clinicalRecordAdmission"]["fhirRepresentation"]
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertEqual(representation["resourceType"], "DocumentReference")
        self.assertEqual(
            representation["contentTypeByRelease"],
            {
                "dstu2": "application/fhir+json; fhirVersion=1.0",
                "r4": "application/fhir+json; fhirVersion=4.0",
            },
        )
        self.assertIn("* content.format = $recordingFormat#fhir-resource", profiles)
        self.assertIn("* obeys healthkit-clinical-fhir-content-type-1", profiles)
        self.assertNotIn("HealthKitClinicalFHIRRelease", profiles)
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("HealthKitClinicalFHIRRelease", terminology)

    def test_clinical_document_has_one_provenance_target_hierarchy(self) -> None:
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Profile: HealthKitClinicalRecordDocument\n"
            "Parent: HealthKitRecordingDocument",
            profiles,
        )
        target_rule = next(
            line for line in profiles.splitlines()
            if line.startswith("* target only Reference(")
        )
        self.assertIn("HealthKitRecordingDocument", target_rule)
        self.assertNotIn("HealthKitClinicalRecordDocument", target_rule)

    def test_examples_do_not_reintroduce_a_generic_metadata_channel(self) -> None:
        examples = (ROOT / "healthkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("component[+].code.text", examples)
        self.assertNotIn("ThirdPartyPedometerFirmware", examples)
        self.assertNotIn("stays lossless", examples)

    def test_inventory_is_exact_closed_and_unique(self) -> None:
        rows = self.catalog["rows"]
        source = self.catalog["source"]
        self.assertEqual(
            source["sdkBaseline"],
            {
                "platform": "iPhoneOS",
                "version": "26.5",
                "xcodeVersion": "26.6",
                "xcodeBuild": "17F113",
            },
        )
        self.assertEqual(source["platform"], "Apple HealthKit")
        self.assertEqual(source["accessed"], "2026-08-21")
        self.assertEqual(source["rowCount"], len(rows))
        self.assertEqual(source["derivedAggregateCount"], 1)
        self.assertIn("derived mappings are excluded", source["rowScope"])
        identifiers = [row["sourceTypeIdentifier"] for row in rows]
        self.assertEqual(identifiers, sorted(identifiers))
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertFalse(any("#" in identifier for identifier in identifiers))
        for evidence in source["evidence"]:
            url, path = evidence.get("url", ""), evidence.get("path", "")
            self.assertTrue(
                url.startswith("https://developer.apple.com/") or (ROOT / path).is_file(),
                evidence,
            )
        statuses = set(self.catalog["statusVocabulary"])
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "sourceTypeIdentifier",
                    "title",
                    "symbols",
                    "documentation",
                    "status",
                    "measurementIDs",
                    "profiles",
                }
                | ({"requirement"} if "requirement" in row else set())
                | (
                    {"clinicalAdmissionContract"}
                    if "clinicalAdmissionContract" in row
                    else set()
                ),
            )
            self.assertIn(row["status"], statuses)
            self.assertEqual(len(row["profiles"]), len(set(row["profiles"])))
            if row["status"] == "supported":
                self.assertTrue(row["measurementIDs"])
                self.assertTrue(row["profiles"])
            elif row["status"] == "platform-exclusive":
                self.assertTrue(row["profiles"])
            else:
                self.assertIsInstance(row.get("requirement"), str)
                self.assertTrue(row["requirement"])

    def test_producer_numeric_canonicalization_reuses_the_mobile_contract(self) -> None:
        self.assertEqual(
            self.catalog["producerCanonicalization"],
            {
                "mobileEffectiveContract": "catalog/measurement-catalog.json#effectiveCanonicalization",
                "effectivePrecision": "millisecond",
                "effectiveRounding": "half-even",
                "scalarQuantityDecimal": "shortest-round-trip",
                "identityPreimages": "unmodified",
                "sensorAndEcgTiming": "excluded",
            },
        )
        self.assertEqual(
            self.mobile["effectiveCanonicalization"]["precision"], "millisecond"
        )
        self.assertEqual(
            self.mobile["effectiveCanonicalization"]["rounding"], "half-even"
        )

    def test_application_device_separates_opaque_snapshot_from_bundle_product(self) -> None:
        contract = self.catalog["applicationDeviceIdentity"]
        self.assertEqual(
            contract["profile"],
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-application-device",
        )
        self.assertEqual(contract["snapshotIdentifierRole"], "device-snapshot")
        self.assertEqual(
            contract["bundleIdentifier"],
            {
                "system": "https://grovealliance.org/fhir/healthkit/NamingSystem/apple-bundle-id",
                "typeSystem": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-identifier-type",
                "typeCode": "apple-bundle-id",
                "cardinality": "1..1",
                "meaning": "Exact Apple application product bundle identifier; never an installation, host, account, or person identifier.",
            },
        )
        self.assertIn("caller explicitly classifies", contract["classificationRule"])
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn("Profile: HealthKitApplicationDevice", profiles)
        self.assertIn("identifier[appleBundleId].type", profiles)

    def test_platform_additions_and_derived_aggregate_are_explicit(self) -> None:
        rows = {row["sourceTypeIdentifier"]: row for row in self.catalog["rows"]}
        # This was the one screening notification refused while its eleven peers
        # were supported, and the row carried no rationale for the difference; the notification
        # contract states only that the notification was raised, never a diagnosis.
        hypertension = rows["HKCategoryTypeIdentifierHypertensionEvent"]
        self.assertEqual(hypertension["status"], "supported")
        self.assertEqual(hypertension["measurementIDs"], ["hypertension-notification"])

        renamed = rows["HKCategoryTypeIdentifierAudioExposureEvent"]
        self.assertEqual(renamed["title"], "Audio Exposure Event")
        self.assertIn(
            "HKCategoryTypeIdentifierEnvironmentalAudioExposureEvent",
            renamed["symbols"],
        )

        aggregates = self.catalog["derivedAggregates"]
        self.assertEqual(len(aggregates), 1)
        self.assertEqual(
            aggregates[0],
            {
                "id": "sleep-duration-session-aggregate",
                "title": "Sleep Duration Session Aggregate",
                "sourceTypeIdentifiers": ["HKCategoryTypeIdentifierSleepAnalysis"],
                "scope": "derived-from-platform-samples",
                "status": "deferred",
                "measurementIDs": ["sleep-duration"],
                "profiles": [
                    "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                    "grove-mobile-sleep-duration"
                ],
                "requirement": (
                    "This is not a HealthKit platform source identifier. The Grove "
                    "FHIR contracts do not define the session-boundary aggregation contract; "
                    "individual admitted samples map only to sleep stage."
                ),
            },
        )

    def test_profile_relocation_and_standard_bmi_claim_are_exact(self) -> None:
        self.assertEqual(
            self.catalog["sourceTypeExtension"],
            {
                "url": "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-source-type",
                "valueSystem": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-source-type",
                "valueElement": "valueCode",
                "cardinality": "exactly one",
                "contexts": [
                    "Observation",
                    "DocumentReference",
                    "VisionPrescription",
                    "MedicationAdministration",
                    "MedicationStatement",
                ],
                "rule": "Every admitted HealthKit output preserves its exact sourceTypeIdentifier in this lineage extension. Observation.code and DocumentReference.type remain clinical or document concepts; the HealthKit SDK source class is not asserted as an equivalent coding of either meaning.",
            },
        )
        self.assertEqual(
            self.catalog["conversionProvenanceProfile"],
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-conversion-provenance",
        )
        old_suffixes = tuple(f"/{profile}" for profile in OLD_MOBILE)
        for row in self.catalog["rows"]:
            self.assertFalse(any(profile.endswith(old_suffixes) for profile in row["profiles"]))
        bmi_claim = self.catalog["standardAdapterClaims"]["body-mass-index"]
        self.assertEqual(
            bmi_claim["profiles"],
            [
                "http://hl7.org/fhir/StructureDefinition/bmi",
                "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation",
            ],
        )
        bmi_row = next(
            row for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKQuantityTypeIdentifierBodyMassIndex"
        )
        self.assertEqual(bmi_row["profiles"], bmi_claim["profiles"])
        glucose = next(
            row for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKQuantityTypeIdentifierBloodGlucose"
        )
        self.assertEqual(glucose["status"], "supported")
        self.assertEqual(
            glucose["measurementIDs"], ["blood-glucose-unspecified-specimen"]
        )
        ecg = next(
            row for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKDataTypeIdentifierElectrocardiogram"
        )
        self.assertEqual(ecg["status"], "supported")
        self.assertEqual(
            ecg["profiles"],
            self.catalog["sensorAdapterClaims"]["electrocardiogram"]["profiles"],
        )
        self.assertEqual(ecg["measurementIDs"], ["electrocardiogram"])
        self.assertIn("timeSinceSampleStart", ecg["requirement"])
        self.assertIn("without fetching or resampling", ecg["requirement"])
        contract = self.catalog["sensorAdapterClaims"]["electrocardiogram"]
        self.assertIn(
            "offset[i] = offset[0] + i * SampledData.period",
            contract["admissionRule"],
        )
        self.assertIn("every voltage is present", contract["admissionRule"])
        symptom = contract["correlatedSymptomEvidence"]
        self.assertEqual(symptom["cardinality"], "0..*")
        self.assertIn("Observation.hasMember", symptom["r4Element"])
        self.assertEqual(len(symptom["sourceTypes"]), 7)
        self.assertIn("source-output Identifier", symptom["rule"])
        self.assertIn("own event Bundle", symptom["exchangeRule"])
        self.assertIn("normal HealthKit", symptom["sourceRevisionRule"])
        self.assertNotIn("authorization", json.dumps(contract).lower())
        self.assertEqual(
            [item["outputRole"] for item in contract["outputs"]],
            ["electrocardiogram", "average-heart-rate"],
        )
        self.assertEqual(
            contract["outputs"][1]["code"],
            {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"},
        )
        self.assertIn("validation input only", contract["wireMapping"]["samplingFrequency"])
        self.assertIn(
            "validation input only", contract["wireMapping"]["numberOfVoltageMeasurements"]
        )
        graph = self.claims["healthKitEcgGraphClaim"]
        self.assertEqual(
            graph["averageHeartRate"]["reference"],
            {
                "sourceOutput": "average-heart-rate",
                "r4Path": "Observation.derivedFrom",
                "targetOutput": "electrocardiogram",
                "targetType": "Observation",
                "referenceShape": "resolving-literal",
                "min": 1,
                "max": 1,
            },
        )
        self.assertFalse(graph["correlatedSymptoms"]["sameEventBundle"])
        self.assertEqual(
            graph["correlatedSymptoms"]["statusConditionedCardinality"],
            [
                {"status": "notSet", "min": 0, "max": 0},
                {"status": "none", "min": 0, "max": 0},
                {"status": "present", "min": 1, "max": "*"},
            ],
        )
        examples = (ROOT / "healthkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )
        average_example = examples.split(
            "Instance: HealthKitECGAverageHeartRateExample", 1
        )[1].split("\nInstance:", 1)[0]
        self.assertIn(
            '* category = $observationCategory#vital-signs "Vital Signs"',
            average_example,
        )
        self.assertIn(
            "* derivedFrom = Reference(HealthKitECGObservationExample)",
            average_example,
        )
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(encoding="utf-8")
        for mapping in contract["closedValueMappings"].values():
            for value in mapping["values"]:
                self.assertIn(f"* #{value['code']} ", terminology)
        self.assertIn("startDate/endDate", contract["effectiveRule"])

    def test_sync_revision_metadata_is_an_exact_fail_closed_pair(self) -> None:
        revision = self.catalog["identity"]["writerRecord"]["revision"]
        self.assertEqual(revision["sourceIdentifier"], "HKMetadataKeySyncIdentifier")
        self.assertEqual(revision["sourceVersion"], "HKMetadataKeySyncVersion")
        self.assertEqual(revision["presenceRule"], "both-or-neither")
        self.assertEqual(revision["versionMinimum"], 0)
        self.assertNotIn("versionMaximum", revision)
        self.assertEqual(revision["invalidDisposition"], "reject-source-record")
        self.assertIn("non-empty String", revision["identifierRule"])
        self.assertIn("canonical unsigned decimal", revision["versionRule"])
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("MUST reject either half-pair", mapping)
        self.assertIn("MUST NOT fabricate version `0`", mapping)

    def test_mobile_healthkit_coverage_is_bidirectional(self) -> None:
        supported_rows: dict[str, list[str]] = {}
        for row in self.catalog["rows"]:
            if row["status"] != "supported":
                continue
            for measurement_id in row["measurementIDs"]:
                supported_rows.setdefault(measurement_id, []).append(
                    row["sourceTypeIdentifier"]
                )
        shared = {item["id"]: item for item in self.mobile["measurements"]}
        for measurement_id, measurement in shared.items():
            if measurement["coverage"]["healthkit"] == "supported":
                self.assertIn(measurement_id, supported_rows)
        adapter_only = (
            set(self.catalog["standardAdapterClaims"])
            | set(self.catalog["sensorAdapterClaims"])
        )
        self.assertEqual(set(supported_rows) - set(shared), adapter_only)
        for measurement_id in set(supported_rows) & set(shared):
            self.assertEqual(shared[measurement_id]["coverage"]["healthkit"], "supported")


if __name__ == "__main__":
    unittest.main()
