"""Consistency checks for receiver inputs and expectations, not a receiver implementation."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import hashlib
import json
import unittest

from Scripts.producer_validation.manifest import validate_manifest
from Scripts.producer_validation.io import json_pointer
from Scripts.receiver_lifecycle_fixtures import BASE, CORPUS, ROOT, VERSION, generated_files, observation, resources


def pair(identifier):
    return identifier["system"], identifier["value"]


def role_pair(resource, role):
    return pair(next(item for item in resource["identifier"] if item["type"]["coding"][0]["code"] == role))


class ReceiverLifecycleTests(unittest.TestCase):
    def test_generated_inputs_and_checksums_are_exact(self):
        for path, expected in generated_files().items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_text(), expected)
        index = json.loads((CORPUS / "events.json").read_text())
        self.assertEqual(index["contractLock"]["baseSourceRevision"], "444e06fb25680c3af29e5d3ccbebeb0249be7318")
        self.assertEqual(index["contractLock"]["releaseVersion"], "0.6.0")
        self.assertEqual(index["contractLock"]["fhirVersion"], "4.0.1")
        self.assertEqual(index["contractLock"]["exchangeProtocolSHA256"], hashlib.sha256((ROOT / "catalog/exchange-protocol.json").read_bytes()).hexdigest())
        for event in index["events"].values():
            content = (CORPUS / event["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), event["sha256"])
            self.assertEqual(json.loads(content)["identifier"], event["eventIdentity"])

    def test_protocol_rules_and_base_events_still_match_the_pinned_source(self):
        protocol = json.loads((ROOT / "catalog/exchange-protocol.json").read_text())
        del protocol["testVectors"]
        rules = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(rules).hexdigest(), "d07e055cbabd12264045306fd215ebc477fa0401ca2a869fe0f7fe29338b5092")
        for name, digest in {
            "exchange-bundle.json": "94cc1e1f5d7aade571b2d59cff12ea0438d49e030deb43391e59cc8e9081d2b2",
            "retraction-bundle.json": "54085f51d0d7629bc5a556cb9ea2813b7c7d6defadb8f2d3340270bc88f5d226",
        }.items():
            self.assertEqual(hashlib.sha256((BASE / name).read_bytes()).hexdigest(), digest)

    def test_every_event_passes_the_existing_structural_contract(self):
        _, paths = validate_manifest(CORPUS / "official-validator-manifest.json")
        self.assertEqual(len(paths), 16)
        self.assertEqual(set(paths), set((CORPUS / "resources").glob("*.json")))

    def test_writer_order_cannot_be_replaced_by_sequence_time_or_float(self):
        bundles = resources()
        original, corrected = (observation(bundles[name]) for name in ("original", "corrected"))
        versions = [next(item["valueString"] for item in value["extension"] if item["url"] == VERSION) for value in (original, corrected)]
        self.assertGreater(int(versions[1]), int(versions[0]))
        self.assertEqual(float(versions[1]), float(versions[0]))
        self.assertLess(int(bundles["corrected"]["identifier"]["value"].split(":")[-1]), int(bundles["original"]["identifier"]["value"].split(":")[-1]))
        self.assertLess(corrected["issued"], original["issued"])
        for role in ("writer-record", "source-record", "source-output"):
            self.assertEqual(role_pair(original, role), role_pair(corrected, role))
        self.assertEqual(bundles["original"]["entry"][2]["fullUrl"], bundles["corrected"]["entry"][2]["fullUrl"])

    def test_changed_retry_is_a_different_payload_under_the_same_event(self):
        bundles = resources()
        self.assertEqual(bundles["original"]["identifier"], bundles["altered-retry"]["identifier"])
        self.assertNotEqual(bundles["original"], bundles["altered-retry"])
        for name in ("unordered-a", "unordered-b"):
            resource = observation(bundles[name])
            self.assertFalse(any(item["url"] == VERSION for item in resource["extension"]))
            self.assertFalse(any(item["type"]["coding"][0]["code"] == "writer-record" for item in resource["identifier"]))

    def test_pending_target_matches_identifier_without_replacing_the_referrer(self):
        bundles = resources()
        pending, target = bundles["pending"], bundles["target"]
        self.assertFalse(any(entry["resource"]["resourceType"] == "QuestionnaireResponse" for entry in pending["entry"]))
        response = next(entry["resource"] for entry in target["entry"] if entry["resource"]["resourceType"] == "QuestionnaireResponse")
        reference = observation(pending)["derivedFrom"][0]
        corpus = json.loads((CORPUS / "sequences.json").read_text())
        logical = corpus["logicalReferences"]["questionnaire"]
        self.assertEqual(json_pointer(bundles[logical["sourceEvent"]], logical["referencePointer"], "referencePointer"), reference)
        self.assertEqual(json_pointer(bundles[logical["targetEvent"]], logical["targetPointer"], "targetPointer"), response)
        self.assertEqual(set(reference), {"type", "identifier"})
        self.assertEqual(reference["type"], "QuestionnaireResponse")
        self.assertEqual(pair(reference["identifier"]), pair(response["identifier"]))
        self.assertNotEqual(role_pair(observation(pending), "source-output"), role_pair(observation(target), "source-output"))

    def test_retraction_reuses_the_pinned_logical_target(self):
        bundles = resources()
        self.assertEqual(bundles["retraction"], json.loads((BASE / "retraction-bundle.json").read_text()))
        target = bundles["retraction"]["entry"][0]["resource"]["target"][0]
        self.assertNotIn("reference", target)
        self.assertEqual(pair(target["identifier"]), role_pair(observation(bundles["original"]), "source-output"))

    def test_retraction_suppresses_corrections_in_both_arrival_orders(self):
        corpus = json.loads((CORPUS / "sequences.json").read_text())
        sequences = {sequence["id"]: sequence for sequence in corpus["sequences"]}
        for name, delivery in {
            "correction-before-retraction": ["corrected", "retraction", "original", "corrected"],
            "retraction-before-correction": ["retraction", "corrected", "original", "corrected"],
        }.items():
            with self.subTest(sequence=name):
                self.assertIn(name, sequences)
                steps = sequences[name]["steps"]
                self.assertEqual([step["event"] for step in steps], delivery)
                for step in steps[delivery.index("retraction"):]:
                    self.assertEqual(step["expect"]["retracted"], ["original"])
                    self.assertEqual(step["expect"]["current"], [])
                    self.assertEqual(step["expect"]["visible"], [])
                    self.assertEqual(step["expect"]["newlyVisible"], [])
                self.assertEqual(set(steps[-1]["expect"]["versions"]), {"original", "corrected"})

    def test_sequences_have_complete_monotonic_history_and_no_provisional_visibility(self):
        corpus = json.loads((CORPUS / "sequences.json").read_text())
        self.assertEqual(corpus["policy"]["visiblePurpose"], "purpose-a")
        self.assertEqual(corpus["policy"]["deniedPurposes"], ["purpose-b"])
        self.assertEqual(corpus["replayWholeSequence"], {
            "repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []
        })
        self.assertEqual(corpus["logicalReferences"], {"questionnaire": {
            "sourceEvent": "pending", "referencePointer": "/entry/2/resource/derivedFrom/0",
            "targetEvent": "target", "targetPointer": "/entry/4/resource"
        }})
        expected_ids = {"exact-and-conflicting-replay", "correction-before-original", "original-before-correction", "unordered-conflict", "pending-reference-resolution", "retraction-before-target", "retraction-after-target", "correction-before-retraction", "retraction-before-correction"}
        self.assertEqual({sequence["id"] for sequence in corpus["sequences"]}, expected_ids)
        self.assertEqual(len(corpus["sequences"]), len(expected_ids))
        fields = {"history", "versions", "current", "pending", "retracted", "conflicts", "visible", "newlyVisible", "references"}
        bundles = resources()
        names = set(bundles)
        for sequence in corpus["sequences"]:
            previous_history, previous_versions, previous_visible = set(), set(), set()
            for index, step in enumerate(sequence["steps"]):
                with self.subTest(sequence=sequence["id"], step=index):
                    self.assertIn(step["event"], names)
                    self.assertEqual(set(step["expect"]), fields)
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
                    self.assertLessEqual(state["pending"] | state["conflicts"], state["versions"])
                    retracted_outputs = {
                        role_pair(observation(bundles[name]), "source-output") for name in state["retracted"]
                    }
                    # Tombstones address logical outputs, not one event alias. A corrected
                    # event keeps that output identity and must not escape an older tombstone.
                    for name in state["current"] | state["visible"]:
                        self.assertNotIn(role_pair(observation(bundles[name]), "source-output"), retracted_outputs)
                    self.assertLessEqual(state["visible"], state["current"] - state["pending"] - state["conflicts"])
                    self.assertEqual(state["newlyVisible"], state["visible"] - previous_visible)
                    previous_history, previous_versions, previous_visible = state["history"], state["versions"], state["visible"]


if __name__ == "__main__":
    unittest.main()
