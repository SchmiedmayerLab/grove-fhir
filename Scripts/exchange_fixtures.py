"""Key synthetic record-centric exchange fixtures under the public test key."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

# The fixture generators build Bundles as lossless trees (Scripts/canonical_json.loads_lossless),
# so every number keeps its lexeme, and mint every content-derived key from the final content:
# each shared node's content snapshot, each QuestionnaireResponse's grove-context-snapshot copy,
# each conversion Provenance's record version and its grove-record-version copy, and each
# retraction Provenance's record-retraction key. A key changes its node's fullUrl, which changes
# every node that references it, so keying repeats until no fullUrl moves.

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from Scripts.canonical_json import JSONNumber, loads_lossless
from Scripts.exchange_protocol import (
    CONTEXT_SNAPSHOT_EXTENSION,
    IDENTIFIER_ROLE_SYSTEM,
    RECORD_VERSION_EXTENSION,
    content_digest,
    context_snapshot_identity,
    device_snapshot_identity,
    entry_full_url,
    record_content_digest,
    record_outputs,
    record_retraction_identity,
    record_version_identity,
)


# Public synthetic fixture key (catalog testVectors.keyHex); never a deployment secret.
KEY = bytes(range(32))
KEY_ID = "test-key"
EPOCH = 1
SYSTEM_ROOT = "https://study.example.org/fhir/NamingSystem"
ENTRY_KEY_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key"
)
ACTIVE_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle"
)
SUBJECT = ("https://study.example.org/fhir/identifiers/participant", "participant-001")
DEVICE_NODE_ROLES = {
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-application-device": "application",
    "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-application-device": "application",
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-host-device": "host",
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-recording-device": "recording-device",
}
CONTEXT_NODE_ROLES = {
    "Patient": "patient",
    "ResearchStudy": "research-study",
    "ResearchSubject": "research-subject",
    "PlanDefinition": "plan-definition",
}
MAX_ROUNDS = 16


def system(role: str, key_id: str = KEY_ID, epoch: int = EPOCH) -> str:
    """Return the recommended fixture NamingSystem of one identifier role."""
    return f"{SYSTEM_ROOT}/grove-{role}-v0/{key_id}/{epoch}"


def typed_identifier(role: str, value: str) -> dict[str, Any]:
    return {
        "type": {"coding": [{"system": IDENTIFIER_ROLE_SYSTEM, "code": role}]},
        "system": system(role),
        "value": value,
    }


def read_lossless(path: Path) -> Any:
    return loads_lossless(path.read_bytes())


def lossless(value: Any) -> Any:
    """Convert a json.loads tree to a lossless one; an int keeps its decimal lexeme."""
    if isinstance(value, (JSONNumber, str)) or value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return JSONNumber(str(value))
    if isinstance(value, float):
        return JSONNumber(repr(value))
    if isinstance(value, Mapping):
        return {name: lossless(child) for name, child in value.items()}
    if isinstance(value, list):
        return [lossless(child) for child in value]
    raise TypeError(f"{type(value).__name__} is not a JSON value")


def dumps(value: Any, indent: int = 0) -> str:
    """Format a lossless tree as json.dumps(indent=2, ensure_ascii=False) formats it."""
    if isinstance(value, JSONNumber):
        return str(value)
    if isinstance(value, str) or value is None or isinstance(value, bool):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return json.dumps(value)
    inner = " " * (indent + 2)
    if isinstance(value, Mapping):
        if not value:
            return "{}"
        members = ",\n".join(
            f"{inner}{json.dumps(name, ensure_ascii=False)}: {dumps(child, indent + 2)}"
            for name, child in value.items()
        )
        return "{\n" + members + "\n" + " " * indent + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        items = ",\n".join(f"{inner}{dumps(child, indent + 2)}" for child in value)
        return "[\n" + items + "\n" + " " * indent + "]"
    raise TypeError(f"{type(value).__name__} is not a JSON value")


def encoded(value: Any) -> str:
    return dumps(value) + "\n"


def plain(value: Any) -> Any:
    """Return the json.loads form of a lossless tree, as a reader of the committed file sees it."""
    return json.loads(encoded(value))


def rewrite_references(value: Any, replacements: Mapping[str, str]) -> None:
    if isinstance(value, dict):
        for name, child in value.items():
            if name == "reference" and isinstance(child, str) and child in replacements:
                value[name] = replacements[child]
            else:
                rewrite_references(child, replacements)
    elif isinstance(value, list):
        for child in value:
            rewrite_references(child, replacements)


def role_of(identifier: Any) -> str | None:
    if not isinstance(identifier, Mapping):
        return None
    codings = (identifier.get("type") or {}).get("coding") or []
    for coding in codings:
        if isinstance(coding, Mapping) and coding.get("system") == IDENTIFIER_ROLE_SYSTEM:
            return coding.get("code")
    return None


def typed(resource: Mapping[str, Any], role: str) -> dict[str, Any] | None:
    identifiers = resource.get("identifier")
    if isinstance(identifiers, Mapping):
        identifiers = [identifiers]
    for identifier in identifiers or []:
        if role_of(identifier) == role:
            return identifier
    return None


def _set_extension(resource: dict[str, Any], url: str, identifier: dict[str, Any]) -> None:
    extensions = resource.setdefault("extension", [])
    for extension in extensions:
        if extension.get("url") == url:
            extension["valueIdentifier"] = copy.deepcopy(identifier)
            return
    extensions.append({"url": url, "valueIdentifier": copy.deepcopy(identifier)})


def _set_typed_identifier(resource: dict[str, Any], identifier: dict[str, Any]) -> None:
    existing = typed(resource, role_of(identifier))
    if existing is not None:
        existing["system"] = identifier["system"]
        existing["value"] = identifier["value"]
        return
    resource.setdefault("identifier", []).append(copy.deepcopy(identifier))


def _set_entry_key(entry: dict[str, Any], identifier: Mapping[str, Any]) -> None:
    key = {
        "type": copy.deepcopy(identifier["type"]),
        "system": identifier["system"],
        "value": identifier["value"],
    }
    others = [
        extension for extension in entry.get("extension", [])
        if extension.get("url") != ENTRY_KEY_EXTENSION
    ]
    entry["extension"] = [{"url": ENTRY_KEY_EXTENSION, "valueIdentifier": key}, *others]


def _output_key(resource: Mapping[str, Any]) -> Mapping[str, Any]:
    for role in ("source-output", "source-artifact"):
        identifier = typed(resource, role)
        if identifier is not None:
            return identifier
    raise ValueError(f"{resource.get('resourceType')} output carries no source-output Identifier")


def _source_pair(provenance: Mapping[str, Any]) -> tuple[str, str]:
    identifier = provenance["entity"][0]["what"]["identifier"]
    return str(identifier["system"]), str(identifier["value"])


def _keyed(entry: dict[str, Any], bundle: Mapping[str, Any], subject: tuple[str, str]) -> Mapping[str, Any]:
    resource = entry["resource"]
    resource_type = resource.get("resourceType")
    if resource_type == "Device":
        profiles = resource.get("meta", {}).get("profile", [])
        node_role = next(DEVICE_NODE_ROLES[profile] for profile in profiles if profile in DEVICE_NODE_ROLES)
        value = device_snapshot_identity(
            key=KEY, key_id=KEY_ID, epoch=EPOCH, subject_system=subject[0], subject_value=subject[1],
            node_role=node_role, content_digest=content_digest(resource),
        )
        identifier = typed_identifier("device-snapshot", value)
        _set_typed_identifier(resource, identifier)
        return identifier
    if resource_type in CONTEXT_NODE_ROLES:
        value = context_snapshot_identity(
            key=KEY, key_id=KEY_ID, epoch=EPOCH, subject_system=subject[0], subject_value=subject[1],
            node_role=CONTEXT_NODE_ROLES[resource_type], content_digest=content_digest(resource),
        )
        identifier = typed_identifier("context-snapshot", value)
        _set_typed_identifier(resource, identifier)
        return identifier
    if resource_type == "QuestionnaireResponse":
        value = context_snapshot_identity(
            key=KEY, key_id=KEY_ID, epoch=EPOCH, subject_system=subject[0], subject_value=subject[1],
            node_role="questionnaire-response", content_digest=content_digest(resource),
        )
        identifier = typed_identifier("context-snapshot", value)
        _set_extension(resource, CONTEXT_SNAPSHOT_EXTENSION, identifier)
        return identifier
    if resource_type == "Provenance":
        source_system, source_value = _source_pair(resource)
        if ACTIVE_BUNDLE_PROFILE in bundle.get("meta", {}).get("profile", []):
            digest = record_content_digest(resource, record_outputs(bundle, resource))
            value = record_version_identity(
                key=KEY, key_id=KEY_ID, epoch=EPOCH, source_record_system=source_system,
                source_record_value=source_value, record_content_digest=digest,
            )
            identifier = typed_identifier("record-version", value)
            _set_extension(resource, RECORD_VERSION_EXTENSION, identifier)
            return identifier
        value = record_retraction_identity(
            key=KEY, key_id=KEY_ID, epoch=EPOCH, source_record_system=source_system,
            source_record_value=source_value,
        )
        return typed_identifier("record-retraction", value)
    return _output_key(resource)


def rekey(bundle: dict[str, Any], subject: tuple[str, str] = SUBJECT) -> dict[str, Any]:
    """Mint every entry key of a lossless Bundle in place and return it.

    Output keys are their typed source-output or source-artifact Identifiers and never change.
    Every other key is derived from final content, so keying repeats until no fullUrl moves.
    """
    for _ in range(MAX_ROUNDS):
        moved = False
        for entry in bundle["entry"]:
            identifier = _keyed(entry, bundle, subject)
            _set_entry_key(entry, identifier)
            full_url = entry_full_url(identifier["system"], identifier["value"])
            previous = entry.get("fullUrl")
            if previous != full_url:
                entry["fullUrl"] = full_url
                if isinstance(previous, str):
                    rewrite_references(bundle, {previous: full_url})
                moved = True
        if not moved:
            return bundle
    raise RuntimeError("fixture keys did not converge; the Bundle has a reference cycle")


def entry_key(entry: Mapping[str, Any]) -> Mapping[str, Any]:
    return next(
        extension["valueIdentifier"] for extension in entry["extension"]
        if extension.get("url") == ENTRY_KEY_EXTENSION
    )
