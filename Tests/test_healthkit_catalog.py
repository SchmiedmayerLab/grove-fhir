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
                | ({"requirement"} if "requirement" in row else set()),
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

    def test_platform_additions_and_derived_aggregate_are_explicit(self) -> None:
        rows = {row["sourceTypeIdentifier"]: row for row in self.catalog["rows"]}
        expected_additions = {
            "HKCategoryTypeIdentifierHypertensionEvent",
        }
        self.assertTrue(expected_additions <= set(rows))
        for identifier in expected_additions:
            self.assertEqual(rows[identifier]["status"], "intentionally-unsupported")
            self.assertEqual(rows[identifier]["measurementIDs"], [])
            self.assertEqual(rows[identifier]["profiles"], [])

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
                    "This is not a HealthKit platform source identifier. Version 0.3.0 "
                    "does not define the session-boundary aggregation contract; "
                    "individual admitted samples map only to sleep stage."
                ),
            },
        )

    def test_profile_relocation_and_standard_bmi_claim_are_exact(self) -> None:
        self.assertEqual(
            self.catalog["sourceTypeCoding"],
            {
                "system": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-source-type",
                "element": "Observation.code.coding",
                "cardinality": "exactly one",
                "rule": "Every admitted HealthKit Observation preserves its exact sourceTypeIdentifier as an additional provider coding; the shared or authoritative standard coding remains the normative result meaning.",
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
        self.assertEqual(symptom["cardinality"], "0..7")
        self.assertEqual(
            [child["url"] for child in symptom["children"]],
            [
                "sourceIdentifier",
                "effectivePeriod",
                "symptomType",
                "severity",
                "sourceName",
                "sourceBundleIdentifier",
                "sourceVersion",
                "sourceProductType",
                "sourceOperatingSystemMajorVersion",
                "sourceOperatingSystemMinorVersion",
                "sourceOperatingSystemPatchVersion",
            ],
        )
        self.assertEqual(
            [child["type"] for child in symptom["children"]],
            [
                "Identifier",
                "Period",
                "code",
                "code",
                "string",
                "string",
                "string",
                "string",
                "integer",
                "integer",
                "integer",
            ],
        )
        self.assertIn("complete HKSourceRevision", contract["admissionRule"])
        self.assertIn("same symptom type", contract["admissionRule"])
        self.assertIn("Symptom UUIDs are unique", contract["admissionRule"])
        disclosure = contract["sourceRevisionDisclosure"]
        self.assertEqual(disclosure["requiredProducerInput"], "explicitly-authorized")
        self.assertIn("fails closed", disclosure["failureRule"])
        self.assertIn("not encoded as a FHIR", disclosure["scope"])
        self.assertIn("startDate/endDate", contract["effectiveRule"])

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
