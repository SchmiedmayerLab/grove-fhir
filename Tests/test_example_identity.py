"""Keep SensorKit examples aligned with the opaque v0 identity contract."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HMAC_VALUE = re.compile(r"v0:test-key:1:[A-Za-z0-9_-]{43}")


class ExampleIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (ROOT / "sensorkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )

    def test_every_opaque_example_identity_has_the_canonical_v0_shape(self) -> None:
        values = re.findall(
            r'^\* identifier\[(?:sourceRecord|sourceOutput|sourceArtifact)\]\.value = "([^"]+)"$',
            self.source,
            re.MULTILINE,
        )
        self.assertTrue(values)
        for value in values:
            with self.subTest(value=value):
                self.assertIsNotNone(HMAC_VALUE.fullmatch(value))

    def test_each_output_identity_is_unique_even_when_a_source_record_has_two_outputs(self) -> None:
        values = re.findall(
            r'^\* identifier\[sourceOutput\]\.value = "([^"]+)"$',
            self.source,
            re.MULTILINE,
        )
        self.assertTrue(values)
        self.assertEqual(len(values), len(set(values)))

    def test_every_recording_document_has_record_output_and_artifact_identity(self) -> None:
        blocks = re.split(r"(?=^Instance: )", self.source, flags=re.MULTILINE)
        recordings = [
            block for block in blocks if "InstanceOf: SensorKitRecordingDocument" in block
        ]
        self.assertTrue(recordings)
        for block in recordings:
            name = re.search(r"^Instance: (\S+)", block, re.MULTILINE)
            with self.subTest(instance=name.group(1) if name else "unknown"):
                for role in ("sourceRecord", "sourceOutput", "sourceArtifact"):
                    self.assertEqual(
                        len(
                            re.findall(
                                rf"^\* identifier\[{role}\]\.value = ",
                                block,
                                re.MULTILINE,
                            )
                        ),
                        1,
                    )
                self.assertEqual(
                    len(re.findall(r"^\* content\.attachment\.data = ", block, re.MULTILINE)),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
