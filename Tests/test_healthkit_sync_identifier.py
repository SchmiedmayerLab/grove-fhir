"""Admission and rejection cases for the readable HealthKit sync Identifier."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import copy
import json
from pathlib import Path
import unittest

from Scripts.producer_validation import context, identity
from Scripts.producer_validation.diagnostics import ProducerValidationError
from Scripts.producer_validation.healthkit_metadata import validate_healthkit_metadata
from Scripts.producer_validation.profiles import validate_writer_record_revision
from Tests.producer_validation_test_support import key_system, test_identity


ROOT = Path(__file__).parents[1]
CORPUS = ROOT / "Conformance/corpora/healthkit-sync-identifier"
HEALTHKIT = "https://grovealliance.org/fhir/healthkit/"
ROLE_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
SUBJECT = ["https://study.example.org/fhir/identifiers/participant", "participant-001"]


def load(name):
    return json.loads((CORPUS / f"{name}.json").read_text(encoding="utf-8"))


def coding(identifier):
    return (identifier.get("type") or {"coding": [{}]})["coding"][0]


def sync_identifier(resource):
    return next(item for item in resource["identifier"] if coding(item).get("code") == "healthkit-sync-id")


def native_identifier(resource):
    return next(item for item in resource["identifier"] if "type" not in item)


def role(resource, code):
    return next(item for item in resource["identifier"] if coding(item) == {"system": ROLE_SYSTEM, "code": code})


def validate(*resources):
    identity.validate_governed_source_identifiers(list(resources), "Record")


class HealthKitSyncIdentifierTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8"))
        self.contract = self.catalog["identity"]["writerRecord"]["revision"]["readableIdentifier"]

    def test_contract_names_one_type_under_the_native_identifier_setting(self):
        allowance = context.EXCHANGE_PROTOCOL["governedSourceIdentifier"]["validation"]["designatedNode"]
        self.assertEqual(allowance["maxPerPrimaryOutput"], 1)
        self.assertEqual(
            allowance["writerAssignedIdentifier"],
            {
                "maxPerPrimaryOutput": 1,
                "requiredBeside": ["native-record-identifier", "writer-record", "writer-record-version"],
                "disclosurePolicy": "native-record-identifier",
                "adapterTypes": {"healthkit": {
                    "contract": "catalog/healthkit-adapter.json#/identity/writerRecord/revision/readableIdentifier",
                    "typeSystem": self.contract["typeSystem"],
                    "typeCode": self.contract["typeCode"],
                }},
            },
        )
        self.assertEqual(self.contract["typeSystem"], HEALTHKIT + "CodeSystem/healthkit-identifier-type")
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(encoding="utf-8")
        types = terminology.split("CodeSystem: HealthKitIdentifierTypeCS\n", 1)[1].split("\n\n", 1)[0]
        self.assertIn(f"* #{self.contract['typeCode']} ", types)
        self.assertIn("no separate setting exists", self.contract["disclosureRule"])
        self.assertIn("writing application's bundle identifier", self.contract["disclosureRule"])
        self.assertEqual(self.contract["writerSegment"], "bundle-identifier")
        self.assertIn("withholds the readable Identifier", self.contract["nonConformingWriterRule"])
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        self.assertIn("/healthkit-sync-identifier/" + self.contract["writerSegmentPattern"][1:], profiles)
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        for sentence in (
            "The same opt-in setting also discloses the [readable sync identifier](#readable-sync-identifier) "
            "of a sample that carries a sync pair; no separate setting exists.",
            "Enabling the setting therefore discloses the bundle identifier of the application that wrote "
            "such a sample",
            "With the setting off, the sync identifier text is not exported in any element",
            "withhold the readable sync identifier for its samples",
            "report `HKMetadataKeySyncIdentifier` as a withheld key under `mobile-omission.unmodeled-metadata`",
            "A deployment configures one native identifier system",
            "`HKMetadataKeySyncIdentifier` and `HKMetadataKeySyncVersion` are never metadata entries",
        ):
            with self.subTest(sentence=sentence):
                self.assertIn(sentence, mapping)

    def test_fixtures_agree_with_their_keyed_writer_record(self):
        for name in ("observation", "document"):
            with self.subTest(fixture=name):
                resource = load(name)
                validate(resource)
                validate_writer_record_revision(resource, name)
                readable = sync_identifier(resource)
                prefix, _, segment = readable["system"].rpartition(f"/{self.contract['systemPathSegment']}/")
                writer = segment
                self.assertRegex(writer, self.contract["writerSegmentPattern"])
                self.assertEqual(native_identifier(resource)["system"], prefix)
                self.assertEqual(self.contract["systemBase"], "native-record-identifier-system")
                self.assertEqual(
                    role(resource, "writer-record")["value"],
                    test_identity(
                        "writer-record",
                        [*SUBJECT, HEALTHKIT + "NamingSystem/apple-bundle-id", writer, readable["value"]],
                    ),
                )
                self.assertEqual(role(resource, "writer-record")["system"], key_system("writer-record"))

    def test_equal_text_under_another_writer_or_store_is_another_identifier(self):
        resource = load("observation")
        readable = sync_identifier(resource)
        other_writer = "com.example.other"
        prefix = readable["system"].rsplit("/", 1)[0]
        self.assertNotEqual(readable["system"], f"{prefix}/{other_writer}")
        relocated = copy.deepcopy(resource)
        sync_identifier(relocated)["system"] = f"{prefix}/{other_writer}"
        validate(relocated)

    def test_requires_writer_evidence_and_the_native_record_identifier(self):
        for name in ("observation", "document"):
            resource = load(name)
            without_native = copy.deepcopy(resource)
            without_native["identifier"].remove(native_identifier(without_native))
            without_writer = copy.deepcopy(resource)
            without_writer["identifier"].remove(role(without_writer, "writer-record"))
            without_version = copy.deepcopy(resource)
            without_version["extension"] = [
                item for item in without_version["extension"]
                if item["url"] != context.WRITER_RECORD_VERSION_EXTENSION
            ]
            same_system = copy.deepcopy(resource)
            native_identifier(same_system)["system"] = sync_identifier(same_system)["system"].rsplit("/", 3)[0]
            for label, mutated in (
                ("native", without_native), ("writer", without_writer),
                ("version", without_version), ("system", same_system),
            ):
                with self.subTest(fixture=name, missing=label), self.assertRaises(ProducerValidationError):
                    validate(mutated)
            # Writer evidence without the readable value stays conformant: the setting is off.
            keyed_only = copy.deepcopy(resource)
            keyed_only["identifier"].remove(sync_identifier(keyed_only))
            keyed_only["identifier"].remove(native_identifier(keyed_only))
            validate(keyed_only)
            validate_writer_record_revision(keyed_only, name)

    def test_system_names_the_store_scope_and_one_plain_bundle_identifier(self):
        resource = load("observation")
        prefix = sync_identifier(resource)["system"].rsplit("/", 1)[0]
        for system in (
            "https://study.example.org/fhir/NamingSystem/healthkit-sync-identifier",
            prefix + "/",
            prefix + "/com.example_scale",
            prefix + "/com.example.scale/extra",
            prefix + "/com.example%2Escale",
            prefix + "/Y29tLmV4YW1wbGUuc2NhbGU=",
            prefix + "/com.exämple.scale",
            "/healthkit-sync-identifier/com.example.scale",
            prefix.replace("healthkit-sync-identifier", "sync") + "/com.example.scale",
        ):
            mutated = copy.deepcopy(resource)
            sync_identifier(mutated)["system"] = system
            with self.subTest(system=system), self.assertRaisesRegex(
                ProducerValidationError, "native record Identifier system|absolute|extends its system"
            ):
                validate(mutated)

    def test_at_most_one_and_only_its_exact_type(self):
        resource = load("observation")
        repeated = copy.deepcopy(resource)
        second = copy.deepcopy(sync_identifier(resource))
        second["value"] = "another-reading"
        repeated["identifier"].append(second)
        with self.assertRaisesRegex(ProducerValidationError, "more than one readable sync"):
            validate(repeated)
        second_native = copy.deepcopy(resource)
        second_native["identifier"].append({"system": "https://store.example.org/other", "value": "other"})
        with self.assertRaisesRegex(ProducerValidationError, "more than one governed"):
            validate(second_native)
        untyped = copy.deepcopy(resource)
        del sync_identifier(untyped)["type"]
        with self.assertRaisesRegex(ProducerValidationError, "more than one governed"):
            validate(untyped)
        extra_coding = copy.deepcopy(resource)
        sync_identifier(extra_coding)["type"]["coding"].append({"system": "https://example.org/types", "code": "x"})
        with self.assertRaisesRegex(ProducerValidationError, "exactly its one type Coding"):
            validate(extra_coding)
        grove_role = copy.deepcopy(resource)
        sync_identifier(grove_role)["type"]["coding"].append({"system": ROLE_SYSTEM, "code": "writer-record"})
        with self.assertRaises(ProducerValidationError):
            validate(grove_role)

    def test_only_the_designated_healthkit_primary_carries_it(self):
        workout = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-workout",
                HEALTHKIT + "StructureDefinition/healthkit-observation",
            ]},
            "extension": [
                {"url": HEALTHKIT + "StructureDefinition/healthkit-source-type", "valueCode": "HKWorkoutTypeIdentifier"},
                {"url": context.WRITER_RECORD_VERSION_EXTENSION, "valueString": "1"},
            ],
            "identifier": copy.deepcopy(load("observation")["identifier"]),
        }
        segment = copy.deepcopy(workout)
        segment["meta"]["profile"][0] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-workout-segment"
        segment["identifier"] = [
            item for item in segment["identifier"]
            if coding(item).get("system") == ROLE_SYSTEM
        ]
        role(segment, "source-output")["value"] = "v0:test-key:1:" + "S" * 43
        validate(workout, segment)
        moved = copy.deepcopy(segment)
        moved["identifier"].extend([native_identifier(workout), sync_identifier(workout)])
        primary = copy.deepcopy(workout)
        primary["identifier"] = [item for item in primary["identifier"] if coding(item).get("system") == ROLE_SYSTEM]
        with self.assertRaisesRegex(ProducerValidationError, "catalog-designated"):
            validate(primary, moved)
        # A support resource never repeats the pair, and another adapter's output never carries it.
        with self.assertRaisesRegex(ProducerValidationError, "appear exactly once"):
            validate(workout, segment, {"resourceType": "Device", "identifier": [sync_identifier(workout)]})
        foreign = load("observation")
        foreign["extension"][0] = {
            "url": "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type",
            "valueCode": "WeightRecord",
        }
        with self.assertRaises(ProducerValidationError):
            validate(foreign)
        prescription = load("observation")
        prescription["resourceType"] = "VisionPrescription"
        with self.assertRaises(ProducerValidationError):
            validate(prescription)

    def test_sync_pair_is_never_a_metadata_entry(self):
        url = self.catalog["metadataExtension"]["url"]
        for key in ("HKMetadataKeySyncIdentifier", "HKMetadataKeySyncVersion"):
            for name in ("observation", "document"):
                resource = load(name)
                resource["extension"].append({"url": url, "extension": [{"url": "entry", "extension": [
                    {"url": "key", "valueString": key},
                    {"url": "value", "valueString": "scale-reading-0042"},
                ]}]})
                with self.subTest(key=key, fixture=name), self.assertRaisesRegex(ProducerValidationError, key):
                    validate_healthkit_metadata(resource, name)


if __name__ == "__main__":
    unittest.main()
