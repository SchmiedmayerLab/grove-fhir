#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads(
    (ROOT / "catalog/format-registry.json").read_text(encoding="utf-8")
)


class FormatRegistryTests(unittest.TestCase):
    def test_registry_is_closed_and_complete(self) -> None:
        self.assertEqual(
            list(REGISTRY["formats"]),
            [
                "heart-rate-samples",
                "triaxial-acceleration-samples",
                "ambient-light-samples",
                "ambient-pressure-samples",
                "pedometer-samples",
                "wrist-temperature-samples",
                "triaxial-rotation-samples",
                "odometer-samples",
                "beat-interval-series",
                "location-track-samples",
                "fhir-collection-bundle",
                "fhir-r4-resource",
                "clinical-document",
                "native-recording",
                "provider-recording",
                "photoplethysmogram-samples",
            ],
        )
        for code, fmt in REGISTRY["formats"].items():
            self.assertEqual(fmt["status"], "active", code)
            self.assertTrue(fmt["title"], code)
            self.assertIn("contentType", fmt, code)
            self.assertTrue(fmt.get("specification") or fmt.get("encoding"), code)
            if "encoding" in fmt:
                self.assertIn(fmt["encoding"], REGISTRY["encodings"], code)
                self.assertTrue(fmt["columns"], code)

    def test_format_content_types_are_admitted_mime_codes(self) -> None:
        terminology = (ROOT / "sensor/input/fsh/generated-recording-mime-types.fsh").read_text(
            encoding="utf-8"
        )
        expected = {fmt["contentType"] for fmt in REGISTRY["formats"].values()}
        composed = set(
            re.findall(r"^\* urn:ietf:bcp:13#(\S+) ", terminology, re.MULTILINE)
        )
        # The Validator reads the pinned expansion offline, so an admitted code that
        # never reaches it is rejected at conformance time rather than here.
        expanded = set(
            re.findall(
                r"^\* \^expansion\.contains\[=\]\.code = #(\S+)$",
                terminology,
                re.MULTILINE,
            )
        )
        self.assertEqual(composed, expected)
        self.assertEqual(expanded, expected)

    def test_csv_column_schemas_are_closed(self) -> None:
        schemas = {
            code: fmt
            for code, fmt in REGISTRY["formats"].items()
            if fmt.get("encoding") == "csv"
        }
        self.assertEqual(
            set(schemas),
            {
                "heart-rate-samples",
                "triaxial-acceleration-samples",
                "ambient-light-samples",
                "ambient-pressure-samples",
                "pedometer-samples",
                "wrist-temperature-samples",
                "triaxial-rotation-samples",
                "odometer-samples",
                "beat-interval-series",
                "location-track-samples",
            },
        )
        for stream, schema in schemas.items():
            names = [column["name"] for column in schema["columns"]]
            self.assertEqual(len(names), len(set(names)), stream)
            for column in schema["columns"]:
                self.assertIn(column["type"], {"timestamp", "number", "integer", "string"})
                self.assertTrue(column["meaning"], f"{stream}.{column['name']}")

    def test_a_format_code_never_names_its_encoding(self) -> None:
        # The code names the payload's schema; the encoding is the media type's job.
        for code in REGISTRY["formats"]:
            for encoding in ("csv", "json", "binary", "octet"):
                self.assertNotIn(encoding, code.split("-"), code)

    def test_sensorkit_streams_reference_registered_formats(self) -> None:
        adapter = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        registered = set(REGISTRY["formats"])
        raw_rows = 0
        for entry in adapter["entries"]:
            raw = entry.get("raw")
            if not isinstance(raw, dict) or raw.get("status") != "mapped-standard":
                continue
            raw_rows += 1
            self.assertIn("formats", raw, entry["sourceTypeCode"])
            for code in raw["formats"]:
                self.assertIn(code, registered, entry["sourceTypeCode"])
            if not raw["formats"]:
                self.assertTrue(raw.get("formatsReason"), entry["sourceTypeCode"])
        self.assertGreaterEqual(raw_rows, 20)
        csv_codes = {
            code for code, fmt in REGISTRY["formats"].items() if fmt.get("encoding") == "csv"
        }
        cited = {
            code
            for entry in adapter["entries"]
            if isinstance(entry.get("raw"), dict)
            for code in entry["raw"].get("formats", [])
            if code in csv_codes
        }
        # Both are HealthKit recording schemas rather than SensorKit streams: a beat-to-beat
        # interval series and a workout route are HealthKit series, so no SensorKit row cites them.
        self.assertEqual(cited, csv_codes - {"beat-interval-series", "location-track-samples"})

    def test_rendered_outputs_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "Scripts/render-format-registry.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()


class RegistryIsPlatformNeutralTests(unittest.TestCase):
    """The shared registry names payload schemas, never the platforms that produce them.

    A column's meaning may still name the platform enumeration that defines its values: that is
    what the value means, and dropping it would make the column unreadable. What may not appear
    is a claim about which platform the format itself belongs to.
    """

    def test_no_format_declares_a_producing_platform(self) -> None:
        for code, fmt in REGISTRY["formats"].items():
            self.assertNotIn("source", fmt, code)

    def test_no_concept_definition_names_a_platform_symbol(self) -> None:
        fsh = (ROOT / "sensor/input/fsh/generated-recording-formats.fsh").read_text(encoding="utf-8")
        for line in fsh.splitlines():
            if not line.startswith("* #"):
                continue
            for symbol in ("SRSensor.", "CMRecorded", "CMHighFrequency", "HKDataTypeIdentifier"):
                self.assertNotIn(symbol, line, f"{symbol} in {line[:60]}")

    def test_the_formats_page_states_no_format_level_provenance(self) -> None:
        page = (ROOT / "sensor/input/pagecontent/formats.md").read_text(encoding="utf-8")
        for lead in ("Source:", "First defined for:"):
            self.assertNotIn(lead, page, lead)
