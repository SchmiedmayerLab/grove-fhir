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
import tempfile
import unittest
from pathlib import Path

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
                "exactly one shared measurement profile and exactly one adapter profile",
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


if __name__ == "__main__":
    unittest.main()
