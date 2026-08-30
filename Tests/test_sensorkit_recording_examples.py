"""Keep SensorKit recording examples executable against the published wire contracts."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import math
import re
import struct
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = (ROOT / "sensorkit/input/fsh/examples.fsh").read_text(encoding="utf-8")
REGISTRY = json.loads((ROOT / "catalog/format-registry.json").read_text(encoding="utf-8"))
ADAPTER = json.loads((ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8"))

NUMBER = re.compile(REGISTRY["encodings"]["csv"]["numberPattern"])
INTEGER = re.compile(REGISTRY["encodings"]["csv"]["integerPattern"])


def instance_blocks() -> dict[str, str]:
    return {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"^Instance: (\S+)\n(.*?)(?=^Instance: |\Z)",
            EXAMPLES,
            re.MULTILINE | re.DOTALL,
        )
    }


def required_match(block: str, pattern: str) -> str:
    match = re.search(pattern, block, re.MULTILINE)
    if match is None:
        raise AssertionError(f"example block does not match {pattern!r}")
    return match.group(1)


def attachment_bytes(block: str) -> bytes:
    encoded = required_match(block, r'^\* content\.attachment\.data = "([^"]+)"$')
    return base64.b64decode(encoded, validate=True)


def native_json(block: str) -> dict[str, object] | list[object]:
    payload = attachment_bytes(block)
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError("native JSON must not carry a byte-order mark")

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number {value}")

    value = json.loads(
        payload.decode("utf-8", errors="strict"),
        parse_constant=reject_constant,
    )
    if not isinstance(value, (dict, list)):
        raise ValueError("native JSON root must be an object or array")
    return value


def component_counts(block: str) -> dict[str, int]:
    return {
        name: int(value)
        for name, value in re.findall(
            r"^\* component\[([^]]+)\]\.valueQuantity = ([0-9]+) '\{count\}'(?: \"\{count\}\")?$",
            block,
            re.MULTILINE,
        )
    }


def coverage(block: str) -> tuple[float, float]:
    start = required_match(block, r'^\* effectivePeriod\.start = "([^"]+)"$')
    end = required_match(block, r'^\* effectivePeriod\.end = "([^"]+)"$')
    return datetime.fromisoformat(start).timestamp(), datetime.fromisoformat(end).timestamp()


class PPGReader:
    """Small independent reader for the registry's closed PPG wire grammar."""

    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.offset = 0

    def take(self, count: int) -> bytes:
        end = self.offset + count
        if count < 0 or end > len(self.payload):
            raise ValueError("truncated PPG payload")
        value = self.payload[self.offset:end]
        self.offset = end
        return value

    def varint(self) -> int:
        value = 0
        for index in range(10):
            byte = self.take(1)[0]
            if index == 9 and byte > 1:
                raise ValueError("PPG varint exceeds 64 bits")
            value |= (byte & 0x7F) << (index * 7)
            if byte & 0x80 == 0:
                if index > 0 and byte == 0:
                    raise ValueError("PPG varint is not shortest-form")
                return value
        raise ValueError("unterminated PPG varint")

    def signed_varint(self) -> int:
        value = self.varint()
        return value - (1 << 64) if value & (1 << 63) else value

    def float64(self) -> float:
        raw = self.take(8)
        bits = int.from_bytes(raw, byteorder="big")
        value = struct.unpack(">d", raw)[0]
        if not math.isfinite(value) or bits == 0x8000000000000000:
            raise ValueError("PPG float is not canonical and finite")
        return value

    def boolean(self) -> bool:
        value = self.take(1)[0]
        if value not in {0, 1}:
            raise ValueError("PPG boolean is not canonical")
        return value == 1

    def string(self) -> str:
        return self.take(self.varint()).decode("utf-8", errors="strict")

    def array(self, read_element):  # type: ignore[no-untyped-def]
        return [read_element() for _ in range(self.varint())]

    def unsigned_set(self) -> list[int]:
        values = self.array(self.varint)
        if any(left >= right for left, right in zip(values, values[1:])):
            raise ValueError("PPG set is not unique and ascending")
        return values

    def finish(self) -> None:
        if self.offset != len(self.payload):
            raise ValueError("PPG payload has trailing bytes")


