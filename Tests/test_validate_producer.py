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
from pathlib import Path
from unittest import mock

from Scripts import fhir_fixture_corpus as CORPUS


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_producer", ROOT / "Scripts/validate-producer.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


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

            resource["entry"][1]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.251000000Z"
            )
            validate()
            resource["entry"][1]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.250999927Z"
            )
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "not millisecond-canonical"
            ):
                validate()
            resource["entry"][1]["resource"]["effectiveDateTime"] = (
                "2026-08-20T15:30:00.252Z"
            )
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "effective instant does not equal"
            ):
                validate()
            resource["entry"][1]["resource"]["effectiveDateTime"] = (
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
                "resourcePointer": "/entry/1/resource",
            }]
            resource["entry"][1]["resource"]["valueQuantity"]["value"] = 73
            with self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "clinical projection does not equal"
            ):
                validate()

            resource["entry"][1]["resource"]["valueQuantity"]["value"] = 72
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

    def test_identifier_canonicalization_uses_jcs_string_escaping(self) -> None:
        self.assertEqual(
            VALIDATOR.canonical_identifier_name('https://example.org/"quoted"', "line\nback\\slash\u0001"),
            '["https://example.org/\\"quoted\\"","line\\nback\\\\slash\\u0001"]',
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
            {
                "missing-entry-identifier",
                "non-deterministic-full-url",
                "unresolved-internal-reference",
                "wrong-heart-rate-unit",
            },
        )
        for case_id in (
            "missing-entry-identifier",
            "non-deterministic-full-url",
            "unresolved-internal-reference",
        ):
            with self.subTest(case=case_id), self.assertRaises(
                VALIDATOR.ProducerValidationError
            ):
                VALIDATOR.validate_exchange_bundle(cases[case_id], case_id)
        VALIDATOR.validate_exchange_bundle(
            cases["wrong-heart-rate-unit"], "wrong-heart-rate-unit"
        )

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

        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "missing the applicable adapter"
        ):
            VALIDATOR.validate_adapter_profile_claim(
                {"resourceType": "Observation", "meta": {"profile": [shared]}},
                "Observation",
                {adapter},
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

    def test_health_connect_specimen_claim_is_explicit_and_exact(self) -> None:
        profile = (
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-specimen"
        )
        specimen = {
            "resourceType": "Specimen",
            "meta": {"profile": [profile]},
            "identifier": [{
                "system": (
                    "https://grovealliance.org/fhir/health-connect/NamingSystem/"
                    "health-connect-specimen-id"
                ),
                "value": "v1:" + "0" * 64,
            }],
        }
        VALIDATOR.validate_health_connect_specimen_claim(specimen, "Specimen")
        for invalid_profiles in ([], [profile, "http://example.org/extra"]):
            invalid = copy.deepcopy(specimen)
            invalid["meta"]["profile"] = invalid_profiles
            with self.subTest(profiles=invalid_profiles), self.assertRaisesRegex(
                VALIDATOR.ProducerValidationError, "must directly claim exactly"
            ):
                VALIDATOR.validate_health_connect_specimen_claim(invalid, "Specimen")

    def test_health_connect_conversion_provenance_claim_is_child_only(self) -> None:
        profile = (
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-conversion-provenance"
        )
        source_system = (
            "https://grovealliance.org/fhir/health-connect/NamingSystem/"
            "health-connect-record-id"
        )
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [profile]},
            "target": [{"reference": "urn:uuid:00000000-0000-5000-8000-000000000000"}],
            "entity": [{
                "role": "source",
                "what": {"identifier": {"system": source_system, "value": "v1:" + "0" * 64}},
            }],
        }
        VALIDATOR.validate_adapter_conversion_provenance(provenance, "Provenance")
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
        }
        VALIDATOR.validate_health_connect_source_type(health_connect, "HealthConnect")
        wrong_record = copy.deepcopy(health_connect)
        wrong_record["extension"][0]["valueCode"] = "StepsRecord"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "does not admit its claimed measurement"
        ):
            VALIDATOR.validate_health_connect_source_type(wrong_record, "HealthConnect")

        connected_catalog = json.loads(
            (ROOT / "catalog/providers-adapter.json").read_text(encoding="utf-8")
        )
        source_vector = next(
            vector for vector in connected_catalog["identity"]["vectors"]
            if vector["role"] == "sourceRecord" and vector["inputs"][3] == "heart-rate"
        )
        output_vector = next(
            vector for vector in connected_catalog["identity"]["vectors"]
            if vector["role"] == "output" and vector["inputs"][-1] == "native-recording"
        )
        connected = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                connected_catalog["recordingDocument"]["sourceNeutralProfile"],
                connected_catalog["recordingDocument"]["adapterProfile"],
            ]},
            "identifier": [
                {
                    "system": connected_catalog["identity"]["sourceRecord"]["system"],
                    "value": source_vector["identifierValue"],
                },
                {
                    "system": connected_catalog["identity"]["output"]["system"],
                    "value": output_vector["identifierValue"],
                },
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
            "identifier": [{
                "system": (
                    "https://grovealliance.org/fhir/sensorkit/NamingSystem/"
                    "sensorkit-record-id"
                ),
                "value": "879d9ea2-21cb-4527-b59b-2831dc4c84ab",
            }],
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

        symptom_children = [
            {
                "url": "sourceIdentifier",
                "valueIdentifier": {
                    "system": (
                        "https://grovealliance.org/fhir/healthkit/NamingSystem/"
                        "healthkit-object-id"
                    ),
                    "value": "ad32cfc5-025a-493e-bc1b-85378817ac1c",
                },
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
        second["extension"][0]["valueIdentifier"]["value"] = (
            "bd32cfc5-025a-493e-bc1b-85378817ac1c"
        )
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
        repeated_symptom_uuid["extension"][-1]["extension"][0]["valueIdentifier"]["value"] = (
            "ad32cfc5-025a-493e-bc1b-85378817ac1c"
        )
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
        source_system = catalog["identity"]["sourceRecord"]["system"]
        output_system = catalog["identity"]["output"]["system"]
        source_value = "2fea27a0-5575-4fd2-83d7-d46b03059ddc"
        preimage = VALIDATOR.canonical_string_array(
            [source_system, source_value, "ecg-waveform"]
        )
        output_value = str(VALIDATOR.uuid.uuid5(
            VALIDATOR.uuid.UUID(catalog["identity"]["output"]["namespace"]),
            preimage,
        ))
        ecg = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-ecg-observation",
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-ecg-observation",
            ]},
            "identifier": [
                {"system": source_system, "value": source_value},
                {"system": output_system, "value": output_value},
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

    def test_sensorkit_device_usage_graph_requires_linked_native_recording(self) -> None:
        source_system = (
            "https://grovealliance.org/fhir/sensorkit/NamingSystem/"
            "sensorkit-record-id"
        )
        output_system = (
            "https://grovealliance.org/fhir/sensorkit/NamingSystem/"
            "sensorkit-output-id"
        )
        source_value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"
        source_type_url = (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-source-type"
        )
        observation_output = "6e7453a7-0045-5f96-a847-5a956a817dd4"
        document_output = "d42f2915-17ba-5891-a068-9a6a9d6732b6"
        document_url = VALIDATOR.expected_entry_full_url(
            output_system, document_output
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-device-usage-observation"
            ]},
            "identifier": [
                {"system": source_system, "value": source_value},
                {"system": output_system, "value": observation_output},
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
                {"system": source_system, "value": source_value},
                {"system": output_system, "value": document_output},
            ],
            "extension": [{"url": source_type_url, "valueCode": "device-usage"}],
            "content": [{
                "attachment": {
                    "data": "AQID",
                    "size": 3,
                    "hash": "cDeAcZjCKn0rCAc3HXY3eahP388=",
                }
            }],
            "context": {"related": [{
                "reference": VALIDATOR.expected_entry_full_url(
                    output_system, observation_output
                )
            }]},
        }

        provenance_entry_system = "https://example.org/fhir/identifiers/conversion"
        provenance_entry_value = "sensorkit-device-usage-conversion"
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-conversion-provenance"
            ]},
            "target": [
                {"reference": VALIDATOR.expected_entry_full_url(output_system, observation_output)},
                {"reference": document_url},
            ],
            "entity": [{
                "role": "source",
                "what": {"identifier": {"system": source_system, "value": source_value}},
            }],
        }

        def entry(
            resource: dict[str, object], output: str, system: str = output_system
        ) -> dict[str, object]:
            return {
                "extension": [{
                    "url": VALIDATOR.ENTRY_IDENTIFIER_EXTENSION,
                    "valueIdentifier": {"system": system, "value": output},
                }],
                "fullUrl": VALIDATOR.expected_entry_full_url(system, output),
                "resource": resource,
            }

        bundle = {
            "resourceType": "Bundle",
            "meta": {"profile": [VALIDATOR.EXCHANGE_BUNDLE_PROFILE]},
            "identifier": {"system": "https://example.org/exchange", "value": "one"},
            "type": "collection",
            "entry": [
                entry(observation, observation_output),
                entry(document, document_output),
                entry(provenance, provenance_entry_value, provenance_entry_system),
            ],
        }
        VALIDATOR.validate_exchange_bundle(bundle, "Bundle")

        missing_raw_target = copy.deepcopy(bundle)
        missing_raw_target["entry"][2]["resource"]["target"] = [
            missing_raw_target["entry"][2]["resource"]["target"][0]
        ]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "target every structured and raw output"
        ):
            VALIDATOR.validate_exchange_bundle(missing_raw_target, "Bundle")

        missing_document = copy.deepcopy(bundle)
        missing_document["entry"] = missing_document["entry"][:1]
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "unresolved internal UUID reference|same Bundle"
        ):
            VALIDATOR.validate_exchange_bundle(missing_document, "Bundle")

        mismatched_identity = copy.deepcopy(bundle)
        other_source = "95ee78bd-a754-4d3d-b084-6031b42d666c"
        other_preimage = VALIDATOR.canonical_string_array(
            [source_system, other_source, "native-recording"]
        )
        other_output = str(VALIDATOR.uuid.uuid5(
            VALIDATOR.uuid.UUID("c0b8814a-8178-5e92-996a-c4cf36cd640b"),
            other_preimage,
        ))
        mismatched_identity["entry"][1]["resource"]["identifier"][0]["value"] = other_source
        mismatched_identity["entry"][1]["resource"]["identifier"][1]["value"] = other_output
        mismatched_identity["entry"][1]["extension"][0]["valueIdentifier"]["value"] = other_output
        mismatched_identity["entry"][1]["fullUrl"] = VALIDATOR.expected_entry_full_url(
            output_system, other_output
        )
        mismatched_identity["entry"][0]["resource"]["derivedFrom"][0]["reference"] = (
            mismatched_identity["entry"][1]["fullUrl"]
        )
        mismatched_identity["entry"][2]["resource"]["target"][1]["reference"] = (
            mismatched_identity["entry"][1]["fullUrl"]
        )
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError, "same source-record [Ii]dentifier"
        ):
            VALIDATOR.validate_exchange_bundle(mismatched_identity, "Bundle")

        wrong_provenance_source = copy.deepcopy(bundle)
        wrong_provenance_source["entry"][2]["resource"]["entity"][0]["what"][
            "identifier"
        ]["value"] = "95ee78bd-a754-4d3d-b084-6031b42d666c"
        with self.assertRaisesRegex(
            VALIDATOR.ProducerValidationError,
            "exactly one conversion Provenance|no output for its source record",
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
                VALIDATOR.run_validator(validator, [], resources)

            self.assertEqual(len(commands), 1)
            command = commands[0]
            self.assertIn(["-version", "4.0.1"], [command[index:index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-tx", "n/a"], [command[index:index + 2] for index in range(len(command) - 1)])
            self.assertIn("-no-http-access", command)
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
