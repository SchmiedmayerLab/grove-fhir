"""Pin the cross-event binding policy without pretending to verify a production receiver."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import json
import unittest

from Scripts.receiver_lifecycle_fixtures import CORPUS, identity_sequences, observation, resources
from Tests.test_receiver_lifecycle import pair, role_pair
from Tests.test_revision_membership import writer_version


class OutputRecordBindingTests(unittest.TestCase):
    def setUp(self):
        self.bundles = resources()
        self.corpus = json.loads((CORPUS / "identity-sequences.json").read_text())

    def test_claims_share_output_and_writer_but_not_source_record(self):
        original, changed = (observation(self.bundles[name]) for name in ("multi-v2", "changed-source-record"))
        self.assertEqual(role_pair(original, "source-output"), role_pair(changed, "source-output"))
        self.assertEqual(role_pair(original, "writer-record"), role_pair(changed, "writer-record"))
        self.assertNotEqual(role_pair(original, "source-record"), role_pair(changed, "source-record"))
        self.assertGreater(int(writer_version(changed)), int(writer_version(original)))
        self.assertNotEqual(self.bundles["multi-v2"]["identifier"], self.bundles["changed-source-record"]["identifier"])
        # Each graph agrees internally. Only retained receiver history identifies the contradiction.
        for name in ("multi-v2", "changed-source-record"):
            bundle = self.bundles[name]
            self.assertEqual(sum(entry["resource"]["resourceType"] == "Observation" for entry in bundle["entry"]), 1)
            provenance = next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")
            self.assertEqual(pair(provenance["entity"][0]["what"]["identifier"]), role_pair(observation(bundle), "source-record"))

    def test_both_first_bindings_are_explicit_and_only_one_event_is_retained(self):
        self.assertEqual(self.corpus, identity_sequences())
        self.assertEqual(self.corpus["schemaVersion"], 0)
        self.assertEqual(len(self.corpus["sequences"]), 4)
        active_sequences = [sequence for sequence in self.corpus["sequences"] if sequence["id"].endswith("-binds-output-first")]
        self.assertEqual(len(active_sequences), 2)
        self.assertEqual({sequence["steps"][0]["event"] for sequence in active_sequences},
                         {"multi-v2", "changed-source-record"})
        for sequence in active_sequences:
            first, second, replay, retry = sequence["steps"]
            with self.subTest(sequence=sequence["id"]):
                self.assertNotEqual(first["event"], second["event"])
                self.assertEqual(first["event"], replay["event"])
                self.assertEqual(second, retry)
                self.assertEqual([step["expect"]["disposition"] for step in sequence["steps"]],
                                 ["accepted", "rejected", "replayed", "rejected"])
                for step in sequence["steps"]:
                    state = step["expect"]
                    self.assertEqual(state["history"], [first["event"]])
                    self.assertEqual(state["bindingEvent"], first["event"])
                    self.assertEqual(state["current"], [first["event"]])
                    self.assertEqual(state["retractionEvents"], [])
                    self.assertEqual(state["grants"], {"purpose-a": [first["event"]], "purpose-b": []})
                    self.assertEqual(state["receiptEvent"], None if state["disposition"] == "rejected" else first["event"])
                    self.assertEqual(state["reason"], "source-output-record-conflict" if state["disposition"] == "rejected" else None)

    def test_every_step_has_the_same_expectation_fields(self):
        fields = {
            "history", "bindingEvent", "current", "grants", "retractionEvents",
            "disposition", "receiptEvent", "reason",
        }
        for sequence in self.corpus["sequences"]:
            for index, step in enumerate(sequence["steps"]):
                with self.subTest(sequence=sequence["id"], step=index):
                    self.assertEqual(set(step["expect"]), fields)

    def test_retraction_claim_matches_original_record_but_not_changed_record(self):
        provenance = next(entry["resource"] for entry in self.bundles["retraction"]["entry"]
                          if entry["resource"]["resourceType"] == "Provenance")
        target = pair(provenance["target"][0]["identifier"])
        source = pair(provenance["entity"][0]["what"]["identifier"])
        for name in ("multi-v2", "changed-source-record"):
            self.assertEqual(target, role_pair(observation(self.bundles[name]), "source-output"))
        self.assertEqual(source, role_pair(observation(self.bundles["multi-v2"]), "source-record"))
        self.assertNotEqual(source, role_pair(observation(self.bundles["changed-source-record"]), "source-record"))

    def test_retraction_first_keeps_later_matching_target_suppressed_without_losing_receipts(self):
        sequences = {sequence["id"]: sequence["steps"] for sequence in self.corpus["sequences"]}
        steps = sequences["retraction-binds-before-active-claim"]
        self.assertEqual([step["event"] for step in steps],
                         ["retraction", "changed-source-record", "multi-v2", "multi-v2", "retraction", "changed-source-record"])
        self.assertEqual([step["expect"]["disposition"] for step in steps],
                         ["accepted", "rejected", "accepted", "replayed", "replayed", "rejected"])
        for index, step in enumerate(steps):
            state = step["expect"]
            self.assertEqual(state["bindingEvent"], "retraction")
            self.assertEqual(state["history"], ["retraction"] + (["multi-v2"] if index >= 2 else []))
            self.assertEqual(state["grants"], {"purpose-a": ["multi-v2"] if index >= 2 else [], "purpose-b": []})
            self.assertEqual(state["current"], [])
            self.assertEqual(state["retractionEvents"], ["retraction"])
            self.assertEqual(state["receiptEvent"], None if state["disposition"] == "rejected" else step["event"])
            self.assertEqual(state["reason"], "source-output-record-conflict" if state["disposition"] == "rejected" else None)

    def test_rejected_retraction_cannot_suppress_the_first_active_claim(self):
        sequence = next(sequence for sequence in self.corpus["sequences"]
                        if sequence["id"] == "active-binding-rejects-contradictory-retraction")
        self.assertEqual([step["event"] for step in sequence["steps"]],
                         ["changed-source-record", "retraction", "changed-source-record", "retraction"])
        self.assertEqual([step["expect"]["disposition"] for step in sequence["steps"]],
                         ["accepted", "rejected", "replayed", "rejected"])
        for step in sequence["steps"]:
            state = step["expect"]
            self.assertEqual(state["bindingEvent"], "changed-source-record")
            self.assertEqual(state["history"], ["changed-source-record"])
            self.assertEqual(state["current"], ["changed-source-record"])
            self.assertEqual(state["grants"], {"purpose-a": ["changed-source-record"], "purpose-b": []})
            self.assertEqual(state["retractionEvents"], [])
            self.assertEqual(state["receiptEvent"], None if state["disposition"] == "rejected" else "changed-source-record")
            self.assertEqual(state["reason"], "source-output-record-conflict" if state["disposition"] == "rejected" else None)

    def test_whole_sequence_requires_restart_replay_without_new_visibility(self):
        self.assertEqual(self.corpus["replayWholeSequence"], {
            "repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []
        })


if __name__ == "__main__":
    unittest.main()
