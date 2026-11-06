"""Record-centric exchange Bundles: records, shared nodes, record versions, and retractions."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from decimal import Decimal
from typing import Any

from Scripts.producer_validation import exchange_bundle
from Tests.producer_validation_test_support import (
    CONTEXT_SNAPSHOT_EXTENSION,
    ENTRY_KEY_EXTENSION,
    EXCHANGE_BUNDLE_PROFILE,
    ProducerValidationTestCase,
    RECORD_VERSION_EXTENSION,
    ROOT,
    copy,
    entry_full_url,
    entry_key,
    identifier_role,
    is_retraction_provenance,
    json,
    key_system,
    provenances,
    record_unit,
    rekey_records,
    retraction_bundle,
    source_record_pair,
    two_record_bundle,
    typed_identifier,
)


RETRACTION_BASE = ROOT / "Conformance/corpora/mobile-exchange/retraction-bundle.json"


def entries_of(bundle: dict[str, Any], resource_type: str) -> list[dict[str, Any]]:
    return [entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == resource_type]


class RecordBundleTests(ProducerValidationTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.active = two_record_bundle()
        self.conversions = [entry for entry in provenances(self.active)]
        self.outputs = entries_of(self.active, "Observation")

    def codes(self, bundle: dict[str, Any], label: str = "Bundle") -> list[str]:
        return [item["code"] for item in exchange_bundle.exchange_bundle_diagnostics(bundle, label)]

    def assert_code(self, bundle: dict[str, Any], *codes: str) -> None:
        actual = self.codes(bundle)
        self.assertEqual(len(actual), 1, actual)
        self.assertIn(actual[0], codes)

    def output_of(self, provenance: dict[str, Any]) -> dict[str, Any]:
        url = provenance["resource"]["target"][0]["reference"]
        return next(entry for entry in self.active["entry"] if entry["fullUrl"] == url)

    def test_the_rekey_helper_reproduces_the_record_version_vectors(self) -> None:
        # The spec's P' and O, keyed as one record: the helper every negative case relies on
        # mints exactly the published record-version keys and fullUrls.
        from Tests.test_exchange_protocol import RECORD_CONTENT_OUTPUT, RECORD_CONTENT_PROVENANCE, RECORD_VERSIONS

        for name, value in (("heart-rate-72", 72), ("heart-rate-72-0", Decimal("72.0"))):
            output = json.loads(RECORD_CONTENT_OUTPUT)
            output["valueQuantity"]["value"] = value
            source_output = next(item for item in output["identifier"] if identifier_role(item) == "source-output")
            bundle = {"resourceType": "Bundle", "entry": [
                {
                    "extension": [{"url": ENTRY_KEY_EXTENSION, "valueIdentifier": copy.deepcopy(source_output)}],
                    "fullUrl": "urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5",
                    "resource": output,
                },
                {
                    "extension": [{"url": ENTRY_KEY_EXTENSION, "valueIdentifier": typed_identifier(
                        "record-version", key_system("record-version"), "v0:test-key:1:" + "A" * 43
                    )}],
                    "fullUrl": "urn:uuid:00000000-0000-5000-8000-000000000000",
                    "resource": {"id": "not-in-the-digest", **json.loads(RECORD_CONTENT_PROVENANCE)},
                },
            ]}
            rekey_records(bundle, subject=("https://study.example.org/fhir/identifiers/participant", "participant-001"))
            provenance = bundle["entry"][1]
            with self.subTest(vector=name):
                self.assertEqual((entry_key(provenance)["value"], provenance["fullUrl"]), RECORD_VERSIONS[name])
                self.assertEqual(
                    provenance["resource"]["extension"],
                    [{"url": RECORD_VERSION_EXTENSION, "valueIdentifier": entry_key(provenance)}],
                )

    # Records and shared nodes

    def test_records_share_their_nodes_and_pass(self) -> None:
        self.assertNotIn("identifier", self.active)
        self.assertGreaterEqual(len(self.conversions), 2)
        sources = {
            json.dumps(entry["resource"]["entity"][0]["what"]["identifier"], sort_keys=True)
            for entry in self.conversions
        }
        self.assertEqual(len(sources), len(self.conversions))
        urls = [entry["fullUrl"] for entry in self.active["entry"]]
        self.assertEqual(len(urls), len(set(urls)))
        units = [record_unit(self.active, entry) for entry in self.conversions]
        shared = set.intersection(*units)
        # Patient and the application Device lie in every record unit and appear once.
        for resource_type in ("Patient", "Device"):
            with self.subTest(shared=resource_type):
                self.assertTrue({entry["fullUrl"] for entry in entries_of(self.active, resource_type)} & shared)
        self.assertEqual(set.union(*units), set(urls))
        self.assertEqual(self.codes(self.active), [])

    def test_bundle_identifier_is_an_optional_untyped_transport_id(self) -> None:
        transported = copy.deepcopy(self.active)
        transported["identifier"] = {
            "system": "urn:ietf:rfc:3986", "value": "urn:uuid:5d0f6f2a-7f3d-4e1f-9a38-0b52a1f7c0de"
        }
        self.assertEqual(self.codes(transported), [])
        # No format: a value without a system is admitted, as the Bundle profiles admit it.
        unformatted = copy.deepcopy(self.active)
        unformatted["identifier"] = {"value": "upload-1"}
        self.assertEqual(self.codes(unformatted), [])
        typed = copy.deepcopy(self.active)
        typed["identifier"] = typed_identifier(
            "record-version", key_system("record-version"), entry_key(self.conversions[0])["value"]
        )
        self.assertEqual(self.codes(typed), ["mobile-exchange.bundle-identifier"])
        # Untyped: a type outside the Grove identifier roles is refused as well.
        other_typed = copy.deepcopy(self.active)
        other_typed["identifier"] = {
            "type": {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "RI"}
                ]
            },
            "system": "urn:ietf:rfc:3986",
            "value": "urn:uuid:5d0f6f2a-7f3d-4e1f-9a38-0b52a1f7c0de",
        }
        self.assertEqual(self.codes(other_typed), ["mobile-exchange.bundle-identifier"])

    def test_packing_time_and_repacking_change_no_record_version(self) -> None:
        keys = {entry_key(entry)["value"] for entry in self.conversions}
        repacked = copy.deepcopy(self.active)
        repacked["timestamp"] = "2026-08-22T00:00:00Z"
        self.assertEqual(self.codes(repacked), [])
        self.assertEqual({entry_key(entry)["value"] for entry in provenances(repacked)}, keys)
        # Each record packed alone, with only the shared nodes its unit reaches, keeps its key.
        for provenance in self.conversions:
            unit = record_unit(self.active, provenance)
            alone = copy.deepcopy(self.active)
            alone["entry"] = [entry for entry in alone["entry"] if entry["fullUrl"] in unit]
            with self.subTest(record=provenance["fullUrl"]):
                self.assertEqual(self.codes(alone), [])
                self.assertEqual(rekey_records(copy.deepcopy(alone)), alone)
                self.assertIn(entry_key(provenances(alone)[0])["value"], keys)

    def test_every_output_is_targeted_by_exactly_one_conversion_provenance(self) -> None:
        repeated = copy.deepcopy(self.active)
        target = provenances(repeated)[0]["resource"]["target"]
        target.append(copy.deepcopy(target[0]))
        self.assert_code(rekey_records(repeated), "mobile-exchange.output-targeted-once")

        twice = copy.deepcopy(self.active)
        first, second = provenances(twice)[:2]
        second["resource"]["target"].append(copy.deepcopy(first["resource"]["target"][0]))
        self.assert_code(
            rekey_records(twice), "mobile-exchange.output-targeted-once", "mobile-exchange.provenance-targets"
        )

        never = copy.deepcopy(self.active)
        never["entry"].remove(provenances(never)[1])
        self.assert_code(
            never,
            "mobile-exchange.output-targeted-once",
            "mobile-exchange.transform-provenance",
            "mobile-exchange.provenance-targets",
        )

    def test_two_versions_of_one_source_record_travel_in_different_bundles(self) -> None:
        bundle = copy.deepcopy(self.active)
        first, second = provenances(bundle)[:2]
        source = copy.deepcopy(first["resource"]["entity"][0]["what"]["identifier"])
        second["resource"]["entity"][0]["what"]["identifier"] = copy.deepcopy(source)
        output = next(entry for entry in bundle["entry"] if entry["fullUrl"] == second["resource"]["target"][0]["reference"])
        output["resource"]["identifier"] = [
            copy.deepcopy(source) if identifier_role(item) == "source-record" else item
            for item in output["resource"]["identifier"]
        ]
        self.assert_code(rekey_records(bundle), "mobile-exchange.distinct-source-record")

    def test_references_between_records_are_identifier_only(self) -> None:
        literal = copy.deepcopy(self.active)
        first, second = provenances(literal)[:2]
        other = first["resource"]["target"][0]["reference"]
        output = next(entry for entry in literal["entry"] if entry["fullUrl"] == second["resource"]["target"][0]["reference"])
        output["resource"].setdefault("derivedFrom", []).append({"reference": other})
        self.assert_code(rekey_records(literal), "mobile-exchange.cross-record-reference")

        logical = copy.deepcopy(self.active)
        first, second = provenances(logical)[:2]
        target = next(entry for entry in logical["entry"] if entry["fullUrl"] == first["resource"]["target"][0]["reference"])
        output = next(entry for entry in logical["entry"] if entry["fullUrl"] == second["resource"]["target"][0]["reference"])
        identifier = next(item for item in target["resource"]["identifier"] if identifier_role(item) == "source-output")
        output["resource"].setdefault("derivedFrom", []).append(
            {"type": "Observation", "identifier": copy.deepcopy(identifier)}
        )
        self.assertEqual(self.codes(rekey_records(logical)), [])

    def test_every_record_of_a_bundle_states_one_subject(self) -> None:
        bundle = copy.deepcopy(self.active)
        output = next(
            entry for entry in bundle["entry"]
            if entry["fullUrl"] == provenances(bundle)[1]["resource"]["target"][0]["reference"]
        )
        output["resource"]["subject"] = {
            "type": "Patient",
            "identifier": {"system": "https://study.example.org/fhir/identifiers/participant", "value": "participant-002"},
        }
        self.assert_code(rekey_records(bundle), "mobile-exchange.single-subject")

    def test_supporting_nodes_are_connected_by_directed_record_units(self) -> None:
        bundle = copy.deepcopy(self.active)
        device = copy.deepcopy(entries_of(bundle, "Device")[0])
        device["fullUrl"] = "urn:uuid:00000000-0000-5000-8000-0000000000ff"
        entry_key(device)["value"] = "v0:test-key:1:" + "A" * 43
        device["resource"]["deviceName"] = [{"type": "user-friendly-name", "name": "Unreferenced"}]
        # The orphan references the shared Device, so it is connected only undirected (H10).
        device["resource"]["parent"] = {"reference": entries_of(bundle, "Device")[0]["fullUrl"]}
        bundle["entry"].append(device)
        self.assert_code(rekey_records(bundle), "mobile-support.connected")

    # Content and record keys

    def test_tampered_content_snapshots_fail_the_recompute(self) -> None:
        for resource_type in ("Device", "Patient", "QuestionnaireResponse"):
            with self.subTest(node=resource_type):
                tampered = copy.deepcopy(self.active)
                node = entries_of(tampered, resource_type)[0]["resource"]
                node["meta"] = {**node.get("meta", {}), "tag": [{"system": "https://example.org/tag", "code": "changed"}]}
                self.assert_code(tampered, "mobile-exchange.content-snapshot-key")

    def test_record_version_key_covers_the_outputs_and_the_provenance(self) -> None:
        changed_output = copy.deepcopy(self.active)
        output = next(
            entry for entry in changed_output["entry"]
            if entry["fullUrl"] == provenances(changed_output)[0]["resource"]["target"][0]["reference"]
        )
        output["resource"]["valueQuantity"]["value"] = 99
        self.assert_code(changed_output, "mobile-exchange.record-version-key")

        changed_provenance = copy.deepcopy(self.active)
        provenances(changed_provenance)[0]["resource"]["recorded"] = "2026-08-20T17:31:02Z"
        self.assert_code(changed_provenance, "mobile-exchange.record-version-key")

        wrong_role = copy.deepcopy(self.active)
        key = entry_key(provenances(wrong_role)[0])
        key.update(typed_identifier("source-output", key_system("source-output"), key["value"]))
        provenance = provenances(wrong_role)[0]
        provenance["fullUrl"] = entry_full_url(key["system"], key["value"])
        # The extension still repeats the entry key, so only the key's role is wrong.
        for extension in provenance["resource"]["extension"]:
            if extension["url"] == RECORD_VERSION_EXTENSION:
                extension["valueIdentifier"] = copy.deepcopy(key)
        self.assert_code(wrong_role, "mobile-exchange.entry-key-selection")

    def test_a_record_version_is_recomputed_only_under_the_test_key(self) -> None:
        bundle = copy.deepcopy(self.active)
        provenance = provenances(bundle)[0]
        key = entry_key(provenance)
        # A production key cannot be recomputed, so only its shape is checked.
        key["system"] = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/production-key/1"
        key["value"] = "v0:production-key:1:" + key["value"].rsplit(":", 1)[1]
        provenance["fullUrl"] = entry_full_url(key["system"], key["value"])
        for extension in provenance["resource"]["extension"]:
            if extension["url"] == RECORD_VERSION_EXTENSION:
                extension["valueIdentifier"] = copy.deepcopy(key)
        self.assertEqual(self.codes(bundle), [])

    def test_decimal_lexemes_are_part_of_the_record_version(self) -> None:
        lexeme = copy.deepcopy(self.active)
        output = next(
            entry for entry in lexeme["entry"]
            if entry["fullUrl"] == provenances(lexeme)[0]["resource"]["target"][0]["reference"]
        )
        integer = output["resource"]["valueQuantity"]["value"]
        self.assertIsInstance(integer, int)
        output["resource"]["valueQuantity"]["value"] = Decimal(f"{integer}.0")
        rekey_records(lexeme)
        before, after = entry_key(self.conversions[0]), entry_key(provenances(lexeme)[0])
        self.assertEqual(before["system"], after["system"])
        self.assertNotEqual(before["value"], after["value"])
        # The output fullUrl is the same in every version; the Provenance fullUrl names the version.
        self.assertEqual(output["fullUrl"], self.output_of(self.conversions[0])["fullUrl"])
        self.assertNotEqual(provenances(lexeme)[0]["fullUrl"], self.conversions[0]["fullUrl"])

    def test_conversion_provenance_repeats_its_record_version(self) -> None:
        for provenance in self.conversions:
            extensions = [
                item for item in provenance["resource"]["extension"] if item["url"] == RECORD_VERSION_EXTENSION
            ]
            with self.subTest(provenance=provenance["fullUrl"]):
                self.assertEqual(len(extensions), 1)
                self.assertEqual(
                    (extensions[0]["valueIdentifier"]["system"], extensions[0]["valueIdentifier"]["value"]),
                    (entry_key(provenance)["system"], entry_key(provenance)["value"]),
                )

        missing = copy.deepcopy(self.active)
        resource = provenances(missing)[0]["resource"]
        resource["extension"] = [item for item in resource["extension"] if item["url"] != RECORD_VERSION_EXTENSION]
        if not resource["extension"]:
            del resource["extension"]
        self.assert_code(missing, "mobile-exchange.record-version-extension")

        mismatch = copy.deepcopy(self.active)
        first, second = provenances(mismatch)[:2]
        for extension in first["resource"]["extension"]:
            if extension["url"] == RECORD_VERSION_EXTENSION:
                extension["valueIdentifier"] = copy.deepcopy(entry_key(second))
        self.assert_code(mismatch, "mobile-exchange.record-version-extension")

        twice = copy.deepcopy(self.active)
        resource = provenances(twice)[0]["resource"]
        resource["extension"].append(copy.deepcopy(
            next(item for item in resource["extension"] if item["url"] == RECORD_VERSION_EXTENSION)
        ))
        self.assert_code(twice, "mobile-exchange.record-version-extension")

    def test_questionnaire_response_repeats_its_context_snapshot(self) -> None:
        response = entries_of(self.active, "QuestionnaireResponse")[0]
        extensions = [item for item in response["resource"]["extension"] if item["url"] == CONTEXT_SNAPSHOT_EXTENSION]
        self.assertEqual(len(extensions), 1)
        self.assertEqual(identifier_role(entry_key(response)), "context-snapshot")
        self.assertEqual(
            (extensions[0]["valueIdentifier"]["system"], extensions[0]["valueIdentifier"]["value"]),
            (entry_key(response)["system"], entry_key(response)["value"]),
        )
        # Its one R4 identifier stays the submission's business identifier.
        self.assertIsNone(identifier_role(response["resource"]["identifier"]))

        missing = copy.deepcopy(self.active)
        resource = entries_of(missing, "QuestionnaireResponse")[0]["resource"]
        resource["extension"] = [item for item in resource["extension"] if item["url"] != CONTEXT_SNAPSHOT_EXTENSION]
        self.assert_code(missing, "mobile-exchange.context-snapshot-extension")

        mismatch = copy.deepcopy(self.active)
        resource = entries_of(mismatch, "QuestionnaireResponse")[0]["resource"]
        for extension in resource["extension"]:
            if extension["url"] == CONTEXT_SNAPSHOT_EXTENSION:
                extension["valueIdentifier"] = copy.deepcopy(entry_key(entries_of(mismatch, "Patient")[0]))
        self.assert_code(mismatch, "mobile-exchange.context-snapshot-extension")

        elsewhere = copy.deepcopy(self.active)
        patient = entries_of(elsewhere, "Patient")[0]
        patient["resource"]["extension"] = [
            {"url": CONTEXT_SNAPSHOT_EXTENSION, "valueIdentifier": copy.deepcopy(entry_key(patient))}
        ]
        self.assert_code(rekey_records(elsewhere), "mobile-exchange.context-snapshot-extension")

    def test_every_resource_of_a_record_canonicalizes(self) -> None:
        bundle = copy.deepcopy(self.active)
        output = self.output_of(provenances(bundle)[0])
        output = next(entry for entry in bundle["entry"] if entry["fullUrl"] == output["fullUrl"])
        # grove-canonical-json-v0 refuses a member name above U+007F (H27).
        output["resource"]["valueQuantity"]["é"] = 1
        self.assert_code(bundle, "mobile-exchange.canonical-json")

    # Retraction Bundles

    def test_a_retraction_bundle_carries_one_keyed_provenance_per_source_record(self) -> None:
        base = json.loads(RETRACTION_BASE.read_text(encoding="utf-8"))
        for bundle in (base, retraction_bundle(self.active)):
            retractions = provenances(bundle)
            with self.subTest(bundle=bundle.get("id", "built")):
                self.assertNotIn("identifier", bundle)
                self.assertGreaterEqual(len(retractions), 2)
                self.assertEqual(self.codes(bundle, "retraction"), [])
                for provenance in retractions:
                    self.assertTrue(is_retraction_provenance(provenance["resource"]))
                    self.assertEqual(identifier_role(entry_key(provenance)), "record-retraction")
                    # A retraction Provenance carries its key on the entry alone.
                    self.assertFalse(any(
                        item.get("url") == RECORD_VERSION_EXTENSION
                        for item in provenance["resource"].get("extension", [])
                    ))
                self.assertEqual(
                    len({entry_key(provenance)["value"] for provenance in retractions}), len(retractions)
                )
                # The assembler is the shared application Device, carried once and never retracted.
                devices = entries_of(bundle, "Device")
                self.assertEqual(len(devices), len({entry["fullUrl"] for entry in devices}))
                for provenance in retractions:
                    self.assertIn(
                        provenance["resource"]["agent"][0]["who"].get("reference"),
                        {entry["fullUrl"] for entry in devices},
                    )

    def test_retraction_key_is_a_function_of_the_source_record_alone(self) -> None:
        bundle = retraction_bundle(self.active)
        later = copy.deepcopy(bundle)
        for provenance in provenances(later):
            provenance["resource"]["recorded"] = "2026-08-22T08:00:01Z"
            provenance["resource"]["occurredDateTime"] = "2026-08-22T08:00:00Z"
        self.assertEqual(
            [entry_key(entry)["value"] for entry in provenances(rekey_records(later))],
            [entry_key(entry)["value"] for entry in provenances(bundle)],
        )
        mismatch = copy.deepcopy(bundle)
        first, second = provenances(mismatch)[:2]
        source = copy.deepcopy(second["resource"]["entity"][0]["what"]["identifier"])
        first["resource"]["entity"][0]["what"]["identifier"] = source
        first["resource"]["target"][0]["identifier"] = copy.deepcopy(source)
        self.assert_code(
            mismatch, "mobile-retraction.retraction-key", "mobile-retraction.provenance",
            "mobile-exchange.distinct-entry-key",
        )
        other = copy.deepcopy(bundle)
        other_source, _ = source_record_pair("record-never-converted")
        provenance = provenances(other)[0]["resource"]
        provenance["entity"][0]["what"]["identifier"] = copy.deepcopy(other_source)
        provenance["target"][0]["identifier"] = copy.deepcopy(other_source)
        self.assert_code(other, "mobile-retraction.retraction-key")

    def test_one_source_record_is_retracted_once_per_bundle(self) -> None:
        bundle = retraction_bundle(self.active)
        duplicate = copy.deepcopy(provenances(bundle)[0])
        duplicate["resource"]["id"] = "retraction-duplicate"
        duplicate["resource"]["recorded"] = "2026-08-21T09:00:01Z"
        bundle["entry"].append(duplicate)
        self.assert_code(bundle, "mobile-retraction.provenance", "mobile-exchange.distinct-entry-key")

    def test_a_retraction_provenance_carries_no_record_version(self) -> None:
        bundle = retraction_bundle(self.active)
        provenance = provenances(bundle)[0]
        provenance["resource"]["extension"] = [
            {"url": RECORD_VERSION_EXTENSION, "valueIdentifier": copy.deepcopy(entry_key(provenance))}
        ]
        self.assert_code(bundle, "mobile-exchange.record-version-extension")

    def test_devices_are_never_retraction_targets(self) -> None:
        bundle = retraction_bundle(self.active)
        device = entries_of(bundle, "Device")[0]
        snapshot = next(item for item in device["resource"]["identifier"] if identifier_role(item) == "device-snapshot")
        provenance = provenances(bundle)[0]["resource"]
        provenance["target"] = [{
            "extension": [{
                "url": "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role",
                "valueCode": "device-snapshot",
            }],
            "type": "Device",
            "identifier": copy.deepcopy(snapshot),
        }]
        self.assert_code(bundle, "mobile-retraction.target-role", "mobile-retraction.role-target-type")

    def test_the_two_bundle_profiles_are_never_mixed(self) -> None:
        both = copy.deepcopy(self.active)
        both["meta"]["profile"].append(
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-retraction-bundle"
        )
        self.assert_code(both, "mobile-exchange.bundle-profile")

        # An active Bundle carries no retraction Provenance (catalog transform-provenance); its
        # Provenance profile or key-role check (provenanceKey.active) may refuse it first.
        active_with_retraction = copy.deepcopy(self.active)
        active_with_retraction["entry"].append(copy.deepcopy(provenances(retraction_bundle(self.active))[0]))
        self.assert_code(
            active_with_retraction,
            "mobile-exchange.transform-provenance",
            "mobile-exchange.provenance-profile",
            "mobile-exchange.entry-key-selection",
        )

        # A retraction Bundle carries no transform Provenance (catalog mobile-retraction.provenance).
        retraction_with_conversion = retraction_bundle(self.active)
        retraction_with_conversion["entry"].append(copy.deepcopy(self.conversions[0]))
        self.assertNotEqual(self.codes(retraction_with_conversion), [])
        self.assertEqual(self.active["meta"]["profile"], [EXCHANGE_BUNDLE_PROFILE])
