"""Hold every adapter catalog to the platform inventory recorded as evidence.

These checks are the reason a catalog may call itself closed. They compare the catalog
against `*/input/data/*-inventory.json`, which is generated from the platform rather
than written by hand, and they run offline so neither an Apple SDK nor network access
can turn them into skips.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parents[1]
FHIR_CODE = re.compile(r"[^\s]+(\s[^\s]+)*")


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def compare(evidence: dict[str, Any], rows: dict[str, Any], expected: int) -> None:
    """Fail unless the catalog is exactly the recorded platform inventory.

    `expected` is the count read from the platform. Without it, dropping the same
    entries from catalog and evidence together still satisfies set equality.
    """
    if len(evidence) != expected:
        raise AssertionError(f"evidence holds {len(evidence)} entries, expected {expected}")
    if len(rows) != expected:
        raise AssertionError(f"catalog holds {len(rows)} rows, expected {expected}")
    problems = []
    if fabricated := sorted(rows.keys() - evidence.keys()):
        problems.append(f"catalog claims codes the platform does not publish: {fabricated}")
    if omitted := sorted(evidence.keys() - rows.keys()):
        problems.append(f"catalog omits published platform codes: {omitted}")
    if problems:
        raise AssertionError("; ".join(problems))


class HealthKitInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = load("healthkit/input/data/healthkit-inventory.json")["sourceTypes"]
        cls.catalog = load("catalog/healthkit-adapter.json")
        cls.rows = {row["sourceTypeIdentifier"]: row for row in cls.catalog["rows"]}

    def test_catalog_is_exactly_the_recorded_platform_inventory(self) -> None:
        compare(self.evidence, self.rows, expected=220)

    def test_every_row_carries_the_platform_facts_it_was_verified_against(self) -> None:
        for code, fact in self.evidence.items():
            self.assertEqual(self.rows[code]["symbols"], fact["symbols"], code)
            self.assertEqual(self.rows[code]["documentation"], fact["documentation"], code)

    def test_a_code_is_an_identifier_rather_than_a_constant_name(self) -> None:
        # Apple can rename a constant while keeping its value, and can publish a sample
        # type with no constant at all. Only the runtime identifier is emittable, so a
        # declaring name that is not itself an identifier must never become a code.
        names = {name for fact in self.evidence.values() for name in fact["symbols"]}
        self.assertNotIn("HKCategoryTypeIdentifierEnvironmentalAudioExposureEvent", self.rows)
        self.assertIn("HKCategoryTypeIdentifierEnvironmentalAudioExposureEvent", names)

    def test_the_row_count_is_not_an_independently_maintained_number(self) -> None:
        self.assertEqual(self.catalog["source"]["rowCount"], len(self.rows))

    def test_codes_are_usable_as_fhir_codes(self) -> None:
        for code in self.rows:
            self.assertTrue(FHIR_CODE.fullmatch(code), code)


class SensorKitInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = load("sensorkit/input/data/sensorkit-inventory.json")["sensors"]
        cls.rows = {
            entry["symbol"]: entry
            for entry in load("catalog/sensorkit-adapter.json")["entries"]
        }

    def test_catalog_is_exactly_the_recorded_platform_inventory(self) -> None:
        compare(self.evidence, self.rows, expected=24)

    def test_every_entry_carries_the_platform_facts(self) -> None:
        for symbol, fact in self.evidence.items():
            self.assertEqual(self.rows[symbol]["identifier"], fact["identifier"], symbol)
            self.assertEqual(self.rows[symbol]["documentation"], fact["documentation"], symbol)


class HealthConnectInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = load("health-connect/input/data/health-connect-inventory.json")["records"]
        cls.rows = {
            row["token"]: row
            for row in load("catalog/health-connect-adapter.json")["recordTypes"]
        }

    def test_catalog_is_exactly_the_recorded_platform_inventory(self) -> None:
        compare(self.evidence, self.rows, expected=41)

    def test_every_record_records_its_documentation_page(self) -> None:
        for token, fact in self.evidence.items():
            self.assertEqual(self.rows[token]["documentation"], fact["documentation"], token)

    def test_displays_are_authored_rather_than_repeated_class_names(self) -> None:
        for token, row in self.rows.items():
            self.assertNotEqual(row["title"], token, token)


class ComparisonTests(unittest.TestCase):
    """The comparison itself must fail on the defects it exists to catch."""

    EVIDENCE = {"RealCodeOne": {}, "RealCodeTwo": {}, "RealCodeThree": {}}

    def test_a_substitution_names_both_the_fabricated_and_the_omitted_code(self) -> None:
        # Substitution keeps the count intact, so only the set comparison can catch it.
        rows = {"RealCodeOne": {}, "RealCodeTwo": {}, "RealCodeFour": {}}
        with self.assertRaises(AssertionError) as raised:
            compare(self.EVIDENCE, rows, expected=3)
        self.assertIn("RealCodeFour", str(raised.exception))
        self.assertIn("RealCodeThree", str(raised.exception))

    def test_shrinking_both_sides_together_is_rejected(self) -> None:
        pair = {"RealCodeOne": {}, "RealCodeTwo": {}}
        with self.assertRaises(AssertionError):
            compare(pair, pair, expected=3)

    def test_two_empty_sides_do_not_pass_as_agreement(self) -> None:
        with self.assertRaises(AssertionError):
            compare({}, {}, expected=3)


if __name__ == "__main__":
    unittest.main()
