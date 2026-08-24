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
                "grove-csv-1",
                "fhir-json-1",
                "native-json-1",
                "provider-json-1",
                "grove-ppg-1",
                "grove-batch-archive-1",
                "fhir-resource-1",
            ],
        )
        for code, fmt in REGISTRY["formats"].items():
            self.assertEqual(fmt["status"], "active", code)
            self.assertTrue(fmt["title"], code)
            self.assertIn("contentType", fmt, code)
            self.assertTrue(fmt["specification"], code)

    def test_format_content_types_are_admitted_mime_codes(self) -> None:
        terminology = (ROOT / "sensor/input/fsh/terminology.fsh").read_text(
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
        schemas = REGISTRY["formats"]["grove-csv-1"]["columnSchemas"]
        self.assertEqual(
            set(schemas),
            {
                "heart-rate",
                "accelerometer",
                "ambient-light",
                "ambient-pressure",
                "pedometer",
                "wrist-temperature",
                "rotation-rate",
                "odometer",
                "heartbeat-series",
            },
        )
        for stream, schema in schemas.items():
            self.assertTrue(schema["source"], stream)
            names = [column["name"] for column in schema["columns"]]
            self.assertEqual(len(names), len(set(names)), stream)
            for column in schema["columns"]:
                self.assertIn(column["type"], {"timestamp", "number", "integer", "string"})
                self.assertTrue(column["meaning"], f"{stream}.{column['name']}")

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
        streams_with_csv = {
            entry["sourceTypeCode"]
            for entry in adapter["entries"]
            if isinstance(entry.get("raw"), dict)
            and "grove-csv-1" in entry["raw"].get("formats", [])
        }
        # heartbeat-series is a HealthKit recording schema, not a SensorKit stream.
        self.assertEqual(
            streams_with_csv,
            set(REGISTRY["formats"]["grove-csv-1"]["columnSchemas"]) - {"heartbeat-series"},
        )

    def test_rendered_outputs_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "Scripts/render-format-registry.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