def read_ppg_counts(
    payload: bytes,
) -> tuple[dict[str, int], list[Decimal], list[tuple[int, list[int], int]]]:
    reader = PPGReader(payload)
    optical_sample_count = 0
    accelerometer_sample_count = 0
    payload_instants: list[Decimal] = []
    optical_channels: list[tuple[int, list[int], int]] = []

    def read_record() -> None:
        nonlocal optical_sample_count, accelerometer_sample_count
        session_start = Decimal(str(reader.float64()))
        record_offset = reader.signed_varint()
        record_instant = (
            session_start + Decimal(record_offset) / Decimal(1_000_000_000)
        )
        payload_instants.extend([session_start, record_instant])
        if reader.boolean():
            reader.float64()
        reader.array(reader.string)

        def read_optical_sample() -> None:
            emitter = reader.signed_varint()
            photodiodes = reader.unsigned_set()
            signal_identifier = reader.signed_varint()
            optical_channels.append((emitter, photodiodes, signal_identifier))
            reader.float64()
            reader.float64()
            reader.float64()
            sample_offset = reader.signed_varint()
            payload_instants.append(
                session_start + Decimal(sample_offset) / Decimal(1_000_000_000)
            )
            reader.array(reader.string)
            if reader.boolean():
                for _ in range(4):
                    reader.float64()
            if reader.boolean():
                reader.float64()

        def read_accelerometer_sample() -> None:
            sample_offset = reader.signed_varint()
            payload_instants.append(
                session_start + Decimal(sample_offset) / Decimal(1_000_000_000)
            )
            for _ in range(4):
                reader.float64()

        optical_samples = reader.array(read_optical_sample)
        accelerometer_samples = reader.array(read_accelerometer_sample)
        optical_sample_count += len(optical_samples)
        accelerometer_sample_count += len(accelerometer_samples)

    records = reader.array(read_record)
    reader.finish()
    return (
        {
            "recordCount": len(records),
            "opticalSampleCount": optical_sample_count,
            "accelerometerSampleCount": accelerometer_sample_count,
        },
        payload_instants,
        optical_channels,
    )


def read_csv_rows(payload: bytes, format_code: str) -> list[dict[str, str]]:
    text = payload.decode("utf-8", errors="strict")
    if not text.endswith("\n") or "\r" in text:
        raise ValueError("registered CSV rows must use a final LF and no CR")
    parsed = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    columns = [column["name"] for column in REGISTRY["formats"][format_code]["columns"]]
    if not parsed or parsed[0] != columns:
        raise ValueError("registered CSV header does not match its format")
    rows = parsed[1:]
    if any(len(row) != len(columns) for row in rows):
        raise ValueError("registered CSV row has the wrong number of columns")

    canonical = io.StringIO(newline="")
    writer = csv.writer(canonical, lineterminator="\n")
    writer.writerows(parsed)
    if canonical.getvalue() != text:
        raise ValueError("registered CSV is not canonically quoted")

    for row in rows:
        for field, column in zip(row, REGISTRY["formats"][format_code]["columns"], strict=True):
            if field == "":
                if not column["nullable"]:
                    raise ValueError(f"empty non-nullable {column['name']} field")
                continue
            if column["type"] in {"number", "timestamp"}:
                try:
                    number = float(field)
                except (OverflowError, ValueError) as error:
                    raise ValueError(f"invalid {column['type']} field") from error
                if (
                    NUMBER.fullmatch(field) is None
                    or not math.isfinite(number)
                ):
                    raise ValueError(f"invalid {column['type']} field")
            elif column["type"] == "integer" and INTEGER.fullmatch(field) is None:
                raise ValueError("invalid integer field")
    return [dict(zip(columns, row, strict=True)) for row in rows]


