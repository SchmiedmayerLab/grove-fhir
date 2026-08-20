"""Validate the normative source-neutral measurement catalog."""

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
SOURCES = {"healthkit", "health-connect", "sensorkit", "google-health-api", "oura", "withings"}


class MeasurementCatalogTests(unittest.TestCase):
    def test_catalog_is_closed_complete_and_matches_package_graph(self) -> None:
        catalog = json.loads((ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8"))
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["fhirVersion"], "4.0.1")
        self.assertEqual(catalog["version"], "0.2.0")
        profiles = set(next(package for package in graph["packages"] if package["source"] == "mobile")["profiles"])
        statuses = set(catalog["statusVocabulary"])
        identifiers: set[str] = set()
        for measurement in catalog["measurements"]:
            self.assertNotIn(measurement["id"], identifiers)
            identifiers.add(measurement["id"])
            self.assertIn(measurement["profile"], profiles)
            self.assertEqual(set(measurement["coverage"]), SOURCES)
            self.assertTrue(set(measurement["coverage"].values()) <= statuses)
            self.assertIn(measurement["effective"], {"dateTime", "Period"})
            code = measurement["code"]
            self.assertTrue(code["system"].startswith(("http://loinc.org", "https://grovealliance.org/fhir/")))
            if measurement["quantity"] is not None:
                self.assertEqual(measurement["quantity"]["system"], "http://unitsofmeasure.org")
            for component in measurement.get("components", []):
                self.assertEqual(component["quantity"]["system"], "http://unitsofmeasure.org")
        sleep_stage = next(item for item in catalog["measurements"] if item["id"] == "sleep-stage")
        self.assertEqual(
            sleep_stage["allowedValues"],
            ["awake", "in-bed", "out-of-bed", "asleep-unspecified", "light", "deep", "rem", "unknown"],
        )
        serum_plasma = next(
            item for item in catalog["measurements"] if item["id"] == "serum-plasma-glucose"
        )
        self.assertEqual(
            [specimen["id"] for specimen in serum_plasma["specimenAlternatives"]],
            ["plasma", "serum"],
        )
        self.assertEqual(
            identifiers,
            {"active-energy", "basal-body-temperature", "blood-glucose", "capillary-blood-glucose", "serum-plasma-glucose", "interstitial-glucose", "blood-pressure", "body-height", "body-mass-index", "body-temperature", "body-weight", "distance", "heart-rate", "oxygen-saturation", "respiratory-rate", "sleep-duration", "sleep-stage", "step-count"},
        )

    def test_uuid_vector_uses_the_normative_entry_identity_algorithm(self) -> None:
        import importlib.util
        import uuid

        spec = importlib.util.spec_from_file_location(
            "validate_producer", ROOT / "Scripts/validate-producer.py"
        )
        assert spec and spec.loader
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        contract = json.loads((ROOT / "catalog/exchange-identity.json").read_text(encoding="utf-8"))
        for vector in contract["vectors"]:
            value = validator.canonical_identifier_name(vector["system"], vector["value"])
            self.assertEqual(value, vector["input"])
            generated = uuid.uuid5(uuid.UUID(contract["fullUrlAlgorithm"]["namespace"]), value)
            self.assertEqual(f"urn:uuid:{generated}", vector["fullUrl"])

    def test_uuid_algorithm_rejects_invalid_unicode(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "validate_producer_invalid_unicode", ROOT / "Scripts/validate-producer.py"
        )
        assert spec and spec.loader
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        with self.assertRaisesRegex(validator.ProducerValidationError, "invalid Unicode surrogate"):
            validator.canonical_identifier_name("https://example.org", "bad\ud800value")


if __name__ == "__main__":
    unittest.main()
