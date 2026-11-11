"""Reference algorithms for the Grove exchange and identity protocol."""

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
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

try:
    from Scripts.canonical_json import canonical_bytes
except ModuleNotFoundError:  # Direct execution places Scripts itself on sys.path.
    from canonical_json import canonical_bytes  # type: ignore[no-redef]


IDENTITY_DOMAIN = "org.grovealliance.fhir.identity.v0"
RECORD_CONTENT_DOMAIN = "org.grovealliance.fhir.record-content.v0"
FULL_URL_NAMESPACE = uuid.UUID("43df4575-bff7-5a57-9a80-2472cd2b0623")

TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")
POSITIVE_DECIMAL = re.compile(r"^[1-9][0-9]*$")
UNSIGNED_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)$")
UNSIGNED_DECIMAL_COMPONENTS = frozenset({"part-index"})
# A base64url SHA-256 digest without padding, 43 characters.
DIGEST = re.compile(r"^[A-Za-z0-9_-]{43}$")
DIGEST_COMPONENTS = frozenset({"content-digest", "record-content-digest"})
ABSOLUTE_URI = re.compile(
    r"^[A-Za-z][A-Za-z0-9+.-]*:"
    r"(?:[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=-]|%[0-9A-Fa-f]{2})+$"
)
HMAC_IDENTITY = re.compile(
    r"^v0:(?P<key_id>[A-Za-z0-9._-]+):(?P<epoch>[1-9][0-9]*):"
    r"(?P<digest>[A-Za-z0-9_-]{43})$"
)

IDENTIFIER_ROLE_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
RECORD_VERSION_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-record-version"
)
CONTEXT_SNAPSHOT_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-context-snapshot"
)

# The node roles of the two content-snapshot kinds; context-snapshot's are the catalog's
# entryIdentity.contextSnapshotRoles.
DEVICE_SNAPSHOT_NODE_ROLES = ("application", "host", "recording-device")
CONTEXT_SNAPSHOT_NODE_ROLES = (
    "patient",
    "research-study",
    "research-subject",
    "plan-definition",
    "questionnaire-response",
)
SNAPSHOT_NODE_ROLES = {
    "device-snapshot": frozenset(DEVICE_SNAPSHOT_NODE_ROLES),
    "context-snapshot": frozenset(CONTEXT_SNAPSHOT_NODE_ROLES),
}
# The typed Resource.identifier that carries a shared node's content-snapshot key. A
# QuestionnaireResponse carries its key in grove-context-snapshot instead, because its one R4
# identifier holds the submission's business identifier.
SNAPSHOT_IDENTIFIER_ROLE_BY_RESOURCE_TYPE = {
    "Device": "device-snapshot",
    "Patient": "context-snapshot",
    "ResearchStudy": "context-snapshot",
    "ResearchSubject": "context-snapshot",
    "PlanDefinition": "context-snapshot",
}

IDENTITY_KIND_COMPONENT_NAMES = {
    "source-record": (
        "adapter-id",
        "source-type",
        "repository-scope-system",
        "repository-scope-value",
        "native-record-id",
    ),
    "source-output": (
        "adapter-id",
        "source-type",
        "repository-scope-system",
        "repository-scope-value",
        "native-record-id",
        "output-role",
        "output-discriminator",
    ),
    "writer-record": (
        "writer-application-system",
        "writer-application-value",
        "writer-record-id",
    ),
    "provider-record": (
        "provider-code",
        "source-type",
        "provider-scope-system",
        "provider-scope-value",
        "native-record-id",
    ),
    "provider-output": (
        "provider-code",
        "source-type",
        "provider-scope-system",
        "provider-scope-value",
        "native-record-id",
        "output-role",
        "output-discriminator",
    ),
    "source-artifact": (
        "adapter-id",
        "source-type",
        "repository-scope-system",
        "repository-scope-value",
        "native-record-id",
        "format-code",
        "part-index",
    ),
    "provider-artifact": (
        "provider-code",
        "source-type",
        "provider-scope-system",
        "provider-scope-value",
        "native-record-id",
        "format-code",
        "part-index",
    ),
    "source-context": (
        "adapter-id",
        "context-type",
        "repository-scope-system",
        "repository-scope-value",
        "native-context-id",
    ),
    "recording-device": (
        "adapter-id",
        "subject-system",
        "subject-value",
        "stable-unit-token",
    ),
    "device-snapshot": (
        "subject-system",
        "subject-value",
        "node-role",
        "content-digest",
    ),
    "context-snapshot": (
        "subject-system",
        "subject-value",
        "node-role",
        "content-digest",
    ),
    "record-version": (
        "source-record-system",
        "source-record-value",
        "record-content-digest",
    ),
    "record-retraction": (
        "source-record-system",
        "source-record-value",
    ),
}
IDENTITY_KIND_COMPONENTS = {
    kind: len(names) for kind, names in IDENTITY_KIND_COMPONENT_NAMES.items()
}

