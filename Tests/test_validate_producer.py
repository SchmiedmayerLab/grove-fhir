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
        self.assertEqual([path.name for path in resources], ["heart-rate.json"])

    def test_missing_profile_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/heart-rate.json").read_text(encoding="utf-8")
        )
        resource["meta"]["profile"] = ["http://hl7.org/fhir/StructureDefinition/heartrate"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "resources/heart-rate.json").write_text(json.dumps(resource), encoding="utf-8")
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
            resource = self.example.parent / "resources/heart-rate.json"
            (root / "resources/heart-rate.json").write_bytes(resource.read_bytes())
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(VALIDATOR.ProducerValidationError, "must be unique"):
                VALIDATOR.validate_manifest(path)

    def test_cli_requires_official_validator_outside_structural_mode(self) -> None:
        self.assertEqual(VALIDATOR.main(["--manifest", str(self.example)]), 1)


if __name__ == "__main__":
    unittest.main()
