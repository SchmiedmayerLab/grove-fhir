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

    def test_repository_example_is_structurally_valid(self) -> None:
        manifest, resources = VALIDATOR.validate_manifest(self.example)
        self.assertEqual(manifest["fhirVersion"], "4.0.1")
        self.assertEqual([path.name for path in resources], ["exchange-bundle.json"])

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

    def test_validator_runs_each_resource_offline_and_parses_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
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
                    "resourceType": "OperationOutcome",
                    "issue": [{"severity": "information", "code": "informational"}],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="validated")

            with mock.patch.object(VALIDATOR.subprocess, "run", side_effect=successful_run):
                VALIDATOR.run_validator(validator, [], resources)

            self.assertEqual(len(commands), 2)
            for command, resource in zip(commands, resources, strict=True):
                self.assertIn(["-version", "4.0.1"], [command[index:index + 2] for index in range(len(command) - 1)])
                self.assertIn(["-tx", "n/a"], [command[index:index + 2] for index in range(len(command) - 1)])
                self.assertIn("-no-http-access", command)
                self.assertEqual(command[-1], str(resource))

    def test_validator_error_in_any_produced_outcome_fails_even_with_zero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resource = root / "resource.json"
            resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def error_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps({
                    "resourceType": "Bundle",
                    "type": "collection",
                    "entry": [
                        {"resource": {"resourceType": "OperationOutcome", "issue": [
                            {"severity": "information", "code": "informational"}
                        ]}},
                        {"resource": {"resourceType": "OperationOutcome", "issue": [
                            {"severity": "error", "code": "invalid", "diagnostics": "bad unit"}
                        ]}},
                    ],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="")

            with mock.patch.object(VALIDATOR.subprocess, "run", side_effect=error_run):
                with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "bad unit"):
                    VALIDATOR.run_validator(validator, [], [resource])

    def test_validator_process_and_output_failures_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resource = root / "resource.json"
            resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def nonzero_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps({
                    "resourceType": "OperationOutcome",
                    "issue": [{"severity": "information", "code": "informational"}],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 2, stdout="failed")

            with mock.patch.object(VALIDATOR.subprocess, "run", side_effect=nonzero_run):
                with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "process failed"):
                    VALIDATOR.run_validator(validator, [], [resource])

            with mock.patch.object(
                VALIDATOR.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, stdout="no output"),
            ):
                with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "no trustworthy"):
                    VALIDATOR.run_validator(validator, [], [resource])


if __name__ == "__main__":
    unittest.main()