# The provider namespace is closed by the Grove FHIR contracts. Provider-scoped inputs deliberately use
# provider-* identity kinds so the same tuple can never alias an adapter-scoped identity.
PROVIDER_CODES = frozenset({"google-health-api", "oura", "withings"})


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


def frame_bytes(values: Iterable[bytes]) -> bytes:
    """Encode byte strings as unsigned 32-bit big-endian length-prefixed fields."""
    output = bytearray()
    for value in values:
        if not isinstance(value, bytes):
            raise ExchangeProtocolError("framed values must be bytes")
        if len(value) > 0xFFFFFFFF:
            raise ExchangeProtocolError("a framed value exceeds 2^32-1 bytes")
        output.extend(struct.pack(">I", len(value)))
        output.extend(value)
    return bytes(output)


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
    component_names = IDENTITY_KIND_COMPONENT_NAMES.get(identity_kind)
    if component_names is None:
        raise ExchangeProtocolError("identity_kind is not admitted by the Grove FHIR contracts")
    if len(components) != len(component_names):
        raise ExchangeProtocolError(
            f"{identity_kind} requires exactly {len(component_names)} components"
        )
    for component_name, component in zip(component_names, components, strict=True):
        if not isinstance(component, str):
            raise ExchangeProtocolError(
                f"{identity_kind}.{component_name} must be a string"
            )
        if component == "":
            raise ExchangeProtocolError(
                f"{identity_kind}.{component_name} must not be empty"
            )
        try:
            _utf8(component)
        except ExchangeProtocolError as error:
            raise ExchangeProtocolError(
                f"{identity_kind}.{component_name} must contain Unicode scalar values"
            ) from error
        if component_name in UNSIGNED_DECIMAL_COMPONENTS and UNSIGNED_DECIMAL.fullmatch(component) is None:
            raise ExchangeProtocolError(
                f"{identity_kind}.{component_name} must be a canonical unsigned decimal"
            )
        if component_name in DIGEST_COMPONENTS and DIGEST.fullmatch(component) is None:
            raise ExchangeProtocolError(
                f"{identity_kind}.{component_name} must be a 43-character base64url "
                "SHA-256 digest without padding"
            )
        if component_name == "node-role" and component not in SNAPSHOT_NODE_ROLES[identity_kind]:
            raise ExchangeProtocolError(
                f"{identity_kind}.node-role must be one of "
                f"{', '.join(sorted(SNAPSHOT_NODE_ROLES[identity_kind]))}"
            )
    provider_scoped_kinds = {
        "provider-record",
        "provider-output",
        "provider-artifact",
    }
    generic_source_kinds = {
        "source-record",
        "source-output",
        "source-artifact",
    }
    first_component = components[0]
    if identity_kind in provider_scoped_kinds and first_component not in PROVIDER_CODES:
        raise ExchangeProtocolError(
            f"{identity_kind}.provider-code is not admitted by the Grove FHIR contracts"
        )
    if identity_kind in generic_source_kinds and first_component in PROVIDER_CODES:
        expected_kind = {
            "source-record": "provider-record",
            "source-output": "provider-output",
            "source-artifact": "provider-artifact",
        }[identity_kind]
        raise ExchangeProtocolError(
            f"provider components require identity kind {expected_kind}"
        )
    preimage = frame_fields([IDENTITY_DOMAIN, identity_kind, *components])
    digest = hmac.new(key, preimage, hashlib.sha256).digest()
    return f"v0:{key_id}:{epoch_text}:{base64url_no_padding(digest)}"


