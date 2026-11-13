"""Consistency checks for receiver inputs and expectations, not a receiver implementation."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import hashlib
import json
import unittest

from Scripts.producer_validation import exchange_bundle
from Scripts.producer_validation.manifest import validate_manifest
from Scripts.producer_validation.io import json_pointer
from Scripts.receiver_lifecycle_fixtures import BASE, CORPUS, ROOT, VERSION, generated_files, observation, resources
from Tests.receiver_selection_reference import ENTRY_KEY, LIFECYCLE_EVENT_SYSTEM, bundle_versions, select


# The receiver-lifecycle Bundles, one alias each.
BUNDLES = {
    "original", "corrected", "altered-retry", "reformatted-retry", "lexeme-retry", "reconverted",
    "unordered-a", "unordered-b", "pending", "target", "retraction", "source-record-target-retraction",
    "multi-v1", "multi-v2", "multi-v3", "equal-version-later-recorded", "equal-version-reconversion",
    "equal-version-equal-recorded", "other-writer", "missing-order", "changed-source-record", "mixed-admission",
}
SEQUENCES = {
    "exact-and-conflicting-replay", "reformatted-replay", "lexeme-version-after-original",
    "lexeme-version-before-original", "correction-before-original", "original-before-correction",
    "unordered-later-recorded-first", "unordered-later-recorded-last", "reconversion-after-original",
    "reconversion-before-original", "pending-reference-resolution", "retraction-before-target",
    "retraction-after-target", "correction-before-retraction", "retraction-before-correction",
}
FIELDS = {"history", "versions", "current", "pending", "retracted", "visible", "newlyVisible", "references"}


def pair(identifier):
    return identifier["system"], identifier["value"]


def role_pair(resource, role):
    return pair(next(item for item in resource["identifier"] if item["type"]["coding"][0]["code"] == role))


def entry_keys(bundle, resource_type=None):
    """The (system, value) entry keys of a Bundle, in entry order, optionally of one resource type."""
    return [
        pair(next(item["valueIdentifier"] for item in entry["extension"] if item["url"] == ENTRY_KEY))
        for entry in bundle["entry"]
        if resource_type is None or entry["resource"]["resourceType"] == resource_type
    ]


def conversion(bundle):
    return next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")


def is_retraction(bundle):
    return any(
        coding.get("system") == LIFECYCLE_EVENT_SYSTEM
        for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"
        for coding in entry["resource"]["activity"]["coding"]
    )


class ReceiverLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.bundles = resources()
        self.corpus = json.loads((CORPUS / "sequences.json").read_text())
        self.sequences = {sequence["id"]: sequence["steps"] for sequence in self.corpus["sequences"]}

    def derived_current(self, history):
        """The current aliases the versionSelection set rule selects for one delivered history.

        Each source record selects one version; the first accepted content of a record-version
        key stays (an altered retry is never a version), and a retracted record has none.
        """
        retracted, by_key, by_record = set(), {}, {}
        for name in history:
            bundle = self.bundles[name]
            if is_retraction(bundle):
                retracted.update(
                    pair(entry["resource"]["entity"][0]["what"]["identifier"])
                    for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"
                )
                continue
            for record, version in bundle_versions(bundle, name):
                if version.key not in by_key:
                    by_key[version.key] = version
                    by_record.setdefault(record, []).append(version)
        return sorted(select(versions).name for record, versions in by_record.items() if record not in retracted)

    def test_generated_inputs_and_checksums_are_exact(self):
        for path, expected in generated_files().items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_text(), expected)
        self.assertFalse((CORPUS / "events.json").exists())
        index = json.loads((CORPUS / "bundles.json").read_text())
        lock = index["contractLock"]
        self.assertRegex(lock["baseSourceRevision"], r"^[0-9a-f]{40}$")
        self.assertNotEqual(lock["baseSourceRevision"], "928db16ef8bfd86d2a171727d2d1cb9f8979a442")
        self.assertEqual(lock["releaseVersion"], "0.8.0")
        self.assertEqual(lock["fhirVersion"], "4.0.1")
        self.assertEqual(lock["exchangeProtocolSHA256"], hashlib.sha256((ROOT / "catalog/exchange-protocol.json").read_bytes()).hexdigest())
        self.assertEqual(set(index["bundles"]), BUNDLES)
        self.assertEqual(set(self.bundles), BUNDLES)
        for name, item in index["bundles"].items():
            with self.subTest(bundle=name):
                content = (CORPUS / item["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), item["sha256"])
                bundle = json.loads(content)
                self.assertNotIn("identifier", bundle)
                self.assertNotIn("eventIdentity", item)
                # The lock names every record version by its Provenance entry key.
                self.assertEqual([pair(key) for key in item["recordVersions"]], entry_keys(bundle, "Provenance"))

    def test_protocol_rules_and_base_bundles_still_match_the_pinned_source(self):
        protocol = json.loads((ROOT / "catalog/exchange-protocol.json").read_text())
        del protocol["testVectors"]
        metadata = protocol["governedSourceIdentifier"]["validation"]["forbiddenIdentityUseEnforcement"]["untypedMetadata"]
        self.assertEqual(metadata, {
            "r4Paths": [],
            "matchRule": "no-untyped-carrier-admitted",
            "enforcement": "typed-healthkit-metadata-extension-and-no-automatic-native-uuid-copy",
        })
        # The metadata restoration changes only this carrier rule. Keep the original digest
        # guarding every other protocol rule and all source Bundles, rather than rebaselining them.
        metadata["matchRule"] = "no-generic-carrier-admitted"
        metadata["enforcement"] = "closed-adapter-metadata-allowlists-and-no-grove-generic-extension"
        rules = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(rules).hexdigest(), "bf408a97524fc62036ae40fdb7a37f98b0a0474eff51e6807e1877c3e06598a7")
        for name, digest in {
            "exchange-bundle.json": "62678f09d8288cbbbabf2f976750dd3dccf627fb6403ec96ec68ec66be918c12",
            "retraction-bundle.json": "02eef355417fcca1d8c0d6ed5def2f6349bae7fc8cf0625e7414b5c17461152b",
            "source-record-target-retraction-bundle.json": "bea24e01e77c180c8f7c69cb9fc90bfc5cddba375d949ca7646ae4929b3cafd3",
        }.items():
            self.assertEqual(hashlib.sha256((BASE / name).read_bytes()).hexdigest(), digest)

    def test_retries_and_lexemes_are_told_apart_by_the_record_version_key(self):
        def tokens(name):
            return json.loads((CORPUS / "resources" / f"{name}.json").read_text(), parse_int=str, parse_float=str)

        def raw(name):
            return (CORPUS / "resources" / f"{name}.json").read_bytes()

        original, reformatted, lexeme, altered = (
            tokens(name) for name in ("original", "reformatted-retry", "lexeme-retry", "altered-retry")
        )
        self.assertNotEqual(raw("original"), raw("reformatted-retry"))
        self.assertEqual(original, reformatted)
        self.assertNotEqual(original, lexeme)
        # Only the lexeme differs in the outputs, so a float reading cannot tell the two apart.
        self.assertEqual(observation(json.loads(raw("original"))), observation(json.loads(raw("lexeme-retry"))))
        self.assertNotEqual(original, altered)
        keys = {name: entry_keys(self.bundles[name], "Provenance") for name in ("original", "reformatted-retry", "lexeme-retry", "altered-retry")}
        # Member order changes no canonical byte, so the reformatted retry is the exact retry.
        self.assertEqual(keys["reformatted-retry"], keys["original"])
        # 72.0 for 72 changes the canonical bytes, so the lexeme retry is a new version.
        self.assertNotEqual(keys["lexeme-retry"], keys["original"])
        # The altered retry keeps the key over other tokens: a producer integrity failure.
        self.assertEqual(keys["altered-retry"], keys["original"])
        for name in ("reformatted-retry", "lexeme-retry", "altered-retry"):
            self.assertEqual(
                role_pair(observation(self.bundles[name]), "source-output"),
                role_pair(observation(self.bundles["original"]), "source-output"),
            )
        # The lexeme version keeps the original's recorded instant, so the tie-break orders them.
        self.assertEqual(conversion(self.bundles["lexeme-retry"])["recorded"], conversion(self.bundles["original"])["recorded"])
        altered_final = self.sequences["exact-and-conflicting-replay"][-1]["expect"]
        self.assertEqual(self.sequences["reformatted-replay"][-1]["expect"], altered_final)
        self.assertEqual(altered_final["versions"], ["original"])
        protocol = json.loads((ROOT / "catalog/exchange-protocol.json").read_text())
        self.assertEqual(set(protocol["payload"]["equality"]), {"formatting", "decimalLexeme", "alteredRetry", "vectors"})

    def test_lexeme_versions_reach_the_same_tie_break_in_both_arrival_orders(self):
        original, lexeme = (entry_keys(self.bundles[name], "Provenance")[0] for name in ("original", "lexeme-retry"))
        winner = "lexeme-retry" if lexeme[1].encode() > original[1].encode() else "original"
        for name in ("lexeme-version-after-original", "lexeme-version-before-original"):
            with self.subTest(sequence=name):
                final = self.sequences[name][-1]["expect"]
                self.assertEqual(set(final["versions"]), {"original", "lexeme-retry"})
                self.assertEqual(final["current"], [winner])
        self.assertEqual(
            [step["bundle"] for step in self.sequences["lexeme-version-after-original"]][:2], ["original", "lexeme-retry"]
        )
        self.assertEqual(
            [step["bundle"] for step in self.sequences["lexeme-version-before-original"]][:2], ["lexeme-retry", "original"]
        )

    def test_all_but_the_altered_retry_pass_the_structural_contract(self):
        _, paths = validate_manifest(CORPUS / "official-validator-manifest.json")
        self.assertEqual(len(paths), len(BUNDLES) - 1)
        self.assertEqual(set(paths), set((CORPUS / "resources").glob("*.json")) - {CORPUS / "resources/altered-retry.json"})
        for name, bundle in self.bundles.items():
            with self.subTest(bundle=name):
                codes = [item["code"] for item in exchange_bundle.exchange_bundle_diagnostics(bundle, name)]
                # Only the conformance kit can see the altered retry, by recomputing under the test key.
                self.assertEqual(codes, ["mobile-exchange.record-version-key"] if name == "altered-retry" else [])

    def test_writer_order_beats_recorded_and_cannot_be_replaced_by_float(self):
        original, corrected = (observation(self.bundles[name]) for name in ("original", "corrected"))
        versions = [next(item["valueString"] for item in value["extension"] if item["url"] == VERSION) for value in (original, corrected)]
        self.assertGreater(int(versions[1]), int(versions[0]))
        self.assertEqual(float(versions[1]), float(versions[0]))
        # The correction is recorded earlier, so only writer evidence makes it current.
        self.assertEqual(conversion(self.bundles["original"])["recorded"], "2026-08-20T17:30:02Z")
        self.assertEqual(conversion(self.bundles["corrected"])["recorded"], "2026-08-20T17:30:01Z")
        for role in ("writer-record", "source-record", "source-output"):
            self.assertEqual(role_pair(original, role), role_pair(corrected, role))
        output_url = conversion(self.bundles["original"])["target"][0]["reference"]
        self.assertEqual(output_url, conversion(self.bundles["corrected"])["target"][0]["reference"])
        self.assertNotEqual(entry_keys(self.bundles["original"], "Provenance"), entry_keys(self.bundles["corrected"], "Provenance"))
        for name in ("correction-before-original", "original-before-correction"):
            self.assertEqual(self.sequences[name][-1]["expect"]["current"], ["corrected"])

    def test_recorded_orders_versions_without_writer_evidence(self):
        for name in ("unordered-a", "unordered-b"):
            resource = observation(self.bundles[name])
            self.assertFalse(any(item["url"] == VERSION for item in resource["extension"]))
            self.assertFalse(any(item["type"]["coding"][0]["code"] == "writer-record" for item in resource["identifier"]))
        self.assertEqual(conversion(self.bundles["unordered-a"])["recorded"], "2026-08-20T17:30:05Z")
        self.assertEqual(conversion(self.bundles["unordered-b"])["recorded"], "2026-08-20T17:30:04Z")
        for name in ("unordered-later-recorded-first", "unordered-later-recorded-last"):
            self.assertEqual(self.sequences[name][-1]["expect"]["current"], ["unordered-a"])
        # A re-conversion is a later recorded version of the same source record.
        self.assertEqual(conversion(self.bundles["reconverted"])["recorded"], "2026-08-20T17:31:02Z")
        self.assertEqual(
            role_pair(observation(self.bundles["reconverted"]), "source-record"),
            role_pair(observation(self.bundles["original"]), "source-record"),
        )
        for name in ("reconversion-after-original", "reconversion-before-original"):
            self.assertEqual(self.sequences[name][-1]["expect"]["current"], ["reconverted"])

    def test_altered_retry_keeps_the_record_version_with_other_content(self):
        original, altered = self.bundles["original"], self.bundles["altered-retry"]
        self.assertEqual(entry_keys(original, "Provenance"), entry_keys(altered, "Provenance"))
        self.assertNotEqual(original, altered)
        self.assertNotEqual(observation(original), observation(altered))

    def test_pending_target_matches_identifier_without_replacing_the_referrer(self):
        pending, target = self.bundles["pending"], self.bundles["target"]
        self.assertFalse(any(entry["resource"]["resourceType"] == "QuestionnaireResponse" for entry in pending["entry"]))
        response = next(entry["resource"] for entry in target["entry"] if entry["resource"]["resourceType"] == "QuestionnaireResponse")
        reference = observation(pending)["derivedFrom"][0]
        logical = self.corpus["logicalReferences"]["questionnaire"]
        self.assertEqual(set(logical), {"sourceBundle", "referencePointer", "targetBundle", "targetPointer"})
        self.assertEqual(json_pointer(self.bundles[logical["sourceBundle"]], logical["referencePointer"], "referencePointer"), reference)
        self.assertEqual(json_pointer(self.bundles[logical["targetBundle"]], logical["targetPointer"], "targetPointer"), response)
        self.assertEqual(set(reference), {"type", "identifier"})
        self.assertEqual(reference["type"], "QuestionnaireResponse")
        self.assertEqual(pair(reference["identifier"]), pair(response["identifier"]))
        self.assertNotEqual(role_pair(observation(pending), "source-output"), role_pair(observation(target), "source-output"))
        self.assertNotEqual(role_pair(observation(pending), "source-record"), role_pair(observation(target), "source-record"))

    def test_mixed_admission_packs_two_records_that_keep_their_versions(self):
        mixed = self.bundles["mixed-admission"]
        self.assertEqual(
            set(entry_keys(mixed, "Provenance")),
            set(entry_keys(self.bundles["changed-source-record"], "Provenance") + entry_keys(self.bundles["target"], "Provenance")),
        )
        self.assertEqual(len(entry_keys(mixed, "Provenance")), 2)

    def test_retraction_reuses_the_pinned_logical_target(self):
        self.assertEqual(self.bundles["retraction"], json.loads((BASE / "retraction-bundle.json").read_text()))
        provenance = conversion(self.bundles["retraction"])
        target = provenance["target"][0]
        self.assertNotIn("reference", target)
        self.assertEqual(pair(target["identifier"]), role_pair(observation(self.bundles["original"]), "source-output"))
        self.assertEqual(
            pair(provenance["entity"][0]["what"]["identifier"]),
            role_pair(observation(self.bundles["original"]), "source-record"),
        )

    def test_retraction_suppresses_every_version_in_both_arrival_orders(self):
        for name, delivery in {
            "correction-before-retraction": ["corrected", "retraction", "original", "corrected"],
            "retraction-before-correction": ["retraction", "corrected", "original", "corrected"],
        }.items():
            with self.subTest(sequence=name):
                self.assertIn(name, self.sequences)
                steps = self.sequences[name]
                self.assertEqual([step["bundle"] for step in steps], delivery)
                for step in steps[delivery.index("retraction"):]:
                    self.assertEqual(step["expect"]["retracted"], ["original"])
                    self.assertEqual(step["expect"]["current"], [])
                    self.assertEqual(step["expect"]["visible"], [])
                    self.assertEqual(step["expect"]["newlyVisible"], [])
                self.assertEqual(set(steps[-1]["expect"]["versions"]), {"original", "corrected"})

    def test_declared_current_matches_the_reference_selection_rule(self):
        for name, steps in self.sequences.items():
            for index, step in enumerate(steps):
                with self.subTest(sequence=name, step=index):
                    self.assertEqual(step["expect"]["current"], self.derived_current(step["expect"]["history"]))

    def test_policy_follows_version_selection(self):
        policy = self.corpus["policy"]
        self.assertNotIn("conflict", policy)
        self.assertIn("versionSelection", policy["order"])
        self.assertIn("never un-retracted", policy["retraction"])
        self.assertNotIn("Reappearance", policy["retraction"])
        self.assertIn("every version", policy["arrays"])
        for clause in policy.values():
            if isinstance(clause, str):
                self.assertNotRegex(clause, r"\bevents?\b")

    def test_sequences_have_complete_monotonic_history_and_no_provisional_visibility(self):
        self.assertEqual(self.corpus["policy"]["visiblePurpose"], "purpose-a")
        self.assertEqual(self.corpus["policy"]["deniedPurposes"], ["purpose-b"])
        self.assertEqual(self.corpus["replayWholeSequence"], {
            "repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []
        })
        self.assertNotIn("events", self.corpus)
        self.assertNotIn("restored-producer", json.dumps(self.corpus))
        self.assertTrue(any(step.get("transport") == "restored-transport" for steps in self.sequences.values() for step in steps))
        self.assertEqual({sequence["id"] for sequence in self.corpus["sequences"]}, SEQUENCES)
        self.assertEqual(len(self.corpus["sequences"]), len(SEQUENCES))
        names = set(self.bundles)
        for sequence in self.corpus["sequences"]:
            previous_history, previous_versions, previous_visible = set(), set(), set()
            for index, step in enumerate(sequence["steps"]):
                with self.subTest(sequence=sequence["id"], step=index):
                    # A step may replay its Bundle through another authenticated transport.
                    self.assertEqual(set(step) - {"transport"}, {"bundle", "expect"})
                    self.assertEqual(step.get("transport", "restored-transport"), "restored-transport")
                    self.assertIn(step["bundle"], names)
                    self.assertEqual(set(step["expect"]), FIELDS)
                    references = step["expect"]["references"]
                    expected_references = {"questionnaire": "pending" if index == 0 else "resolved"} if sequence["id"] == "pending-reference-resolution" else {}
                    self.assertEqual(references, expected_references)
                    state = {key: set(value) for key, value in step["expect"].items() if key != "references"}
                    for key, values in state.items():
                        self.assertEqual(len(values), len(step["expect"][key]))
                        self.assertLessEqual(values, names)
                    self.assertLessEqual(previous_history, state["history"])
                    self.assertLessEqual(previous_versions, state["versions"])
                    self.assertLessEqual(state["versions"], state["history"])
                    self.assertLessEqual(state["current"], state["versions"])
                    self.assertLessEqual(state["pending"], state["versions"])
                    # A retraction addresses its whole source record (H26): no version of a
                    # retracted record is current, whatever source-output identity it carries.
                    retracted_records = {
                        role_pair(observation(self.bundles[name]), "source-record") for name in state["retracted"]
                    }
                    for name in state["current"] | state["visible"]:
                        self.assertNotIn(role_pair(observation(self.bundles[name]), "source-record"), retracted_records)
                    self.assertLessEqual(state["visible"], state["current"] - state["pending"])
                    self.assertEqual(state["newlyVisible"], state["visible"] - previous_visible)
                    previous_history, previous_versions, previous_visible = state["history"], state["versions"], state["visible"]


if __name__ == "__main__":
    unittest.main()