def csv_bytes(format_code: str, row: list[str]) -> bytes:
    columns = [
        column["name"] for column in REGISTRY["formats"][format_code]["columns"]
    ]
    value = io.StringIO(newline="")
    writer = csv.writer(value, lineterminator="\n")
    writer.writerows([columns, row])
    return value.getvalue().encode("utf-8")


class SensorKitRecordingExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blocks = instance_blocks()
        cls.catalog_rows = {
            row["sourceTypeCode"]: row for row in ADAPTER["entries"]
        }

    def test_every_linked_summary_and_document_share_one_source_record(self) -> None:
        linked = 0
        for observation_name, observation in self.blocks.items():
            match = re.search(
                r"^\* derivedFrom = Reference\((\S+)\)$", observation, re.MULTILINE
            )
            if match is None:
                continue
            linked += 1
            document_name = match.group(1)
            document = self.blocks[document_name]
            with self.subTest(observation=observation_name, document=document_name):
                self.assertIn("InstanceOf: SensorKitRecordingDocument", document)
                for field in ("system", "value"):
                    pattern = rf'^\* identifier\[sourceRecord\]\.{field} = "([^"]+)"$'
                    self.assertEqual(
                        required_match(observation, pattern),
                        required_match(document, pattern),
                    )
                self.assertEqual(
                    required_match(
                        observation,
                        r"^\* extension\[sensorKitSourceType\]\.valueCode = #(\S+)$",
                    ),
                    required_match(
                        document,
                        r"^\* extension\[sensorKitSourceType\]\.valueCode = #(\S+)$",
                    ),
                )
                self.assertEqual(
                    required_match(
                        document,
                        r"^\* context\.related = Reference\((\S+)\)$",
                    ),
                    observation_name,
                )
                document_date = datetime.fromisoformat(required_match(
                    document,
                    r'^\* date = "([^"]+)"$',
                )).timestamp()
                _start, end = coverage(observation)
                self.assertGreaterEqual(document_date, end)
        self.assertEqual(linked, 7)

    def test_every_recording_uses_an_admitted_registered_format_and_exact_integrity(self) -> None:
        recordings = 0
        for name, block in self.blocks.items():
            if "InstanceOf: SensorKitRecordingDocument" not in block:
                continue
            recordings += 1
            with self.subTest(instance=name):
                source_type = required_match(
                    block,
                    r"^\* extension\[sensorKitSourceType\]\.valueCode = #(\S+)$",
                )
                format_code = required_match(
                    block, r"^\* content\.format = \$recordingFormat#(\S+) "
                )
                content_type = required_match(
                    block, r"^\* content\.attachment\.contentType = #(\S+)$"
                )
                payload = attachment_bytes(block)
                declared_size = int(required_match(
                    block, r"^\* content\.attachment\.size = ([0-9]+)$"
                ))
                declared_hash = required_match(
                    block, r'^\* content\.attachment\.hash = "([^"]+)"$'
                )

                self.assertIn(format_code, self.catalog_rows[source_type]["raw"]["formats"])
                format_entry = REGISTRY["formats"][format_code]
                self.assertIn(
                    content_type,
                    format_entry.get("contentTypes", [format_entry.get("contentType")]),
                )
                self.assertNotIn("* content.format.version =", block)
                self.assertEqual(declared_size, len(payload))
                # SHA-1 is required here by FHIR R4 Attachment.hash.
                self.assertEqual(
                    declared_hash,
                    base64.b64encode(hashlib.sha1(payload).digest()).decode("ascii"),
                )
        self.assertEqual(recordings, 7)

    def test_native_recordings_use_the_generic_utf8_json_container(self) -> None:
        native_recordings = 0
        for name, block in self.blocks.items():
            if "InstanceOf: SensorKitRecordingDocument" not in block:
                continue
            if "$recordingFormat#native-recording " not in block:
                continue
            native_recordings += 1
            with self.subTest(instance=name):
                self.assertIsInstance(native_json(block), (dict, list))
        self.assertEqual(native_recordings, 4)

    def test_device_usage_summary_matches_its_native_example(self) -> None:
        document = self.blocks["SensorKitDeviceUsageDocumentExample"]
        observation = self.blocks["SensorKitDeviceUsageExample"]
        payload = native_json(document)
        self.assertIsInstance(payload, dict)
        assert isinstance(payload, dict)
        required_fields = self.catalog_rows["device-usage"]["raw"]["requiredForFields"]
        self.assertTrue(set(required_fields) <= set(payload))
        self.assertEqual(
            component_counts(observation),
            {
                "screenWakes": payload["totalScreenWakes"],
                "unlocks": payload["totalUnlocks"],
            },
        )
        self.assertEqual(
            float(required_match(
                observation,
                r'^\* valueQuantity = ([0-9.]+) \'s\'(?: "seconds")?$',
            )),
            payload["totalUnlockDuration"],
        )
        start, end = coverage(observation)
        self.assertEqual(payload["timestamp"], start)
        self.assertEqual(payload["timestamp"] + payload["duration"], end)

    def test_ecg_native_examples_project_exact_waveform_values_and_context(self) -> None:
        pairs = (
            (
                "SensorKitECGDocumentExample",
                "SensorKitECGExample",
                "leftArmMinusRightArm",
                "guided",
            ),
            (
                "SensorKitInverseECGDocumentExample",
                "SensorKitInverseECGExample",
                "rightArmMinusLeftArm",
                "unguided",
            ),
        )
        for document_name, observation_name, lead, guidance in pairs:
            with self.subTest(document=document_name):
                payload = native_json(self.blocks[document_name])
                self.assertIsInstance(payload, list)
                assert isinstance(payload, list)
                self.assertEqual(len(payload), 2)
                batches = [batch for batch in payload if isinstance(batch, dict)]
                self.assertEqual(len(batches), len(payload))
                self.assertEqual({batch["frequency"] for batch in batches}, {250})
                self.assertEqual({batch["lead"] for batch in batches}, {lead})
                sessions = [batch["session"] for batch in batches]
                self.assertTrue(
                    all(isinstance(session, dict) for session in sessions)
                )
                self.assertEqual(
                    {session["identifier"] for session in sessions},
                    {sessions[0]["identifier"]},
                )
                self.assertEqual(
                    {session["state"] for session in sessions}, {"begin", "end"}
                )
                self.assertEqual(
                    {session["guidance"] for session in sessions}, {guidance}
                )

                samples = [
                    sample
                    for batch in batches
                    for sample in batch["data"]
                ]
                self.assertTrue(all(isinstance(sample, dict) for sample in samples))
                observation = self.blocks[observation_name]
                projected = [sample["valueMicrovolts"] / 1000 for sample in samples]
                actual = [
                    float(value)
                    for value in required_match(
                        observation,
                        r'^\* component\[0\]\.valueSampledData\.data = "([^"]+)"$',
                    ).split()
                ]
                self.assertEqual(actual, projected)
                self.assertEqual(
                    float(required_match(
                        observation,
                        r"^\* component\[0\]\.valueSampledData\.period = ([0-9.]+)$",
                    )),
                    1000 / batches[0]["frequency"],
                )
                self.assertEqual(
                    required_match(observation, r"^\* method = \$sensorKitValue#(\S+) "),
                    guidance,
                )
                self.assertEqual(
                    required_match(
                        observation,
                        r"^\* component\.code\.coding\[sensorKitECGLead\] = "
                        r"\$sensorKitECGLead#(\S+) ",
                    ),
                    lead,
                )
                sample_times = [
                    batch["date"] + index / batch["frequency"]
                    for batch in batches
                    for index, _sample in enumerate(batch["data"])
                ]
                start, end = coverage(observation)
                self.assertAlmostEqual(min(sample_times), start, places=6)
                self.assertAlmostEqual(max(sample_times), end, places=6)

    def test_keyboard_summary_matches_its_native_example(self) -> None:
        document = self.blocks["SensorKitKeyboardMetricsDocumentExample"]
        observation = self.blocks["SensorKitKeyboardMetricsExample"]
        payload = native_json(document)
        self.assertIsInstance(payload, list)
        assert isinstance(payload, list)
        self.assertEqual(len(payload), 1)
        report = payload[0]
        self.assertIsInstance(report, dict)
        assert isinstance(report, dict)
        self.assertIn("durationMetrics", report)
        summary_counts = component_counts(observation)
        count_mapping = {
            "totalWords": "totalWords",
            "totalAlteredWords": "totalAlteredWords",
            "totalTaps": "totalTaps",
            "totalDeletes": "totalDeletes",
            "totalEmojis": "totalEmojis",
            "totalAutocorrections": "totalAutoCorrections",
            "totalPauses": "totalPauses",
            "totalTypingEpisodes": "totalTypingEpisodes",
        }
        self.assertEqual(
            summary_counts,
            {
                summary_name: report["counts"][native_name]
                for summary_name, native_name in count_mapping.items()
            },
        )
        self.assertEqual(
            float(required_match(observation, r"^\* valueQuantity = ([0-9.]+) 's'$")),
            report["totalTypingDuration"],
        )
        self.assertEqual(
            float(required_match(
                observation,
                r"^\* component\[typingSpeed\]\.valueQuantity = ([0-9.]+) '/s'$",
            )),
            report["typingSpeed"] / 60,
        )
        start, end = coverage(observation)
        self.assertEqual(report["timestamp"], start)
        self.assertEqual(report["timestamp"] + report["duration"], end)

    def test_csv_integer_decimal_and_empty_field_lexemes_are_canonical(self) -> None:
        format_code = "triaxial-acceleration-samples"
        valid = ["1787209200", "0", "1.0", "-0.5", "0.0", "iPhone16,2"]
        self.assertEqual(len(read_csv_rows(csv_bytes(format_code, valid), format_code)), 1)

        invalid_integer_lexemes = ["-0", "00", "01", "-01", "+1", "1.0", "1e1"]
        for lexeme in invalid_integer_lexemes:
            row = valid.copy()
            row[1] = lexeme
            with self.subTest(integer=lexeme), self.assertRaisesRegex(
                ValueError, "invalid integer"
            ):
                read_csv_rows(csv_bytes(format_code, row), format_code)

        invalid_number_lexemes = [
            "-0",
            "-0.0",
            "00",
            "01",
            "+1",
            "1.00",
            "1.20",
            "1e1",
        ]
        for lexeme in invalid_number_lexemes:
            row = valid.copy()
            row[2] = lexeme
            with self.subTest(number=lexeme), self.assertRaisesRegex(
                ValueError, "invalid number"
            ):
                read_csv_rows(csv_bytes(format_code, row), format_code)

        non_nullable_empty = valid.copy()
        non_nullable_empty[2] = ""
        with self.assertRaisesRegex(ValueError, "empty non-nullable x"):
            read_csv_rows(csv_bytes(format_code, non_nullable_empty), format_code)

        nullable_empty = ["1787209200", "36.5", "0.1", ""]
        wrist_rows = read_csv_rows(
            csv_bytes("wrist-temperature-samples", nullable_empty),
            "wrist-temperature-samples",
        )
        self.assertEqual(wrist_rows[0]["condition"], "")

    def test_ppg_signed_and_unsigned_varints_are_distinct(self) -> None:
        all_bits_set = b"\xff" * 9 + b"\x01"

        signed = PPGReader(all_bits_set)
        self.assertEqual(signed.signed_varint(), -1)
        signed.finish()

        unsigned = PPGReader(all_bits_set)
        self.assertEqual(unsigned.varint(), (1 << 64) - 1)
        unsigned.finish()

        photodiodes = PPGReader(b"\x02\x01" + all_bits_set)
        self.assertEqual(photodiodes.unsigned_set(), [1, (1 << 64) - 1])
        photodiodes.finish()

        with self.assertRaisesRegex(ValueError, "unique and ascending"):
            PPGReader(b"\x02\x01\x01").unsigned_set()

        negative_two = b"\xfe" + b"\xff" * 8 + b"\x01"
        unsigned_int64_high_bit = b"\x80" * 9 + b"\x01"
        full_record = b"".join((
            b"\x01",  # record count
            struct.pack(">d", 1_787_209_200.0),
            b"\x07",  # record offset from the session start anchor
            b"\x00",  # temperature absent
            b"\x00",  # usage count
            b"\x01",  # optical sample count
            all_bits_set,  # emitter = -1
            b"\x01" + unsigned_int64_high_bit,  # one photodiode = 2^63
            negative_two,  # signal identifier = -2
            struct.pack(">d", 520.0),
            struct.pack(">d", 525.0),
            struct.pack(">d", 64.0),
            b"\x02",  # optical sample offset from the same session start anchor
            b"\x00",  # condition count
            b"\x00",  # noise terms absent
            b"\x00",  # normalized reflectance absent
            b"\x01",  # accelerometer sample count
            b"\x03",  # accelerometer sample offset from the same anchor
            struct.pack(">dddd", 32.0, 1.0, 2.0, 3.0),
        ))
        counts, instants, optical_channels = read_ppg_counts(full_record)
        self.assertEqual(
            counts,
            {
                "recordCount": 1,
                "opticalSampleCount": 1,
                "accelerometerSampleCount": 1,
            },
        )
        self.assertEqual(optical_channels, [(-1, [1 << 63], -2)])
        self.assertEqual(
            instants,
            [
                Decimal("1787209200.0"),
                Decimal("1787209200.000000007"),
                Decimal("1787209200.000000002"),
                Decimal("1787209200.000000003"),
            ],
        )

    def test_accelerometer_counts_and_coverage_come_from_the_registered_csv(self) -> None:
        document = self.blocks["SensorKitAccelerometerDocumentExample"]
        observation = self.blocks["SensorKitAccelerometerExample"]
        rows = read_csv_rows(
            attachment_bytes(document), "triaxial-acceleration-samples"
        )
        self.assertEqual(
            component_counts(observation),
            {
                "sampleCount": len(rows),
                "batchCount": len({
                    (row["device"], row["identifier"])
                    for row in rows
                }),
            },
        )
        start, end = coverage(observation)
        self.assertTrue(all(start <= float(row["timestamp"]) <= end for row in rows))

    def test_ppg_counts_and_coverage_come_from_the_registered_binary(self) -> None:
        specification = REGISTRY["formats"]["photoplethysmogram-samples"]["specification"]
        self.assertEqual(
            [field["field"] for field in specification["record"]],
            [
                "startDate",
                "nanosecondsSinceStart",
                "temperature",
                "usage",
                "opticalSamples",
                "accelerometerSamples",
            ],
        )
        document = self.blocks["SensorKitPPGDocumentExample"]
        observation = self.blocks["SensorKitPPGExample"]
        counts, payload_instants, optical_channels = read_ppg_counts(
            attachment_bytes(document)
        )
        self.assertEqual(component_counts(observation), counts)
        self.assertEqual(optical_channels, [(3, [1, 2], 4)])
        start, end = coverage(observation)
        self.assertTrue(
            all(
                Decimal(str(start)) <= value <= Decimal(str(end))
                for value in payload_instants
            )
        )

    def test_wrist_temperature_count_and_coverage_come_from_the_registered_csv(self) -> None:
        document = self.blocks["SensorKitWristTemperatureDocumentExample"]
        observation = self.blocks["SensorKitWristTemperatureExample"]
        rows = read_csv_rows(
            attachment_bytes(document), "wrist-temperature-samples"
        )
        self.assertEqual(component_counts(observation)["sampleCount"], len(rows))
        start, end = coverage(observation)
        self.assertTrue(all(start <= float(row["timestamp"]) <= end for row in rows))


if __name__ == "__main__":
    unittest.main()
