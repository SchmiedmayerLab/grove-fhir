"""Exact temporal, SampledData, and Attachment payload validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import binascii
import hashlib
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any

from .context import FHIR_INSTANT, SAMPLED_DECIMAL
from .diagnostics import ProducerValidationError


def parse_fhir_instant(value: Any, label: str) -> Decimal:
    """Return exact epoch milliseconds without truncating fractional seconds."""
    if not isinstance(value, str):
        raise ProducerValidationError(f"{label} must be an offset-bearing dateTime")
    match = FHIR_INSTANT.fullmatch(value)
    if match is None:
        raise ProducerValidationError(f"{label} is not an exact offset-bearing dateTime")
    offset = "+00:00" if match.group("offset") == "Z" else match.group("offset")
    try:
        parsed = datetime.fromisoformat(
            f"{match.group('date')}T{match.group('time')}{offset}"
        )
    except ValueError as error:
        raise ProducerValidationError(f"{label} is not a valid dateTime") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProducerValidationError(f"{label} must carry a UTC offset")
    utc = parsed.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    whole = utc - epoch
    seconds = Decimal(whole.days) * Decimal(86_400) + Decimal(whole.seconds)
    fraction_text = match.group("fraction")
    fraction = (
        Decimal(int(fraction_text)) / (Decimal(10) ** len(fraction_text))
        if fraction_text is not None
        else Decimal(0)
    )
    return (seconds + fraction) * Decimal(1000)

def round_mobile_epoch_milliseconds(value: Decimal) -> Decimal:
    """Round an exact epoch-millisecond value to a millisecond, ties to even."""
    return value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN)

def validate_sampled_data(
    sampled: Any,
    effective: Any,
    label: str,
) -> None:
    """Enforce the exact registered uniform-frame and interval semantics."""
    if not isinstance(sampled, dict):
        raise ProducerValidationError(f"{label} must be SampledData")
    for forbidden in ("factor", "lowerLimit", "upperLimit"):
        if forbidden in sampled:
            raise ProducerValidationError(f"{label}.{forbidden} is not admitted")
    period_value = sampled.get("period")
    if isinstance(period_value, bool) or not isinstance(
        period_value, (int, float, Decimal)
    ):
        raise ProducerValidationError(f"{label}.period must be a positive number")
    try:
        period = Decimal(str(period_value))
    except InvalidOperation as error:
        raise ProducerValidationError(f"{label}.period must be a positive number") from error
    if not period.is_finite() or period <= 0:
        raise ProducerValidationError(f"{label}.period must be greater than zero")
    dimensions = sampled.get("dimensions")
    if isinstance(dimensions, bool) or not isinstance(dimensions, int) or dimensions <= 0:
        raise ProducerValidationError(f"{label}.dimensions must be a positive integer")
    data = sampled.get("data")
    if not isinstance(data, str) or not data or data != data.strip():
        raise ProducerValidationError(f"{label}.data must be a non-empty decimal sequence")
    tokens = re.split(r"\s+", data)
    if any(SAMPLED_DECIMAL.fullmatch(token) is None for token in tokens):
        raise ProducerValidationError(
            f"{label}.data admits only complete decimal values; E, U, L, and missing tokens fail closed"
        )
    if len(tokens) % dimensions != 0:
        raise ProducerValidationError(
            f"{label}.data token count must be divisible by dimensions"
        )
    frame_count = len(tokens) // dimensions
    if frame_count < 2:
        raise ProducerValidationError(
            f"{label} must contain at least two complete sampled-data frames"
        )
    if not isinstance(effective, dict):
        raise ProducerValidationError(f"{label} requires an effectivePeriod")
    start = parse_fhir_instant(effective.get("start"), f"{label} effectivePeriod.start")
    end = parse_fhir_instant(effective.get("end"), f"{label} effectivePeriod.end")
    actual_milliseconds = end - start
    expected_milliseconds = Decimal(frame_count - 1) * period
    if actual_milliseconds != expected_milliseconds:
        raise ProducerValidationError(
            f"{label} effectivePeriod.end must equal first frame plus "
            "(frameCount - 1) * period milliseconds"
        )

def validate_recording_attachment(attachment: Any, label: str) -> None:
    """Require verifiable exact bytes for every admitted native recording."""
    if not isinstance(attachment, dict):
        raise ProducerValidationError(f"{label} must be an Attachment")
    has_data = isinstance(attachment.get("data"), str)
    has_url = isinstance(attachment.get("url"), str) and bool(attachment.get("url"))
    if has_data == has_url:
        raise ProducerValidationError(f"{label} must contain exactly one of data or url")
    size = attachment.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ProducerValidationError(f"{label}.size is required and must be a byte count")
    encoded_hash = attachment.get("hash")
    if not isinstance(encoded_hash, str):
        raise ProducerValidationError(f"{label}.hash is required")
    try:
        digest = base64.b64decode(encoded_hash, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ProducerValidationError(f"{label}.hash must be base64 SHA-1") from error
    if len(digest) != 20:
        raise ProducerValidationError(f"{label}.hash must encode exactly one SHA-1 digest")
    if has_data:
        try:
            payload = base64.b64decode(attachment["data"], validate=True)
        except (binascii.Error, ValueError) as error:
            raise ProducerValidationError(f"{label}.data must be valid base64") from error
        if len(payload) != size:
            raise ProducerValidationError(f"{label}.size does not match embedded bytes")
        if hashlib.sha1(payload).digest() != digest:  # noqa: S324 -- mandated by FHIR R4 Attachment.hash
            raise ProducerValidationError(f"{label}.hash does not match embedded bytes")
