"""Lock the Health Connect 1.1 inventory, mappings, and v0 protocol binding."""

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
STATUSES = {
    "supported",
    "mapped-standard",
    "platform-exclusive",
    "unmodeled",
    "deferred",
    "intentionally-unsupported",
}
RECORD_TYPES = {
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
    "PlannedExerciseSessionRecord",
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
SPECIMEN_TYPES = {
    "SPECIMEN_SOURCE_WHOLE_BLOOD",
    "SPECIMEN_SOURCE_CAPILLARY_BLOOD",
    "SPECIMEN_SOURCE_PLASMA",
    "SPECIMEN_SOURCE_SERUM",
    "SPECIMEN_SOURCE_INTERSTITIAL_FLUID",
}
SLEEP_STAGE_TYPES = {
    "STAGE_TYPE_UNKNOWN",
    "STAGE_TYPE_AWAKE",
    "STAGE_TYPE_SLEEPING",
    "STAGE_TYPE_OUT_OF_BED",
    "STAGE_TYPE_LIGHT",
    "STAGE_TYPE_DEEP",
    "STAGE_TYPE_REM",
    "STAGE_TYPE_AWAKE_IN_BED",
}


class HealthConnectCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = json.loads(
            (ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8")
        )
        cls.protocol = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        cls.claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        cls.measurement_rows = {
            item["id"]: item
            for item in json.loads(
                (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
            )["measurements"]
        }
        cls.known_measurements = set(cls.measurement_rows)
        cls.known_measurements.update(
            item["id"] for item in cls.adapter["adapterMeasurements"]
        )
        cls.rows = {row["token"]: row for row in cls.adapter["recordTypes"]}

    def test_record_type_inventory_is_exact_closed_and_complete(self) -> None:
        self.assertEqual(self.adapter["source"]["version"], "1.1.0")
        tokens = [row["token"] for row in self.adapter["recordTypes"]]
        self.assertEqual(tokens, sorted(RECORD_TYPES))
        self.assertEqual(len(tokens), 41)
        self.assertEqual(len(tokens), self.adapter["source"]["recordTypeCount"])
        self.assertEqual(len(tokens), len(set(tokens)))
        self.assertEqual(set(self.adapter["statusVocabulary"]), STATUSES)
        for row in self.adapter["recordTypes"]:
            self.assertIn(row["status"], STATUSES)
            self.assertEqual(bool(row["outputs"]), row["status"] == "supported")
            for output in row["outputs"]:
                self.assertIn(output["measurement"], self.known_measurements)
                self.assertIn(output["countRule"], self.adapter["outputCountRules"])
            for context in row["context"]:
                self.assertIn(context, self.adapter["contextMappings"])

    def test_every_unsupported_record_states_why(self) -> None:
        for row in self.adapter["recordTypes"]:
            if row["status"] == "supported":
                continue
            with self.subTest(record=row["token"]):
                self.assertIsInstance(row.get("reason"), str)
                self.assertTrue(row["reason"])

    def test_output_count_vocabulary_is_the_protocol_vocabulary(self) -> None:
        self.assertEqual(
            set(self.adapter["outputCountRules"]),
            set(self.protocol["outputCountRules"]),
        )
        self.assertEqual(
            set(self.adapter["identity"]["sourceOutput"]["outputDiscriminatorRules"]),
            {
                "exactly-one",
                "one-per-sample",
                "one-per-stage",
                "one-per-present-field",
                "specimen",
                "graph-specific",
            },
        )
        graph_references = {
            output["graphRule"]
            for record in self.adapter["recordTypes"]
            for output in record["outputs"]
            if output["countRule"] == "graph-specific"
        }
        self.assertEqual(graph_references, set(self.adapter["graphRules"]))
        output_roles = set(
            self.adapter["identity"]["sourceOutput"]["outputRoles"]
        )
        self.assertEqual(
            output_roles,
            {
                "single", "sample", "sleep-stage", "present-field",
                "specimen", "workout-segment",
            },
        )
        for name, rule in self.adapter["graphRules"].items():
            with self.subTest(graph_rule=name):
                self.assertTrue(rule["cardinality"])
                self.assertTrue(rule["outputs"])
                self.assertLessEqual(
                    {output["outputRole"] for output in rule["outputs"]},
                    output_roles,
                )

        glucose = self.adapter["graphRules"][
            "exactly-one-admitted-specimen-output"
        ]
        self.assertEqual(
            [
                (output["resourceRole"], output["outputRole"])
                for output in glucose["outputs"]
            ],
            [
                ("structured-observation", "single"),
                ("synthesized-specimen", "specimen"),
            ],
        )
        workout = self.adapter["graphRules"][
            "one-per-source-segment-or-lap"
        ]
        self.assertIn("ExerciseLap", workout["cardinality"])
        self.assertIn("EXERCISE_LAP", workout["projectionRule"])

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
        self.assertEqual(
            [
                item["id"]
                for item in measurements["serum-plasma-glucose"][
                    "specimenAlternatives"
                ]
            ],
            ["plasma", "serum"],
        )

    def test_conversion_provenance_is_child_only_and_covers_every_output(self) -> None:
        claim = next(
            item
            for item in self.claims["adapterConversionProvenanceClaims"]
            if item["adapter"] == "health-connect"
        )
        self.assertEqual(claim["sourceIdentifierRole"], "source-record")
        self.assertEqual(claim["sourceIdentityKind"], "source-record")
        self.assertIn("inherited Mobile profile is not repeated", claim["rule"])
        self.assertEqual(
            set(claim["targetAdapterProfiles"]),
            {
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-specimen",
                *{
                    item["profile"] for item in self.adapter["adapterMeasurements"]
                },
            },
        )
        profiles = (ROOT / "health-connect/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "* target only Reference(HealthConnectObservation or HealthConnectSpecimen)",
            profiles,
        )

    def test_context_mappings_are_closed_and_lossless(self) -> None:
        contexts = self.adapter["contextMappings"]
        specimens = contexts["bloodGlucoseSpecimen"]["values"]
        self.assertEqual(
            {row["source"] for row in specimens if row["status"] == "supported"},
            SPECIMEN_TYPES,
        )
        self.assertEqual(
            {
                row["source"]
                for row in specimens
                if row["status"] == "intentionally-unsupported"
            },
            {"SPECIMEN_SOURCE_TEARS", "SPECIMEN_SOURCE_UNKNOWN"},
        )
        sleep = contexts["sleepStage"]
        self.assertEqual(
            {row["source"] for row in sleep["values"]}, SLEEP_STAGE_TYPES
        )
        self.assertEqual(contexts["sessionTitle"]["valueType"], "string")
        self.assertEqual(
            contexts["sessionTitle"]["appliesToMeasurements"],
            ["workout", "sleep-duration", "mindfulness-session"],
        )
        self.assertEqual(
            contexts["sleepNotes"]["r4Element"], "Observation.note.text"
        )

        expected_contexts = {
            "CervicalMucusRecord": [
                "cervicalMucusAppearance", "cervicalMucusSensation",
            ],
            "ExerciseSessionRecord": [
                "exerciseType", "exerciseSegmentType", "sessionTitle",
                "exerciseNotes",
            ],
            "MenstruationFlowRecord": ["menstruationFlow"],
            "OvulationTestRecord": ["ovulationTestResult"],
            "SexualActivityRecord": ["sexualActivityProtection"],
            "SkinTemperatureRecord": ["skinTemperatureMeasurementLocation"],
        }
        for record_type, expected in expected_contexts.items():
            with self.subTest(record_type=record_type):
                self.assertEqual(self.rows[record_type]["context"], expected)

    def test_exact_source_context_domains_match_complete_fsh_code_systems(self) -> None:
        terminology = (ROOT / "health-connect/input/fsh/terminology.fsh").read_text(
            encoding="utf-8"
        )

        def concepts(code_system: str) -> set[str]:
            block = terminology.split(f"CodeSystem: {code_system}\n", 1)[1]
            block = block.split("\nValueSet:", 1)[0]
            return {
                line.split(' "', 1)[0].removeprefix("* #")
                for line in block.splitlines()
                if line.startswith("* #")
            }

        mappings = {
            "menstruationFlow": "HealthConnectMenstruationFlowCS",
            "ovulationTestResult": "HealthConnectOvulationTestResultCS",
            "sexualActivityProtection": "HealthConnectSexualActivityProtectionCS",
            "cervicalMucusAppearance": "HealthConnectCervicalMucusAppearanceCS",
            "cervicalMucusSensation": "HealthConnectCervicalMucusSensationCS",
            "exerciseType": "HealthConnectExerciseTypeCS",
            "exerciseSegmentType": "HealthConnectExerciseSegmentTypeCS",
        }
        for context_name, code_system in mappings.items():
            mapping = self.adapter["contextMappings"][context_name]
            catalog_codes = set(mapping.get("allowedSourceCodes", [])) or {
                row["code"] for row in mapping["values"]
            }
            with self.subTest(context=context_name):
                self.assertEqual(catalog_codes, concepts(code_system))

        self.assertIn(
            "RESULT_POSITIVE", self.adapter["contextMappings"]["ovulationTestResult"]
            ["values"][2]["code"],
        )
        self.assertIn(
            "PROTECTION_USED_UNPROTECTED",
            {
                row["code"]
                for row in self.adapter["contextMappings"]
                ["sexualActivityProtection"]["values"]
            },
        )

    def test_health_connect_identifier_and_note_slices_are_closed(self) -> None:
        profiles = (ROOT / "health-connect/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        observation = profiles.split("Profile: HealthConnectObservation", 1)[1].split(
            "\nProfile:", 1
        )[0]
        specimen = profiles.split("Profile: HealthConnectSpecimen", 1)[1].split(
            "\nProfile:", 1
        )[0]
        self.assertIn("* identifier 2..* MS", observation)
        self.assertIn("* identifier ^slicing.rules = #open", observation)
        self.assertIn("* note 0..1 MS", observation)
        self.assertIn("* note.author[x] 0..0", observation)
        self.assertIn("* note.time 0..0", observation)
        self.assertIn("* identifier 2..2 MS", specimen)
        self.assertIn("* identifier ^slicing.rules = #closed", specimen)

    def test_session_title_is_profile_scoped_to_three_primary_summaries(self) -> None:
        profiles = (ROOT / "health-connect/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        invariant = profiles.split(
            "Invariant: health-connect-session-title-1", 1
        )[1].split("\nInvariant:", 1)[0]
        self.assertIn("count() = 1", invariant)
        for record_type, profile, code in (
            ("ExerciseSessionRecord", "grove-mobile-workout", "workout"),
            ("SleepSessionRecord", "grove-mobile-sleep-duration", "93832-4"),
            (
                "MindfulnessSessionRecord",
                "grove-mobile-mindfulness-session",
                "mindfulness-session-duration",
            ),
        ):
            with self.subTest(record_type=record_type):
                self.assertIn(record_type, invariant)
                self.assertIn(profile, invariant)
                self.assertIn(code, invariant)

        observation = profiles.split(
            "Profile: HealthConnectObservation", 1
        )[1].split("\nProfile:", 1)[0]
        self.assertIn("health-connect-session-title-1", observation)
        self.assertIn("HealthConnectSessionTitle named sessionTitle 0..1 MS", observation)
        nonblank = profiles.split(
            "Invariant: health-connect-session-text-nonblank-1", 1
        )[1].split("\nInvariant:", 1)[0]
        # This suite runs before SUSHI in a clean CI checkout, so lock the tracked
        # FSH escape layer rather than depending on ignored fsh-generated output.
        # SUSHI consumes each four-backslash FSH token as the intended two-character
        # FHIRPath regular-expression escape (\\S).
        self.assertEqual(nonblank.count(r"(?s).*\\\\S.*"), 2)
        self.assertIn("note.all(text.toString().matches(", nonblank)
        self.assertNotIn("Every output also declares exactly one shared", profiles)
        self.assertIn("one exact profile-claim mode", profiles)
        retention_policy = (
            "RETAIN preserves the non-blank source field; OMIT deliberately omits it; "
            "the producer must explicitly select one"
        )
        for key in ("sessionTitle", "exerciseNotes", "sleepNotes", "mindfulnessNotes"):
            self.assertEqual(self.adapter["contextMappings"][key]["retentionPolicy"], retention_policy)

    def test_mindfulness_and_vo2_context_is_exact(self) -> None:
        self.assertEqual(
            self.rows["MindfulnessSessionRecord"]["context"],
            ["mindfulnessSessionType", "sessionTitle", "mindfulnessNotes"],
        )
        mindfulness = self.adapter["contextMappings"]["mindfulnessSessionType"]
        self.assertEqual(mindfulness["r4Element"], "Observation.method")
        self.assertEqual(len(mindfulness["values"]), 6)
        self.assertEqual(
            {row["source"] for row in mindfulness["values"]},
            {row["code"] for row in mindfulness["values"]},
        )
        self.assertEqual(
            self.rows["Vo2MaxRecord"]["context"], ["vo2MaxMeasurementMethod"]
        )
        method = self.adapter["contextMappings"]["vo2MaxMeasurementMethod"]
        self.assertEqual(method["r4Element"], "Observation.method")
        self.assertEqual(len(method["values"]), 6)

    def test_resting_heart_rate_is_point_in_time_not_daily_average(self) -> None:
        self.assertEqual(
            self.rows["RestingHeartRateRecord"]["outputs"],
            [{"measurement": "resting-heart-rate", "countRule": "exactly-one"}],
        )
        self.assertEqual(
            self.measurement_rows["resting-heart-rate"]["effective"], "dateTime"
        )
        self.assertEqual(
            [
                (coding["system"], coding["code"])
                for coding in self.measurement_rows["resting-heart-rate"][
                    "requiredCodings"
                ]
            ],
            [("http://loinc.org", "8867-4")],
        )
        self.assertEqual(
            self.measurement_rows["resting-heart-rate-daily-average"]["effective"],
            "Period",
        )
        self.assertEqual(
            self.measurement_rows["resting-heart-rate-daily-average"]["coverage"][
                "health-connect"
            ],
            "unmodeled",
        )

    def test_exchange_identity_binding_matches_protocol_component_order(self) -> None:
        binding = self.adapter["identity"]
        self.assertEqual(binding["contract"], "catalog/exchange-protocol.json")
        self.assertEqual(binding["protocolVersion"], 0)
        self.assertEqual(binding["adapterId"], "health-connect")
        kinds = {
            row["kind"]: row["components"]
            for row in self.protocol["opaqueIdentity"]["identityKinds"]
        }
        self.assertEqual(
            binding["sourceRecord"]["components"], kinds["source-record"]
        )
        self.assertEqual(
            binding["sourceOutput"]["components"], kinds["source-output"]
        )
        self.assertFalse(
            {"measured-value", "measurement-value", "quantity-value"}
            & set(binding["sourceRecord"]["components"])
        )

    def test_sample_vector_uses_the_closed_health_connect_coordinates(self) -> None:
        vector = next(
            row
            for row in self.protocol["testVectors"]["identities"]
            if row["id"] == "multi-output-sample"
        )
        self.assertEqual(vector["identityKind"], "source-output")
        self.assertEqual(vector["components"][0:2], ["health-connect", "HeartRateRecord"])
        self.assertEqual(vector["components"][-2], "sample")
        self.assertEqual(
            vector["components"][-1],
            "2026-08-19T10:30:00.000000000Z|0",
        )
        self.assertIn(
            "<canonical UTC instant with nine fractional digits>|",
            self.adapter["identity"]["sourceOutput"]["outputDiscriminatorRules"][
                "one-per-sample"
            ],
        )

    def test_writer_identity_is_source_supplied_only(self) -> None:
        writer = self.adapter["identity"]["writerRecord"]
        self.assertEqual(writer["condition"], "Metadata.clientRecordId is present.")
        revision = writer["revision"]
        self.assertEqual(revision["presenceRule"], "identifier-controls-pair")
        self.assertEqual(revision["versionMinimum"], 0)
        self.assertEqual(revision["versionMaximum"], 9223372036854775807)
        self.assertIn("defaults to 0", revision["versionRule"])
        self.assertIn("non-blank", revision["identifierRule"])
        self.assertEqual(revision["invalidDisposition"], "reject-source-record")
        self.assertIn("never infer", writer["version"])
        self.assertIn("synthesize", writer["version"])

    def test_recording_device_requires_true_per_unit_evidence(self) -> None:
        device = self.adapter["recordingDeviceIdentity"]
        self.assertEqual(device["status"], "stable-token-required")
        self.assertIn("no per-unit", device["stableUnitToken"])
        self.assertIn("Omit", device["fallback"])
        self.assertNotIn("derived", json.dumps(device).lower())


if __name__ == "__main__":
    unittest.main()
