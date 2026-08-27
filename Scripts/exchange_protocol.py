"""Reference algorithms for the Grove 0.6 exchange and identity protocol."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import struct
import uuid
from collections.abc import Iterable, Sequence


IDENTITY_DOMAIN = "org.grovealliance.fhir.identity.v2"
ENTRY_NODE_DOMAIN = "org.grovealliance.fhir.entry-node.v2"
FULL_URL_NAMESPACE = uuid.UUID("43df4575-bff7-5a57-9a80-2472cd2b0623")

TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")
POSITIVE_DECIMAL = re.compile(r"^[1-9][0-9]*$")
ABSOLUTE_URI = re.compile(
    r"^[A-Za-z][A-Za-z0-9+.-]*:"
    r"(?:[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=-]|%[0-9A-Fa-f]{2})+$"
)
HMAC_IDENTITY = re.compile(
    r"^v2:(?P<key_id>[A-Za-z0-9._-]+):(?P<epoch>[1-9][0-9]*):"
    r"(?P<digest>[A-Za-z0-9_-]{43})$"
)
EVENT_IDENTITY = re.compile(
    r"^e2:(?P<producer>[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}):(?P<sequence>[1-9][0-9]*)$"
)
ENTRY_NODE_IDENTITY = re.compile(
    r"^n2:(?P<role>[a-z][a-z0-9-]*):(?P<ordinal>0|[1-9][0-9]*):"
    r"(?P<digest>[A-Za-z0-9_-]{43})$"
)

IDENTITY_KIND_COMPONENTS = {
    "source-record": 5,
    "source-output": 7,
    "writer-record": 3,
    "provider-record": 5,
    "source-artifact": 7,
    "source-context": 5,
    "recording-device": 4,
    "device-snapshot": 4,
}


class ExchangeProtocolError(ValueError):
    """Raised when an exchange-protocol value is not canonical."""


def _utf8(value: str) -> bytes:
    if not isinstance(value, str):
        raise ExchangeProtocolError("framed values must be strings")
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ExchangeProtocolError("framed values must contain Unicode scalar values")
    try:
        return value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as error:
        raise ExchangeProtocolError(
            "framed values must contain Unicode scalar values"
        ) from error


def frame_fields(values: Iterable[str]) -> bytes:
    """Encode strings as unsigned 32-bit big-endian length-prefixed UTF-8 fields."""
    output = bytearray()
    for value in values:
        encoded = _utf8(value)
        if len(encoded) > 0xFFFFFFFF:
            raise ExchangeProtocolError("a framed value exceeds 2^32-1 UTF-8 bytes")
        output.extend(struct.pack(">I", len(encoded)))
        output.extend(encoded)
    return bytes(output)


def base64url_no_padding(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def require_absolute_uri(value: str, label: str) -> None:
    """Reject IRIs, whitespace, malformed escapes, and relative URI references."""
    if not isinstance(value, str) or ABSOLUTE_URI.fullmatch(value) is None:
        raise ExchangeProtocolError(f"{label} must be an absolute RFC 3986 URI")


def derive_hmac_identity(
    *,
    key: bytes,
    key_id: str,
    epoch: str | int,
    identity_kind: str,
    components: Sequence[str],
) -> str:
    """Derive one deployment-scoped opaque business identifier value."""
    if not isinstance(key, bytes) or len(key) < 32:
        raise ExchangeProtocolError("the HMAC key must contain at least 32 bytes")
    if not isinstance(key_id, str) or TOKEN.fullmatch(key_id) is None:
        raise ExchangeProtocolError("key_id must be a nonempty ASCII token")
    epoch_text = str(epoch)
    if POSITIVE_DECIMAL.fullmatch(epoch_text) is None:
        raise ExchangeProtocolError("epoch must be a canonical positive decimal integer")
    if not isinstance(identity_kind, str) or TOKEN.fullmatch(identity_kind) is None:
        raise ExchangeProtocolError("identity_kind must be a nonempty ASCII token")
    if not isinstance(components, Sequence) or isinstance(components, (str, bytes)):
        raise ExchangeProtocolError("components must be a sequence of strings")
    expected_components = IDENTITY_KIND_COMPONENTS.get(identity_kind)
    if expected_components is None:
        raise ExchangeProtocolError("identity_kind is not admitted by Grove 0.6")
    if len(components) != expected_components:
        raise ExchangeProtocolError(
            f"{identity_kind} requires exactly {expected_components} components"
        )
    preimage = frame_fields([IDENTITY_DOMAIN, identity_kind, *components])
    digest = hmac.new(key, preimage, hashlib.sha256).digest()
    return f"v2:{key_id}:{epoch_text}:{base64url_no_padding(digest)}"


def parse_hmac_identity(value: str) -> tuple[str, str, str]:
    if not isinstance(value, str):
        raise ExchangeProtocolError("identity must be a string")
    match = HMAC_IDENTITY.fullmatch(value)
    if match is None:
        raise ExchangeProtocolError("identity is not a canonical Grove v2 HMAC value")
    return match.group("key_id"), match.group("epoch"), match.group("digest")


def event_identity(producer_instance: str, sequence: int | str) -> str:
    """Create the durable identifier for one immutable source-record event."""
    try:
        producer = str(uuid.UUID(producer_instance))
    except (AttributeError, ValueError) as error:
        raise ExchangeProtocolError(
            "producer_instance must be a canonical UUID"
        ) from error
    if producer != producer_instance:
        raise ExchangeProtocolError("producer_instance must be a lowercase canonical UUID")
    sequence_text = str(sequence)
    if POSITIVE_DECIMAL.fullmatch(sequence_text) is None:
        raise ExchangeProtocolError(
            "event sequence must be a canonical positive decimal integer"
        )
    return f"e2:{producer}:{sequence_text}"


def entry_node_identity(
    *,
    event_system: str,
    event_value: str,
    role: str,
    ordinal: int | str,
) -> str:
    """Create an event-scoped node key for a resource without business identity."""
    require_absolute_uri(event_system, "event_system")
    if EVENT_IDENTITY.fullmatch(event_value) is None:
        raise ExchangeProtocolError("event_value must be a canonical Grove v2 event value")
    if not isinstance(role, str) or re.fullmatch(r"[a-z][a-z0-9-]*", role) is None:
        raise ExchangeProtocolError("entry-node role must be a lowercase code token")
    ordinal_text = str(ordinal)
    if re.fullmatch(r"0|[1-9][0-9]*", ordinal_text) is None:
        raise ExchangeProtocolError("entry-node ordinal must be a canonical unsigned integer")
    digest = hashlib.sha256(
        frame_fields(
            [ENTRY_NODE_DOMAIN, event_system, event_value, role, ordinal_text]
        )
    ).digest()
    return f"n2:{role}:{ordinal_text}:{base64url_no_padding(digest)}"


def _uuid_v5_bytes(namespace: uuid.UUID, name: bytes) -> uuid.UUID:
    digest = bytearray(hashlib.sha1(namespace.bytes + name).digest()[:16])
    digest[6] = (digest[6] & 0x0F) | 0x50
    digest[8] = (digest[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(digest))


def entry_full_url(system: str, value: str) -> str:
    """Format a complete entry key as a deterministic lowercase UUID URN."""
    require_absolute_uri(system, "entry identifier system")
    if not value:
        raise ExchangeProtocolError("entry identifier value must not be empty")
    name = frame_fields([system, value])
    return f"urn:uuid:{_uuid_v5_bytes(FULL_URL_NAMESPACE, name)}"
