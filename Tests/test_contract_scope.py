#!/usr/bin/env python3
"""Keep the active guides limited to the reviewed Mobile and HealthKit scope."""

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
DECLARATION = re.compile(
    r"^(Profile|Extension|CodeSystem|ValueSet|Instance|Invariant):\s+(\S+)",
    re.MULTILINE,
)

MOBILE_DECLARATIONS = {
    ("Profile", "GroveSensorDevice"),
    ("Profile", "GroveGatewayDevice"),
    ("Profile", "GroveMobileSensorObservation"),
    ("Extension", "GroveInferredValue"),
    ("Extension", "GroveRecordingMethod"),
    ("Extension", "GrovePlatformMetadata"),
    ("CodeSystem", "GroveDeviceVersionType"),
    ("CodeSystem", "GroveRecordingMethodCS"),
    ("ValueSet", "GroveRecordingMethodVS"),
    ("CodeSystem", "GroveDeviceType"),
    ("ValueSet", "GroveDeviceTypeVS"),
    ("ValueSet", "GrovePlatformMetadataKeyVS"),
}

HEALTHKIT_KEY_SPACE_DECLARATIONS = {
    ("CodeSystem", "HealthKitSampleTypeCS"),
    ("ValueSet", "HealthKitSampleTypeVS"),
    ("CodeSystem", "HealthKitMetadataKeyCS"),
    ("ValueSet", "HealthKitMetadataKeyVS"),
}


def declarations(path: Path) -> set[tuple[str, str]]:
    return set(DECLARATION.findall(path.read_text(encoding="utf-8")))


class ContractScopeTests(unittest.TestCase):
    def test_mobile_guide_contains_only_reviewed_declarations(self) -> None:
        directory = ROOT / "ig/input/fsh"
        self.assertEqual(
            {path.name for path in directory.glob("*.fsh")},
            {"aliases.fsh", "extensions.fsh", "profiles.fsh", "terminology.fsh"},
        )
        actual: set[tuple[str, str]] = set()
        for path in directory.glob("*.fsh"):
            actual.update(declarations(path))
        self.assertEqual(actual, MOBILE_DECLARATIONS)

    def test_platform_guide_contains_only_healthkit_terminology(self) -> None:
        directory = ROOT / "platforms/input/fsh"
        self.assertEqual(
            {path.name for path in directory.glob("*.fsh")},
            {"generated-healthkit-values.fsh", "key-spaces.fsh"},
        )
        self.assertEqual(
            declarations(directory / "key-spaces.fsh"),
            HEALTHKIT_KEY_SPACE_DECLARATIONS,
        )
        generated = declarations(directory / "generated-healthkit-values.fsh")
        self.assertEqual(len(generated), 42)
        self.assertTrue(all(kind == "CodeSystem" for kind, _ in generated))


if __name__ == "__main__":
    unittest.main()
