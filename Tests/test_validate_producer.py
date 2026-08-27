"""Tests for the producer-neutral Grove FHIR conformance kit."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

from Scripts import fhir_fixture_corpus as CORPUS
from Scripts.exchange_protocol import (
    derive_hmac_identity,
    entry_node_identity,
    event_identity,
)


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_producer", ROOT / "Scripts/validate-producer.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def typed_identifier(role: str, system: str, value: str) -> dict[str, object]:
    return {
        "type": {"coding": [{
            "system": VALIDATOR.IDENTIFIER_ROLE_SYSTEM,
            "code": role,
        }]},
        "system": system,
        "value": value,
    }


class ProducerConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.example = ROOT / "Conformance/example-producer/manifest.json"

    @staticmethod
    def outcome(path: Path, issues: list[dict[str, str]]) -> dict[str, object]:
        return {
            "resourceType": "OperationOutcome",
            "extension": [{
                "url": VALIDATOR.VALIDATOR_FILE_EXTENSION,
                "valueString": str(path),
            }],
            "issue": issues,
        }

    def test_repository_example_is_structurally_valid(self) -> None:
        manifest, resources = VALIDATOR.validate_manifest(self.example)
        self.assertEqual(manifest["fhirVersion"], "4.0.1")
        self.assertEqual([path.name for path in resources], ["exchange-bundle.json"])
        self.assertEqual(manifest["semanticVectors"][0]["id"], "heart-rate")

    def test_official_manifest_validates_both_normative_exchange_bases(self) -> None:
        path = (
            ROOT
            / "Conformance/corpora/mobile-exchange/official-validator-manifest.json"
        )
        manifest, resources = VALIDATOR.validate_manifest(path)
        self.assertEqual(manifest["producer"]["version"], "0.6.0")
        self.assertEqual(
            [resource.name for resource in resources],
            ["exchange-bundle.json", "retraction-bundle.json"],
        )
        self.assertEqual(
            [resource.parent for resource in resources],
            [path.parent, path.parent],
        )

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
            VALIDATOR.selected_entry_identifier(device, "Device/test"),
            ("device-snapshot", (system, snapshot)),
        )
        self.assertEqual(
            list(VALIDATOR.IDENTIFIER_PRIORITY),
            VALIDATOR.EXCHANGE_PROTOCOL["entryIdentity"]["resourceIdentifierPriority"],
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
                VALIDATOR.validate_manifest(manifest_path)

            validate()

            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.251000000Z"
            )
            validate()
            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.250999927Z"
            )
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "not millisecond-canonical"
            ):
                validate()
            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.252Z"
            )
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "effective instant does not equal"
            ):
                validate()
            resource["entry"][2]["resource"]["effectiveDateTime"] = (
                "2026-08-20T08:30:00.251-07:00"
            )

            manifest["semanticVectors"] = []
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "missing heart-rate"
            ):
                validate()

            manifest["semanticVectors"] = [{
                "id": "heart-rate",
                "path": "resources/exchange-bundle.json",
                "resourcePointer": "/entry/2/resource",
            }]
            resource["entry"][2]["resource"]["valueQuantity"]["value"] = 73
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "clinical projection does not equal"
            ):
                validate()

            resource["entry"][2]["resource"]["valueQuantity"]["value"] = 72
            manifest["semanticVectors"][0]["resourcePointer"] = "/entry/01/resource"
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "invalid array index"
            ):
                validate()

    def test_missing_profile_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(encoding="utf-8")
        )
        resource["meta"]["profile"] = ["http://hl7.org/fhir/StructureDefinition/heartrate"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "resources/exchange-bundle.json").write_text(json.dumps(resource), encoding="utf-8")
            with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "missing required profiles"):
                VALIDATOR.validate_manifest(root / "manifest.json")

    def test_exchange_references_are_closed_over_bundle_entries(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        observation = next(
            entry["resource"] for entry in resource["entry"]
            if entry["resource"].get("resourceType") == "Observation"
        )
        observation["subject"]["reference"] = (
            "https://outside.example/fhir/Patient/123"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            (root / "resources/exchange-bundle.json").write_text(
                json.dumps(resource), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                "reference must resolve to an entry UUID URN",
            ):
                VALIDATOR.validate_manifest(root / "manifest.json")

    def test_exchange_profiles_references_entities_and_retraction_roles_fail_closed(self) -> None:
        active = json.loads(
            (ROOT / "Conformance/example-producer/resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        VALIDATOR.validate_exchange_bundle(active, "active")
        observation_index = next(
            index for index, entry in enumerate(active["entry"])
            if entry["resource"].get("resourceType") == "Observation"
        )
        provenance_index = next(
            index for index, entry in enumerate(active["entry"])
            if entry["resource"].get("resourceType") == "Provenance"
        )
        patient_url = next(
            entry["fullUrl"] for entry in active["entry"]
            if entry["resource"].get("resourceType") == "Patient"
        )
        device_url = next(
            entry["fullUrl"] for entry in active["entry"]
            if entry["resource"].get("resourceType") == "Device"
        )

        for profiles in ([], ["https://example.org/fhir/StructureDefinition/arbitrary"]):
            invalid = copy.deepcopy(active)
            invalid["entry"][observation_index]["resource"]["meta"]["profile"] = profiles
            with self.subTest(profiles=profiles), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                "active Observation must carry|admitted shared semantic profile",
            ):
                VALIDATOR.validate_exchange_bundle(invalid, "active")

        wrong_subject = copy.deepcopy(active)
        wrong_subject["entry"][observation_index]["resource"]["subject"]["reference"] = device_url
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, r"Observation\.subject must reference Patient"
        ):
            VALIDATOR.validate_exchange_bundle(wrong_subject, "active")

        false_declared_type = copy.deepcopy(active)
        false_declared_type["entry"][observation_index]["resource"]["subject"]["type"] = "Device"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "type must equal the referenced resource type Patient",
        ):
            VALIDATOR.validate_exchange_bundle(false_declared_type, "active")

        logical_subject = copy.deepcopy(active)
        logical_subject["entry"][observation_index]["resource"]["subject"] = {
            "type": "Patient",
            "identifier": {
                "system": "https://deployment.example/fhir/NamingSystem/patient-pseudonym",
                "value": "participant-42",
            },
        }
        VALIDATOR.validate_exchange_bundle(logical_subject, "active")

        untyped_logical_subject = copy.deepcopy(logical_subject)
        del untyped_logical_subject["entry"][observation_index]["resource"]["subject"]["type"]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "logical reference type must be Patient",
        ):
            VALIDATOR.validate_exchange_bundle(untyped_logical_subject, "active")

        mixed_subject = copy.deepcopy(active)
        mixed_subject["entry"][observation_index]["resource"]["subject"]["identifier"] = {
            "system": "https://deployment.example/fhir/NamingSystem/patient-pseudonym",
            "value": "participant-42",
        }
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "must not mix a resolving literal with a logical identifier",
        ):
            VALIDATOR.validate_exchange_bundle(mixed_subject, "active")

        wrong_gateway = copy.deepcopy(active)
        wrong_gateway["entry"][observation_index]["resource"]["extension"][0][
            "valueReference"
        ]["reference"] = patient_url
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            r"extension\[[0-9]+\]\.valueReference must reference Device",
        ):
            VALIDATOR.validate_exchange_bundle(wrong_gateway, "active")

        literal_source = copy.deepcopy(active)
        literal_source["entry"][provenance_index]["resource"]["entity"][0]["what"][
            "reference"
        ] = patient_url
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "source must be exactly one logical Identifier entity",
        ):
            VALIDATOR.validate_exchange_bundle(literal_source, "active")

        additional_source = copy.deepcopy(active)
        additional_source["entry"][provenance_index]["resource"]["entity"].append(
            copy.deepcopy(
                additional_source["entry"][provenance_index]["resource"]["entity"][0]
            )
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "identify exactly one source record"
        ):
            VALIDATOR.validate_exchange_bundle(additional_source, "active")

        retraction = json.loads(
            (ROOT / "Conformance/corpora/mobile-exchange/retraction-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        VALIDATOR.validate_exchange_bundle(retraction, "retraction")
        wrong_target_type = copy.deepcopy(retraction)
        wrong_target_type["entry"][0]["resource"]["target"][0]["type"] = "Device"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "role primary-output does not admit resource type Device",
        ):
            VALIDATOR.validate_exchange_bundle(wrong_target_type, "retraction")

        wrong_target_identifier_role = copy.deepcopy(retraction)
        wrong_target_identifier_role["entry"][0]["resource"]["target"][0]["identifier"][
            "type"
        ]["coding"][0]["code"] = "device-snapshot"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "role primary-output requires the source-output identifier role",
        ):
            VALIDATOR.validate_exchange_bundle(wrong_target_identifier_role, "retraction")

        retraction_literal_source = copy.deepcopy(retraction)
        retraction_provenance = retraction_literal_source["entry"][0]["resource"]
        retraction_provenance["contained"] = [{
            "resourceType": "Patient",
            "id": "forbidden-source",
        }]
        retraction_provenance["entity"][0]["what"]["reference"] = "#forbidden-source"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "contains a Resource; Mobile event graphs require addressable Bundle entries",
        ):
            VALIDATOR.validate_exchange_bundle(retraction_literal_source, "retraction")

    def test_reviewed_quantity_value_domains_accept_boundaries_and_reject_bypasses(self) -> None:
        body_fat = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-body-fat-percentage"
        )
        step_count = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-step-count"
        )
        state_of_mind = (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-state-of-mind"
        )
        for profile, values in (
            (body_fat, (0, Decimal("23.5"), 100)),
            (step_count, (0, 12)),
            (state_of_mind, (-1, 0, 1)),
        ):
            for value in values:
                VALIDATOR.validate_quantity_value_domain(
                    {"valueQuantity": {"value": value}}, "Observation/test", profile
                )
        for profile, value, message in (
            (body_fat, -0.1, "inclusive minimum 0"),
            (body_fat, 100.1, "inclusive maximum 100"),
            (step_count, -1, "inclusive minimum 0"),
            (step_count, 1.5, "must be an integer"),
            (state_of_mind, -1.1, "inclusive minimum -1"),
            (state_of_mind, 1.1, "inclusive maximum 1"),
        ):
            with self.subTest(profile=profile, value=value), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, message
            ):
                VALIDATOR.validate_quantity_value_domain(
                    {"valueQuantity": {"value": value}}, "Observation/test", profile
                )

    def test_manifest_cannot_hide_an_extra_direct_grove_profile(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        resource["meta"]["profile"].append(
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-recording-document"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            (root / "resources/exchange-bundle.json").write_text(
                json.dumps(resource), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                "requiredProfiles must equal",
            ):
                VALIDATOR.validate_manifest(root / "manifest.json")

    def test_path_traversal_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        manifest["resources"][0]["path"] = "../heart-rate.json"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "unsafe resource path"):
                VALIDATOR.validate_manifest(path)

    def test_intermediate_symlink_component_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            (outside / "resource.json").write_text("{}", encoding="utf-8")
            (root / "linked").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "symlink component"
            ):
                VALIDATOR.safe_resource_path(root, "linked/resource.json")

    def test_manifest_leaf_and_intermediate_symlinks_are_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf = root / "manifest-link.json"
            leaf.symlink_to(self.example)
            with self.subTest(kind="leaf"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "manifest path contains a symlink"
            ):
                VALIDATOR.resolve_unlinked_regular_file(leaf, "manifest")

            linked_directory = root / "linked"
            linked_directory.symlink_to(self.example.parent, target_is_directory=True)
            with self.subTest(kind="intermediate"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "manifest path contains a symlink"
            ):
                VALIDATOR.resolve_unlinked_regular_file(
                    linked_directory / "manifest.json", "manifest"
                )

    def test_package_leaf_and_intermediate_symlinks_are_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            real_directory = root / "real"
            real_directory.mkdir()
            package = real_directory / "package.tgz"
            package.write_bytes(b"package")
            leaf = root / "package-link.tgz"
            leaf.symlink_to(package)
            with self.subTest(kind="leaf"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "mobile package path contains a symlink"
            ):
                VALIDATOR.parse_package_arguments([f"mobile={leaf}"])

            linked_directory = root / "linked"
            linked_directory.symlink_to(real_directory, target_is_directory=True)
            with self.subTest(kind="intermediate"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "mobile package path contains a symlink"
            ):
                VALIDATOR.parse_package_arguments(
                    [f"mobile={linked_directory / 'package.tgz'}"]
                )

    def test_validator_leaf_and_intermediate_symlinks_are_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            real_directory = root / "real"
            real_directory.mkdir()
            validator = real_directory / "validator.jar"
            validator.write_bytes(b"jar")
            leaf = root / "validator-link.jar"
            leaf.symlink_to(validator)
            with self.subTest(kind="leaf"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "Validator JAR path contains a symlink"
            ):
                VALIDATOR.run_validator(leaf, [], [])

            linked_directory = root / "linked"
            linked_directory.symlink_to(real_directory, target_is_directory=True)
            with self.subTest(kind="intermediate"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "Validator JAR path contains a symlink"
            ):
                VALIDATOR.run_validator(linked_directory / "validator.jar", [], [])

    def test_validator_rejects_a_linked_private_fhir_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            real_home = root / "home"
            (real_home / ".fhir" / "packages").mkdir(parents=True)
            linked_home = root / "linked-home"
            linked_home.symlink_to(real_home, target_is_directory=True)
            with mock.patch.object(VALIDATOR, "FHIR_TOOL_HOME", linked_home):
                with self.assertRaisesRegex(
                    VALIDATOR.ProducerValidationError,
                    "private FHIR home path contains a symlink",
                ):
                    VALIDATOR.run_validator(validator, [], [])

    def test_duplicate_package_alias_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        manifest["packages"].append(copy.deepcopy(manifest["packages"][0]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            resource = self.example.parent / "resources/exchange-bundle.json"
            (root / "resources/exchange-bundle.json").write_bytes(resource.read_bytes())
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "must be unique"):
                VALIDATOR.validate_manifest(path)

    def test_cli_requires_official_validator_outside_structural_mode(self) -> None:
        self.assertEqual(VALIDATOR.main(["--manifest", str(self.example)]), 1)

    def test_identifier_name_composes_without_escaping(self) -> None:
        self.assertEqual(
            VALIDATOR.canonical_identifier_name('https://example.org/"quoted"', "line\nback\\slash"),
            'https://example.org/"quoted"|line\nback\\slash',
        )

    def test_full_url_framing_admits_separators_without_boundary_collisions(self) -> None:
        self.assertNotEqual(
            VALIDATOR.expected_entry_full_url("https://example.org/a:b", "x"),
            VALIDATOR.expected_entry_full_url("https://example.org/a", "b:x"),
        )

    def test_mobile_exchange_corpus_is_closed_and_reason_specific(self) -> None:
        corpus_root = ROOT / "Conformance/corpora/mobile-exchange"
        corpus = CORPUS.load_manifest(corpus_root / "corpus.json")
        self.assertEqual(CORPUS.validate_manifest(corpus), [])
        bases = CORPUS.load_bases(corpus, corpus_root / "corpus.json")
        example = json.loads(
            (ROOT / "Conformance/example-producer/resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(bases["mobile-exchange"], example)
        cases = CORPUS.build_cases(corpus, bases)
        self.assertEqual(
            set(cases),
            {case["id"] for case in corpus["cases"]},
        )
        results = {
            "schemaVersion": 1,
            "baseDiagnostics": {
                base_id: VALIDATOR.exchange_bundle_diagnostics(resource, base_id)
                for base_id, resource in bases.items()
            },
            "caseDiagnostics": {
                case_id: VALIDATOR.exchange_bundle_diagnostics(resource, case_id)
                for case_id, resource in cases.items()
            },
        }
        self.assertEqual(CORPUS.validate_results(corpus, results), [])

    def test_adapter_observation_claims_exactly_shared_plus_adapter(self) -> None:
        shared = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-heart-rate"
        )
        adapter = (
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-observation"
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [shared, adapter]},
        }
        VALIDATOR.validate_adapter_profile_claim(observation, "Observation")
        for extra in (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-observation",
            "http://hl7.org/fhir/StructureDefinition/heartrate",
        ):
            invalid = copy.deepcopy(observation)
            invalid["meta"]["profile"].append(extra)
            with self.subTest(extra=extra), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                "exactly one shared semantic profile",
            ):
                VALIDATOR.validate_adapter_profile_claim(invalid, "Observation")

        missing_shared = copy.deepcopy(observation)
        missing_shared["meta"]["profile"] = [adapter]
        with self.assertRaises(VALIDATOR.ProducerValidationError):
            VALIDATOR.validate_adapter_profile_claim(missing_shared, "Observation")

        sensor = copy.deepcopy(observation)
        sensor["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-ecg-observation"
        )
        VALIDATOR.validate_adapter_profile_claim(sensor, "Observation")

        # A producer manifest is a package capability declaration, not a claim that
        # every resource was produced by every listed adapter. Source-neutral output
        # therefore remains valid when an otherwise unused adapter package is present.
        source_neutral = {
            "resourceType": "Observation", "meta": {"profile": [shared]}
        }
        VALIDATOR.validate_adapter_profile_claim(
            source_neutral, "Observation", {adapter}
        )
        VALIDATOR.validate_active_observation_profile_claim(
            source_neutral, "Observation", {adapter}
        )
        wrong_adapter = copy.deepcopy(observation)
        wrong_adapter["meta"]["profile"][1] = (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-observation"
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exact package is absent"
        ):
            VALIDATOR.validate_adapter_profile_claim(
                wrong_adapter, "Observation", {adapter}
            )

    def test_adapter_source_markers_require_their_adapter_profile(self) -> None:
        shared = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-heart-rate"
        )
        base = {
            "resourceType": "Observation",
            "meta": {"profile": [shared]},
            "code": {"coding": []},
            "extension": [],
        }
        healthkit = copy.deepcopy(base)
        healthkit["code"]["coding"].append(
            {
                "system": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-source-type",
                "code": "HKQuantityTypeIdentifierHeartRate",
            }
        )
        health_connect = copy.deepcopy(base)
        health_connect["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type",
                "valueCode": "HeartRateRecord",
            }
        )
        provider = copy.deepcopy(base)
        provider["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                "valueCode": "withings",
            }
        )
        sensorkit = copy.deepcopy(base)
        sensorkit["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type",
                "valueCode": "accelerometer",
            }
        )
        for name, resource in (
            ("HealthKit", healthkit),
            ("Health Connect", health_connect),
            ("Provider", provider),
            ("SensorKit", sensorkit),
        ):
            with self.subTest(adapter=name), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                rf"{name} source marker without an exact {name} adapter profile",
            ):
                VALIDATOR.validate_adapter_source_marker_claim(resource, "Observation")

    def test_every_adapter_profile_requires_its_exact_manifest_package(self) -> None:
        graph = json.loads(
            (ROOT / "catalog/package-graph.json").read_text(encoding="utf-8")
        )
        expected_by_package = {
            package["packageId"]: {
                f"{package['canonical']}/StructureDefinition/{profile}"
                for profile in package["profiles"]
            }
            for package in graph["packages"]
            if package["packageId"] in VALIDATOR.ADAPTER_PACKAGE_PROFILES
        }
        self.assertEqual(VALIDATOR.ADAPTER_PACKAGE_PROFILES, expected_by_package)
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        profiles = [
            claims["healthConnectPlatformExclusiveClaims"]["profiles"][0],
            claims["sensorKitPlatformExclusiveClaims"]["profiles"][0],
            claims["sensorKitRecordingDocumentClaim"]["profiles"][1],
            claims["providerRecordingDocumentClaim"]["profiles"][1],
            *[
                claim["profile"]
                for claim in claims["adapterConversionProvenanceClaims"]
            ],
        ]
        for profile in profiles:
            resource = {"resourceType": "Basic", "meta": {"profile": [profile]}}
            with self.subTest(profile=profile), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "exact package is absent"
            ):
                VALIDATOR.validate_active_adapter_package_claims(
                    resource, "Resource", set()
                )
            VALIDATOR.validate_active_adapter_package_claims(
                resource, "Resource", {profile}
            )

    def test_conversion_claim_rules_never_encode_retraction_by_status_mutation(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        for claim in claims["adapterConversionProvenanceClaims"]:
            rule = claim["rule"]
            with self.subTest(adapter=claim["adapter"]):
                self.assertNotIn("entered-in-error", rule)
                self.assertIn("never encodes retraction by mutating output status", rule)
                self.assertIn("separate retraction Bundle", rule)
                self.assertIn("no conversion Provenance", rule)

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
                VALIDATOR.validate_active_observation_profile_claim(
                    resource, "Observation", {profile}
                )

            invalid = copy.deepcopy(resource)
            invalid["meta"]["profile"].append(
                "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                "grove-mobile-blood-glucose-unspecified-specimen"
            )
            with self.subTest(profile=profile, shape="extra"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                "admitted shared semantic profile",
            ):
                VALIDATOR.validate_active_observation_profile_claim(
                    invalid, "Observation", {profile}
                )

    def test_healthkit_child_profiles_and_multi_output_rows_are_per_resource(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        child = claims["healthKitSingleProfileObservationClaims"]["profiles"][0]
        row = next(
            item for item in catalog["rows"]
            if item["status"] == "supported" and child in item["profiles"]
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [child]},
            "code": {"coding": [{
                "system": catalog["sourceTypeCoding"]["system"],
                "code": row["sourceTypeIdentifier"],
            }]},
        }
        VALIDATOR.validate_active_observation_profile_claim(
            observation, "HealthKit child", {child}
        )
        VALIDATOR.validate_healthkit_source_type(observation, "HealthKit child")

        extra = copy.deepcopy(observation)
        extra["meta"]["profile"].append(
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-heart-rate"
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "no arbitrary direct profile"
        ):
            VALIDATOR.validate_active_observation_profile_claim(
                extra, "HealthKit child", {child}
            )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exact direct profile claims"
        ):
            VALIDATOR.validate_healthkit_source_type(extra, "HealthKit child")

        workout = next(
            item for item in catalog["rows"]
            if item["sourceTypeIdentifier"] == "HKWorkoutTypeIdentifier"
        )
        generic = VALIDATOR.HEALTHKIT_OBSERVATION_PROFILE
        for shared_profile in workout["profiles"]:
            output = {
                "resourceType": "Observation",
                "meta": {"profile": [shared_profile, generic]},
                "code": {"coding": [{
                    "system": catalog["sourceTypeCoding"]["system"],
                    "code": workout["sourceTypeIdentifier"],
                }]},
            }
            with self.subTest(profile=shared_profile):
                VALIDATOR.validate_healthkit_source_type(output, "HealthKit workout")
        combined = copy.deepcopy(output)
        combined["meta"]["profile"] = [*workout["profiles"], generic]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exact direct profile claims"
        ):
            VALIDATOR.validate_healthkit_source_type(combined, "HealthKit workout")

    def test_healthkit_native_resource_claims_and_document_provenance_are_closed(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )

        def grove(role: str, fill: str) -> dict[str, object]:
            return typed_identifier(
                role,
                f"https://example.org/fhir/NamingSystem/{role}/test-key/1",
                "v2:test-key:1:" + fill * 43,
            )

        source = grove("source-record", "A")
        clinical_profile = claims["healthKitClinicalRecordDocumentClaim"]["profiles"][0]
        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [clinical_profile]},
            "identifier": [
                copy.deepcopy(source),
                grove("source-output", "B"),
                grove("source-artifact", "C"),
            ],
        }
        VALIDATOR.validate_healthkit_resource_claims(document, "HealthKit clinical")

        extra_profile = copy.deepcopy(document)
        extra_profile["meta"]["profile"].append(VALIDATOR.SENSOR_RECORDING_PROFILE)
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "directly claim exactly"
        ):
            VALIDATOR.validate_healthkit_resource_claims(
                extra_profile, "HealthKit clinical"
            )

        healthkit_provenance = next(
            claim for claim in claims["adapterConversionProvenanceClaims"]
            if claim["adapter"] == "healthkit"
        )
        document_url = "urn:uuid:00000000-0000-5000-8000-000000000201"
        provenance_url = "urn:uuid:00000000-0000-5000-8000-000000000202"
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [healthkit_provenance["profile"]]},
            "target": [{"reference": document_url}],
            "entity": [{
                "role": "source",
                "what": {"identifier": copy.deepcopy(source)},
            }],
        }
        VALIDATOR.validate_adapter_provenance_graph(
            [document, provenance],
            {document_url: document, provenance_url: provenance},
            "HealthKit graph",
        )

    def test_adapter_only_active_output_types_reject_unprofiled_mobile_targets(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        expected = {
            claims["healthConnectSpecimenClaim"]["resourceType"]:
                claims["healthConnectSpecimenClaim"]["profile"],
            **{
                claim["resourceType"]: claim["profile"]
                for claim in claims["healthKitPlatformExclusiveResourceClaims"]
            },
        }
        for resource_type, profile in expected.items():
            with self.subTest(resource_type=resource_type, shape="unprofiled"), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "adapter-only profile"
            ):
                VALIDATOR.validate_active_adapter_only_output_profile_claim(
                    {"resourceType": resource_type}, resource_type
                )
            with self.subTest(resource_type=resource_type, shape="exact"):
                VALIDATOR.validate_active_adapter_only_output_profile_claim(
                    {"resourceType": resource_type, "meta": {"profile": [profile]}},
                    resource_type,
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
        VALIDATOR.validate_health_connect_specimen_claim(specimen, "Specimen")
        for invalid_profiles in ([profile, "http://example.org/extra"],):
            invalid = copy.deepcopy(specimen)
            invalid["meta"]["profile"] = invalid_profiles
            with self.subTest(profiles=invalid_profiles), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "must directly claim exactly"
            ):
                VALIDATOR.validate_health_connect_specimen_claim(invalid, "Specimen")
        extra_identifier = copy.deepcopy(specimen)
        extra_identifier["identifier"].append({
            "system": "https://source.example/native",
            "value": "clear-native-specimen-id",
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exactly two identifiers"
        ):
            VALIDATOR.validate_health_connect_specimen_claim(
                extra_identifier, "Specimen"
            )
        extra_snomed = copy.deepcopy(specimen)
        extra_snomed["type"]["coding"].append({
            "system": "http://snomed.info/sct",
            "code": "999999999999999999",
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exactly one admitted SNOMED"
        ):
            VALIDATOR.validate_health_connect_specimen_claim(extra_snomed, "Specimen")

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
        VALIDATOR.validate_adapter_conversion_provenance(provenance, "Provenance")
        literal_data_origin = copy.deepcopy(provenance)
        literal_data_origin["entity"][0]["agent"][0]["who"]["reference"] = (
            "urn:uuid:00000000-0000-5000-8000-000000000001"
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "identifier-only Device Reference",
        ):
            VALIDATOR.validate_adapter_conversion_provenance(
                literal_data_origin, "Provenance"
            )
        invalid_source_system = copy.deepcopy(provenance)
        invalid_source_system["entity"][0]["what"]["identifier"]["system"] = (
            "https://example.org/bad path"
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "absolute RFC 3986 URI"
        ):
            VALIDATOR.validate_adapter_conversion_provenance(
                invalid_source_system, "Provenance"
            )
        provenance["meta"]["profile"].insert(
            0,
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-conversion-provenance",
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "directly claim exactly"
        ):
            VALIDATOR.validate_adapter_conversion_provenance(provenance, "Provenance")

    def test_adapter_source_types_are_explicit_and_contract_bound(self) -> None:
        healthkit_catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )
        healthkit_row = next(
            row for row in healthkit_catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKQuantityTypeIdentifierHeartRate"
        )
        healthkit = {
            "resourceType": "Observation",
            "meta": {"profile": [
                *healthkit_row["profiles"],
                "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
                "healthkit-observation",
            ]},
            "code": {"coding": [{
                "system": healthkit_catalog["sourceTypeCoding"]["system"],
                "code": healthkit_row["sourceTypeIdentifier"],
            }]},
        }
        VALIDATOR.validate_healthkit_source_type(healthkit, "HealthKit")
        missing_healthkit = copy.deepcopy(healthkit)
        missing_healthkit["code"]["coding"] = []
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exactly one HealthKit source-type"
        ):
            VALIDATOR.validate_healthkit_source_type(missing_healthkit, "HealthKit")

        health_connect_catalog = json.loads(
            (ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8")
        )
        health_connect = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                "grove-mobile-heart-rate",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                "health-connect-observation",
            ]},
            "extension": [{
                "url": health_connect_catalog["sourceTypeExtension"]["url"],
                "valueCode": "HeartRateRecord",
            }],
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/source-record/test-key/1",
                    "v2:test-key:1:" + "A" * 43,
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                    "v2:test-key:1:" + "B" * 43,
                ),
            ],
        }
        VALIDATOR.validate_health_connect_source_type(health_connect, "HealthConnect")
        wrong_record = copy.deepcopy(health_connect)
        wrong_record["extension"][0]["valueCode"] = "StepsRecord"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "does not admit its claimed measurement"
        ):
            VALIDATOR.validate_health_connect_source_type(wrong_record, "HealthConnect")

        clear_identifier = copy.deepcopy(health_connect)
        clear_identifier["identifier"].append({
            "system": "https://source.example/native",
            "value": "clear-native-id",
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "must all use admitted Grove roles"
        ):
            VALIDATOR.validate_health_connect_source_type(
                clear_identifier, "HealthConnect"
            )

        invalid_unselected_system = copy.deepcopy(health_connect)
        invalid_unselected_system["identifier"][0]["system"] = "relative/system"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "absolute RFC 3986 URI"
        ):
            VALIDATOR.validate_health_connect_source_type(
                invalid_unselected_system, "HealthConnect"
            )

        connected_catalog = json.loads(
            (ROOT / "catalog/providers-adapter.json").read_text(encoding="utf-8")
        )
        provider_components = [
            "google-health-api",
            "heart-rate",
            "https://accounts.example.org",
            "participant-1",
            "native-1",
        ]
        source_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="provider-record", components=provider_components,
        )
        output_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-output",
            components=[
                "google-health-api", "heart-rate", "https://accounts.example.org",
                "participant-1", "native-1", "source-artifact", "native-recording",
            ],
        )
        connected = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                connected_catalog["recordingDocument"]["sourceNeutralProfile"],
                connected_catalog["recordingDocument"]["adapterProfile"],
            ]},
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/provider-record/test-key/1",
                    source_value,
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                    output_value,
                ),
            ],
            "extension": [
                {
                    "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                    "valueCode": "google-health-api",
                },
                {
                    "url": connected_catalog["sourceTypeExtension"]["url"],
                    "valueCode": "google-health-api/heart-rate",
                },
            ],
        }
        VALIDATOR.validate_provider_identity(connected, "Connected")
        cross_provider = copy.deepcopy(connected)
        cross_provider["extension"][1]["valueCode"] = "oura/heartrate"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "unknown or cross-provider"
        ):
            VALIDATOR.validate_provider_identity(cross_provider, "Connected")

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
        VALIDATOR.validate_health_connect_source_type(observation, "Menstruation")

        unknown = copy.deepcopy(observation)
        unknown["valueCodeableConcept"]["coding"][1]["code"] = "FLOW_NOT_REAL"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exactly one admitted"
        ):
            VALIDATOR.validate_health_connect_source_type(unknown, "Menstruation")

        invented_site = copy.deepcopy(observation)
        invented_site["bodySite"] = {"coding": [{
            "system": "https://example.org/bogus",
            "code": "not-a-location",
        }]}
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "does not admit Health Connect body site"
        ):
            VALIDATOR.validate_health_connect_source_type(
                invented_site, "Menstruation"
            )

        invented_note = copy.deepcopy(observation)
        invented_note["note"] = [{"text": "not a source field"}]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "does not admit source-authored notes"
        ):
            VALIDATOR.validate_health_connect_source_type(
                invented_note, "Menstruation"
            )

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
            VALIDATOR.ProducerValidationError, "does not admit.*meal context"
        ):
            VALIDATOR.validate_health_connect_source_type(meal_context, "Menstruation")

        mindfulness_context = copy.deepcopy(observation)
        mindfulness_context["extension"].append({
            "url": catalog["contextMappings"]["mindfulnessSessionType"]["extension"],
            "valueCoding": {
                "system": catalog["contextMappings"]["mindfulnessSessionType"]
                ["codeSystem"],
                "code": "MINDFULNESS_SESSION_TYPE_MEDITATION",
            },
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "mindfulness session type exactly"
        ):
            VALIDATOR.validate_health_connect_source_type(
                mindfulness_context, "Menstruation"
            )

        vo2_method = copy.deepcopy(observation)
        vo2_method["method"] = {"coding": [{
            "system": catalog["contextMappings"]["vo2MaxMeasurementMethod"]
            ["codeSystem"],
            "code": "MEASUREMENT_METHOD_COOPER_TEST",
        }]}
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "VO2 method outside"
        ):
            VALIDATOR.validate_health_connect_source_type(vo2_method, "Menstruation")

        mindfulness = copy.deepcopy(observation)
        mindfulness["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-mindfulness-session"
        )
        mindfulness["extension"][0]["valueCode"] = "MindfulnessSessionRecord"
        mindfulness["valueCodeableConcept"] = None
        mindfulness["extension"].append({
            "url": catalog["contextMappings"]["mindfulnessSessionType"]["extension"],
            "valueCoding": {
                "system": catalog["contextMappings"]["mindfulnessSessionType"]
                ["codeSystem"],
                "code": "MINDFULNESS_SESSION_TYPE_NOT_REAL",
            },
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exactly one admitted"
        ):
            VALIDATOR.validate_health_connect_source_type(mindfulness, "Mindfulness")

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
        VALIDATOR.validate_health_connect_output_graph(
            [height], {height_url: height}, "HealthConnect"
        )

        duplicate = observation("HeightRecord", "grove-mobile-body-height", "G")
        duplicate_url = "urn:uuid:00000000-0000-5000-8000-000000000102"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "must emit exactly one body-height"
        ):
            VALIDATOR.validate_health_connect_output_graph(
                [height, duplicate],
                {height_url: height, duplicate_url: duplicate},
                "HealthConnect",
            )

        weight = observation("WeightRecord", "grove-mobile-body-weight", "H")
        weight_url = "urn:uuid:00000000-0000-5000-8000-000000000103"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "cannot name multiple Record types"
        ):
            VALIDATOR.validate_health_connect_output_graph(
                [height, weight],
                {height_url: height, weight_url: weight},
                "HealthConnect",
            )

    def test_sensorkit_specific_and_recording_claims_are_exact(self) -> None:
        provider_profile = (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-on-wrist-observation"
        )
        provider = {
            "resourceType": "Observation",
            "meta": {"profile": [provider_profile]},
        }
        VALIDATOR.validate_sensorkit_profile_claim(provider, "Observation")
        invalid_provider = copy.deepcopy(provider)
        invalid_provider["meta"]["profile"].append(
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-observation"
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "directly claim exactly one"
        ):
            VALIDATOR.validate_sensorkit_profile_claim(
                invalid_provider, "Observation"
            )

        document_profiles = [
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-recording-document",
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-recording-document",
        ]
        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": document_profiles},
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/source-record/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-record",
                        components=["sensorkit", "rotation-rate", "scope", "one", "record"],
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
                        components=[
                            "sensorkit", "rotation-rate", "scope", "one", "record",
                            "source-artifact", "native-recording",
                        ],
                    ),
                ),
                typed_identifier(
                    "source-artifact",
                    "https://example.org/fhir/NamingSystem/source-artifact/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-artifact",
                        components=[
                            "sensorkit", "rotation-rate", "scope", "one", "record",
                            "native-recording", "0",
                        ],
                    ),
                ),
            ],
        }
        VALIDATOR.validate_sensorkit_profile_claim(document, "DocumentReference")
        invalid_document = copy.deepcopy(document)
        invalid_document["meta"]["profile"] = document_profiles[1:]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "directly claim exactly"
        ):
            VALIDATOR.validate_sensorkit_profile_claim(
                invalid_document, "DocumentReference"
            )

    def test_healthkit_ecg_contract_fails_closed_on_incomplete_evidence(self) -> None:
        extension_root = (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
        )
        ecg = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-ecg-observation",
                extension_root + "healthkit-ecg-observation",
            ]},
            "code": {"coding": [{
                "system": (
                    "https://grovealliance.org/fhir/healthkit/CodeSystem/"
                    "healthkit-source-type"
                ),
                "code": "HKDataTypeIdentifierElectrocardiogram",
            }]},
            "effectivePeriod": {
                "start": "2026-08-20T09:00:00.002000001Z",
                "end": "2026-08-20T09:00:00.006000001Z",
            },
            "extension": [
                {
                    "url": extension_root + "healthkit-ecg-classification",
                    "valueCode": "sinusRhythm",
                },
                {
                    "url": extension_root + "healthkit-ecg-symptoms-status",
                    "valueCode": "none",
                },
                {
                    "url": extension_root + "healthkit-ecg-sampling-frequency",
                    "valueQuantity": {
                        "value": 500,
                        "system": "http://unitsofmeasure.org",
                        "code": "Hz",
                    },
                },
                {
                    "url": extension_root + "healthkit-ecg-voltage-measurement-count",
                    "valueInteger": 3,
                },
                {
                    "url": extension_root + "healthkit-ecg-source-period",
                    "valuePeriod": {
                        "start": "2026-08-20T09:00:00.000000001Z",
                        "end": "2026-08-20T09:00:00.010000001Z",
                    },
                },
            ],
            "component": [{
                "code": {"coding": [{
                    "system": "urn:iso:std:iso:11073:10101",
                    "code": "131329",
                }]},
                "valueSampledData": {
                    "origin": {
                        "value": 0,
                        "system": "http://unitsofmeasure.org",
                        "code": "mV",
                    },
                    "period": 2,
                    "dimensions": 1,
                    "data": "0.01 0.02 0.03",
                },
            }],
        }
        VALIDATOR.validate_resource_profile_claims(ecg, "HealthKit ECG")

        symptom_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        symptom_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-record",
            components=[
                "healthkit", "HKCategoryTypeIdentifierDizziness",
                "https://example.org/healthkit-store", "default",
                "ad32cfc5-025a-493e-bc1b-85378817ac1c",
            ],
        )
        second_symptom_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-record",
            components=[
                "healthkit", "HKCategoryTypeIdentifierDizziness",
                "https://example.org/healthkit-store", "default",
                "bd32cfc5-025a-493e-bc1b-85378817ac1c",
            ],
        )
        symptom_children = [
            {
                "url": "sourceIdentifier",
                "valueIdentifier": typed_identifier(
                    "source-record", symptom_system, symptom_value
                ),
            },
            {
                "url": "effectivePeriod",
                "valuePeriod": {
                    "start": "2026-08-20T08:59:00Z",
                    "end": "2026-08-20T08:59:30Z",
                },
            },
            {"url": "symptomType", "valueCode": "HKCategoryTypeIdentifierDizziness"},
            {"url": "severity", "valueCode": "mild"},
            {"url": "sourceName", "valueString": "Grove Health"},
            {
                "url": "sourceBundleIdentifier",
                "valueString": "org.grovealliance.health",
            },
            {"url": "sourceVersion", "valueString": "2.0.0"},
            {"url": "sourceProductType", "valueString": "Watch6,4"},
            {"url": "sourceOperatingSystemMajorVersion", "valueInteger": 12},
            {"url": "sourceOperatingSystemMinorVersion", "valueInteger": 0},
            {"url": "sourceOperatingSystemPatchVersion", "valueInteger": 1},
        ]
        with_symptom = copy.deepcopy(ecg)
        with_symptom["extension"][1]["valueCode"] = "present"
        with_symptom["extension"].append({
            "url": extension_root + "healthkit-ecg-correlated-symptom",
            "extension": symptom_children,
        })
        VALIDATOR.validate_resource_profile_claims(with_symptom, "HealthKit ECG")
        same_type_distinct_sample = copy.deepcopy(with_symptom)
        second = copy.deepcopy(same_type_distinct_sample["extension"][-1])
        second["extension"][0]["valueIdentifier"]["value"] = second_symptom_value
        same_type_distinct_sample["extension"].append(second)
        VALIDATOR.validate_resource_profile_claims(
            same_type_distinct_sample, "HealthKit ECG"
        )

        mutations = []
        count_mismatch = copy.deepcopy(ecg)
        count_mismatch["extension"][3]["valueInteger"] = 2
        mutations.append((count_mismatch, "count does not match"))
        frequency_mismatch = copy.deepcopy(ecg)
        frequency_mismatch["extension"][2]["valueQuantity"]["value"] = 400
        mutations.append((frequency_mismatch, "frequency and SampledData.period disagree"))
        missing_source_period = copy.deepcopy(ecg)
        missing_source_period["extension"] = missing_source_period["extension"][:-1]
        mutations.append((missing_source_period, "exactly one sourcePeriod"))
        missing_symptom_evidence = copy.deepcopy(ecg)
        missing_symptom_evidence["extension"][1]["valueCode"] = "present"
        mutations.append((missing_symptom_evidence, "must agree with symptomsStatus"))
        outside_source_period = copy.deepcopy(ecg)
        outside_source_period["extension"][4]["valuePeriod"]["end"] = (
            "2026-08-20T09:00:00.005000001Z"
        )
        mutations.append((outside_source_period, "must lie within"))
        missing_source_revision = copy.deepcopy(with_symptom)
        missing_source_revision["extension"][-1]["extension"] = (
            missing_source_revision["extension"][-1]["extension"][:-1]
        )
        mutations.append((missing_source_revision, "incomplete"))
        repeated_symptom_uuid = copy.deepcopy(same_type_distinct_sample)
        repeated_symptom_uuid["extension"][-1]["extension"][0]["valueIdentifier"]["value"] = symptom_value
        mutations.append((repeated_symptom_uuid, "invalid or repeated source identity"))
        for invalid, diagnostic in mutations:
            with self.subTest(diagnostic=diagnostic), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, diagnostic
            ):
                VALIDATOR.validate_resource_profile_claims(invalid, "HealthKit ECG")

    def test_sensorkit_ecg_structured_projection_is_exact(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        source_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        output_system = "https://example.org/fhir/NamingSystem/source-output/test-key/1"
        components = [
            "sensorkit", "ecg", "https://example.org/repository", "default",
            "2fea27a0-5575-4fd2-83d7-d46b03059ddc",
        ]
        source_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-record", components=components,
        )
        output_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-output",
            components=[*components, "waveform", "0"],
        )
        ecg = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-ecg-observation",
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-ecg-observation",
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, output_value),
            ],
            "extension": [
                {
                    "url": (
                        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                        "sensorkit-source-type"
                    ),
                    "valueCode": "ecg",
                },
                {
                    "url": (
                        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                        "sensorkit-ecg-session-guidance"
                    ),
                    "valueCode": "guided",
                },
            ],
            "effectivePeriod": {
                "start": "2026-08-20T09:10:00Z",
                "end": "2026-08-20T09:10:00.012Z",
            },
            "component": [{
                "code": {"coding": [
                    {
                        "system": "urn:iso:std:iso:11073:10101",
                        "code": "131329",
                    },
                    {
                        "system": (
                            "https://grovealliance.org/fhir/sensorkit/CodeSystem/"
                            "sensorkit-ecg-lead"
                        ),
                        "code": "leftArmMinusRightArm",
                    },
                ]},
                "valueSampledData": {
                    "origin": {
                        "value": 0,
                        "system": "http://unitsofmeasure.org",
                        "code": "mV",
                    },
                    "period": 4,
                    "dimensions": 1,
                    "data": "0.01 0.02 0.03 0.04",
                },
            }],
        }
        VALIDATOR.validate_resource_profile_claims(ecg, "SensorKit ECG")

        missing_guidance = copy.deepcopy(ecg)
        missing_guidance["extension"] = missing_guidance["extension"][:1]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "session guidance"
        ):
            VALIDATOR.validate_resource_profile_claims(
                missing_guidance, "SensorKit ECG"
            )
        left_without_standard_lead = copy.deepcopy(ecg)
        left_without_standard_lead["component"][0]["code"]["coding"] = (
            left_without_standard_lead["component"][0]["code"]["coding"][1:]
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "orientation and standard Lead-I"
        ):
            VALIDATOR.validate_resource_profile_claims(
                left_without_standard_lead, "SensorKit ECG"
            )
        inverse_lead = copy.deepcopy(ecg)
        inverse_lead["component"][0]["code"]["coding"] = [
            {
                "system": (
                    "https://grovealliance.org/fhir/sensorkit/CodeSystem/"
                    "sensorkit-ecg-lead"
                ),
                "code": "rightArmMinusLeftArm",
            }
        ]
        VALIDATOR.validate_resource_profile_claims(
            inverse_lead, "SensorKit inverse-lead ECG"
        )
        inverse_with_false_lead_i = copy.deepcopy(ecg)
        inverse_with_false_lead_i["component"][0]["code"]["coding"][1]["code"] = (
            "rightArmMinusLeftArm"
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "orientation and standard Lead-I"
        ):
            VALIDATOR.validate_resource_profile_claims(
                inverse_with_false_lead_i, "SensorKit ECG"
            )

    def test_sensor_recording_allows_writer_and_open_untyped_identifiers_only(self) -> None:
        def grove(role: str, fill: str) -> dict[str, object]:
            return typed_identifier(
                role,
                f"https://example.org/fhir/NamingSystem/{role}/test-key/1",
                "v2:test-key:1:" + fill * 43,
            )

        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [VALIDATOR.SENSOR_RECORDING_PROFILE]},
            "identifier": [
                grove("source-record", "A"),
                grove("source-output", "B"),
                grove("source-artifact", "C"),
                grove("writer-record", "D"),
                {
                    "system": "https://example.org/fhir/identifiers/local-accession",
                    "value": "local-1",
                },
            ],
            "content": [{
                "attachment": {
                    "contentType": "application/vnd.grovealliance.native+json",
                    "data": "e30=",
                    "size": 2,
                    "hash": "vyGp6PvFo4RvsFtPoIWeCReyIC8=",
                }
            }],
        }
        VALIDATOR.validate_sensor_contract(document, "DocumentReference/test")

        unexpected = copy.deepcopy(document)
        unexpected["identifier"].append(grove("source-context", "E"))
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "unexpected=\\['source-context'\\]"
        ):
            VALIDATOR.validate_sensor_contract(
                unexpected, "DocumentReference/test"
            )

    def test_sensorkit_device_usage_graph_requires_linked_native_recording(self) -> None:
        key = bytes(range(32))
        source_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        output_system = "https://example.org/fhir/NamingSystem/source-output/test-key/1"
        artifact_system = "https://example.org/fhir/NamingSystem/source-artifact/test-key/1"
        event_system = "https://example.org/fhir/NamingSystem/event"
        node_system = "https://example.org/fhir/NamingSystem/entry-node"
        components = [
            "sensorkit",
            "device-usage",
            "https://example.org/fhir/NamingSystem/source-repository",
            "default",
            "b4df30d0-2a34-492e-a68e-b1eab1cb471d",
        ]
        source_value = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-record",
            components=components,
        )
        observation_output = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-output",
            components=[*components, "summary", "0"],
        )
        document_output = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-output",
            components=[*components, "source-artifact", "native-recording"],
        )
        artifact_value = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-artifact",
            components=[*components, "native-recording", "0"],
        )

        def typed_identifier(role: str, system: str, value: str) -> dict[str, object]:
            return {
                "type": {"coding": [{
                    "system": VALIDATOR.IDENTIFIER_ROLE_SYSTEM,
                    "code": role,
                }]},
                "system": system,
                "value": value,
            }

        source_type_url = (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-source-type"
        )
        observation_url = VALIDATOR.expected_entry_full_url(output_system, observation_output)
        document_url = VALIDATOR.expected_entry_full_url(output_system, document_output)
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-device-usage-observation"
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, observation_output),
            ],
            "extension": [{"url": source_type_url, "valueCode": "device-usage"}],
            "derivedFrom": [{"reference": document_url}],
        }
        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-recording-document",
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-recording-document",
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, document_output),
                typed_identifier("source-artifact", artifact_system, artifact_value),
            ],
            "extension": [{"url": source_type_url, "valueCode": "device-usage"}],
            "content": [{
                "attachment": {
                    "contentType": "application/vnd.grovealliance.native+json",
                    "data": "e30=",
                    "size": 2,
                    "hash": "vyGp6PvFo4RvsFtPoIWeCReyIC8=",
                },
                "format": {
                    "system": "https://grovealliance.org/fhir/sensor/CodeSystem/grove-recording-format",
                    "code": "native-recording",
                    "version": VALIDATOR.RELEASE_VERSION,
                },
            }],
            "context": {"related": [{
                "reference": observation_url
            }]},
        }

        event_value = event_identity("1f5c58aa-6ec6-4e79-a682-829a9debd3f5", 9)
        provenance_entry_value = entry_node_identity(
            event_system=event_system,
            event_value=event_value,
            role="conversion-provenance",
            ordinal=0,
        )
        provenance_url = VALIDATOR.expected_entry_full_url(
            node_system, provenance_entry_value
        )
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-conversion-provenance"
            ]},
            "target": [
                {"reference": observation_url},
                {"reference": document_url},
            ],
            "occurredDateTime": "2026-08-20T08:00:00Z",
            "recorded": "2026-08-20T08:00:01Z",
            "activity": {"coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle",
                "code": "transform",
            }]},
            "entity": [{
                "role": "source",
                "what": {"identifier": typed_identifier(
                    "source-record", source_system, source_value
                )},
            }],
        }

        def entry(
            resource: dict[str, object], output: str, role: str, system: str
        ) -> dict[str, object]:
            return {
                "extension": [{
                    "url": VALIDATOR.ENTRY_IDENTIFIER_EXTENSION,
                    "valueIdentifier": typed_identifier(role, system, output),
                }],
                "fullUrl": VALIDATOR.expected_entry_full_url(system, output),
                "resource": resource,
            }

        bundle = {
            "resourceType": "Bundle",
            "meta": {"profile": [VALIDATOR.EXCHANGE_BUNDLE_PROFILE]},
            "identifier": typed_identifier("event", event_system, event_value),
            "type": "collection",
            "timestamp": "2026-08-20T08:00:01Z",
            "entry": [
                entry(observation, observation_output, "source-output", output_system),
                entry(document, document_output, "source-output", output_system),
                entry(provenance, provenance_entry_value, "entry-node", node_system),
            ],
        }
        VALIDATOR.validate_exchange_bundle(bundle, "Bundle")

        duplicate_transform_system = copy.deepcopy(bundle)
        duplicate_transform_system["entry"][2]["resource"]["activity"]["coding"].append({
            "system": "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle",
            "code": "amend",
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "exactly one coding across the ISO transform and Grove retraction lifecycle systems",
        ):
            VALIDATOR.validate_exchange_bundle(duplicate_transform_system, "Bundle")

        contradictory_lifecycle = copy.deepcopy(bundle)
        contradictory_lifecycle["entry"][2]["resource"]["activity"]["coding"].append({
            "system": VALIDATOR.LIFECYCLE_EVENT_SYSTEM,
            "code": VALIDATOR.SOURCE_RECORD_RETRACTED,
        })
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "exactly one coding across the ISO transform and Grove retraction lifecycle systems",
        ):
            VALIDATOR.validate_exchange_bundle(contradictory_lifecycle, "Bundle")

        translated_lifecycle = copy.deepcopy(bundle)
        translated_lifecycle["entry"][2]["resource"]["activity"]["coding"].append({
            "system": "https://study.example.org/fhir/CodeSystem/lifecycle-translation",
            "code": "converted",
        })
        VALIDATOR.validate_exchange_bundle(translated_lifecycle, "Bundle")

        missing_raw_target = copy.deepcopy(bundle)
        missing_raw_target["entry"][2]["resource"]["target"] = [
            missing_raw_target["entry"][2]["resource"]["target"][0]
        ]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "target every and only source-derived output|target every structured and raw output",
        ):
            VALIDATOR.validate_exchange_bundle(missing_raw_target, "Bundle")

        missing_document = copy.deepcopy(bundle)
        missing_document["entry"] = missing_document["entry"][:1]
        with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError,
                "exactly one transform Provenance|reference must resolve to an entry UUID URN|same Bundle",
        ):
            VALIDATOR.validate_exchange_bundle(missing_document, "Bundle")

        mismatched_identity = copy.deepcopy(bundle)
        other_source = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-record",
            components=[*components[:-1], "95ee78bd-a754-4d3d-b084-6031b42d666c"],
        )
        mismatched_identity["entry"][1]["resource"]["identifier"][0]["value"] = other_source
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "exactly one source record|same source-record [Ii]dentifier"
        ):
            VALIDATOR.validate_exchange_bundle(mismatched_identity, "Bundle")

        wrong_provenance_source = copy.deepcopy(bundle)
        wrong_provenance_source["entry"][2]["resource"]["entity"][0]["what"][
            "identifier"
        ]["value"] = other_source
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "source must equal|exactly one conversion Provenance|no output for its source record",
        ):
            VALIDATOR.validate_exchange_bundle(wrong_provenance_source, "Bundle")

    def test_sampled_data_timing_and_numeric_frames_fail_closed(self) -> None:
        sampled = {
            "origin": {"value": 0, "system": "http://unitsofmeasure.org", "code": "1"},
            "period": 10,
            "dimensions": 3,
            "data": "1 2 3 4 5 6 7 8 9",
        }
        effective = {
            "start": "2026-08-20T10:30:00Z",
            "end": "2026-08-20T10:30:00.020Z",
        }
        VALIDATOR.validate_sampled_data(sampled, effective, "SampledData")

        precise = copy.deepcopy(sampled)
        precise.update({
            "period": VALIDATOR.Decimal("0.000001"),
            "dimensions": 1,
            "data": "1 2",
        })
        VALIDATOR.validate_sampled_data(
            precise,
            {
                "start": "2026-08-20T10:30:00.123456789Z",
                "end": "2026-08-20T10:30:00.123456790Z",
            },
            "HighPrecisionSampledData",
        )

        mutations = [
            ({"period": 0}, "greater than zero"),
            ({"dimensions": 0}, "positive integer"),
            ({"data": "1 2 E"}, "decimal values"),
            ({"data": "1 2 3 4"}, "divisible by dimensions"),
            ({"data": "1 2 3"}, "at least two complete"),
        ]
        for replacement, reason in mutations:
            invalid = copy.deepcopy(sampled)
            invalid.update(replacement)
            with self.subTest(replacement=replacement), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, reason
            ):
                VALIDATOR.validate_sampled_data(invalid, effective, "SampledData")

        wrong_end = copy.deepcopy(effective)
        wrong_end["end"] = "2026-08-20T10:30:00.030Z"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "effectivePeriod.end"
        ):
            VALIDATOR.validate_sampled_data(sampled, wrong_end, "SampledData")

        scaled = copy.deepcopy(sampled)
        scaled["factor"] = 0.5
        with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "factor"):
            VALIDATOR.validate_sampled_data(scaled, effective, "SampledData")

    def test_recording_attachment_requires_exact_size_and_sha1(self) -> None:
        attachment = {
            "data": "AQID",
            "size": 3,
            "hash": "cDeAcZjCKn0rCAc3HXY3eahP388=",
        }
        VALIDATOR.validate_recording_attachment(attachment, "Attachment")

        for field in ("size", "hash"):
            invalid = copy.deepcopy(attachment)
            del invalid[field]
            with self.subTest(field=field), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, field
            ):
                VALIDATOR.validate_recording_attachment(invalid, "Attachment")

        changed = copy.deepcopy(attachment)
        changed["data"] = "AQIE"
        with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "hash does not match"):
            VALIDATOR.validate_recording_attachment(changed, "Attachment")

        url_only = {
            "url": "https://recordings.example.org/version/one.bin",
            "size": 3,
            "hash": "cDeAcZjCKn0rCAc3HXY3eahP388=",
        }
        VALIDATOR.validate_recording_attachment(url_only, "Attachment")
        del url_only["hash"]
        with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "hash is required"):
            VALIDATOR.validate_recording_attachment(url_only, "Attachment")

    def test_validator_runs_one_offline_batch_and_parses_attributed_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resources = [root / "one.json", root / "two.json"]
            for resource in resources:
                resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")
            commands: list[list[str]] = []

            def successful_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                commands.append(command)
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps({
                    "resourceType": "Bundle",
                    "type": "collection",
                    "entry": [
                        {"resource": self.outcome(resource, [
                            {"severity": "information", "code": "informational"}
                        ])}
                        for resource in sorted(resources)
                    ],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="validated")

            with mock.patch.object(VALIDATOR.subprocess, "run", side_effect=successful_run):
                VALIDATOR.run_validator(
                    validator, [], resources, allow_example_urls=True
                )

            self.assertEqual(len(commands), 1)
            command = commands[0]
            self.assertIn(["-version", "4.0.1"], [command[index:index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-tx", "n/a"], [command[index:index + 2] for index in range(len(command) - 1)])
            self.assertIn("-no-http-access", command)
            self.assertIn(
                ["-allow-example-urls", "true"],
                [command[index:index + 2] for index in range(len(command) - 1)],
            )
            self.assertIn(f"-Duser.home={VALIDATOR.FHIR_TOOL_HOME}", command)
            self.assertEqual(command[-2:], [str(resource) for resource in sorted(resources)])

    def test_validator_error_in_any_produced_outcome_fails_even_with_zero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resource = root / "resource.json"
            resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def error_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps(self.outcome(resource, [
                    {"severity": "error", "code": "invalid", "diagnostics": "bad unit"}
                ])), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="")

            with mock.patch.object(
                VALIDATOR.subprocess, "run", side_effect=error_run
            ) as run:
                with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "bad unit"):
                    VALIDATOR.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 1)

    def test_validator_process_and_output_failures_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resource = root / "resource.json"
            resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def nonzero_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps(self.outcome(resource, [
                    {"severity": "information", "code": "informational"}
                ])), encoding="utf-8")
                return subprocess.CompletedProcess(command, 2, stdout="failed")

            with mock.patch.object(
                VALIDATOR.subprocess, "run", side_effect=nonzero_run
            ) as run:
                with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "process failed"):
                    VALIDATOR.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 2)

            with mock.patch.object(
                VALIDATOR.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout="no output " + "x" * 5000
                ),
            ) as run:
                with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "no trustworthy"):
                    VALIDATOR.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 2)

            with mock.patch.object(
                VALIDATOR.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["java"],
                    timeout=VALIDATOR.VALIDATOR_TIMEOUT_SECONDS,
                    output=b"partial validator log",
                ),
            ) as run:
                with self.assertRaisesRegex(
                    VALIDATOR.ProducerValidationError, "timed out after 180 seconds"
                ):
                    VALIDATOR.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 2)

    def test_validator_retries_wrong_batch_shape_once_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resources = [root / "one.json", root / "two.json"]
            for resource in resources:
                resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def wrong_count(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps({
                    "resourceType": "Bundle",
                    "type": "collection",
                    "entry": [{"resource": self.outcome(resources[0], [
                        {"severity": "information", "code": "informational"}
                    ])}],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="wrong count")

            with mock.patch.object(
                VALIDATOR.subprocess, "run", side_effect=wrong_count
            ) as run:
                with self.assertRaisesRegex(
                    VALIDATOR.ProducerValidationError, "output count does not match"
                ):
                    VALIDATOR.run_validator(validator, [], resources)
                self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
