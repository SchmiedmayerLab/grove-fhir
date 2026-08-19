"""Tests for deterministic one-mutation FHIR fixture corpora."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

from Scripts import fhir_fixture_corpus as CORPUS


class FHIRFixtureCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = {
            "resourceType": "Observation",
            "id": "base",
            "status": "final",
            "code": {"coding": [{"system": "https://example.org", "code": "heart-rate"}]},
            "valueQuantity": {"value": 72, "unit": "beats/min"},
        }
        self.manifest = {
            "schemaVersion": 1,
            "bases": [{"id": "heart-rate", "path": "base.json"}],
            "cases": [
                {
                    "id": "missing-status",
                    "base": "heart-rate",
                    "patch": [{"op": "remove", "path": "/status"}],
                    "expectedRule": {
                        "code": "observation.status-required",
                        "reason": "Observation.status is required",
                        "location": "Observation.status",
                        "severity": "error",
                    },
                },
                {
                    "id": "wrong-value-type",
                    "base": "heart-rate",
                    "patch": [
                        {
                            "op": "replace",
                            "path": "/valueQuantity/value",
                            "value": "seventy-two",
                        }
                    ],
                    "expectedRule": {
                        "code": "observation.quantity-number",
                        "reason": "Quantity.value must be numeric",
                    },
                },
            ],
        }

    def _write_corpus(self, directory: Path) -> Path:
        manifest = directory / "corpus.json"
        (directory / "base.json").write_bytes(CORPUS.canonical_json_bytes(self.base))
        manifest.write_bytes(CORPUS.canonical_json_bytes(self.manifest))
        return manifest

    def test_canonical_json_is_stable_and_strict(self) -> None:
        first = {"z": [3, 2, 1], "a": {"β": True, "a": None}}
        second = {"a": {"a": None, "β": True}, "z": [3, 2, 1]}
        self.assertEqual(CORPUS.canonical_json_bytes(first), CORPUS.canonical_json_bytes(second))
        self.assertEqual(
            CORPUS.canonical_json_bytes(first),
            '{"a":{"a":null,"β":true},"z":[3,2,1]}\n'.encode(),
        )
        with self.assertRaises(ValueError):
            CORPUS.canonical_json_bytes({"not-finite": float("nan")})

    def test_each_patch_is_isolated_from_the_shared_base(self) -> None:
        original = deepcopy(self.base)
        removed = CORPUS.apply_patch_operation(
            self.base, {"op": "remove", "path": "/code/coding/0/code"}
        )
        added = CORPUS.apply_patch_operation(
            self.base,
            {"op": "add", "path": "/code/coding/-", "value": {"code": "second"}},
        )
        escaped = CORPUS.apply_patch_operation(
            {"a/b": {"~key": 1}},
            {"op": "replace", "path": "/a~1b/~0key", "value": 2},
        )

        self.assertEqual(self.base, original)
        self.assertNotIn("code", removed["code"]["coding"][0])
        self.assertEqual(len(added["code"]["coding"]), 2)
        self.assertEqual(escaped, {"a/b": {"~key": 2}})

    def test_json_type_changes_are_real_mutations(self) -> None:
        result = CORPUS.apply_patch_operation(
            {"resourceType": "Parameters", "value": 1},
            {"op": "replace", "path": "/value", "value": True},
        )
        self.assertIs(result["value"], True)

    def test_rejects_non_mutating_or_ambiguous_cases(self) -> None:
        with self.assertRaisesRegex(CORPUS.CorpusError, "must change"):
            CORPUS.apply_patch_operation(
                self.base, {"op": "replace", "path": "/status", "value": "final"}
            )
        failures = CORPUS.validate_patch_operation(
            {"op": "test", "path": "/status", "value": "final"}
        )
        self.assertIn("patch op 'test' is not a mutation", failures)
        with self.assertRaisesRegex(CORPUS.CorpusError, "child of patch from"):
            CORPUS.apply_patch_operation(
                self.base, {"op": "move", "from": "/code", "path": "/code/coding/0"}
            )

    def test_expected_rule_schema_is_closed_and_reason_specific(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["cases"][0]["expectedRule"] = {
            "code": "Display Name",
            "reason": " trailing ",
            "expression": "status.exists()",
            "severity": "notice",
        }
        manifest["cases"][1]["patch"].append({"op": "remove", "path": "/status"})
        failures = CORPUS.validate_manifest(manifest)
        self.assertIn(
            "case 1 expectedRule contains unsupported fields: expression", failures
        )
        self.assertIn(
            "case 1 expectedRule code must be a stable lowercase rule code", failures
        )
        self.assertIn(
            "case 1 expectedRule reason must be a nonempty exact string", failures
        )
        self.assertIn(
            "case 1 expectedRule severity must be fatal, error, warning, or information",
            failures,
        )
        self.assertIn("case 2 patch must contain exactly one operation", failures)

        malformed = deepcopy(self.manifest)
        malformed["cases"][0]["patch"] = [{"op": [], "path": "/status"}]
        malformed["cases"][0]["expectedRule"]["severity"] = []
        failures = CORPUS.validate_manifest(malformed)
        self.assertIn(
            "case 1 patch op must be add, remove, replace, move, or copy", failures
        )
        self.assertIn(
            "case 1 expectedRule severity must be fatal, error, warning, or information",
            failures,
        )

    def test_materialization_is_byte_for_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._write_corpus(root)
            first = root / "first"
            second = root / "second"
            first_index = CORPUS.materialize_corpus(manifest, first)
            second_index = CORPUS.materialize_corpus(manifest, second)

            self.assertEqual(first_index, second_index)
            first_files = sorted(
                path.relative_to(first) for path in first.rglob("*") if path.is_file()
            )
            second_files = sorted(
                path.relative_to(second) for path in second.rglob("*") if path.is_file()
            )
            self.assertEqual(first_files, second_files)
            for path in first_files:
                self.assertEqual((first / path).read_bytes(), (second / path).read_bytes())
            self.assertEqual(
                json.loads((first / "invalid/missing-status.json").read_text()),
                {
                    "resourceType": "Observation",
                    "id": "base",
                    "code": self.base["code"],
                    "valueQuantity": self.base["valueQuantity"],
                },
            )

    def test_decimal_lexical_precision_survives_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "corpus.json"
            (root / "base.json").write_text(
                '{"resourceType":"Observation","status":"final",'
                '"valueQuantity":{"value":1.20}}\n',
                encoding="utf-8",
            )
            manifest.write_bytes(CORPUS.canonical_json_bytes(self.manifest))
            output = root / "output"
            CORPUS.materialize_corpus(manifest, output)
            self.assertIn(
                b'"value":1.20', (output / "valid/heart-rate.json").read_bytes()
            )
            loaded = CORPUS.strict_json_loads(
                (output / "valid/heart-rate.json").read_text(encoding="utf-8")
            )
            self.assertEqual(loaded["valueQuantity"]["value"].as_tuple().exponent, -2)
            self.assertNotEqual(
                CORPUS.canonical_json_bytes(Decimal("1.20")),
                CORPUS.canonical_json_bytes(Decimal("1.2")),
            )

    def test_duplicate_keys_non_finite_numbers_and_stale_outputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(CORPUS.CorpusError, "duplicate JSON object key"):
            CORPUS.strict_json_loads('{"status":"final","status":"amended"}')
        with self.assertRaisesRegex(CORPUS.CorpusError, "non-finite"):
            CORPUS.strict_json_loads('{"value":NaN}')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._write_corpus(root)
            output = root / "output"
            output.mkdir()
            (output / "obsolete.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(CORPUS.CorpusError, "stale files"):
                CORPUS.materialize_corpus(manifest, output)

    def test_base_resource_may_not_escape_through_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus"
            corpus.mkdir()
            outside = root / "outside.json"
            outside.write_bytes(CORPUS.canonical_json_bytes(self.base))
            (corpus / "base.json").symlink_to(outside)
            manifest_path = corpus / "corpus.json"
            manifest_path.write_bytes(CORPUS.canonical_json_bytes(self.manifest))
            manifest = CORPUS.load_manifest(manifest_path)
            with self.assertRaisesRegex(CORPUS.CorpusError, "may not contain symlinks"):
                CORPUS.load_bases(manifest, manifest_path)
            manifest_link = corpus / "manifest-link.json"
            manifest_link.symlink_to(manifest_path)
            with self.assertRaisesRegex(CORPUS.CorpusError, "manifest may not be a symlink"):
                CORPUS.load_manifest(manifest_link)

    def test_results_must_match_the_exact_rule_and_reason(self) -> None:
        results = {
            "schemaVersion": 1,
            "baseDiagnostics": {"heart-rate": []},
            "caseDiagnostics": {
                "missing-status": [deepcopy(self.manifest["cases"][0]["expectedRule"])],
                "wrong-value-type": [deepcopy(self.manifest["cases"][1]["expectedRule"])],
            },
        }
        self.assertEqual(CORPUS.validate_results(self.manifest, results), [])

        results["caseDiagnostics"]["missing-status"][0]["reason"] = "Some failure"
        failures = CORPUS.validate_results(self.manifest, results)
        self.assertEqual(len(failures), 1)
        self.assertIn("missing-status did not report its exact expectedRule", failures[0])

    def test_in_process_validator_uses_the_same_results_contract(self) -> None:
        bases = {"heart-rate": self.base}
        cases = CORPUS.build_cases(self.manifest, bases)

        def validator(resource: dict[str, object]) -> list[dict[str, str]]:
            if "status" not in resource:
                return [deepcopy(self.manifest["cases"][0]["expectedRule"])]
            if resource.get("valueQuantity") == {
                "value": "seventy-two",
                "unit": "beats/min",
            }:
                return [deepcopy(self.manifest["cases"][1]["expectedRule"])]
            return []

        self.assertEqual(
            CORPUS.validate_with(self.manifest, bases, cases, validator), []
        )


if __name__ == "__main__":
    unittest.main()
