"""The reference versionSelection rule, checked against the catalog and the D2-A cases."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from itertools import combinations, permutations
import json
from pathlib import Path
import unittest

from Tests.receiver_selection_reference import (
    ROLE_SYSTEM,
    WRITER_VERSION,
    Version,
    current_outputs,
    instant,
    select,
    writer_evidence,
    writer_version_greater,
)


ROOT = Path(__file__).parents[1]
WRITER = ("https://study.example.org/fhir/NamingSystem/grove-writer-record-v0/test-key/1", "writer-w")
OTHER_WRITER = ("https://study.example.org/fhir/NamingSystem/grove-writer-record-v0/test-key/1", "writer-w-prime")
VERSION_SYSTEM = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"


def version(name, recorded, writer=None, value=None, outputs=()):
    return Version(
        key=(VERSION_SYSTEM, value or f"v0:test-key:1:{name}"),
        recorded=recorded,
        writer=writer,
        outputs=tuple(outputs) or (name,),
        name=name,
    )


class VersionSelectionReferenceTests(unittest.TestCase):
    """The reference rule itself, checked against the catalog's statements and the D2-A cases."""

    def test_writer_evidence_beats_a_later_recorded_instant(self):
        older = version("older", "2026-08-20T17:30:09Z", (WRITER, "9007199254740992"))
        newer = version("newer", "2026-08-20T17:30:07Z", (WRITER, "9007199254740993"))
        for order in permutations((older, newer)):
            self.assertEqual(select(order), newer)

    def test_recorded_orders_versions_without_comparable_writer_evidence(self):
        base = version("base", "2026-08-20T17:30:08Z", (WRITER, "9007199254740993"))
        for candidate in (
            version("other-writer", "2026-08-20T17:30:09Z", (OTHER_WRITER, "1")),
            version("missing", "2026-08-20T17:30:09Z"),
            version("equal-version", "2026-08-20T17:30:09Z", (WRITER, "9007199254740993")),
        ):
            with self.subTest(candidate=candidate.name):
                self.assertEqual(select([base, candidate]), candidate)
                self.assertEqual(select([candidate, base]), candidate)

    def test_recorded_is_an_exact_instant_never_text_or_milliseconds(self):
        # Bytewise, "…:00Z" sorts after "…:00.5Z"; as instants it is earlier.
        self.assertGreater(b"2026-08-20T17:30:00Z", b"2026-08-20T17:30:00.5Z")
        self.assertLess(instant("2026-08-20T17:30:00Z"), instant("2026-08-20T17:30:00.5Z"))
        self.assertEqual(instant("2026-08-20T17:30:08Z"), instant("2026-08-20T17:30:08.000Z"))
        self.assertEqual(instant("2026-08-20T10:30:02-07:00"), instant("2026-08-20T17:30:02Z"))
        self.assertEqual(instant("2026-08-21T01:00:02+07:30"), instant("2026-08-20T17:30:02Z"))
        # A millisecond date value would round these two to one instant.
        self.assertLess(instant("2026-08-20T17:30:00.0001Z"), instant("2026-08-20T17:30:00.0002Z"))
        earlier = version("text-later", "2026-08-20T17:30:00Z")
        later = version("text-earlier", "2026-08-20T17:30:00.5Z")
        self.assertEqual(select([earlier, later]), later)
        for invalid in ("2026-08-20T17:30:00", "2026-08-20 17:30:00Z", "2026-08-20"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                instant(invalid)

    def test_equal_instants_reach_the_bytewise_tie_break(self):
        # The record-version vectors of 72 and 72.0 under one source record: the same writer
        # evidence (none) and the same recorded instant, so z2SX… wins over xjbz….
        seventy_two = version(
            "72", "2026-08-20T17:30:02Z", value="v0:test-key:1:xjbzwZqYyBE1boHxzOoS09iLXEMrvo0o8dpxtlwPQhE"
        )
        seventy_two_0 = version(
            "72.0", "2026-08-20T17:30:02.000Z", value="v0:test-key:1:z2SXdSGr63iLne5oavwMibQClshhTEABve_JEZLljCo"
        )
        for order in permutations((seventy_two, seventy_two_0)):
            self.assertEqual(select(order), seventy_two_0)
        # Equal values: the greater system decides, by unsigned bytes.
        low = Version(("https://a.example/s", "v0:k:1:x"), "2026-08-20T17:30:02Z", None, ("low",), "low")
        high = Version(("https://b.example/s", "v0:k:1:x"), "2026-08-20T17:30:02Z", None, ("high",), "high")
        self.assertEqual(select([high, low]), high)
        # Unsigned UTF-8 bytes, not UTF-16 code units: U+10000 is greater than U+FFFF.
        bmp = version("bmp", "2026-08-20T17:30:02Z", value="v0:k:1:￿")
        astral = version("astral", "2026-08-20T17:30:02Z", value="v0:k:1:\U00010000")
        self.assertEqual(select([bmp, astral]), astral)

    def test_the_catalog_vectors_reach_the_documented_tie_break(self):
        catalog = json.loads((ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["recordVersion"]["receiverUse"], "equality-and-tie-break")
        identities = {vector["id"]: vector for vector in catalog["testVectors"]["identities"]}
        systems = {row["identityKind"]: row["system"] for row in catalog["testVectors"]["identitySystems"]}
        versions = [
            Version((systems["record-version"], identities[name]["value"]), "2026-08-20T17:30:02Z", None, (name,), name)
            for name in ("record-version-heart-rate-72", "record-version-heart-rate-72-0")
        ]
        # Both versions name one source record: the same source-record pair, another content digest.
        self.assertEqual(
            [identities[version.name]["components"][:2] for version in versions][0],
            [identities[version.name]["components"][:2] for version in versions][1],
        )
        for order in permutations(versions):
            self.assertEqual(select(order).name, "record-version-heart-rate-72-0")

    def test_the_set_rule_never_returns_a_superseded_writer_version(self):
        # Pairwise D2-A is cyclic here: a > b by writer version, b > c and c > a by recorded.
        a = version("a", "2026-08-20T17:30:01Z", (WRITER, "2"))
        b = version("b", "2026-08-20T17:30:03Z", (WRITER, "1"))
        c = version("c", "2026-08-20T17:30:02Z")
        self.assertEqual(select([a, b]), a)
        self.assertEqual(select([b, c]), b)
        self.assertEqual(select([c, a]), c)
        for order in permutations((a, b, c)):
            self.assertEqual(select(order), c)
        for size in (2, 3):
            for subset in combinations((a, b, c), size):
                if a in subset:
                    self.assertNotEqual(select(subset), b)

    def test_writer_versions_are_canonical_unsigned_decimals(self):
        self.assertTrue(writer_version_greater("10", "9"))
        self.assertTrue(writer_version_greater("9007199254740993", "9007199254740992"))
        self.assertFalse(writer_version_greater("9007199254740992", "9007199254740992"))
        # A float reading would call these two equal.
        self.assertEqual(float("9007199254740993"), float("9007199254740992"))
        for invalid in ("01", "-1", "1.0", "", " 1"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                writer_version_greater(invalid, "1")

    def test_writer_evidence_is_one_statement_or_none(self):
        def output(writer=None, writer_version=None):
            resource = {"resourceType": "Observation", "identifier": [], "extension": []}
            if writer is not None:
                resource["identifier"].append({
                    "type": {"coding": [{"system": ROLE_SYSTEM, "code": "writer-record"}]},
                    "system": writer[0], "value": writer[1],
                })
            if writer_version is not None:
                resource["extension"].append({"url": WRITER_VERSION, "valueString": writer_version})
            return resource

        stated = output(WRITER, "7")
        self.assertEqual(writer_evidence([stated]), (WRITER, "7"))
        # Outputs stating nothing are ignored; agreeing statements are one statement.
        self.assertEqual(writer_evidence([stated, output(), output(WRITER, "7")]), (WRITER, "7"))
        for outputs in ([], [output()], [output(WRITER)], [stated, output(WRITER, "8")], [stated, output(OTHER_WRITER, "7")]):
            with self.subTest(outputs=outputs):
                self.assertIsNone(writer_evidence(outputs))

    def test_membership_is_the_selected_versions_outputs_and_a_retraction_clears_it(self):
        first = version("v1", "2026-08-20T17:30:09Z", (WRITER, "1"), outputs=("primary", "secondary"))
        second = version("v2", "2026-08-20T17:30:08Z", (WRITER, "2"), outputs=("primary",))
        self.assertEqual(current_outputs([first, second]), ("primary",))
        self.assertEqual(current_outputs([first, second], retracted=True), ())
        self.assertEqual(current_outputs([]), ())


if __name__ == "__main__":
    unittest.main()
