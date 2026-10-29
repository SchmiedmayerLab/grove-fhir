"""Pin the source-record target retraction policy without pretending to verify a production receiver."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import json
import unittest

from Scripts.receiver_lifecycle_fixtures import CORPUS, resources, source_record_target_retraction_sequences
from Tests.test_receiver_lifecycle import pair


ROLE_EXTENSION = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role"
RETRACTION = "source-record-target-retraction"
STATE = ("history", "versions", "current", "retractedRecords", "retiredDeviceSnapshots", "visible", "newlyVisible")


def provenance(bundle):
    return next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")


def source_entity(bundle):
    return pair(provenance(bundle)["entity"][0]["what"]["identifier"])


class SourceRecordTargetRetractionTests(unittest.TestCase):
    def setUp(self):
        self.bundles = resources()
        self.corpus = json.loads((CORPUS / "source-record-target-retraction-sequences.json").read_text())
        self.sequences = {sequence["id"]: sequence["steps"] for sequence in self.corpus["sequences"]}
        self.records = {alias: pair(identifier) for alias, identifier in self.corpus["records"].items()}

    def test_expected_states_are_pinned_to_the_fixture_graphs(self):
        self.assertEqual(self.corpus, source_record_target_retraction_sequences(self.bundles))
        self.assertEqual(len(self.sequences), 4)
        for alias, output in self.corpus["outputs"].items():
            with self.subTest(output=alias):
                # An output is whatever the conversion Provenance targets, not only an Observation.
                self.assertIn({"reference": output["fullUrl"]}, provenance(self.bundles[output["event"]])["target"])
        for alias, device in self.corpus["deviceSnapshots"].items():
            with self.subTest(device=alias):
                entry = next(item for item in self.bundles[device["event"]]["entry"] if item["fullUrl"] == device["fullUrl"])
                self.assertEqual(entry["resource"]["resourceType"], "Device")

    def test_the_target_is_one_untyped_repetition_of_the_source_entity(self):
        retraction = provenance(self.bundles[RETRACTION])
        self.assertEqual(len(retraction["target"]), 1)
        target = retraction["target"][0]
        self.assertNotIn("type", target)
        self.assertEqual([item["valueCode"] for item in target["extension"] if item["url"] == ROLE_EXTENSION], ["source-record"])
        self.assertEqual(target["identifier"], retraction["entity"][0]["what"]["identifier"])
        self.assertEqual(pair(target["identifier"]), self.records["record-heart-001"])
        # The exact example retracts the same source record by naming its output instead.
        self.assertEqual(source_entity(self.bundles["retraction"]), self.records["record-heart-001"])
        for name in ("multi-v1", "multi-v2", "multi-v3"):
            self.assertEqual(source_entity(self.bundles[name]), self.records["record-heart-001"])
        self.assertEqual(source_entity(self.bundles["target"]), self.records["record-2"])
        self.assertEqual(source_entity(self.bundles["changed-source-record"]), self.records["another-record"])

    def test_addressed_nodes_leave_current_selection_and_other_records_stay(self):
        outputs, devices = self.corpus["outputs"], self.corpus["deviceSnapshots"]
        for name, steps in self.sequences.items():
            for index, step in enumerate(steps):
                state = step["expect"]
                with self.subTest(sequence=name, step=index):
                    retracted = {self.records[alias] for alias in state["retractedRecords"]}
                    for alias in state["current"]:
                        self.assertNotIn(source_entity(self.bundles[outputs[alias]["event"]]), retracted)
                    self.assertEqual(state["retiredDeviceSnapshots"], sorted(
                        alias for alias, device in devices.items()
                        if device["event"] in state["history"]
                        and source_entity(self.bundles[device["event"]]) in retracted
                    ))
        steps = self.sequences["source-record-target-retraction-leaves-other-records-current"]
        self.assertEqual([step["expect"]["current"] for step in steps], [["target.primary"]] * 3)

    def test_a_retraction_first_matches_nothing_yet_and_suppresses_later_events(self):
        steps = self.sequences["source-record-target-retraction-before-any-event"]
        first = steps[0]["expect"]
        self.assertEqual(
            (first["disposition"], first["history"], first["versions"], first["current"], first["retiredDeviceSnapshots"]),
            ("accepted", [RETRACTION], [], [], []),
        )
        for step in steps[1:]:
            self.assertEqual((step["expect"]["disposition"], step["expect"]["current"]), ("accepted", []))
        self.assertEqual(steps[-1]["expect"]["retiredDeviceSnapshots"], ["multi-v1.application", "multi-v3.application"])

    def test_replay_and_rejection_change_nothing(self):
        for name, steps in self.sequences.items():
            previous = None
            for index, step in enumerate(steps):
                state = step["expect"]
                with self.subTest(sequence=name, step=index):
                    self.assertEqual(state["visible"], state["current"])
                    if state["disposition"] == "accepted":
                        self.assertEqual(state["history"][-1], step["event"])
                    else:
                        self.assertEqual({key: state[key] for key in STATE if key != "newlyVisible"},
                                         {key: previous[key] for key in STATE if key != "newlyVisible"})
                        self.assertEqual(state["newlyVisible"], [])
                    previous = state

    def test_a_source_record_target_binds_no_output_unlike_an_exact_target(self):
        steps = self.sequences["source-record-target-retraction-binds-no-output"]
        self.assertEqual(
            [(step["event"], step["expect"]["disposition"]) for step in steps],
            [(RETRACTION, "accepted"), ("changed-source-record", "accepted"), ("multi-v2", "rejected"), (RETRACTION, "replayed")],
        )
        self.assertEqual(steps[-1]["expect"]["current"], ["changed-source-record.primary"])
        # The exact retraction names that output, so arriving first it binds the output and rejects the claim.
        identity = json.loads((CORPUS / "identity-sequences.json").read_text())
        exact = next(sequence for sequence in identity["sequences"] if sequence["id"] == "retraction-binds-before-active-claim")
        self.assertEqual(
            [(step["event"], step["expect"]["disposition"]) for step in exact["steps"][:2]],
            [("retraction", "accepted"), ("changed-source-record", "rejected")],
        )


if __name__ == "__main__":
    unittest.main()
