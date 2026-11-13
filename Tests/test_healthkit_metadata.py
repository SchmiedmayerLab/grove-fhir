"""Preservation and rejection cases for the restored source metadata carrier."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import copy
import json
from pathlib import Path
import unittest
from decimal import Decimal

from Scripts.producer_validation.diagnostics import ProducerValidationError
from Scripts.producer_validation.healthkit_metadata import validate_healthkit_metadata
from Tests.producer_validation_test_support import (
    active_base, entry_key, provenances, rekey_records, single_record,
)


URL = "https://grovealliance.org/fhir/core/StructureDefinition/metadata"


def record(entries):
    return {
        "resourceType": "Observation",
        "meta": {"profile": ["https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation"]},
        "extension": [{"url": URL, "extension": sorted(entries, key=lambda item: item["extension"][0]["valueString"].encode("utf-16-be"))}],
    }


def entry(key, name, value):
    return {"url": "entry", "extension": [{"url": "key", "valueString": key}, {"url": "value", name: value}]}


class HealthKitMetadataTests(unittest.TestCase):
    def test_shared_legacy_fixture_is_admitted_without_changing_values(self):
        path = Path(__file__).parents[1] / "Conformance/corpora/healthkit-metadata/legacy-values.json"
        fixture = json.loads(path.read_text(), parse_float=Decimal)
        entries = [entry(item["key"], name, item[name]) for item in fixture["cases"] for name in item if name.startswith("value")]
        resource = record(entries)
        before = copy.deepcopy(resource)
        validate_healthkit_metadata(resource, "shared legacy fixture")
        self.assertEqual(resource, before)

    def test_legacy_typed_values_survive_without_mutation(self):
        resource = record([
            entry("com.example.note", "valueString", "after exercise"),
            entry("count", "valueDecimal", Decimal("1.234567890123456789")),
            entry("manual", "valueBoolean", True),
            entry("date", "valueDateTime", "2026-11-12T18:00:00Z"),
            entry("enum", "valueCoding", {"system": "https://example.org/codes", "code": "1"}),
            entry("HKWeatherTemperature", "valueQuantity", {"value": 22, "system": "http://unitsofmeasure.org", "code": "Cel"}),
        ])
        before = copy.deepcopy(resource)
        validate_healthkit_metadata(resource, "source")
        self.assertEqual(resource, before)

    def test_unicode_and_reserved_characters_remain_exact_keys(self):
        resource = record([entry(key, "valueString", key) for key in ["é", "e\u0301", "a/b", "a%2Fb"]])
        validate_healthkit_metadata(resource, "source")

    def test_duplicate_empty_and_out_of_order_keys_are_rejected(self):
        good = entry("note", "valueString", "value")
        for entries in [[good, good], [entry("", "valueString", "value")]]:
            with self.subTest(entries=entries), self.assertRaises(ProducerValidationError):
                validate_healthkit_metadata(record(entries), "source")
        resource = record([entry("a", "valueString", "a"), entry("b", "valueString", "b")])
        resource["extension"][0]["extension"].reverse()
        with self.assertRaises(ProducerValidationError):
            validate_healthkit_metadata(resource, "source")

    def test_undefined_legacy_child_urls_are_not_valid_exchange_entries(self):
        resource = record([entry("key", "valueString", "value")])
        resource["extension"][0]["extension"] = [{"url": URL + "/key", "valueString": "value"}]
        with self.assertRaises(ProducerValidationError):
            validate_healthkit_metadata(resource, "legacy shape")

    def test_invalid_or_untyped_values_are_rejected(self):
        values = [
            ("valueString", ""), ("valueString", 1), ("valueBoolean", 1),
            ("valueDecimal", True), ("valueDecimal", float("inf")),
            ("valueDecimal", "1"), ("valueDateTime", "2026-11-12"),
            ("valueReference", {"reference": "Patient/other"}),
            ("valueCoding", {"system": "relative", "code": "1"}),
            ("valueCoding", {"system": "https://[invalid", "code": "1"}),
            ("valueQuantity", {"value": 1, "system": "https://example.org", "code": "mg"}),
        ]
        for name, value in values:
            with self.subTest(name=name, value=value), self.assertRaises(ProducerValidationError):
                validate_healthkit_metadata(record([entry("key", name, value)]), "source")

    def test_repeated_containers_and_nested_values_are_rejected(self):
        resource = record([entry("key", "valueString", "value")])
        resource["extension"] *= 2
        with self.assertRaises(ProducerValidationError):
            validate_healthkit_metadata(resource, "source")
        with self.assertRaises(ProducerValidationError):
            validate_healthkit_metadata(record([entry("key", "valueReference", {"reference": "Patient/other"})]), "source")

    def test_clinical_wrapper_preserves_original_attachment(self):
        resource = record([entry("custom", "valueBoolean", False)])
        resource["resourceType"] = "DocumentReference"
        resource["meta"]["profile"] = ["https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-clinical-record-document"]
        resource["content"] = [{"attachment": {"data": "e30="}}]
        before = copy.deepcopy(resource)
        validate_healthkit_metadata(resource, "clinical wrapper")
        self.assertEqual(resource, before)

    def test_unrelated_resources_cannot_claim_healthkit_metadata(self):
        resource = record([entry("key", "valueString", "value")])
        resource["meta"]["profile"] = ["https://example.org/observation"]
        with self.assertRaises(ProducerValidationError):
            validate_healthkit_metadata(resource, "unrelated")

    def test_metadata_changes_version_but_preserves_source_and_output_identity(self):
        bundle = single_record(active_base())
        observation = next(item["resource"] for item in bundle["entry"] if item["resource"]["resourceType"] == "Observation")
        before = copy.deepcopy(bundle)
        observation.setdefault("extension", []).append(record([entry("custom", "valueString", "first")])["extension"][0])
        rekey_records(bundle)
        self.assertEqual(observation["identifier"], next(item["resource"]["identifier"] for item in before["entry"] if item["resource"]["resourceType"] == "Observation"))
        old, new = provenances(before)[0], provenances(bundle)[0]
        self.assertEqual(old["resource"]["entity"], new["resource"]["entity"])
        self.assertEqual(old["resource"]["target"], new["resource"]["target"])
        self.assertNotEqual(entry_key(old), entry_key(new))
        retry = copy.deepcopy(bundle)
        rekey_records(retry)
        self.assertEqual(bundle, retry)
