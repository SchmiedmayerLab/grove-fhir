"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from Scripts.producer_validation import (
    diagnostics,
    payloads,
)
from Tests.producer_validation_test_support import (
    Decimal,
    ProducerValidationTestCase,
    copy,
)

class ProducerPayloadsTests(ProducerValidationTestCase):
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
            "size": 3,
            "hash": "cDeAcZjCKn0rCAc3HXY3eahP388=",
        }
        payloads.validate_recording_attachment(url_only, "Attachment")
        del url_only["hash"]
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "hash is required"):
            payloads.validate_recording_attachment(url_only, "Attachment")
