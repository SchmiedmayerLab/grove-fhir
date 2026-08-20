#!/usr/bin/env python3
"""Keep the redesign inventory synchronized with every FSH declaration."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "ARTIFACT_INVENTORY.md"
FSH_DIRECTORIES = (
    ROOT / "ig/input/fsh",
    ROOT / "platforms/input/fsh",
    ROOT / "archive/v0-healthkit-shaped/input/fsh",
)
DECLARATION = re.compile(
    r"^(Profile|Extension|CodeSystem|ValueSet|Instance|Invariant):\s+(\S+)",
    re.MULTILINE,
)
FSH_ROW = re.compile(
    r"^\| `(?P<source>[^`]+)` \| `(?P<status>[^`]+)` "
    r"\| `(?P<kind>[^`]+)` \| `(?P<name>[^`]+)` \|$",
    re.MULTILINE,
)
FSH_STATUSES = {
    "candidate-mobile",
    "candidate-questionnaire",
    "evidence-pending",
    "excluded-image-annotation",
    "experimental-questionnaire",
    "experimental-sensorkit",
    "generated-platform-terminology",
    "illustrative-mobile-example",
    "illustrative-questionnaire-example",
    "legacy-archive",
}


def bounded_section(text: str, name: str) -> str:
    start_marker = f"<!-- {name}:start -->"
    end_marker = f"<!-- {name}:end -->"
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


class ArtifactInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = INVENTORY.read_text(encoding="utf-8")

    def test_every_fsh_declaration_has_one_disposition(self) -> None:
        actual: set[tuple[str, str, str]] = set()
        for directory in FSH_DIRECTORIES:
            for path in directory.rglob("*.fsh"):
                source = str(path.relative_to(ROOT))
                for kind, name in DECLARATION.findall(path.read_text(encoding="utf-8")):
                    actual.add((source, kind, name))

        section = bounded_section(self.inventory, "fsh-inventory")
        rows = [match.groupdict() for match in FSH_ROW.finditer(section)]
        inventoried = {
            (row["source"], row["kind"], row["name"])
            for row in rows
        }

        self.assertEqual(len(rows), len(inventoried), "inventory contains a duplicate FSH row")
        self.assertEqual(actual, inventoried)
        self.assertTrue(rows)
        self.assertEqual(
            set(row["status"] for row in rows) - FSH_STATUSES,
            set(),
            "inventory contains an unknown FSH disposition",
        )

if __name__ == "__main__":
    unittest.main()
