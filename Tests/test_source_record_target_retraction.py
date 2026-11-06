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
TYPED = "typed-retraction-suppresses-whole-record"
STATE = ("history", "versions", "current", "retractedRecords", "visible", "newlyVisible")


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
        self.typed = {name: steps for name, steps in self.sequences.items() if name.startswith(TYPED)}

    def test_expected_states_are_pinned_to_the_fixture_graphs(self):
        self.assertEqual(self.corpus, source_record_target_retraction_sequences(self.bundles))
        self.assertTrue(self.typed)
        self.assertEqual(len(self.sequences), 4 + len(self.typed))
        # Devices are never retracted, so no Device snapshot is retired or listed.
        self.assertNotIn("deviceSnapshots", self.corpus)
        for alias, output in self.corpus["outputs"].items():
            with self.subTest(output=alias):
                # An output is whatever the conversion Provenance targets, not only an Observation.
                self.assertIn({"reference": output["fullUrl"]}, provenance(self.bundles[output["bundle"]])["target"])
        for clause in ("addressing", "selection"):
            with self.subTest(policy=clause):
                self.assertIn("record version", self.corpus["policy"][clause])
                self.assertNotRegex(self.corpus["policy"][clause], r"\bevents?\b")
                self.assertNotIn("Device", self.corpus["policy"][clause])

    def test_the_target_is_one_untyped_repetition_of_the_source_entity(self):
        retraction = provenance(self.bundles[RETRACTION])
        self.assertEqual(len(retraction["target"]), 1)
        target = retraction["target"][0]
        self.assertNotIn("type", target)
        self.assertEqual([item["valueCode"] for item in target["extension"] if item["url"] == ROLE_EXTENSION], ["source-record"])
        self.assertEqual(target["identifier"], retraction["entity"][0]["what"]["identifier"])
        self.assertEqual(pair(target["identifier"]), self.records["record-heart-001"])
        # The typed example retracts the same source record while naming one output.
        self.assertEqual(source_entity(self.bundles["retraction"]), self.records["record-heart-001"])
        for name in ("multi-v1", "multi-v2", "multi-v3"):
            self.assertEqual(source_entity(self.bundles[name]), self.records["record-heart-001"])
        self.assertEqual(source_entity(self.bundles["target"]), self.records["record-2"])
        self.assertEqual(source_entity(self.bundles["changed-source-record"]), self.records["another-record"])

    def test_retracted_records_have_no_current_output_and_other_records_stay(self):
        outputs = self.corpus["outputs"]
        for name, steps in self.sequences.items():
            for index, step in enumerate(steps):
                state = step["expect"]
                with self.subTest(sequence=name, step=index):
                    self.assertEqual(set(state), {*STATE, "disposition", "receiptBundle", "reason"})
                    retracted = {self.records[alias] for alias in state["retractedRecords"]}
                    for alias in state["current"]:
                        self.assertNotIn(source_entity(self.bundles[outputs[alias]["bundle"]]), retracted)
        steps = self.sequences["source-record-target-retraction-leaves-other-records-current"]
        self.assertEqual([step["expect"]["current"] for step in steps], [["target.primary"]] * 3)

    def test_a_retraction_first_matches_nothing_yet_and_suppresses_later_versions(self):
        steps = self.sequences["source-record-target-retraction-before-any-version"]
        first = steps[0]["expect"]
        self.assertEqual(
            (first["disposition"], first["history"], first["versions"], first["current"]),
            ("accepted", [RETRACTION], [], []),
        )
        for step in steps[1:]:
            self.assertEqual((step["expect"]["disposition"], step["expect"]["current"]), ("accepted", []))

    def test_a_typed_retraction_suppresses_its_whole_record(self):
        # The typed retraction names only the primary output; the record's secondary goes too (H26).
        retraction = provenance(self.bundles["retraction"])
        named = {pair(target["identifier"]) for target in retraction["target"]}
        secondary = self.corpus["outputs"]["multi-v3.secondary"]
        bundle = self.bundles[secondary["bundle"]]
        resource = next(entry["resource"] for entry in bundle["entry"] if entry["fullUrl"] == secondary["fullUrl"])
        output_identity = next(
            pair(item) for item in resource["identifier"] if item["type"]["coding"][0]["code"] == "source-output"
        )
        self.assertNotIn(output_identity, named)
        versions = {"multi-v1", "multi-v2", "multi-v3"}
        orders, secondary_orders = set(), set()
        for name, steps in self.typed.items():
            delivered = [step["bundle"] for step in steps]
            self.assertIn("multi-v3", delivered)
            first = delivered.index("retraction")
            orders.update(
                "before" if index < first else "after"
                for index, bundle in enumerate(delivered) if bundle in versions
            )
            secondary_orders.add("before" if delivered.index("multi-v3") < first else "after")
            for index, step in enumerate(steps):
                state = step["expect"]
                with self.subTest(sequence=name, step=index):
                    if "retraction" in state["history"]:
                        self.assertIn("record-heart-001", state["retractedRecords"])
                        self.assertNotIn("multi-v3.secondary", state["current"])
                        self.assertNotIn("multi-v3.primary", state["current"])
                        self.assertEqual(state["visible"], [])
                    if "multi-v3" in state["history"]:
                        self.assertIn("multi-v3.secondary", state["versions"])
        # Both arrival orders: versions of the record accepted before and after the retraction,
        # and multi-v3, which carries the unnamed secondary output, in each of them.
        self.assertEqual(orders, {"before", "after"})
        self.assertEqual(secondary_orders, {"before", "after"})

    def test_replay_and_rejection_change_nothing(self):
        for name, steps in self.sequences.items():
            previous = None
            for index, step in enumerate(steps):
                state = step["expect"]
                with self.subTest(sequence=name, step=index):
                    self.assertEqual(state["visible"], state["current"])
                    if state["disposition"] == "accepted":
                        self.assertEqual(state["history"][-1], step["bundle"])
                    else:
                        self.assertEqual({key: state[key] for key in STATE if key != "newlyVisible"},
                                         {key: previous[key] for key in STATE if key != "newlyVisible"})
                        self.assertEqual(state["newlyVisible"], [])
                    previous = state

    def test_no_retraction_binds_an_output_whatever_its_targets_name(self):
        steps = self.sequences["source-record-target-retraction-binds-no-output"]
        self.assertEqual(
            [(step["bundle"], step["expect"]["disposition"]) for step in steps],
            [(RETRACTION, "accepted"), ("changed-source-record", "accepted"), ("multi-v2", "rejected"), (RETRACTION, "replayed")],
        )
        self.assertEqual(steps[-1]["expect"]["current"], ["changed-source-record.primary"])
        # As in identity-sequences.json: the typed retraction names that output, yet binds nothing.
        identity = json.loads((CORPUS / "identity-sequences.json").read_text())
        typed = next(sequence for sequence in identity["sequences"] if sequence["id"] == "typed-retraction-binds-no-output")
        self.assertEqual(
            [(step["bundle"], step["expect"]["disposition"]) for step in typed["steps"][:3]],
            [("retraction", "accepted"), ("changed-source-record", "accepted"), ("multi-v2", "rejected")],
        )


if __name__ == "__main__":
    unittest.main()
