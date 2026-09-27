"""Check complete-revision examples and their declared policy, not a production receiver."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import json
from itertools import permutations
import unittest

from Scripts.receiver_lifecycle_fixtures import CORPUS, VERSION, observation, revision_resources, revision_sequences
from Tests.test_receiver_lifecycle import role_pair


def observations(bundle):
    return [entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Observation"]


def writer_version(resource):
    return next(item["valueString"] for item in resource["extension"] if item["url"] == VERSION)


class RevisionMembershipTests(unittest.TestCase):
    def setUp(self):
        self.bundles = revision_resources()
        self.corpus = json.loads((CORPUS / "revision-sequences.json").read_text())
        self.sequences = {item["id"]: item["steps"] for item in self.corpus["sequences"]}

    def test_expected_states_and_output_addresses_are_pinned(self):
        self.assertEqual(self.corpus, revision_sequences(self.bundles))
        self.assertEqual(self.corpus["schemaVersion"], 0)
        self.assertEqual(len(self.sequences), 35)
        addressed = set()
        for alias, output in self.corpus["outputs"].items():
            with self.subTest(output=alias):
                self.assertEqual(set(output), {"event", "fullUrl"})
                entry = next(item for item in observations(self.bundles[output["event"]]) if item["fullUrl"] == output["fullUrl"])
                self.assertEqual(entry["resource"]["resourceType"], "Observation")
                addressed.add((output["event"], output["fullUrl"]))
        expected = {(event, entry["fullUrl"]) for event, bundle in self.bundles.items() for entry in observations(bundle)}
        self.assertEqual(addressed, expected)
        self.assertEqual(len(addressed), len(self.corpus["outputs"]))

    def test_revisions_preserve_source_identity_but_change_complete_membership(self):
        first, second, third = (observations(self.bundles[name]) for name in ("multi-v1", "multi-v2", "multi-v3"))
        self.assertEqual([len(first), len(second), len(third)], [2, 1, 2])
        self.assertEqual(first[0]["fullUrl"], second[0]["fullUrl"])
        self.assertEqual(first[1]["fullUrl"], third[1]["fullUrl"])
        self.assertNotEqual(first[0]["fullUrl"], first[1]["fullUrl"])
        for entries, version in ((first, "9007199254740992"), (second, "9007199254740993"), (third, "9007199254740994")):
            for entry in entries:
                resource = entry["resource"]
                self.assertEqual(role_pair(resource, "source-record"), role_pair(first[0]["resource"], "source-record"))
                self.assertEqual(role_pair(resource, "writer-record"), role_pair(first[0]["resource"], "writer-record"))
                self.assertEqual(writer_version(resource), version)
        for bundle in self.bundles.values():
            provenance = next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")
            self.assertEqual({target["reference"] for target in provenance["target"]}, {entry["fullUrl"] for entry in observations(bundle)})

    def test_both_arrival_orders_remove_the_old_child_from_current_selection(self):
        for name in ("removed-child-does-not-remain-current", "late-old-revision-does-not-add-a-child"):
            with self.subTest(sequence=name):
                final = self.sequences[name][-1]["expect"]
                self.assertEqual(final["current"], ["multi-v2.primary"])
                self.assertEqual(final["visible"], ["multi-v2.primary"])
                self.assertEqual(set(final["versions"]), {"multi-v1.primary", "multi-v1.secondary", "multi-v2.primary"})
                self.assertEqual(final["newlyVisible"], [])

    def test_fixture_exposes_the_independent_per_output_maximum_bug(self):
        # Deliberately wrong selector: it retains the old secondary because v2 has no replacement.
        latest = {}
        for event in ("multi-v1", "multi-v2"):
            for entry in observations(self.bundles[event]):
                resource = entry["resource"]
                key = role_pair(resource, "source-output")
                candidate = (int(writer_version(resource)), event, entry["fullUrl"])
                latest[key] = max(latest.get(key, candidate), candidate)
        incorrect = {(event, url) for _, event, url in latest.values()}
        self.assertEqual(len(incorrect), 2)
        self.assertIn(("multi-v1", self.corpus["outputs"]["multi-v1.secondary"]["fullUrl"]), incorrect)
        self.assertEqual(self.sequences["removed-child-does-not-remain-current"][-1]["expect"]["current"], ["multi-v2.primary"])

    def test_reintroduced_child_has_membership_but_no_inherited_grant(self):
        final = self.sequences["membership-removal-is-not-a-tombstone-or-a-grant"][-1]["expect"]
        self.assertEqual(final["current"], ["multi-v3.primary", "multi-v3.secondary"])
        self.assertEqual(final["visible"], ["multi-v3.primary"])
        self.assertIn("multi-v1.secondary", self.corpus["authorizedOutputs"]["purpose-a"])
        self.assertNotIn("multi-v3.secondary", self.corpus["authorizedOutputs"]["purpose-a"])
        self.assertEqual(self.corpus["authorizedOutputs"]["purpose-b"], [])

    def test_equal_version_and_mixed_evidence_are_distinct_from_exact_replay(self):
        second = observation(self.bundles["multi-v2"])
        conflict = observation(self.bundles["equal-version-conflict"])
        reassembly = observation(self.bundles["equal-version-reassembly"])
        self.assertEqual(writer_version(second), writer_version(conflict))
        self.assertNotEqual(second["note"], conflict["note"])
        for key in ("valueQuantity", "note", "identifier", "effectiveDateTime", "issued"):
            self.assertEqual(second[key], reassembly[key])
        self.assertNotEqual(self.bundles["multi-v2"]["identifier"], self.bundles["equal-version-reassembly"]["identifier"])
        self.assertNotEqual(role_pair(second, "writer-record"), role_pair(observation(self.bundles["other-writer"]), "writer-record"))
        self.assertFalse(any(item["url"] == VERSION for item in observation(self.bundles["missing-order"])["extension"]))
        for candidate in ("equal-version-conflict", "equal-version-reassembly", "other-writer", "missing-order"):
            with self.subTest(candidate=candidate):
                steps = self.sequences[candidate + "-requires-resolution"]
                self.assertEqual(steps[1]["expect"], steps[2]["expect"])
                self.assertEqual(steps[2]["expect"]["current"], [])
                self.assertEqual(steps[2]["expect"]["visible"], [])
                self.assertEqual(steps[2]["expect"]["conflicts"], ["multi-v2", candidate])
                reverse = self.sequences[candidate + "-arrives-first"]
                self.assertEqual(reverse[1]["expect"], reverse[2]["expect"])
                # Arrival history differs, but neither order may resolve the conflict.
                for field in ("history", "versions", "current", "conflicts", "visible", "newlyVisible"):
                    self.assertEqual(set(steps[-1]["expect"][field]), set(reverse[-1]["expect"][field]))

    def test_every_step_retains_history_and_grants_only_listed_exact_versions(self):
        outputs = self.corpus["outputs"]
        for sequence in self.corpus["sequences"]:
            history, versions, visible = set(), set(), set()
            for step in sequence["steps"]:
                state = step["expect"]
                self.assertLessEqual(history, set(state["history"]))
                self.assertLessEqual(versions, set(state["versions"]))
                self.assertLessEqual(set(state["current"]), set(state["versions"]))
                self.assertEqual(set(state["versions"]), {alias for alias, output in outputs.items() if output["event"] in state["history"]})
                self.assertLessEqual(set(state["visible"]), set(state["current"]) & set(self.corpus["authorizedOutputs"]["purpose-a"]))
                self.assertEqual(set(state["newlyVisible"]), set(state["visible"]) - visible)
                self.assertFalse({outputs[alias]["event"] for alias in state["current"]} & set(state["conflicts"]))
                history, versions, visible = set(state["history"]), set(state["versions"]), set(state["visible"])
        self.assertEqual(self.corpus["replayWholeSequence"], {
            "repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []
        })

    def test_higher_comparable_revision_advances_without_erasing_older_conflicts(self):
        for candidate in ("equal-version-conflict", "equal-version-reassembly"):
            for order in permutations(("older", "competing", "newer")):
                name = candidate + "-with-higher-revision-" + "-".join(order)
                with self.subTest(sequence=name):
                    steps = self.sequences[name]
                    delivered = set()
                    for step in steps:
                        delivered.add(step["event"])
                        state = step["expect"]
                        if "multi-v3" in delivered:
                            self.assertEqual(state["current"], ["multi-v3.primary", "multi-v3.secondary"])
                            self.assertEqual(state["visible"], ["multi-v3.primary"])
                        if {"multi-v2", candidate} <= delivered:
                            self.assertEqual(set(state["conflicts"]), {"multi-v2", candidate})
                    self.assertEqual(set(steps[-1]["expect"]["versions"]), {
                        "multi-v2.primary", candidate + ".primary", "multi-v3.primary", "multi-v3.secondary"
                    })

    def test_higher_version_never_orders_missing_or_different_writer_evidence(self):
        for candidate in ("other-writer", "missing-order"):
            for order in permutations(("older", "competing", "newer")):
                name = candidate + "-with-higher-revision-" + "-".join(order)
                with self.subTest(sequence=name):
                    delivered = set()
                    for step in self.sequences[name]:
                        delivered.add(step["event"])
                        if candidate in delivered and len(delivered) > 1:
                            self.assertEqual(step["expect"]["current"], [])
                            self.assertEqual(step["expect"]["visible"], [])
                            self.assertEqual(set(step["expect"]["conflicts"]), delivered)

    def test_higher_revision_sequences_cover_every_order_and_replay_each_event(self):
        for candidate in ("equal-version-conflict", "equal-version-reassembly", "other-writer", "missing-order"):
            prefix = candidate + "-with-higher-revision-"
            matches = [steps for name, steps in self.sequences.items() if name.startswith(prefix)]
            self.assertEqual(len(matches), 6)
            self.assertEqual({tuple(step["event"] for step in steps[:3]) for steps in matches},
                             set(permutations(("multi-v2", candidate, "multi-v3"))))
            finals = []
            for steps in matches:
                self.assertEqual(len(steps), 6)
                self.assertEqual([step["event"] for step in steps[3:]], [step["event"] for step in steps[:3]])
                expected = {**steps[2]["expect"], "newlyVisible": []}
                for step in steps[3:]:
                    self.assertEqual(step["expect"], expected)
                finals.append({key: set(value) for key, value in steps[-1]["expect"].items()})
            self.assertTrue(all(state == finals[0] for state in finals))


if __name__ == "__main__":
    unittest.main()
