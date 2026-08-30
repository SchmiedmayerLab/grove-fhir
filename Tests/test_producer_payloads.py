"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import hashlib
import json

from Scripts.producer_validation import (
    context,
    diagnostics,
    payloads,
    profiles,
    sensorkit,
)
from Tests.producer_validation_test_support import (
    Decimal,
    ProducerValidationTestCase,
    copy,
)

class ProducerPayloadsTests(ProducerValidationTestCase):
    @staticmethod
    def inline(payload: bytes) -> dict[str, str]:
        return {"data": base64.b64encode(payload).decode("ascii")}

    @staticmethod
    def recording_attachment(payload: bytes) -> dict[str, str | int]:
        return {
            "data": base64.b64encode(payload).decode("ascii"),
            "size": len(payload),
            "hash": base64.b64encode(hashlib.sha1(payload).digest()).decode("ascii"),
        }

    def test_sampled_data_timing_and_numeric_frames_fail_closed(self) -> None:
        sampled = {
            "origin": {"value": 0, "system": "http://unitsofmeasure.org", "code": "1"},
            "period": 10,
            "dimensions": 3,
            "data": "1 2 3 4 5 6 7 8 9",
        }
        effective = {
            "start": "2026-08-20T10:30:00Z",
            "end": "2026-08-20T10:30:00.020Z",
        }
        payloads.validate_sampled_data(sampled, effective, "SampledData")

        precise = copy.deepcopy(sampled)
        precise.update({
            "period": Decimal("0.000001"),
            "dimensions": 1,
            "data": "1 2",
        })
        payloads.validate_sampled_data(
            precise,
            {
                "start": "2026-08-20T10:30:00.123456789Z",
                "end": "2026-08-20T10:30:00.123456790Z",
            },
            "HighPrecisionSampledData",
        )

        mutations = [
            ({"period": 0}, "greater than zero"),
            ({"dimensions": 0}, "positive integer"),
            ({"data": "1 2 E"}, "decimal values"),
            ({"data": "1 2 3 4"}, "divisible by dimensions"),
            ({"data": "1 2 3"}, "at least two complete"),
        ]
        for replacement, reason in mutations:
            invalid = copy.deepcopy(sampled)
            invalid.update(replacement)
            with self.subTest(replacement=replacement), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, reason
            ):
                payloads.validate_sampled_data(invalid, effective, "SampledData")

        wrong_end = copy.deepcopy(effective)
        wrong_end["end"] = "2026-08-20T10:30:00.030Z"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "effectivePeriod.end"
        ):
            payloads.validate_sampled_data(sampled, wrong_end, "SampledData")

        scaled = copy.deepcopy(sampled)
        scaled["factor"] = 0.5
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "factor"):
            payloads.validate_sampled_data(scaled, effective, "SampledData")

    def test_ecg_channel_identity_is_complete_and_unique(self) -> None:
        def component(code: str, display: str) -> dict:
            return {
                "code": {"coding": [{
                    "system": "https://example.org/fhir/CodeSystem/ecg-channel",
                    "code": code,
                    "display": display,
                }]},
                "valueSampledData": {
                    "origin": {
                        "value": 0,
                        "system": "http://unitsofmeasure.org",
                        "code": "mV",
                    },
                    "period": 10,
                    "dimensions": 1,
                    "data": "0.1 0.2",
                },
            }

        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [context.SENSOR_ECG_PROFILE]},
            "effectivePeriod": {
                "start": "2026-08-20T10:30:00Z",
                "end": "2026-08-20T10:30:00.010Z",
            },
            "component": [component("lead-i", "Lead I"), component("lead-ii", "Lead II")],
        }
        sensorkit.validate_sensor_contract(observation, "ECG")

        display_only = copy.deepcopy(observation)
        display_only["component"][1]["code"]["coding"][0]["code"] = "lead-i"
        display_only["component"][1]["code"]["coding"][0]["display"] = "Different label"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "duplicates another ECG channel identity"
        ):
            sensorkit.validate_sensor_contract(display_only, "ECG")

        incomplete = copy.deepcopy(observation)
        del incomplete["component"][0]["code"]["coding"][0]["system"]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "non-empty system and code"
        ):
            sensorkit.validate_sensor_contract(incomplete, "ECG")

    def test_recording_attachment_requires_exact_size_and_sha1(self) -> None:
        attachment = {
            "data": "AQID",
            "size": 3,
            "hash": "cDeAcZjCKn0rCAc3HXY3eahP388=",
        }
        payloads.validate_recording_attachment(attachment, "Attachment")

        for field in ("size", "hash"):
            invalid = copy.deepcopy(attachment)
            del invalid[field]
            with self.subTest(field=field), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, field
            ):
                payloads.validate_recording_attachment(invalid, "Attachment")

        changed = copy.deepcopy(attachment)
        changed["data"] = "AQIE"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "hash does not match"):
            payloads.validate_recording_attachment(changed, "Attachment")

        url_only = {
            "url": "https://recordings.example.org/version/one.bin",
            # The preflight validates URL metadata shape but does not fetch these bytes.
            "size": 999,
            "hash": "cDeAcZjCKn0rCAc3HXY3eahP388=",
        }
        payloads.validate_recording_attachment(url_only, "Attachment")
        del url_only["hash"]
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "hash is required"):
            payloads.validate_recording_attachment(url_only, "Attachment")

    def test_inline_native_json_validation_is_only_a_container_check(self) -> None:
        entry = {"contentType": "application/json"}
        for value in (b"{}", b"[]"):
            with self.subTest(value=value):
                payloads.validate_inline_recording_payload(
                    self.inline(value), "native-recording", entry, "Attachment"
                )

        invalid = (
            (b"null", "object or array"),
            (b'"scalar"', "object or array"),
            (b"{", "well-formed UTF-8 JSON"),
            (b"\xef\xbb\xbf{}", "byte-order mark"),
            (b"\xff", "well-formed UTF-8 JSON"),
            (b'{"value":1,"value":2}', "strict well-formed UTF-8 JSON"),
            (b'{"value":NaN}', "strict well-formed UTF-8 JSON"),
        )
        for value, message in invalid:
            with self.subTest(value=value), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, message
            ):
                payloads.validate_inline_recording_payload(
                    self.inline(value), "native-recording", entry, "Attachment"
                )

    def test_inline_fhir_collection_validation_enforces_its_real_envelope(self) -> None:
        entry = {"contentType": "application/fhir+json"}
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": "2026-08-20T10:30:00Z",
            "entry": [{
                "fullUrl": "urn:uuid:1b37bce0-b40a-46d9-89cc-79bc54963bf6",
                "resource": {"resourceType": "Observation", "status": "final"},
            }],
        }

        def validate(value: bytes) -> None:
            payloads.validate_inline_recording_payload(
                self.inline(value),
                "fhir-collection-bundle",
                entry,
                "Attachment",
            )

        validate(json.dumps(bundle, separators=(",", ":")).encode())
        mutations = (
            ({"type": "batch"}, "resourceType Bundle and type collection"),
            ({"timestamp": None}, "offset-bearing dateTime"),
            ({"entry": []}, "at least one source resource"),
            ({"entry": [{
                "fullUrl": "relative",
                "resource": {"resourceType": "Observation"},
            }]}, "absolute non-fragment URI"),
            ({"entry": [{
                "fullUrl": "urn:uuid:1b37bce0-b40a-46d9-89cc-79bc54963bf6",
                "resource": {},
            }]}, "resourceType"),
            ({"entry": [{
                "fullUrl": "urn:uuid:1b37bce0-b40a-46d9-89cc-79bc54963bf6",
                "resource": {"resourceType": "Observation"},
                "request": {},
            }]}, "cannot contain request"),
        )
        for replacement, message in mutations:
            invalid = copy.deepcopy(bundle)
            invalid.update(replacement)
            with self.subTest(message=message), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, message
            ):
                validate(json.dumps(invalid, separators=(",", ":")).encode())

        duplicate_url = copy.deepcopy(bundle)
        duplicate_url["entry"].append(copy.deepcopy(duplicate_url["entry"][0]))
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "duplicates another collection entry"
        ):
            validate(json.dumps(duplicate_url, separators=(",", ":")).encode())

        for raw in (
            b'{"resourceType":"Bundle","resourceType":"Bundle","type":"collection",'
            b'"timestamp":"2026-08-20T10:30:00Z","entry":[]}',
            b'{"resourceType":"Bundle","type":"collection","timestamp":NaN,"entry":[]}',
        ):
            with self.subTest(raw=raw), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "strict well-formed UTF-8 JSON"
            ):
                validate(raw)

    def test_inline_fhir_and_provider_json_claim_only_checked_shapes(self) -> None:
        fhir_entry = {"contentType": "application/fhir+json"}
        payloads.validate_inline_recording_payload(
            self.inline(b'{"resourceType":"Observation"}'),
            "fhir-resource",
            fhir_entry,
            "FHIR attachment",
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "resourceType"
        ):
            payloads.validate_inline_recording_payload(
                self.inline(b'{}'),
                "fhir-resource",
                fhir_entry,
                "FHIR attachment",
            )

        provider_entry = {"contentType": "application/json"}
        payloads.validate_inline_recording_payload(
            self.inline(b'[{"provider":true}]'),
            "provider-recording",
            provider_entry,
            "Provider attachment",
        )

    def test_inline_registered_csv_validation_enforces_lexemes_and_nullability(self) -> None:
        registry = json.loads(
            (context.CATALOG_ROOT / "format-registry.json").read_text(encoding="utf-8")
        )
        acceleration = registry["formats"]["triaxial-acceleration-samples"]
        header = "timestamp,identifier,x,y,z,device\n"
        valid = (header + "1787209200,0,1.0,-0.5,0.0,iPhone16\n").encode()
        payloads.validate_inline_recording_payload(
            self.inline(valid),
            "triaxial-acceleration-samples",
            acceleration,
            "Attachment",
        )

        invalid_rows = (
            ("1787209200,-0,1.0,-0.5,0.0,iPhone16\n", "integer"),
            ("1787209200,00,1.0,-0.5,0.0,iPhone16\n", "integer"),
            ("1787209200,01,1.0,-0.5,0.0,iPhone16\n", "integer"),
            ("1787209200,0,-0,-0.5,0.0,iPhone16\n", "number"),
            ("1787209200,0,1.20,-0.5,0.0,iPhone16\n", "number"),
            ("1787209200,0,,-0.5,0.0,iPhone16\n", "non-nullable x"),
            (
                "1787209200,0," + ("9" * 400) + ",-0.5,0.0,iPhone16\n",
                "number",
            ),
        )
        for row, message in invalid_rows:
            with self.subTest(row=row), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, message
            ):
                payloads.validate_inline_recording_payload(
                    self.inline((header + row).encode()),
                    "triaxial-acceleration-samples",
                    acceleration,
                    "Attachment",
                )

        invalid_structures = (
            (b"wrong,header\n", "header"),
            (
                header.encode() + b'1787209200,"0",1.0,-0.5,0.0,iPhone16\n',
                "canonically quoted",
            ),
            (
                header.encode() + b"1787209200,0,1.0,-0.5,0.0,iPhone16\r\n",
                "LF after every row and no CR",
            ),
            (
                header.encode() + b'1787209200,0,1.0,-0.5,0.0,"iPhone\r16"\n',
                "LF after every row and no CR",
            ),
        )
        for value, message in invalid_structures:
            with self.subTest(message=message), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, message
            ):
                payloads.validate_inline_recording_payload(
                    self.inline(value),
                    "triaxial-acceleration-samples",
                    acceleration,
                    "Attachment",
                )

        wrist = registry["formats"]["wrist-temperature-samples"]
        payloads.validate_inline_recording_payload(
            self.inline(
                b"timestamp,value,errorEstimate,condition\n1787209200,36.5,0.1,\n"
            ),
            "wrist-temperature-samples",
            wrist,
            "Attachment",
        )

    def test_recording_format_validation_checks_inline_payload_syntax(self) -> None:
        resource = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-recording-document"
            ]},
            "content": [{
                "attachment": {
                    "contentType": "application/json",
                    **self.recording_attachment(b"null"),
                },
                "format": {
                    "system": (
                        "https://grovealliance.org/fhir/sensor/CodeSystem/"
                        "grove-recording-format"
                    ),
                    "code": "native-recording",
                },
            }],
        }
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "object or array"
        ):
            profiles.validate_recording_format(resource, "DocumentReference")

        release_coupled = copy.deepcopy(resource)
        release_coupled["content"][0]["attachment"] = {
            "contentType": "application/json",
            **self.recording_attachment(b"{}"),
        }
        release_coupled["content"][0]["format"]["version"] = context.RELEASE_VERSION
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "must omit release-coupled Coding.version",
        ):
            profiles.validate_recording_format(release_coupled, "DocumentReference")
