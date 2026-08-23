"""Lock the Health Connect 1.1 inventory, mappings, and identity grammar."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import unittest
from pathlib import Path

from Scripts import health_connect_identity as identity


ROOT = Path(__file__).parents[1]
STATUSES = {"supported", "mapped-standard", "platform-exclusive", "unmodeled", "deferred", "intentionally-unsupported"}
SUPPORTED = {
    "ActiveCaloriesBurnedRecord",
    "BasalBodyTemperatureRecord",
    "BasalMetabolicRateRecord",
    "BloodGlucoseRecord",
    "BloodPressureRecord",
    "BodyFatRecord",
    "BodyTemperatureRecord",
    "BodyWaterMassRecord",
    "BoneMassRecord",
    "CervicalMucusRecord",
    "CyclingPedalingCadenceRecord",
    "DistanceRecord",
    "ElevationGainedRecord",
    "ExerciseSessionRecord",
    "FloorsClimbedRecord",
    "HeartRateRecord",
    "HeartRateVariabilityRmssdRecord",
    "HeightRecord",
    "HydrationRecord",
    "IntermenstrualBleedingRecord",
    "LeanBodyMassRecord",
    "MenstruationFlowRecord",
    "MenstruationPeriodRecord",
    "MindfulnessSessionRecord",
    "NutritionRecord",
    "OvulationTestRecord",
    "OxygenSaturationRecord",
    "PowerRecord",
    "RespiratoryRateRecord",
    "RestingHeartRateRecord",
    "SexualActivityRecord",
    "SkinTemperatureRecord",
    "SleepSessionRecord",
    "SpeedRecord",
    "StepsCadenceRecord",
    "StepsRecord",
    "TotalCaloriesBurnedRecord",
    "Vo2MaxRecord",
    "WeightRecord",
    "WheelchairPushesRecord",
}


class HealthConnectCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = json.loads((ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8"))
        cls.contract = json.loads((ROOT / "catalog/health-connect-identity.json").read_text(encoding="utf-8"))
        cls.claims = json.loads((ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8"))
        cls.measurements = {
            item["id"] for item in json.loads(
                (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
            )["measurements"]
        }
        cls.measurements.update(
            item["id"] for item in cls.adapter["adapterMeasurements"]
        )

    def test_record_type_inventory_is_exact_closed_and_complete(self) -> None:
        self.assertEqual(self.adapter["source"]["version"], "1.1.0")
        rows = self.adapter["recordTypes"]
        tokens = [row["token"] for row in rows]
        self.assertEqual(len(tokens), 41)
        self.assertEqual(len(tokens), self.adapter["source"]["recordTypeCount"])
        self.assertEqual(tokens, sorted(tokens))
        self.assertEqual(len(tokens), len(set(tokens)))
        self.assertEqual(set(tokens), identity.RECORD_TYPES)
        self.assertEqual({row["status"] for row in rows if row["status"] == "supported" and row["outputs"]}, {"supported"})
        self.assertEqual({row["token"] for row in rows if row["status"] == "supported"}, SUPPORTED)
        self.assertEqual(set(self.adapter["statusVocabulary"]), STATUSES)
        self.assertEqual(
            self.adapter["sourceTypeExtension"]["codeSystem"],
            "https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-record-type",
        )
        for row in rows:
            self.assertIn(row["status"], STATUSES)
            self.assertEqual(bool(row["outputs"]), row["status"] == "supported")
            for output in row["outputs"]:
                self.assertIn(output["measurement"], self.measurements)
            for context in row["context"]:
                self.assertIn(context, self.adapter["contextMappings"])

    def test_every_unsupported_record_states_why(self) -> None:
        # A row that produces no output has to say why, exactly as the HealthKit catalog
        # requires; a silent deferral reads as an oversight rather than a decision.
        for row in self.adapter["recordTypes"]:
            if row["status"] == "supported":
                continue
            with self.subTest(record=row["token"]):
                self.assertIsInstance(row.get("reason"), str)
                self.assertTrue(row["reason"])

    def test_glucose_profiles_are_adapter_specific_and_specimen_exact(self) -> None:
        measurements = {
            item["id"]: item for item in self.adapter["adapterMeasurements"]
        }
        self.assertEqual(
            set(measurements),
            {
                "blood-glucose",
                "capillary-blood-glucose",
                "serum-plasma-glucose",
                "interstitial-glucose",
            },
        )
        for measurement in measurements.values():
            self.assertEqual(measurement["scope"], "health-connect-adapter")
            self.assertEqual(
                measurement["claimMode"], "exactly-one-adapter-specific-profile"
            )
            self.assertTrue(
                measurement["profile"].startswith(
                    "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                    "health-connect-"
                )
            )
        self.assertEqual(
            [item["id"] for item in measurements["serum-plasma-glucose"]["specimenAlternatives"]],
            ["plasma", "serum"],
        )

    def test_conversion_provenance_is_child_only_and_covers_every_output_profile(self) -> None:
        claim = next(
            item
            for item in self.claims["adapterConversionProvenanceClaims"]
            if item["adapter"] == "health-connect"
        )
        self.assertEqual(
            claim["profile"],
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-conversion-provenance",
        )
        self.assertIn("inherited Mobile profile is not repeated", claim["rule"])
        self.assertEqual(
            set(claim["targetAdapterProfiles"]),
            {
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation",
                *{
                    item["profile"] for item in self.adapter["adapterMeasurements"]
                },
            },
        )

    def test_context_mappings_are_closed_and_lossless(self) -> None:
        contexts = self.adapter["contextMappings"]
        specimens = contexts["bloodGlucoseSpecimen"]["values"]
        self.assertEqual(
            {row["source"] for row in specimens if row["status"] == "supported"},
            identity.SPECIMEN_TYPES,
        )
        self.assertEqual(
            {row["source"] for row in specimens if row["status"] == "intentionally-unsupported"},
            {"SPECIMEN_SOURCE_TEARS", "SPECIMEN_SOURCE_UNKNOWN"},
        )
        self.assertEqual({row["coding"]["system"] for row in specimens if row["coding"]}, {"http://snomed.info/sct"})
        sleep = contexts["sleepStage"]
        self.assertEqual({row["source"] for row in sleep["values"]}, identity.SLEEP_STAGE_TYPES)
        self.assertEqual(
            {row["shared"] for row in sleep["values"]},
            {"awake", "out-of-bed", "asleep-unspecified", "light", "deep", "rem", "unknown"},
        )
        self.assertIn("additional coding", sleep["r4Element"])
        self.assertEqual(contexts["sleepTitle"]["valueType"], "string")
        self.assertEqual(contexts["sleepNotes"]["r4Element"], "Observation.note.text")

    def test_mobile_health_connect_coverage_is_bidirectional(self) -> None:
        shared = {
            item["id"]: item
            for item in json.loads(
                (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
            )["measurements"]
        }
        supported_outputs = {
            output["measurement"]
            for row in self.adapter["recordTypes"]
            if row["status"] == "supported"
            for output in row["outputs"]
        }
        adapter_only = {item["id"] for item in self.adapter["adapterMeasurements"]}
        self.assertEqual(supported_outputs - set(shared), adapter_only)
        for measurement_id, measurement in shared.items():
            claimed = measurement["coverage"]["health-connect"] == "supported"
            self.assertEqual(
                claimed,
                measurement_id in supported_outputs,
                measurement_id,
            )

    def test_every_normative_identity_vector_is_exact(self) -> None:
        for vector in self.contract["vectors"]:
            with self.subTest(vector=vector["case"]):
                self.assertEqual(identity.canonical_json(vector["input"]), vector["canonical"])
                self.assertEqual(identity.digest(vector["input"]), vector["value"])

    def test_string_canonicalization_vectors_cover_cross_language_edges(self) -> None:
        for vector in self.contract["canonicalizationVectors"]:
            with self.subTest(vector=vector["case"]):
                self.assertEqual(identity.canonical_json(vector["input"]), vector["canonical"])
                self.assertEqual(identity.digest([vector["input"]]), vector["arrayDigest"])

    def test_helpers_reproduce_typed_vectors(self) -> None:
        vectors = {item["case"]: item for item in self.contract["vectors"]}
        record = vectors["record"]
        self.assertEqual(identity.record(*record["input"][1:]), record["value"])
        source = tuple(vectors["single-output"]["input"][1])
        self.assertEqual(identity.output(source, ["single"]), vectors["single-output"]["value"])
        self.assertEqual(
            identity.output(source, vectors["heart-rate-sample-output"]["input"][2:]),
            vectors["heart-rate-sample-output"]["value"],
        )
        self.assertEqual(
            identity.output(source, vectors["sleep-stage-output"]["input"][2:]),
            vectors["sleep-stage-output"]["value"],
        )
        specimen = vectors["specimen"]
        self.assertEqual(identity.specimen(tuple(specimen["input"][1]), specimen["input"][2]), specimen["value"])
        self.assertEqual(identity.event("conversion", [source], "1"), vectors["conversion"]["value"])
        self.assertEqual(identity.event("exchange", [source], "1"), vectors["exchange"]["value"])

    def test_identity_grammar_fails_closed(self) -> None:
        source = (self.contract["namingSystems"]["record"], "source-id")
        with self.assertRaises(identity.HealthConnectIdentityError):
            identity.canonical_json({"not": "admitted"})
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "surrogate"):
            identity.canonical_json("bad\ud800")
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "record type"):
            identity.record("1f5c58aa-6ec6-4e79-a682-829a9debd3f5", "UnknownRecord", "id")
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "raw record"):
            identity.record("1f5c58aa-6ec6-4e79-a682-829a9debd3f5", "StepsRecord", "")
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "sample instant"):
            identity.output(source, ["sample", "2026-08-20T17:30:15Z", "72", "0"])
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "beats per minute"):
            identity.output(source, ["sample", "2026-08-20T17:30:15.000000000Z", "072", "0"])
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "occurrence"):
            identity.output(source, ["sample", "2026-08-20T17:30:15.000000000Z", "72", "00"])
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "sleep stage token"):
            identity.output(
                source,
                ["sleep-stage", "2026-08-20T17:30:15.000000000Z", "2026-08-20T17:35:15.000000000Z", "LIGHT", "0"],
            )
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "specimen token"):
            identity.specimen(source, "SPECIMEN_SOURCE_TEARS")
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "positive decimal"):
            identity.event("conversion", [source], "01")
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "duplicate"):
            identity.event("conversion", [source, source], "1")
        with self.assertRaisesRegex(identity.HealthConnectIdentityError, "must not be empty"):
            identity.event("exchange", [], "1")

    def test_identifier_set_order_is_canonical_utf8_byte_order(self) -> None:
        identifiers = [("https://é.example", "💚"), ("https://example", "quote\"\\\n")]
        ordered = identity.identifier_set(reversed(identifiers))
        expected = sorted((list(item) for item in identifiers), key=lambda item: identity.canonical_json(item).encode("utf-8"))
        self.assertEqual(ordered, expected)


if __name__ == "__main__":
    unittest.main()
