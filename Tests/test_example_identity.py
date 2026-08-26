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


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_IDENTIFIER = re.compile(
    r'^\* identifier\[sensorKitOutputId\]\.value = "v1:[^|]+\|([a-z-]+)"$', re.MULTILINE
)


class ExampleIdentityTests(unittest.TestCase):
    """A published example must use the discriminators the catalog declares.

    The recording-format registry and the output-identifier discriminator share tokens, and an
    author reaching for the wrong one produces an example the IG build accepts and the producer
    validator rejects. Nothing else compares the two vocabularies.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )

    def declared_discriminators(self) -> set[str]:
        found: set[str] = set()
        for entry in self.catalog["entries"]:
            for section in ("structured", "raw"):
                block = entry.get(section)
                if isinstance(block, dict) and "outputDiscriminator" in block:
                    found.add(block["outputDiscriminator"])
        return found

    def test_every_example_discriminator_is_declared(self) -> None:
        declared = self.declared_discriminators()
        self.assertTrue(declared, "the catalog declares no output discriminators")
        source = (ROOT / "sensorkit/input/fsh/examples.fsh").read_text(encoding="utf-8")
        used = set(OUTPUT_IDENTIFIER.findall(source))
        self.assertTrue(used, "no output identifiers found in the SensorKit examples")
        self.assertEqual(used - declared, set())

    def test_no_example_uses_a_format_code_as_a_discriminator(self) -> None:
        # The two vocabularies overlap on `native-recording`; a format code that is not also a
        # declared discriminator must never appear in an output identifier.
        registry = json.loads(
            (ROOT / "catalog/format-registry.json").read_text(encoding="utf-8")
        )
        declared = self.declared_discriminators()
        format_only = set(registry["formats"]) - declared
        source = (ROOT / "sensorkit/input/fsh/examples.fsh").read_text(encoding="utf-8")
        for discriminator in set(OUTPUT_IDENTIFIER.findall(source)):
            with self.subTest(discriminator=discriminator):
                self.assertNotIn(discriminator, format_only)
