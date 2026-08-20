"""Bind the implementation-neutral Mobile semantic vectors to the exact catalog."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_producer", ROOT / "Scripts/validate-producer.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class MobileSemanticVectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        cls.corpus = json.loads(
            (ROOT / "Conformance/corpora/mobile-semantics/corpus.json").read_text(
                encoding="utf-8"
            ),
            parse_float=Decimal,
        )

    def test_corpus_is_closed_versioned_and_one_vector_per_measurement(self) -> None:
        self.assertEqual(
            set(self.corpus),
            {
                "schemaVersion",
                "fhirVersion",
                "version",
                "catalog",
                "purpose",
                "comparisonRule",
                "effectiveCanonicalization",
                "sourceContextRules",
                "vectors",
            },
        )
        self.assertEqual(self.corpus["schemaVersion"], 1)
        self.assertEqual(self.corpus["fhirVersion"], "4.0.1")
        self.assertEqual(self.corpus["version"], "0.2.0")
        self.assertIn("execute no producer implementation", self.corpus["purpose"])
        expected = [measurement["id"] for measurement in self.catalog["measurements"]]
        actual = [vector["id"] for vector in self.corpus["vectors"]]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(set(actual)))

    def test_effective_canonicalization_is_exact_and_crosses_the_epoch(self) -> None:
        contract = self.corpus["effectiveCanonicalization"]
        self.assertEqual(
            {key: contract[key] for key in ("precision", "rounding", "epoch", "offsetPolicy")},
            {
                "precision": "millisecond",
                "rounding": "half-even",
                "epoch": "1970-01-01T00:00:00Z",
                "offsetPolicy": "preserve-source-offset",
            },
        )
        self.assertEqual(
            contract["excludedContracts"], ["Sensor SampledData", "ECG SampledData"]
        )
        ids = {vector["id"] for vector in contract["vectors"]}
        self.assertEqual(
            ids,
            {
                "positive-below-half",
                "positive-half-to-even",
                "positive-half-to-next-even",
                "negative-half-to-even",
                "negative-half-to-previous-even",
                "offset-preserved",
            },
        )
        for vector in contract["vectors"]:
            actual = VALIDATOR.round_mobile_epoch_milliseconds(
                VALIDATOR.parse_fhir_instant(vector["input"], vector["id"])
            )
            expected = VALIDATOR.parse_fhir_instant(vector["output"], vector["id"])
            self.assertEqual(actual, expected)
            self.assertEqual(
                expected, VALIDATOR.round_mobile_epoch_milliseconds(expected)
            )

        self.assertEqual(
            self.catalog["effectiveCanonicalization"],
            {
                "scope": "Every Mobile scalar or aggregate effectiveDateTime and effectivePeriod endpoint; Sensor and ECG SampledData timing is excluded.",
                "precision": "millisecond",
                "rounding": "half-even",
                "epoch": "1970-01-01T00:00:00Z",
                "offsetPolicy": "Preserve the caller/source numeric UTC offset when it is available; never invent an offset.",
            },
        )

    def test_every_projection_matches_exact_catalog_semantics(self) -> None:
        vectors = {vector["id"]: vector for vector in self.corpus["vectors"]}
        for measurement in self.catalog["measurements"]:
            vector = vectors[measurement["id"]]
            self.assertEqual(
                set(vector),
                {
                    "id",
                    "profile",
                    "code",
                    "effective",
                    "result",
                    "edgeRules",
                    "admittedSourceContext",
                },
            )
            self.assertEqual(
                vector["profile"],
                f"{self.catalog['canonicalRoot']}/{measurement['profile']}",
            )
            self.assertEqual(vector["code"], measurement["code"])
            self.assertEqual(vector["effective"]["type"], measurement["effective"])
            if measurement["effective"] == "Period":
                self.assertLess(
                    vector["effective"]["start"], vector["effective"]["end"]
                )
            else:
                self.assertEqual(set(vector["effective"]), {"type", "value"})
            result = vector["result"]
            if measurement.get("quantity") is not None:
                self.assertEqual(result["type"], "Quantity")
                self.assertEqual(
                    {key: result[key] for key in ("system", "code", "unit")},
                    measurement["quantity"],
                )
            elif measurement["id"] == "blood-pressure":
                self.assertEqual(result["type"], "components")
                self.assertEqual(
                    [component["id"] for component in result["components"]],
                    [component["id"] for component in measurement["components"]],
                )
                for actual, expected in zip(
                    result["components"], measurement["components"], strict=True
                ):
                    self.assertEqual(actual["system"], expected["system"])
                    self.assertEqual(actual["code"], expected["code"])
                    self.assertEqual(actual["quantitySystem"], expected["quantity"]["system"])
                    self.assertEqual(actual["quantityCode"], expected["quantity"]["code"])
                    self.assertEqual(actual["unit"], expected["quantity"]["unit"])
            else:
                self.assertEqual(measurement["id"], "sleep-stage")
                self.assertEqual(result["type"], "CodeableConcept")
                self.assertEqual(result["system"], measurement["resultCodeSystem"])
                self.assertIn(result["code"], measurement["allowedValues"])
            self.assertTrue(vector["edgeRules"])
            self.assertTrue(all(isinstance(rule, str) and rule for rule in vector["edgeRules"]))

    def test_source_context_is_exactly_the_supported_adapter_surface(self) -> None:
        rules = self.corpus["sourceContextRules"]
        for rule_id, rule in rules.items():
            self.assertTrue(rule_id)
            self.assertTrue(set(rule) <= {"inherits", "required", "allowedAdditions"})
            if "inherits" in rule:
                self.assertIn(rule["inherits"], rules)
            self.assertIsInstance(rule.get("required", []), list)
            self.assertIsInstance(rule.get("allowedAdditions", []), list)

        for measurement, vector in zip(
            self.catalog["measurements"], self.corpus["vectors"], strict=True
        ):
            expected_sources = {
                source
                for source, status in measurement["coverage"].items()
                if status == "supported"
            }
            actual_sources = set(vector["admittedSourceContext"])
            self.assertEqual(actual_sources, expected_sources)
            for rule_id in vector["admittedSourceContext"].values():
                self.assertIn(rule_id, rules)


if __name__ == "__main__":
    unittest.main()
