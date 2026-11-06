"""Pin the cross-record binding policy without pretending to verify a production receiver."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import json
import unittest

from Scripts.receiver_lifecycle_fixtures import CORPUS, identity_sequences, observation, resources
from Tests.test_receiver_lifecycle import entry_keys, pair, role_pair
from Tests.test_revision_membership import writer_version


FIELDS = {
    "history", "bindingBundle", "current", "grants", "retractionBundles",
    "disposition", "rejectedRecords", "receiptBundle", "reason",
}


class OutputRecordBindingTests(unittest.TestCase):
    def setUp(self):
        self.bundles = resources()
        self.corpus = json.loads((CORPUS / "identity-sequences.json").read_text())
        self.sequences = {sequence["id"]: sequence["steps"] for sequence in self.corpus["sequences"]}

    def test_claims_share_output_and_writer_but_not_source_record(self):
        original, changed = (observation(self.bundles[name]) for name in ("multi-v2", "changed-source-record"))
        self.assertEqual(role_pair(original, "source-output"), role_pair(changed, "source-output"))
        self.assertEqual(role_pair(original, "writer-record"), role_pair(changed, "writer-record"))
        self.assertNotEqual(role_pair(original, "source-record"), role_pair(changed, "source-record"))
        self.assertGreater(int(writer_version(changed)), int(writer_version(original)))
        self.assertNotEqual(entry_keys(self.bundles["multi-v2"]), entry_keys(self.bundles["changed-source-record"]))
        # Each record agrees internally. Only retained receiver history identifies the contradiction.
        for name in ("multi-v2", "changed-source-record"):
            bundle = self.bundles[name]
            self.assertEqual(sum(entry["resource"]["resourceType"] == "Observation" for entry in bundle["entry"]), 1)
            provenance = next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")
            self.assertEqual(pair(provenance["entity"][0]["what"]["identifier"]), role_pair(observation(bundle), "source-record"))

    def test_both_first_bindings_are_explicit_and_only_one_record_is_retained(self):
        self.assertEqual(self.corpus, identity_sequences())
        self.assertEqual(self.corpus["schemaVersion"], 0)
        self.assertNotIn("events", self.corpus)
        self.assertLessEqual(
            {"typed-retraction-binds-no-output", "retraction-after-contradictory-claim"}, set(self.sequences)
        )
        for removed in ("retraction-binds-before-active-claim", "active-binding-rejects-contradictory-retraction"):
            self.assertNotIn(removed, self.sequences)
        active_sequences = [sequence for sequence in self.corpus["sequences"] if sequence["id"].endswith("-binds-output-first")]
        self.assertEqual(len(active_sequences), 2)
        self.assertEqual({sequence["steps"][0]["bundle"] for sequence in active_sequences},
                         {"multi-v2", "changed-source-record"})
        for sequence in active_sequences:
            first, second, replay, retry = sequence["steps"]
            with self.subTest(sequence=sequence["id"]):
                self.assertNotEqual(first["bundle"], second["bundle"])
                self.assertEqual(first["bundle"], replay["bundle"])
                self.assertEqual(second, retry)
                self.assertEqual([step["expect"]["disposition"] for step in sequence["steps"]],
                                 ["accepted", "rejected", "replayed", "rejected"])
                for step in sequence["steps"]:
                    state = step["expect"]
                    self.assertEqual(state["history"], [first["bundle"]])
                    self.assertEqual(state["bindingBundle"], first["bundle"])
                    self.assertEqual(state["current"], [first["bundle"]])
                    self.assertEqual(state["retractionBundles"], [])
                    self.assertEqual(state["grants"], {"purpose-a": [first["bundle"]], "purpose-b": []})
                    self.assertEqual(state["receiptBundle"], None if state["disposition"] == "rejected" else first["bundle"])
                    self.assertEqual(state["reason"], "source-output-record-conflict" if state["disposition"] == "rejected" else None)
                    self.assertEqual(state["rejectedRecords"], [second["bundle"]] if state["disposition"] == "rejected" else [])

    def test_every_step_has_the_same_expectation_fields(self):
        for sequence in self.corpus["sequences"]:
            for index, step in enumerate(sequence["steps"]):
                with self.subTest(sequence=sequence["id"], step=index):
                    self.assertEqual(set(step), {"bundle", "expect"})
                    self.assertEqual(set(step["expect"]), FIELDS)

    def test_only_an_active_record_version_binds(self):
        policy = self.corpus["policy"]
        self.assertIn("active record version", policy["binding"])
        self.assertIn("binds nothing", policy["binding"])
        self.assertIn("record", policy["rejection"])
        for clause in policy.values():
            self.assertNotRegex(clause, r"\bevents?\b")

    def test_retraction_names_the_shared_output_and_the_original_record(self):
        provenance = next(entry["resource"] for entry in self.bundles["retraction"]["entry"]
                          if entry["resource"]["resourceType"] == "Provenance")
        target = pair(provenance["target"][0]["identifier"])
        source = pair(provenance["entity"][0]["what"]["identifier"])
        for name in ("multi-v2", "changed-source-record"):
            self.assertEqual(target, role_pair(observation(self.bundles[name]), "source-output"))
        self.assertEqual(source, role_pair(observation(self.bundles["multi-v2"]), "source-record"))
        self.assertNotEqual(source, role_pair(observation(self.bundles["changed-source-record"]), "source-record"))

    def test_a_typed_retraction_binds_no_output(self):
        # The retraction names the shared output, yet binds nothing (H26): the later claim under
        # another record binds the output, and the original record's version is then rejected.
        steps = self.sequences["typed-retraction-binds-no-output"]
        self.assertEqual(
            [(step["bundle"], step["expect"]["disposition"]) for step in steps[:3]],
            [("retraction", "accepted"), ("changed-source-record", "accepted"), ("multi-v2", "rejected")],
        )
        for index, step in enumerate(steps):
            state = step["expect"]
            with self.subTest(step=index):
                self.assertEqual(state["retractionBundles"], ["retraction"])
                self.assertEqual(state["bindingBundle"], None if index == 0 else "changed-source-record")
                self.assertEqual(state["current"], [] if index == 0 else ["changed-source-record"])
                self.assertEqual(
                    state["grants"],
                    {"purpose-a": [] if index == 0 else ["changed-source-record"], "purpose-b": []},
                )
                self.assertNotIn("multi-v2", state["history"])
                self.assertEqual(state["receiptBundle"], None if state["disposition"] == "rejected" else step["bundle"])
                self.assertEqual(state["reason"], "source-output-record-conflict" if state["disposition"] == "rejected" else None)
        for step in steps[3:]:
            self.assertIn(step["expect"]["disposition"], {"replayed", "rejected"})

    def test_a_retraction_after_a_contradictory_claim_leaves_that_claim_current(self):
        steps = self.sequences["retraction-after-contradictory-claim"]
        self.assertEqual(
            [(step["bundle"], step["expect"]["disposition"]) for step in steps[:2]],
            [("changed-source-record", "accepted"), ("retraction", "accepted")],
        )
        for index, step in enumerate(steps):
            state = step["expect"]
            with self.subTest(step=index):
                # The retraction suppresses record-heart-001, which holds nothing current.
                self.assertEqual(state["bindingBundle"], "changed-source-record")
                self.assertEqual(state["current"], ["changed-source-record"])
                self.assertEqual(state["grants"], {"purpose-a": ["changed-source-record"], "purpose-b": []})
                self.assertEqual(state["retractionBundles"], [] if index == 0 else ["retraction"])
                self.assertEqual(state["history"], ["changed-source-record"] + ([] if index == 0 else ["retraction"]))
                self.assertIn(state["disposition"], {"accepted", "replayed"})
                self.assertEqual(state["receiptBundle"], step["bundle"])

    def test_a_contradictory_record_is_rejected_alone(self):
        # mixed-admission packs the changed-source-record record beside the target record; the
        # receiver rejects the contradictory record and admits the other one of the same Bundle.
        self.assertIn("per record", self.corpus["policy"]["rejection"])
        (steps,) = (
            steps for steps in self.sequences.values()
            if "mixed-admission" in {step["bundle"] for step in steps}
        )
        delivered = next(step["expect"] for step in steps if step["bundle"] == "mixed-admission")
        self.assertEqual(delivered["rejectedRecords"], ["changed-source-record"])
        self.assertEqual(delivered["reason"], "source-output-record-conflict")
        self.assertEqual(delivered["receiptBundle"], "mixed-admission")
        self.assertIn("mixed-admission", delivered["history"])
        self.assertIn("mixed-admission.target", delivered["current"])
        self.assertIn("mixed-admission.target", delivered["grants"]["purpose-a"])
        self.assertEqual(delivered["bindingBundle"], steps[0]["expect"]["bindingBundle"])
        mixed = entry_keys(self.bundles["mixed-admission"], "Provenance")
        self.assertEqual(len(mixed), 2)
        # A record keeps its version in any Bundle it is packed into.
        self.assertEqual(
            set(mixed),
            set(entry_keys(self.bundles["changed-source-record"], "Provenance") + entry_keys(self.bundles["target"], "Provenance")),
        )

    def test_whole_sequence_requires_restart_replay_without_new_visibility(self):
        self.assertEqual(self.corpus["replayWholeSequence"], {
            "repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []
        })


if __name__ == "__main__":
    unittest.main()
