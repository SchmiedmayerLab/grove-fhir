#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

import base64
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
                self.assertIsInstance(column["nullable"], bool)
                self.assertTrue(column["meaning"], f"{stream}.{column['name']}")
                if column["nullable"]:
                    self.assertIn("empty", column["meaning"].lower())

    def test_csv_lexical_and_empty_field_rules_are_explicit(self) -> None:
        encoding = REGISTRY["encodings"]["csv"]
        number_pattern = re.compile(encoding["numberPattern"])
        integer_pattern = re.compile(encoding["integerPattern"])
        for value in ("0", "0.0", "0.1", "1", "1.0", "1.01", "-0.1", "-1.0"):
            with self.subTest(number=value):
                self.assertIsNotNone(number_pattern.fullmatch(value))
        for value in ("-0", "-0.0", "00", "01", "1.00", "1.20", "+1", "1e1"):
            with self.subTest(invalid_number=value):
                self.assertIsNone(number_pattern.fullmatch(value))
        for value in ("0", "1", "-1"):
            with self.subTest(integer=value):
                self.assertIsNotNone(integer_pattern.fullmatch(value))
        for value in ("-0", "00", "01", "1.0", "+1", "1e1"):
            with self.subTest(invalid_integer=value):
                self.assertIsNone(integer_pattern.fullmatch(value))
        self.assertIn("-0", encoding["integers"])
        self.assertIn("leading zero", encoding["integers"])
        self.assertIn("redundant fractional trailing zero", encoding["numbers"])
        self.assertIn("lone fractional .0", encoding["numbers"])
        self.assertEqual(encoding["numberValueDomain"], "finite-ieee754-binary64")
        self.assertIn("IEEE-754 binary64", encoding["numbers"])
        self.assertIn("IEEE-754 binary64", encoding["timestamps"])
        self.assertIn("CR (0x0D) is prohibited anywhere", encoding["rowTerminator"])
        self.assertIn("`Nullable` column controls empty fields", encoding["emptyFields"])
        self.assertIn("`no` requires a non-empty field", encoding["emptyFields"])
        self.assertIn("`yes` permits an empty field", encoding["emptyFields"])

    def test_ambient_light_uses_the_correct_chromaticity_spelling(self) -> None:
        columns = [
            column["name"]
            for column in REGISTRY["formats"]["ambient-light-samples"]["columns"]
        ]
        self.assertEqual(columns[3:5], ["chromaticityX", "chromaticityY"])

    def test_a_format_code_never_names_its_encoding(self) -> None:
        # The code identifies the payload's wire format; the media type carries its encoding.
        for code in REGISTRY["formats"]:
            for encoding in ("csv", "json", "binary", "octet"):
                self.assertNotIn(encoding, code.split("-"), code)

    def test_native_recording_is_a_generic_json_envelope_not_a_schema_gate(self) -> None:
        specification = REGISTRY["formats"]["native-recording"]["specification"]
        self.assertIn("strict UTF-8 JSON", specification["structure"])
        self.assertIn("object or array root", specification["structure"])
        self.assertIn("duplicate object member names", specification["structure"])
        self.assertIn("scalar roots", specification["structure"])
        self.assertIn("no per-stream field schema", specification["schema"])
        self.assertIn("source category and meaning", specification["schema"])
        self.assertIn("does not reinterpret, sanitize, rewrite, or reserialize", specification["scope"])

        adapter = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        native_rows = [
            entry["raw"]
            for entry in adapter["entries"]
            if "native-recording" in entry.get("raw", {}).get("formats", [])
        ]
        self.assertTrue(native_rows)
        self.assertTrue(all("jsonSchema" not in raw for raw in native_rows))

        page = (ROOT / "sensor/input/pagecontent/formats.md").read_text(encoding="utf-8")
        self.assertIn("carrying source type", page)
        self.assertIn("no per-stream field schema", page)

    def test_fhir_collection_generic_validation_scope_is_explicit(self) -> None:
        validation_scope = REGISTRY["formats"]["fhir-collection-bundle"][
            "specification"
        ]["validationScope"]
        self.assertIn("Grove format validation verifies strict JSON syntax", validation_scope)
        self.assertIn("does not execute the official FHIR Validator", validation_scope)
        self.assertIn("Base FHIR R4 conformance", validation_scope)
        self.assertIn("adapter-declared resource profiles", validation_scope)
        self.assertIn("one-stream/one-source-batch boundary", validation_scope)
        self.assertIn("source ordering", validation_scope)
        self.assertIn("source meaning", validation_scope)
        self.assertIn("producer responsibilities", validation_scope)

        page = (ROOT / "sensor/input/pagecontent/formats.md").read_text(encoding="utf-8")
        self.assertIn(validation_scope, page)

    def test_registry_describes_only_validation_that_is_executed(self) -> None:
        description = REGISTRY["description"]
        self.assertIn("Grove format validation checks", description)
        self.assertIn("FHIR/profile", description)
        self.assertNotIn("receiver can validate the admitted wire format", description)
        fhir_resource_scope = REGISTRY["formats"]["fhir-r4-resource"][
            "specification"
        ]["scope"]
        self.assertIn("`resourceType`-bearing object only", fhir_resource_scope)
        self.assertIn("does not determine the FHIR release", fhir_resource_scope)
        provider_scope = REGISTRY["formats"]["provider-recording"][
            "specification"
        ]["scope"]
        self.assertIn("strict JSON syntax", provider_scope)
        self.assertIn("provider-domain schema", provider_scope)

    def test_ppg_integer_signedness_is_explicit(self) -> None:
        specification = REGISTRY["formats"]["photoplethysmogram-samples"]["specification"]
        optical_fields = {
            field["field"]: field["encoding"] for field in specification["opticalSample"]
        }
        self.assertEqual(optical_fields["emitter"], "varint(int64)")
        self.assertEqual(optical_fields["signalIdentifier"], "varint(int64)")
        self.assertEqual(
            optical_fields["activePhotodiodeIndexes"],
            "set(varint(uint64))",
        )

    def test_ppg_noise_terms_define_their_dimensions(self) -> None:
        specification = REGISTRY["formats"]["photoplethysmogram-samples"]["specification"]
        noise_fields = {
            field["field"]: field for field in specification["noiseTerms"]
        }
        self.assertEqual(noise_fields["whiteNoise"]["unit"], "Normalized Units²/Hz")
        self.assertIn("per hertz", noise_fields["whiteNoise"]["meaning"])
        self.assertEqual(noise_fields["pinkNoise"]["unit"], "Normalized Units²")
        self.assertEqual(noise_fields["backgroundNoise"]["unit"], "Normalized Units")
        self.assertEqual(
            noise_fields["backgroundNoiseOffset"]["unit"],
            "Normalized Units²/Hz",
        )
        self.assertIn(
            "per hertz",
            noise_fields["backgroundNoiseOffset"]["meaning"],
        )

    def test_heartbeat_timestamps_are_unix_epoch_instants(self) -> None:
        timestamp = REGISTRY["formats"]["beat-interval-series"]["columns"][0]
        self.assertEqual(timestamp["name"], "timestamp")
        self.assertIn("Unix epoch", timestamp["meaning"])
        self.assertNotIn("series start", timestamp["meaning"])

        examples = (ROOT / "healthkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )
        block = examples.split(
            "Instance: HealthKitHeartbeatSeriesRecordingExample", 1
        )[1].split("Instance:", 1)[0]
        encoded = re.search(
            r'^\* content\.attachment\.data = "([^"]+)"$',
            block,
            re.MULTILINE,
        )
        self.assertIsNotNone(encoded)
        assert encoded is not None
        rows = base64.b64decode(encoded.group(1), validate=True).decode("utf-8").splitlines()
        self.assertGreater(float(rows[1].split(",", 1)[0]), 1_000_000_000)

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