def parse_hmac_identity(value: str) -> tuple[str, str, str]:
    if not isinstance(value, str):
        raise ExchangeProtocolError("identity must be a string")
    match = HMAC_IDENTITY.fullmatch(value)
    if match is None:
        raise ExchangeProtocolError("identity is not a canonical Grove v0 HMAC value")
    return match.group("key_id"), match.group("epoch"), match.group("digest")


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


def _sha256_digest(data: bytes) -> str:
    return base64url_no_padding(hashlib.sha256(data).digest())


def _resource(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ExchangeProtocolError(f"{label} must be a JSON object")
    return value


def _without_id(resource: Mapping[str, Any]) -> dict[str, Any]:
    return {name: value for name, value in resource.items() if name != "id"}


def _without_extension(resource: dict[str, Any], url: str) -> dict[str, Any]:
    """Drop every element of `extension` whose url is `url`, then `extension` if it is left empty."""
    if "extension" not in resource:
        return resource
    extensions = resource["extension"]
    if not isinstance(extensions, list):
        raise ExchangeProtocolError("extension must be a JSON array")
    kept = [
        extension
        for extension in extensions
        if not (isinstance(extension, Mapping) and extension.get("url") == url)
    ]
    if kept:
        resource["extension"] = kept
    else:
        del resource["extension"]
    return resource


def _has_identifier_role(identifier: Any, role: str) -> bool:
    if not isinstance(identifier, Mapping):
        return False
    identifier_type = identifier.get("type")
    if not isinstance(identifier_type, Mapping):
        return False
    codings = identifier_type.get("coding")
    if not isinstance(codings, list):
        return False
    return any(
        isinstance(coding, Mapping)
        and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
        and coding.get("code") == role
        for coding in codings
    )


def content_digest(resource: Mapping[str, Any]) -> str:
    """Return the content-digest component of a shared node's content-snapshot key.

    The digest is base64url-nopad SHA-256 over the grove-canonical-json-v0 bytes of the resource,
    minus `id` and minus its own snapshot Identifier (`identifier` dropped if it becomes empty). A
    QuestionnaireResponse is taken minus `id` and minus every grove-context-snapshot extension
    (`extension` dropped if it becomes empty). The resource must be a lossless tree
    (canonical_json.loads_lossless), so every number keeps its lexeme.
    """
    resource = _resource(resource, "a shared node")
    resource_type = resource.get("resourceType")
    content = _without_id(resource)
    if resource_type == "QuestionnaireResponse":
        content = _without_extension(content, CONTEXT_SNAPSHOT_EXTENSION)
    else:
        role = SNAPSHOT_IDENTIFIER_ROLE_BY_RESOURCE_TYPE.get(resource_type)
        if role is None:
            raise ExchangeProtocolError(
                f"resourceType {resource_type!r} carries no content-snapshot key"
            )
        if "identifier" in content:
            identifiers = content["identifier"]
            if not isinstance(identifiers, list):
                raise ExchangeProtocolError("identifier must be a JSON array")
            kept = [
                identifier
                for identifier in identifiers
                if not _has_identifier_role(identifier, role)
            ]
            if kept:
                content["identifier"] = kept
            else:
                del content["identifier"]
    return _sha256_digest(canonical_bytes(content))


def record_outputs(
    bundle: Mapping[str, Any], provenance: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    """Resolve each Provenance.target, in order, to the Bundle resource whose fullUrl it names."""
    bundle = _resource(bundle, "the Bundle")
    provenance = _resource(provenance, "the Provenance")
    entries = bundle.get("entry", [])
    if not isinstance(entries, list):
        raise ExchangeProtocolError("Bundle.entry must be a JSON array")
    resources: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(entries):
        entry = _resource(entry, f"Bundle.entry[{index}]")
        full_url = entry.get("fullUrl")
        if not isinstance(full_url, str):
            raise ExchangeProtocolError(f"Bundle.entry[{index}].fullUrl must be a string")
        if full_url in resources:
            raise ExchangeProtocolError(f"Bundle.entry[{index}].fullUrl repeats {full_url}")
        resources[full_url] = _resource(entry.get("resource"), f"Bundle.entry[{index}].resource")
    targets = provenance.get("target")
    if not isinstance(targets, list):
        raise ExchangeProtocolError("Provenance.target must be a JSON array")
    outputs = []
    for index, target in enumerate(targets):
        reference = target.get("reference") if isinstance(target, Mapping) else None
        if not isinstance(reference, str) or reference not in resources:
            raise ExchangeProtocolError(
                f"Provenance.target[{index}] resolves to no entry of the Bundle"
            )
        outputs.append(resources[reference])
    return outputs


def record_content_digest(
    provenance: Mapping[str, Any], outputs: Sequence[Mapping[str, Any]]
) -> str:
    """Return the record-content-digest component of a record-version key.

    base64url-nopad SHA-256 over the u32-framed fields [RECORD_CONTENT_DOMAIN, canonical(P'),
    canonical(O1), ..., canonical(On)]. P' is the conversion Provenance minus `id` and minus every
    grove-record-version extension (`extension` dropped if it is left empty); Oi is the resource the
    i-th Provenance.target resolves to (record_outputs), minus `id`. Nothing else is removed. Every
    resource must be a lossless tree (canonical_json.loads_lossless).
    """
    provenance = _resource(provenance, "the conversion Provenance")
    if provenance.get("resourceType") != "Provenance":
        raise ExchangeProtocolError("the record content starts with a Provenance")
    targets = provenance.get("target")
    if not isinstance(targets, list) or not targets:
        raise ExchangeProtocolError("a conversion Provenance targets at least one output")
    if isinstance(outputs, (str, bytes, Mapping)) or not isinstance(outputs, Sequence):
        raise ExchangeProtocolError("outputs must be a sequence of resources in target order")
    if len(outputs) != len(targets):
        raise ExchangeProtocolError(
            "outputs must hold exactly one resource per Provenance.target, in target order"
        )
    fields = [
        RECORD_CONTENT_DOMAIN.encode("utf-8"),
        canonical_bytes(_without_extension(_without_id(provenance), RECORD_VERSION_EXTENSION)),
    ]
    fields.extend(
        canonical_bytes(_without_id(_resource(output, f"output {index}")))
        for index, output in enumerate(outputs)
    )
    return _sha256_digest(frame_bytes(fields))


def device_snapshot_identity(
    *,
    key: bytes,
    key_id: str,
    epoch: str | int,
    subject_system: str,
    subject_value: str,
    node_role: str,
    content_digest: str,
) -> str:
    """Derive an application, host or recording Device's content-snapshot key value."""
    return derive_hmac_identity(
        key=key,
        key_id=key_id,
        epoch=epoch,
        identity_kind="device-snapshot",
        components=[subject_system, subject_value, node_role, content_digest],
    )


def context_snapshot_identity(
    *,
    key: bytes,
    key_id: str,
    epoch: str | int,
    subject_system: str,
    subject_value: str,
    node_role: str,
    content_digest: str,
) -> str:
    """Derive a Patient, study node or QuestionnaireResponse content-snapshot key value."""
    return derive_hmac_identity(
        key=key,
        key_id=key_id,
        epoch=epoch,
        identity_kind="context-snapshot",
        components=[subject_system, subject_value, node_role, content_digest],
    )


def record_version_identity(
    *,
    key: bytes,
    key_id: str,
    epoch: str | int,
    source_record_system: str,
    source_record_value: str,
    record_content_digest: str,
) -> str:
    """Derive the record-version key of one source-record revision's conversion Provenance."""
    return derive_hmac_identity(
        key=key,
        key_id=key_id,
        epoch=epoch,
        identity_kind="record-version",
        components=[source_record_system, source_record_value, record_content_digest],
    )


def record_retraction_identity(
    *,
    key: bytes,
    key_id: str,
    epoch: str | int,
    source_record_system: str,
    source_record_value: str,
) -> str:
    """Derive the one retraction key of a source record; every retraction of it repeats the key."""
    return derive_hmac_identity(
        key=key,
        key_id=key_id,
        epoch=epoch,
        identity_kind="record-retraction",
        components=[source_record_system, source_record_value],
    )
