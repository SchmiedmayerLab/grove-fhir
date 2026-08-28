"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from Scripts.producer_validation import (
    diagnostics,
    health_connect,
    profiles as profile_validation,
)
from Tests.producer_validation_test_support import (
    ProducerValidationTestCase,
    ROOT,
    copy,
    derive_hmac_identity,
    json,
    typed_identifier,
)

class ProducerHealthConnectTests(ProducerValidationTestCase):
    def test_writer_record_version_pair_accepts_boundaries_and_rejects_malformed_values(self) -> None:
        version_url = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-writer-record-version"
        )
        writer = typed_identifier(
            "writer-record",
            "https://example.org/fhir/NamingSystem/writer-record/test-key/1",
            "v2:test-key:1:" + "A" * 43,
        )
        for version in ("0", "9223372036854775807", "9223372036854775808"):
            resource = {
                "resourceType": "Observation",
                "identifier": [writer],
                "extension": [{"url": version_url, "valueString": version}],
            }
            with self.subTest(version=version):
                profile_validation.validate_writer_record_revision(resource, "Record")
        for version in ("", "-1", "+1", "01", "1.0"):
            resource = {
                "resourceType": "Observation",
                "identifier": [writer],
                "extension": [{"url": version_url, "valueString": version}],
            }
            with self.subTest(version=version), self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "canonical non-negative decimal integer",
            ):
                profile_validation.validate_writer_record_revision(resource, "Record")
        health_connect = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                "health-connect-observation"
            ]},
            "identifier": [writer],
            "extension": [{
                "url": version_url,
                "valueString": "9223372036854775808",
            }],
        }
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exceeds Long.MAX_VALUE"
        ):
            profile_validation.validate_writer_record_revision(
                health_connect, "Health Connect Record"
            )
        profile_validation.validate_writer_record_revision(
            {"resourceType": "Observation", "identifier": [writer]}, "Record"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "adapter requires.*together"
        ):
            profile_validation.validate_writer_record_revision(
                {
                    "resourceType": "Observation",
                    "meta": {"profile": [
                        "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
                        "healthkit-observation"
                    ]},
                    "identifier": [writer],
                },
                "HealthKit Record",
            )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "version requires exactly one writer-record"
        ):
            profile_validation.validate_writer_record_revision(
                {
                    "resourceType": "Observation",
                    "extension": [{"url": version_url, "valueString": "0"}],
                },
                "Record",
            )

    def test_health_connect_glucose_child_is_an_exact_active_claim_mode(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        for profile in claims["healthConnectPlatformExclusiveClaims"]["profiles"]:
            resource = {
                "resourceType": "Observation",
                "meta": {"profile": [profile]},
                "valueQuantity": {"value": 0},
            }
            with self.subTest(profile=profile):
                profile_validation.validate_active_observation_profile_claim(
                    resource, "Observation", {profile}
                )

            invalid = copy.deepcopy(resource)
            invalid["meta"]["profile"].append(
                "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                "grove-mobile-blood-glucose-unspecified-specimen"
            )
            with self.subTest(profile=profile, shape="extra"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "admitted semantic profile",
            ):
                profile_validation.validate_active_observation_profile_claim(
                    invalid, "Observation", {profile}
                )

    def test_health_connect_specimen_claim_is_explicit_and_exact(self) -> None:
        profile = (
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-specimen"
        )
        specimen = {
            "resourceType": "Specimen",
            "meta": {"profile": [profile]},
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/source-record/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-record",
                        components=["health-connect", "BloodGlucoseRecord", "scope", "one", "record"],
                    ),
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-output",
                        components=["health-connect", "BloodGlucoseRecord", "scope", "one", "record", "specimen", "whole-blood"],
                    ),
                ),
            ],
            "type": {"coding": [{
                "system": "http://snomed.info/sct",
                "code": "258580003",
            }]},
        }
        health_connect.validate_health_connect_specimen_claim(specimen, "Specimen")
        for invalid_profiles in ([profile, "http://example.org/extra"],):
            invalid = copy.deepcopy(specimen)
            invalid["meta"]["profile"] = invalid_profiles
            with self.subTest(profiles=invalid_profiles), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "must directly claim exactly"
            ):
                health_connect.validate_health_connect_specimen_claim(invalid, "Specimen")
        extra_identifier = copy.deepcopy(specimen)
        extra_identifier["identifier"].append({
            "system": "https://source.example/native",
            "value": "clear-native-specimen-id",
        })
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly two identifiers"
        ):
            health_connect.validate_health_connect_specimen_claim(
                extra_identifier, "Specimen"
            )
        extra_snomed = copy.deepcopy(specimen)
        extra_snomed["type"]["coding"].append({
            "system": "http://snomed.info/sct",
            "code": "999999999999999999",
        })
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly one admitted SNOMED"
        ):
            health_connect.validate_health_connect_specimen_claim(extra_snomed, "Specimen")

    def test_health_connect_conversion_provenance_claim_is_child_only(self) -> None:
        profile = (
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-conversion-provenance"
        )
        source_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        source_value = derive_hmac_identity(
            key=bytes(range(32)),
            key_id="test-key",
            epoch=1,
            identity_kind="source-record",
            components=[
                "health-connect", "HeartRateRecord", "https://example.org/repository",
                "default", "record-1",
            ],
        )
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [profile]},
            "target": [{"reference": "urn:uuid:00000000-0000-5000-8000-000000000000"}],
            "entity": [{
                "role": "source",
                "what": {"identifier": typed_identifier(
                    "source-record", source_system, source_value
                )},
                "agent": [{
                    "type": {"coding": [{
                        "system": (
                            "http://terminology.hl7.org/CodeSystem/"
                            "provenance-participant-type"
                        ),
                        "code": "enterer",
                    }]},
                    "who": {
                        "type": "Device",
                        "identifier": {
                            "system": (
                                "https://grovealliance.org/fhir/health-connect/"
                                "NamingSystem/android-package-name"
                            ),
                            "value": "org.example.writer",
                        },
                    },
                }],
            }],
        }
        profile_validation.validate_adapter_conversion_provenance(provenance, "Provenance")
        literal_data_origin = copy.deepcopy(provenance)
        literal_data_origin["entity"][0]["agent"][0]["who"]["reference"] = (
            "urn:uuid:00000000-0000-5000-8000-000000000001"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "identifier-only Device Reference",
        ):
            profile_validation.validate_adapter_conversion_provenance(
                literal_data_origin, "Provenance"
            )
        invalid_source_system = copy.deepcopy(provenance)
        invalid_source_system["entity"][0]["what"]["identifier"]["system"] = (
            "https://example.org/bad path"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "absolute RFC 3986 URI"
        ):
            profile_validation.validate_adapter_conversion_provenance(
                invalid_source_system, "Provenance"
            )
        provenance["meta"]["profile"].insert(
            0,
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-conversion-provenance",
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "directly claim exactly"
        ):
            profile_validation.validate_adapter_conversion_provenance(provenance, "Provenance")

    def test_health_connect_source_context_is_closed_and_catalog_driven(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8")
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                "grove-mobile-menstruation-flow",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                "health-connect-observation",
            ]},
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/source-record/test-key/1",
                    "v2:test-key:1:" + "C" * 43,
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                    "v2:test-key:1:" + "D" * 43,
                ),
            ],
            "extension": [{
                "url": catalog["sourceTypeExtension"]["url"],
                "valueCode": "MenstruationFlowRecord",
            }],
            "valueCodeableConcept": {"coding": [
                {
                    "system": "https://grovealliance.org/fhir/mobile/CodeSystem/"
                    "grove-menstruation-flow",
                    "code": "light",
                },
                {
                    "system": catalog["contextMappings"]["menstruationFlow"]
                    ["sourceCodeSystem"],
                    "code": "FLOW_LIGHT",
                },
            ]},
        }
        health_connect.validate_health_connect_source_type(observation, "Menstruation")

        unknown = copy.deepcopy(observation)
        unknown["valueCodeableConcept"]["coding"][1]["code"] = "FLOW_NOT_REAL"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly one admitted"
        ):
            health_connect.validate_health_connect_source_type(unknown, "Menstruation")

        invented_site = copy.deepcopy(observation)
        invented_site["bodySite"] = {"coding": [{
            "system": "https://example.org/bogus",
            "code": "not-a-location",
        }]}
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "does not admit Health Connect body site"
        ):
            health_connect.validate_health_connect_source_type(
                invented_site, "Menstruation"
            )

        blood_pressure = copy.deepcopy(observation)
        blood_pressure["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-blood-pressure"
        )
        blood_pressure["extension"][0]["valueCode"] = "BloodPressureRecord"
        blood_pressure.pop("valueCodeableConcept")
        blood_pressure["bodySite"] = {"coding": [{
            "system": "http://snomed.info/sct",
            "code": "5951000",
            "display": "Structure of left wrist region",
        }]}
        health_connect.validate_health_connect_source_type(
            blood_pressure, "Blood pressure"
        )

        invented_note = copy.deepcopy(observation)
        invented_note["note"] = [{"text": "not a source field"}]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "does not admit source-authored notes"
        ):
            health_connect.validate_health_connect_source_type(
                invented_note, "Menstruation"
            )

        session = copy.deepcopy(observation)
        session["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-sleep-duration"
        )
        session["extension"] = [
            {
                "url": catalog["sourceTypeExtension"]["url"],
                "valueCode": "SleepSessionRecord",
            },
            {
                "url": catalog["contextMappings"]["sessionTitle"]["extension"],
                "valueString": "Overnight sleep",
            },
        ]
        session.pop("valueCodeableConcept")
        session["note"] = [{"text": "Travel night"}]
        health_connect.validate_health_connect_source_type(session, "Sleep summary")

        multiline_note = copy.deepcopy(session)
        multiline_note["note"] = [{"text": "First line\n\nSecond line"}]
        health_connect.validate_health_connect_source_type(
            multiline_note, "Sleep summary with multiline note"
        )

        blank_title = copy.deepcopy(session)
        blank_title["extension"][1]["valueString"] = " \t "
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "outside its admitted"):
            health_connect.validate_health_connect_source_type(blank_title, "Sleep summary")
        duplicate_title = copy.deepcopy(session)
        duplicate_title["extension"].append(copy.deepcopy(duplicate_title["extension"][1]))
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "repeats sessionTitle"):
            health_connect.validate_health_connect_source_type(duplicate_title, "Sleep summary")
        wrong_child = copy.deepcopy(session)
        wrong_child["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-stage"
        )
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "does not admit"):
            health_connect.validate_health_connect_source_type(wrong_child, "Sleep stage")
        blank_note = copy.deepcopy(session)
        blank_note["note"][0]["text"] = "\n\t"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "non-blank text"):
            health_connect.validate_health_connect_source_type(blank_note, "Sleep summary")

        meal_context = copy.deepcopy(observation)
        meal_context["extension"].append({
            "url": catalog["contextMappings"]["bloodGlucoseMealContext"]["extension"],
            "extension": [{
                "url": "mealType",
                "valueCoding": {
                    "system": catalog["contextMappings"]["bloodGlucoseMealContext"]
                    ["mealType"]["codeSystem"],
                    "code": "MEAL_TYPE_BREAKFAST",
                },
            }],
        })
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "does not admit.*meal context"
        ):
            health_connect.validate_health_connect_source_type(meal_context, "Menstruation")

        mindfulness_context = copy.deepcopy(observation)
        mindfulness_context["method"] = {
            "coding": [{
                "system": catalog["contextMappings"]["mindfulnessSessionType"]
                ["codeSystem"],
                "code": "MINDFULNESS_SESSION_TYPE_MEDITATION",
            }],
        }
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "mindfulness method outside"
        ):
            health_connect.validate_health_connect_source_type(
                mindfulness_context, "Menstruation"
            )

        vo2_method = copy.deepcopy(observation)
        vo2_method["method"] = {"coding": [{
            "system": catalog["contextMappings"]["vo2MaxMeasurementMethod"]
            ["codeSystem"],
            "code": "MEASUREMENT_METHOD_COOPER_TEST",
        }]}
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "VO2 method outside"
        ):
            health_connect.validate_health_connect_source_type(vo2_method, "Menstruation")

        mindfulness = copy.deepcopy(observation)
        mindfulness["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-mindfulness-session"
        )
        mindfulness["extension"][0]["valueCode"] = "MindfulnessSessionRecord"
        mindfulness["valueCodeableConcept"] = None
        mindfulness["method"] = {
            "coding": [{
                "system": catalog["contextMappings"]["mindfulnessSessionType"]
                ["codeSystem"],
                "code": "MINDFULNESS_SESSION_TYPE_NOT_REAL",
            }],
        }
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly one admitted"
        ):
            health_connect.validate_health_connect_source_type(mindfulness, "Mindfulness")

    def test_health_connect_exact_output_cardinality_and_record_type_are_closed(self) -> None:
        source_identifier = typed_identifier(
            "source-record",
            "https://example.org/fhir/NamingSystem/source-record/test-key/1",
            "v2:test-key:1:" + "E" * 43,
        )
        record_type_url = json.loads(
            (ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8")
        )["sourceTypeExtension"]["url"]

        def observation(
            record_type: str, measurement_profile: str, output_character: str
        ) -> dict[str, object]:
            return {
                "resourceType": "Observation",
                "meta": {"profile": [
                    "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                    f"{measurement_profile}",
                    "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                    "health-connect-observation",
                ]},
                "identifier": [
                    copy.deepcopy(source_identifier),
                    typed_identifier(
                        "source-output",
                        "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                        "v2:test-key:1:" + output_character * 43,
                    ),
                ],
                "extension": [{"url": record_type_url, "valueCode": record_type}],
            }

        height = observation("HeightRecord", "grove-mobile-body-height", "F")
        height_url = "urn:uuid:00000000-0000-5000-8000-000000000101"
        health_connect.validate_health_connect_output_graph(
            [height], {height_url: height}, "HealthConnect"
        )

        duplicate = observation("HeightRecord", "grove-mobile-body-height", "G")
        duplicate_url = "urn:uuid:00000000-0000-5000-8000-000000000102"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "must emit exactly one body-height"
        ):
            health_connect.validate_health_connect_output_graph(
                [height, duplicate],
                {height_url: height, duplicate_url: duplicate},
                "HealthConnect",
            )

        weight = observation("WeightRecord", "grove-mobile-body-weight", "H")
        weight_url = "urn:uuid:00000000-0000-5000-8000-000000000103"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "cannot name multiple Record types"
        ):
            health_connect.validate_health_connect_output_graph(
                [height, weight],
                {height_url: height, weight_url: weight},
                "HealthConnect",
            )
