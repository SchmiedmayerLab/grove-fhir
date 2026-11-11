"""Check complete-revision examples and their declared policy, not a production receiver."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import json
from itertools import permutations
import unittest

from Scripts.receiver_lifecycle_fixtures import CORPUS, VERSION, observation, revision_resources, revision_sequences
from Tests.receiver_selection_reference import bundle_versions, instant, select
from Tests.test_receiver_lifecycle import role_pair


# The revision candidates, in the order the spec declares their selected versions.
CANDIDATES = (
    "equal-version-later-recorded",
    "equal-version-reconversion",
    "equal-version-equal-recorded",
    "other-writer",
    "missing-order",
)
def observations(bundle):
    return [entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Observation"]


def conversion(bundle):
    return next(entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")


def writer_version(resource):
    return next(item["valueString"] for item in resource["extension"] if item["url"] == VERSION)


class RevisionMembershipTests(unittest.TestCase):
    def setUp(self):
        self.bundles = revision_resources()
        self.corpus = json.loads((CORPUS / "revision-sequences.json").read_text())
        self.sequences = {item["id"]: item["steps"] for item in self.corpus["sequences"]}

    def versions(self, names):
        return [version for name in names for _, version in bundle_versions(self.bundles[name], name)]

    def aliases(self, name):
        return sorted(alias for alias, output in self.corpus["outputs"].items() if output["bundle"] == name)

    def declared_current(self, names):
        """The current output aliases that the reference rule selects for one accepted set."""
        selected = select(self.versions(names))
        if selected is None:
            return []
        return sorted(
            alias for alias, output in self.corpus["outputs"].items()
            if output["bundle"] == selected.name and output["fullUrl"] in selected.outputs
        )

    def candidate_sequences(self, candidate):
        return {
            name: steps for name, steps in self.sequences.items()
            if candidate in {step["bundle"] for step in steps}
        }

    def test_expected_states_and_output_addresses_are_pinned(self):
        self.assertEqual(self.corpus, revision_sequences(self.bundles))
        self.assertEqual(self.corpus["schemaVersion"], 0)
        self.assertEqual(len(self.sequences), 3 + len(CANDIDATES) * 8)
        self.assertEqual(set(self.bundles), {"multi-v1", "multi-v2", "multi-v3", *CANDIDATES})
        addressed = set()
        for alias, output in self.corpus["outputs"].items():
            with self.subTest(output=alias):
                self.assertEqual(set(output), {"bundle", "fullUrl"})
                entry = next(item for item in observations(self.bundles[output["bundle"]]) if item["fullUrl"] == output["fullUrl"])
                self.assertEqual(entry["resource"]["resourceType"], "Observation")
                addressed.add((output["bundle"], output["fullUrl"]))
        expected = {(name, entry["fullUrl"]) for name, bundle in self.bundles.items() for entry in observations(bundle)}
        self.assertEqual(addressed, expected)
        self.assertEqual(len(addressed), len(self.corpus["outputs"]))
        for sequence in self.corpus["sequences"]:
            for step in sequence["steps"]:
                self.assertNotIn("conflicts", step["expect"])

    def test_revisions_preserve_source_identity_but_change_complete_membership(self):
        first, second, third = (observations(self.bundles[name]) for name in ("multi-v1", "multi-v2", "multi-v3"))
        self.assertEqual([len(first), len(second), len(third)], [2, 1, 2])
        self.assertEqual(first[0]["fullUrl"], second[0]["fullUrl"])
        self.assertEqual(first[1]["fullUrl"], third[1]["fullUrl"])
        self.assertNotEqual(first[0]["fullUrl"], first[1]["fullUrl"])
        for entries, writer in ((first, "9007199254740992"), (second, "9007199254740993"), (third, "9007199254740994")):
            for entry in entries:
                resource = entry["resource"]
                self.assertEqual(role_pair(resource, "source-record"), role_pair(first[0]["resource"], "source-record"))
                self.assertEqual(role_pair(resource, "writer-record"), role_pair(first[0]["resource"], "writer-record"))
                self.assertEqual(writer_version(resource), writer)
        # Writer evidence beats recorded throughout: a higher writer version is recorded earlier.
        recorded = {
            name: conversion(self.bundles[name])["resource"]["recorded"] for name in ("multi-v1", "multi-v2", "multi-v3")
        }
        self.assertEqual(recorded, {
            "multi-v1": "2026-08-20T17:30:09Z", "multi-v2": "2026-08-20T17:30:08Z", "multi-v3": "2026-08-20T17:30:07Z",
        })
        keys = set()
        for name, bundle in self.bundles.items():
            provenance = conversion(bundle)
            self.assertEqual(
                {target["reference"] for target in provenance["resource"]["target"]},
                {entry["fullUrl"] for entry in observations(bundle)},
            )
            ((_, selected),) = bundle_versions(bundle, name)
            keys.add(selected.key)
        # Each version has its own record-version key, so its own Provenance fullUrl.
        self.assertEqual(len(keys), len(self.bundles))

    def test_candidates_state_the_declared_writer_evidence_and_instants(self):
        second, third = self.versions(["multi-v2"])[0], self.versions(["multi-v3"])[0]
        by_name = {name: self.versions([name])[0] for name in CANDIDATES}
        for name in ("equal-version-later-recorded", "equal-version-reconversion", "equal-version-equal-recorded"):
            with self.subTest(candidate=name):
                self.assertEqual(by_name[name].writer, second.writer)
        self.assertEqual(instant(by_name["equal-version-later-recorded"].recorded), instant("2026-08-20T17:30:10Z"))
        self.assertEqual(instant(by_name["equal-version-reconversion"].recorded), instant("2026-08-20T17:30:11Z"))
        # The same instant as multi-v2 in another lexeme, so only the tie-break orders them.
        self.assertEqual(by_name["equal-version-equal-recorded"].recorded, "2026-08-20T17:30:08.000Z")
        self.assertNotEqual(by_name["equal-version-equal-recorded"].recorded, second.recorded)
        self.assertEqual(instant(by_name["equal-version-equal-recorded"].recorded), instant(second.recorded))
        self.assertNotEqual(by_name["other-writer"].writer[0], third.writer[0])
        self.assertEqual(by_name["other-writer"].writer[1], third.writer[1])
        self.assertEqual(instant(by_name["other-writer"].recorded), instant("2026-08-20T17:30:06Z"))
        self.assertIsNone(by_name["missing-order"].writer)
        self.assertEqual(by_name["missing-order"].recorded, "2026-08-20T17:30:07.500Z")
        self.assertFalse(any(item["url"] == VERSION for item in observation(self.bundles["missing-order"])["extension"]))
        # A re-conversion repeats the outputs, but its new recorded instant makes a new version.
        reconversion, original = (observation(self.bundles[name]) for name in ("equal-version-reconversion", "multi-v2"))
        for key in ("valueQuantity", "note", "identifier", "effectiveDateTime"):
            self.assertEqual(reconversion[key], original[key])
        self.assertNotEqual(by_name["equal-version-reconversion"].key, second.key)

    def test_declared_states_match_the_reference_selection_rule(self):
        for name, steps in self.sequences.items():
            for index, step in enumerate(steps):
                with self.subTest(sequence=name, step=index):
                    self.assertEqual(step["expect"]["current"], self.declared_current(step["expect"]["history"]))

    def test_declared_current_versions_follow_the_spec_table(self):
        # For the candidates in CANDIDATES order: the selected version of {v2, c}, {c, v3}, {v2, c, v3}.
        tie = "tie-break"
        table = {
            ("multi-v2", "c"): ["c", "c", tie, "multi-v2", "multi-v2"],
            ("c", "multi-v3"): ["multi-v3", "multi-v3", "multi-v3", "multi-v3", "c"],
            ("multi-v2", "c", "multi-v3"): ["multi-v3", "multi-v3", "multi-v3", "multi-v3", "c"],
        }
        second, equal = self.versions(["multi-v2"])[0], self.versions(["equal-version-equal-recorded"])[0]
        tie_winner = "multi-v2" if second.key[1].encode() > equal.key[1].encode() else "equal-version-equal-recorded"
        for members, winners in table.items():
            for candidate, winner in zip(CANDIDATES, winners):
                names = [candidate if member == "c" else member for member in members]
                winner = tie_winner if winner == tie else candidate if winner == "c" else winner
                with self.subTest(members=names):
                    self.assertEqual(self.declared_current(names), self.aliases(winner))
                    for steps in self.candidate_sequences(candidate).values():
                        for step in steps:
                            if sorted(step["expect"]["history"]) == sorted(names):
                                self.assertEqual(step["expect"]["current"], self.aliases(winner))
        # Singletons select themselves; {v2, v3} selects v3.
        for name in ("multi-v1", "multi-v2", "multi-v3", *CANDIDATES):
            self.assertEqual(self.declared_current([name]), self.aliases(name))
        self.assertEqual(self.declared_current(["multi-v2", "multi-v3"]), self.aliases("multi-v3"))

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
        for name in ("multi-v1", "multi-v2"):
            for entry in observations(self.bundles[name]):
                resource = entry["resource"]
                key = role_pair(resource, "source-output")
                candidate = (int(writer_version(resource)), name, entry["fullUrl"])
                latest[key] = max(latest.get(key, candidate), candidate)
        incorrect = {(name, url) for _, name, url in latest.values()}
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

    def test_writer_evidence_beats_recorded_and_recorded_decides_without_it(self):
        # multi-v1 is recorded later than multi-v2 but carries a lower writer version.
        self.assertEqual(self.declared_current(["multi-v1", "multi-v2"]), ["multi-v2.primary"])
        for candidate, winner in (
            ("equal-version-later-recorded", "equal-version-later-recorded"),
            ("equal-version-reconversion", "equal-version-reconversion"),
            ("other-writer", "multi-v2"),
            ("missing-order", "multi-v2"),
        ):
            with self.subTest(candidate=candidate):
                self.assertEqual(self.declared_current(["multi-v2", candidate]), self.aliases(winner))

    def test_the_set_rule_lets_missing_order_follow_the_higher_writer_version(self):
        # multi-v3 drops multi-v2 by writer version; missing-order is then later than multi-v3.
        for names in (["multi-v2", "missing-order", "multi-v3"], ["missing-order", "multi-v3"]):
            with self.subTest(names=names):
                self.assertEqual(self.declared_current(names), ["missing-order.primary"])
        self.assertEqual(self.declared_current(["multi-v2", "missing-order"]), ["multi-v2.primary"])
        third, missing, second = (self.versions([name])[0] for name in ("multi-v3", "missing-order", "multi-v2"))
        self.assertLess(instant(third.recorded), instant(missing.recorded))
        self.assertLess(instant(missing.recorded), instant(second.recorded))

    def test_every_step_retains_history_and_grants_only_listed_exact_versions(self):
        outputs = self.corpus["outputs"]
        for sequence in self.corpus["sequences"]:
            history, versions, visible = set(), set(), set()
            for step in sequence["steps"]:
                state = step["expect"]
                self.assertEqual(set(state), {"history", "versions", "current", "visible", "newlyVisible"})
                self.assertLessEqual(history, set(state["history"]))
                self.assertLessEqual(versions, set(state["versions"]))
                self.assertLessEqual(set(state["current"]), set(state["versions"]))
                self.assertEqual(set(state["versions"]), {alias for alias, output in outputs.items() if output["bundle"] in state["history"]})
                self.assertLessEqual(set(state["visible"]), set(state["current"]) & set(self.corpus["authorizedOutputs"]["purpose-a"]))
                self.assertEqual(set(state["newlyVisible"]), set(state["visible"]) - visible)
                # Every accepted set selects a version: no equal-version conflict stays open.
                self.assertTrue(state["current"])
                history, versions, visible = set(state["history"]), set(state["versions"]), set(state["visible"])
        self.assertEqual(self.corpus["replayWholeSequence"], {
            "repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []
        })

    def test_three_version_sequences_cover_every_order_and_replay_each_bundle(self):
        for candidate in CANDIDATES:
            with self.subTest(candidate=candidate):
                sequences = self.candidate_sequences(candidate)
                self.assertEqual(len(sequences), 8)
                matches = [
                    steps for steps in sequences.values()
                    if {step["bundle"] for step in steps} == {"multi-v2", candidate, "multi-v3"}
                ]
                self.assertEqual(len(matches), 6)
                self.assertEqual({tuple(step["bundle"] for step in steps[:3]) for steps in matches},
                                 set(permutations(("multi-v2", candidate, "multi-v3"))))
                finals = []
                for steps in matches:
                    self.assertEqual(len(steps), 6)
                    self.assertEqual([step["bundle"] for step in steps[3:]], [step["bundle"] for step in steps[:3]])
                    expected = {**steps[2]["expect"], "newlyVisible": []}
                    for step in steps[3:]:
                        self.assertEqual(step["expect"], expected)
                    finals.append({key: set(value) for key, value in steps[-1]["expect"].items()})
                # Arrival order never decides: every order ends in the same state.
                self.assertTrue(all(state == finals[0] for state in finals))


if __name__ == "__main__":
    unittest.main()
