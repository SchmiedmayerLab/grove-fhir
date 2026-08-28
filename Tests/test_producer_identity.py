"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from Scripts.producer_validation import (
    context,
    diagnostics,
    identity,
    manifest as manifest_validation,
)
from Tests.producer_validation_test_support import (
    Path,
    ProducerValidationTestCase,
    copy,
    json,
    tempfile,
    typed_identifier,
)

class ProducerIdentityTests(ProducerValidationTestCase):
    def test_device_snapshot_outranks_stable_recording_device_identity(self) -> None:
        system = "https://study.example.org/fhir/NamingSystem/device"
        recording = "v2:test-key:1:" + "A" * 43
        snapshot = "v2:test-key:1:" + "B" * 43
        device = {
            "resourceType": "Device",
            "identifier": [
                typed_identifier("recording-device", system, recording),
                typed_identifier("device-snapshot", system, snapshot),
            ],
        }
        self.assertEqual(
            identity.selected_entry_identifier(device, "Device/test"),
            ("device-snapshot", (system, snapshot)),
        )
        self.assertEqual(
            list(context.IDENTIFIER_PRIORITY),
            context.EXCHANGE_PROTOCOL["entryIdentity"]["resourceIdentifierPriority"],
        )

    def test_mobile_semantic_vectors_are_generated_bound_and_exact(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            manifest_path = root / "manifest.json"
            resource_path = root / "resources/exchange-bundle.json"

            def validate() -> None:
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                resource_path.write_text(json.dumps(resource), encoding="utf-8")
                manifest_validation.validate_manifest(manifest_path)

            validate()

            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.251000000Z"
            )
            validate()
            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.250999927Z"
            )
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "not millisecond-canonical"
            ):
                validate()
            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.252Z"
            )
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "effective instant does not equal"
            ):
                validate()
            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T08:30:00.251-07:00"
            )

            manifest["semanticVectors"] = []
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "missing heart-rate"
            ):
                validate()

            manifest["semanticVectors"] = [{
                "id": "heart-rate",
                "path": "resources/exchange-bundle.json",
                "resourcePointer": "/entry/2/resource",
            }]
            resource["entry"][2]["resource"]["valueQuantity"]["value"] = 73
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "clinical projection does not equal"
            ):
                validate()

            resource["entry"][2]["resource"]["valueQuantity"]["value"] = 72
            manifest["semanticVectors"][0]["resourcePointer"] = "/entry/01/resource"
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "invalid array index"
            ):
                validate()

    def test_identifier_name_composes_without_escaping(self) -> None:
        self.assertEqual(
            identity.canonical_identifier_name('https://example.org/"quoted"', "line\nback\\slash"),
            'https://example.org/"quoted"|line\nback\\slash',
        )

    def test_full_url_framing_admits_separators_without_boundary_collisions(self) -> None:
        self.assertNotEqual(
            identity.expected_entry_full_url("https://example.org/a:b", "x"),
            identity.expected_entry_full_url("https://example.org/a", "b:x"),
        )

    def test_governed_source_identifier_is_optional_and_primary_only(self) -> None:
        source = typed_identifier(
            "source-record",
            "https://store.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1",
            "v2:test-key:1:" + "A" * 43,
        )
        output = typed_identifier(
            "source-output",
            "https://store.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1",
            "v2:test-key:1:" + "B" * 43,
        )
        native = {
            "system": "https://store.example.org/fhir/NamingSystem/healthkit-object/store-a",
            "value": "AD32CFC5-025A-493E-BC1B-85378817AC1C",
        }
        primary = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate",
                "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation",
            ]},
            "extension": [{
                "url": "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-source-type-extension",
                "valueCode": "HKQuantityTypeIdentifierHeartRate",
            }],
            "identifier": [copy.deepcopy(source), copy.deepcopy(output), copy.deepcopy(native)],
        }
        identity.validate_governed_source_identifiers([primary], "Event")
        without_native = copy.deepcopy(primary)
        without_native["identifier"].pop()
        identity.validate_governed_source_identifiers([without_native], "Event")

        relative_system = copy.deepcopy(primary)
        relative_system["identifier"][2]["system"] = "healthkit/store-a"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "absolute.*URI"):
            identity.validate_governed_source_identifiers([relative_system], "Event")
        blank_value = copy.deepcopy(primary)
        blank_value["identifier"][2]["value"] = ""
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "complete system and value"):
            identity.validate_governed_source_identifiers([blank_value], "Event")
        text_only_type = copy.deepcopy(primary)
        text_only_type["identifier"][2]["type"] = {"text": "HealthKit object UUID"}
        identity.validate_governed_source_identifiers([text_only_type], "Event")
        coded_type = copy.deepcopy(primary)
        coded_type["identifier"][2]["type"] = {
            "coding": [{
                "system": "https://store.example.org/fhir/CodeSystem/native-id-type",
                "code": "healthkit-object-uuid",
            }]
        }
        identity.validate_governed_source_identifiers([coded_type], "Event")
        relative_type_system = copy.deepcopy(coded_type)
        relative_type_system["identifier"][2]["type"]["coding"][0]["system"] = (
            "native-id-type"
        )
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "absolute.*URI"):
            identity.validate_governed_source_identifiers(
                [relative_type_system], "Event"
            )
        invalid_type_code = copy.deepcopy(coded_type)
        invalid_type_code["identifier"][2]["type"]["coding"][0]["code"] = (
            " healthkit-object-uuid "
        )
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "FHIR code"):
            identity.validate_governed_source_identifiers([invalid_type_code], "Event")
        false_grove_type = copy.deepcopy(primary)
        false_grove_type["identifier"][2]["type"] = {
            "coding": [{"system": context.IDENTIFIER_ROLE_SYSTEM, "code": "source-record"}]
        }
        with self.assertRaises(diagnostics.ProducerValidationError):
            identity.validate_governed_source_identifiers([false_grove_type], "Event")
        copied_resource_id = copy.deepcopy(primary)
        copied_resource_id["id"] = native["value"]
        identity.validate_governed_source_identifiers([copied_resource_id], "Event")

        average = copy.deepcopy(primary)
        average["meta"]["profile"][1] = (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-average-heart-rate-observation"
        )
        average["extension"][0]["valueCode"] = "HKDataTypeIdentifierElectrocardiogram"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers([average], "Event")

        workout_primary = copy.deepcopy(primary)
        workout_primary["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-workout"
        )
        workout_primary["extension"][0]["valueCode"] = "HKWorkoutTypeIdentifier"
        workout_segment = copy.deepcopy(workout_primary)
        workout_segment["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-workout-segment"
        )
        workout_segment["identifier"] = [
            copy.deepcopy(source),
            typed_identifier(
                "source-output", output["system"], "v2:test-key:1:" + "W" * 43
            ),
        ]
        identity.validate_governed_source_identifiers(
            [workout_primary, workout_segment], "Event"
        )
        segment_disclosure = copy.deepcopy(workout_segment)
        segment_disclosure["identifier"].append(copy.deepcopy(native))
        workout_without_native = copy.deepcopy(workout_primary)
        workout_without_native["identifier"].pop()
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers(
                [workout_without_native, segment_disclosure], "Event"
            )
        specimen = copy.deepcopy(primary)
        specimen["resourceType"] = "Specimen"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "secondary or support"):
            identity.validate_governed_source_identifiers([specimen], "Event")

        second_primary = copy.deepcopy(primary)
        second_primary["identifier"][2]["value"] = "another-native-id"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "only one primary"):
            identity.validate_governed_source_identifiers(
                [primary, second_primary], "Event"
            )
        support_copy = {
            "resourceType": "Device",
            "identifier": [copy.deepcopy(native)],
        }
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "appear exactly once"):
            identity.validate_governed_source_identifiers([primary, support_copy], "Event")

        support_id_copy = {"resourceType": "Device", "id": native["value"]}
        identity.validate_governed_source_identifiers(
            [primary, support_id_copy], "Event"
        )

        # Value-only coincidences are not identity evidence. The validator therefore
        # does not reject a clinical/component string, Resource.id, or logical target
        # merely because it happens to equal an opaque source value; structural reuse
        # of the exact Identifier system/value pair remains rejected above.
        component_copy = copy.deepcopy(primary)
        component_copy["component"] = [{
            "code": {"text": "Source trace"},
            "valueString": native["value"],
        }]
        identity.validate_governed_source_identifiers([component_copy], "Event")

        retraction_copy = {
            "resourceType": "Provenance",
            "target": [{"identifier": {
                "system": "https://example.org/other-namespace",
                "value": native["value"],
            }}],
        }
        identity.validate_governed_source_identifiers(
            [primary, retraction_copy], "Event"
        )

        sensorkit_marker = {
            "url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type",
            "valueCode": "device-usage",
        }
        structured_primary = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-device-usage-observation"
            ]},
            "extension": [copy.deepcopy(sensorkit_marker)],
            "identifier": [copy.deepcopy(source), copy.deepcopy(output)],
        }
        companion_artifact = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document",
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-recording-document",
            ]},
            "extension": [copy.deepcopy(sensorkit_marker)],
            "identifier": [
                copy.deepcopy(source),
                typed_identifier(
                    "source-output", output["system"], "v2:test-key:1:" + "C" * 43
                ),
                typed_identifier(
                    "source-artifact",
                    "https://store.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1",
                    "v2:test-key:1:" + "D" * 43,
                ),
                copy.deepcopy(native),
            ],
        }
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers(
                [structured_primary, companion_artifact], "Event"
            )

        child = copy.deepcopy(primary)
        child["meta"]["profile"] = [
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-stage",
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation",
        ]
        child["extension"] = [{
            "url": (
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                "health-connect-record-type"
            ),
            "valueCode": "SleepSessionRecord",
        }]
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers([child], "Event")

        self_designated = copy.deepcopy(primary)
        self_designated["extension"] = []
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers([self_designated], "Event")

    def test_governed_source_identifier_uses_health_connect_and_provider_row_output(self) -> None:
        source = typed_identifier(
            "source-record", "https://example.org/source-record",
            "v2:test-key:1:" + "E" * 43,
        )
        native = {
            "system": "https://store.example.org/native-record",
            "value": "upstream-record-1",
        }

        def output(fill: str) -> dict[str, object]:
            return typed_identifier(
                "source-output", "https://example.org/source-output",
                "v2:test-key:1:" + fill * 43,
            )

        hc_marker = {
            "url": "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type",
            "valueCode": "SleepSessionRecord",
        }
        summary = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-duration",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation",
            ]},
            "extension": [copy.deepcopy(hc_marker)],
            "identifier": [copy.deepcopy(source), output("F"), copy.deepcopy(native)],
        }
        stage = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-stage",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation",
            ]},
            "extension": [copy.deepcopy(hc_marker)],
            "identifier": [copy.deepcopy(source), output("G")],
        }
        identity.validate_governed_source_identifiers([summary, stage], "Event")
        child_disclosure = copy.deepcopy(stage)
        child_disclosure["identifier"].append(copy.deepcopy(native))
        summary_without_native = copy.deepcopy(summary)
        summary_without_native["identifier"].pop()
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers(
                [summary_without_native, child_disclosure], "Event"
            )

        provider_extensions = [
            {
                "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                "valueCode": "google-health-api",
            },
            {
                "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider-source-type",
                "valueCode": "google-health-api/steps",
            },
        ]
        provider_single = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count",
                "https://grovealliance.org/fhir/google-health/StructureDefinition/google-health-observation",
            ]},
            "extension": copy.deepcopy(provider_extensions),
            "identifier": [copy.deepcopy(source), output("H"), copy.deepcopy(native)],
        }
        identity.validate_governed_source_identifiers([provider_single], "Event")

        provider_multi = copy.deepcopy(provider_single)
        provider_multi["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
        )
        provider_multi["extension"][0]["valueCode"] = "oura"
        provider_multi["extension"][1]["valueCode"] = "oura/daily_activity"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "catalog-designated"):
            identity.validate_governed_source_identifiers([provider_multi], "Event")
