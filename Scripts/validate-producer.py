#!/usr/bin/env python3
"""Validate producer-emitted R4 resources without executing the producer."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from Scripts.exchange_protocol import (
        ENTRY_NODE_IDENTITY,
        EVENT_IDENTITY,
        HMAC_IDENTITY,
        ExchangeProtocolError,
        entry_full_url,
        entry_node_identity,
        require_absolute_uri,
    )
except ModuleNotFoundError:  # Direct `python Scripts/validate-producer.py` execution.
    from exchange_protocol import (  # type: ignore[no-redef]
        ENTRY_NODE_IDENTITY,
        EVENT_IDENTITY,
        HMAC_IDENTITY,
        ExchangeProtocolError,
        entry_full_url,
        entry_node_identity,
        require_absolute_uri,
    )


PACKAGE_ALIAS = re.compile(r"^[a-z][a-z0-9-]*$")
PACKAGE_ID = re.compile(r"^[a-z0-9.-]+$")
FHIR_ID = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")
GROVE_PROFILE = "https://grovealliance.org/fhir/"
EXCHANGE_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle"
)
RETRACTION_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-retraction-bundle"
)
ENTRY_IDENTIFIER_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-node-key"
)
IDENTIFIER_ROLE_SYSTEM = (
    "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
)
LIFECYCLE_EVENT_SYSTEM = (
    "https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event"
)
RETRACTION_TARGET_ROLE_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role"
)
SOURCE_RECORD_RETRACTED = "source-record-retracted"
VALIDATOR_FILE_EXTENSION = (
    "http://hl7.org/fhir/StructureDefinition/operationoutcome-file"
)
VALIDATOR_ATTEMPTS = 2
VALIDATOR_LOG_LIMIT = 4000
VALIDATOR_TIMEOUT_SECONDS = 180
TOP_LEVEL_KEYS = {
    "schemaVersion",
    "fhirVersion",
    "producer",
    "packages",
    "resources",
    "semanticVectors",
}
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = REPOSITORY_ROOT / "catalog"
FHIR_TOOL_HOME = REPOSITORY_ROOT / ".build" / "fhir-home"
EXCHANGE_PROTOCOL = json.loads(
    (CATALOG_ROOT / "exchange-protocol.json").read_text(encoding="utf-8")
)
ACTIVE_ENTRY_POLICY = EXCHANGE_PROTOCOL["lifecycle"]["active"][
    "entryResourcePolicy"
]
ACTIVE_OUTPUT_RESOURCE_TYPES = frozenset(
    ACTIVE_ENTRY_POLICY["outputResourceTypes"]
)
ACTIVE_SUPPORTING_RESOURCE_TYPES = frozenset(
    ACTIVE_ENTRY_POLICY["supportingResourceTypes"]
)
ACTIVE_ENTRY_RESOURCE_TYPES = frozenset(
    {
        *ACTIVE_OUTPUT_RESOURCE_TYPES,
        *ACTIVE_SUPPORTING_RESOURCE_TYPES,
        ACTIVE_ENTRY_POLICY["lifecycleResourceType"],
    }
)
RETRACTION_TARGET_CONTRACTS = EXCHANGE_PROTOCOL["lifecycle"]["retraction"][
    "targetRoles"
]
RETRACTION_TARGET_ROLES = frozenset(RETRACTION_TARGET_CONTRACTS)
REFERENCE_POLICY = EXCHANGE_PROTOCOL["referencePolicy"]
# The normative protocol is the only priority authority. In particular, a Device snapshot is
# the immutable event node and therefore outranks the same Device's stable physical-unit key.
IDENTIFIER_PRIORITY = tuple(
    EXCHANGE_PROTOCOL["entryIdentity"]["resourceIdentifierPriority"]
)
OPAQUE_IDENTIFIER_ROLES = frozenset(
    identity["identifierRole"]
    for identity in EXCHANGE_PROTOCOL["opaqueIdentity"]["identityKinds"]
)
# Read from the graph rather than restated: a literal here has to be remembered at every
# release, and was left at 0.4.0 through the 0.5.0 bump.
RELEASE_VERSION = json.loads(
    (CATALOG_ROOT / "package-graph.json").read_text(encoding="utf-8")
)["version"]

# The registry generations in which each format code was defined. 0.X releases are breaking and
# the code sets are disjoint, so today this is one generation per code; it becomes a real history
# the first time a code survives a release.
REGISTRY_GENERATIONS = {
    code: (RELEASE_VERSION,)
    for code in json.loads(
        (CATALOG_ROOT / "format-registry.json").read_text(encoding="utf-8")
    )["formats"]
}

# Adapter package/profile membership is projected from the release graph. Keeping a second,
# hand-written list here previously allowed a new profile to bypass package-presence checks.
_PACKAGE_GRAPH = json.loads(
    (CATALOG_ROOT / "package-graph.json").read_text(encoding="utf-8")
)
_MEASUREMENT_CATALOG = json.loads(
    (CATALOG_ROOT / "measurement-catalog.json").read_text(encoding="utf-8")
)
MEASUREMENT_BY_PROFILE = {
    f"https://grovealliance.org/fhir/{entry.get('owner', 'mobile')}"
    f"/StructureDefinition/{entry['profile']}": entry
    for entry in _MEASUREMENT_CATALOG["measurements"]
}
_NON_ADAPTER_SOURCES = {"mobile", "questionnaire", "sensor"}
ADAPTER_PACKAGE_PROFILES = {
    package["packageId"]: {
        f"{package['canonical']}/StructureDefinition/{profile}"
        for profile in package["profiles"]
    }
    for package in _PACKAGE_GRAPH["packages"]
    if package["source"] not in _NON_ADAPTER_SOURCES
}
KNOWN_ADAPTER_PROFILES = {
    profile
    for package_profiles in ADAPTER_PACKAGE_PROFILES.values()
    for profile in package_profiles
}
SENSOR_SAMPLED_PROFILE = (
    "https://grovealliance.org/fhir/sensor/StructureDefinition/"
    "grove-sensor-sampled-data-observation"
)
SENSOR_ECG_PROFILE = (
    "https://grovealliance.org/fhir/sensor/StructureDefinition/"
    "grove-sensor-ecg-observation"
)
SENSOR_RECORDING_PROFILE = (
    "https://grovealliance.org/fhir/sensor/StructureDefinition/"
    "grove-sensor-recording-document"
)
RECORDING_DOCUMENT_PROFILE_TAIL = "-recording-document"
HEALTHKIT_PROFILE_PREFIX = (
    "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
)
HEALTHKIT_OBSERVATION_PROFILE = HEALTHKIT_PROFILE_PREFIX + "healthkit-observation"
HEALTHKIT_RECORDING_PROFILE = HEALTHKIT_PROFILE_PREFIX + "healthkit-recording-document"
HEALTHKIT_CLINICAL_RECORD_PROFILE = (
    HEALTHKIT_PROFILE_PREFIX + "healthkit-clinical-record-document"
)
HEALTHKIT_ECG_PROFILE = (
    HEALTHKIT_PROFILE_PREFIX + "healthkit-ecg-observation"
)
SAMPLED_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")
FHIR_INSTANT = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?P<offset>Z|[+-][0-9]{2}:[0-9]{2})$"
)


PRODUCER_RULE_REASONS = {
    "mobile-exchange.entry-node-key":
        "Every Bundle entry must carry exactly one complete Grove exchange entry node key.",
    "mobile-exchange.deterministic-full-url":
        "Bundle.entry.fullUrl must be the UUID version 5 value derived from its complete entry identifier.",
    "mobile-exchange.resolved-reference":
        "Every internal UUID URN reference must resolve to a Bundle entry fullUrl.",
    "mobile-exchange.event-identity":
        "Bundle.identifier.value must be the canonical e2 producer UUID and positive sequence form.",
    "mobile-exchange.entry-node-digest":
        "An entry-node digest must be derived from the enclosing event identifier, role, and ordinal.",
    "mobile-output.source-output-required":
        "Every active clinical output must carry its exact typed source-output identity in addition to source-record identity.",
    "mobile-exchange.transform-provenance":
        "An active event must contain exactly one transform Provenance and no retraction Provenance.",
    "mobile-retraction.logical-target":
        "A retraction target must be a typed logical Reference without a literal reference.",
    "mobile-retraction.target-role":
        "Every retraction target must carry exactly one closed Grove target-role code.",
    "mobile-retraction.opaque-target":
        "A retraction target must use the exact canonical v2 HMAC identity previously emitted.",
    "mobile-retraction.no-clinical-copy":
        "A retraction event contains its lifecycle Provenance and optional Device agents, never a copied or mutilated clinical resource.",
    "mobile-exchange.lifecycle-coding":
        "A lifecycle Provenance must carry exactly one coding across the ISO transform and Grove retraction lifecycle systems; translations from other systems remain open.",
    "mobile-output.semantic-profile":
        "Every active Observation must directly claim one admitted Grove semantic profile shape; an empty claim cannot bypass semantic validation.",
    "mobile-exchange.reference-target-type":
        "An Observation subject resolves to a Patient entry, not merely to any existing fullUrl.",
    "mobile-exchange.reference-declared-type":
        "When Reference.type is present it must equal the referenced entry's actual resourceType token.",
    "mobile-exchange.logical-source-entity":
        "Lifecycle Provenance carries exactly one logical source-record Identifier entity and never a literal source Reference.",
    "mobile-retraction.role-target-type":
        "Every retraction target role fixes its admitted resource type and Identifier role.",
    "mobile-exchange.single-source-entity":
        "A lifecycle Provenance identifies exactly one source-record entity.",
    "mobile-exchange.reference-shape":
        "A governed Reference is exclusively resolving-literal or identifier-only logical, never both.",
    "mobile-exchange.logical-patient-reference":
        "An identifier-only logical Patient Reference carries the exact Patient type and one complete absolute-system pseudonym Identifier.",
    "mobile-output.adapter-only-profile":
        "An adapter-only active output type must directly claim exactly its one admitted adapter profile.",
    "mobile-exchange.entry-resource-type":
        "An active event admits only its closed output, supporting, and lifecycle resource type set.",
    "mobile-exchange.contained-resource-prohibited":
        "Mobile exchange events prohibit contained resources; every graph node must be an addressable Bundle entry.",
    "mobile-output.document-profile":
        "Every active DocumentReference must directly claim exactly one admitted recording or clinical-document profile mode.",
    "mobile-support.device-profile":
        "Every active Device must directly claim exactly one admitted Grove Device profile mode.",
    "mobile-support.connected":
        "Every supporting resource must be connected to an output or the lifecycle Provenance.",
    "mobile-exchange.provenance-profile":
        "The sole active lifecycle Provenance must directly claim exactly one admitted Mobile or adapter conversion profile.",
}


class ProducerValidationError(ValueError):
    """A deterministic producer-contract validation failure with an optional rule diagnostic."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        reason: str | None = None,
        location: str | None = None,
        severity: str = "error",
    ) -> None:
        super().__init__(message)
        self.diagnostic = None if code is None else {
            "code": code,
            "reason": reason if reason is not None else PRODUCER_RULE_REASONS[code],
            "location": location,
            "severity": severity,
        }


def contract_failure(
    code: str,
    location: str,
    message: str,
    *,
    reason: str | None = None,
) -> ProducerValidationError:
    """Construct one machine-comparable producer diagnostic without replacing human detail."""
    return ProducerValidationError(
        message,
        code=code,
        reason=reason,
        location=location,
    )


def unlinked_path(path: Path, label: str) -> Path:
    """Return one lexical path after rejecting every supplied symlink component."""
    if not isinstance(path, Path) or not path.parts:
        raise ProducerValidationError(f"{label} path is invalid")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ProducerValidationError(f"{label} path must not contain traversal components")
    if path.is_absolute():
        current = Path(path.anchor)
        components = path.parts[1:]
    else:
        # Path.cwd() is the process's physical working directory. The supplied
        # relative components are still inspected before resolution.
        current = Path.cwd()
        components = path.parts
    for component in components:
        current = current / component
        if current.is_symlink():
            raise ProducerValidationError(
                f"{label} path contains a symlink component: {path}"
            )
    return current


def resolve_unlinked_regular_file(path: Path, label: str) -> Path:
    """Require a regular, non-symlink file and resolve only after inspection."""
    candidate = unlinked_path(path, label)
    try:
        mode = candidate.stat().st_mode
    except OSError as error:
        raise ProducerValidationError(f"{label} file is absent: {path}") from error
    if not stat.S_ISREG(mode):
        raise ProducerValidationError(f"{label} path is not a regular file: {path}")
    try:
        return candidate.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(f"{label} file cannot be resolved: {path}") from error


def resolve_unlinked_directory(path: Path, label: str) -> Path:
    """Require a prepared directory whose supplied path contains no symlink."""
    candidate = unlinked_path(path, label)
    try:
        mode = candidate.stat().st_mode
    except OSError as error:
        raise ProducerValidationError(f"{label} directory is absent: {path}") from error
    if not stat.S_ISDIR(mode):
        raise ProducerValidationError(f"{label} path is not a directory: {path}")
    try:
        return candidate.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(
            f"{label} directory cannot be resolved: {path}"
        ) from error


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProducerValidationError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_float=Decimal,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read JSON {path}: {error}") from error


def require_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = set(value) - expected
    if unknown:
        raise ProducerValidationError(f"{label} has unsupported fields: {', '.join(sorted(unknown))}")


def safe_resource_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.endswith(".json"):
        raise ProducerValidationError("resource path must be a relative JSON file")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ProducerValidationError(f"unsafe resource path: {value!r}")
    if root.is_symlink():
        raise ProducerValidationError("manifest resource directory must not be a symlink")
    path = root
    for part in candidate.parts:
        path = path / part
        if path.is_symlink():
            raise ProducerValidationError(
                f"resource path contains a symlink component: {value}"
            )
    try:
        resolved_root = root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(f"resource is absent: {value}") from error
    if not path.is_file() or (
        resolved_path.parent != resolved_root and resolved_root not in resolved_path.parents
    ):
        raise ProducerValidationError(f"resource is absent, linked, or outside the manifest directory: {value}")
    return path


def json_pointer(value: Any, pointer: Any, label: str) -> Any:
    """Resolve one strict RFC 6901 pointer without accepting ambiguous array indexes."""
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise ProducerValidationError(f"{label} must be an RFC 6901 JSON Pointer")
    current = value
    if not pointer:
        return current
    for raw_token in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw_token):
            raise ProducerValidationError(f"{label} contains an invalid JSON Pointer escape")
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise ProducerValidationError(f"{label} does not resolve")
            current = current[token]
        elif isinstance(current, list):
            if re.fullmatch(r"0|[1-9][0-9]*", token) is None:
                raise ProducerValidationError(f"{label} has an invalid array index")
            index = int(token)
            if index >= len(current):
                raise ProducerValidationError(f"{label} does not resolve")
            current = current[index]
        else:
            raise ProducerValidationError(f"{label} traverses a scalar value")
    return current


def nested_fhir_resources(resource: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a resource and every directly embedded Bundle entry resource."""
    resources = [resource]
    if resource.get("resourceType") != "Bundle":
        return resources
    entries = resource.get("entry", [])
    if not isinstance(entries, list):
        return resources
    for entry in entries:
        child = entry.get("resource") if isinstance(entry, dict) else None
        if isinstance(child, dict) and isinstance(child.get("resourceType"), str):
            resources.extend(nested_fhir_resources(child))
    return resources


def mobile_semantic_projection(
    resource: Any, vector: dict[str, Any], label: str
) -> dict[str, Any]:
    """Extract the closed source-neutral clinical projection for one Mobile vector."""
    if not isinstance(resource, dict) or resource.get("resourceType") != "Observation":
        raise ProducerValidationError(f"{label} must resolve to an Observation")
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or vector["profile"] not in profiles:
        raise ProducerValidationError(
            f"{label} does not directly claim semantic vector {vector['id']}"
        )

    expected_code = vector["code"]
    codings = resource.get("code", {}).get("coding", [])
    code_matches = [
        coding
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == expected_code["system"]
        and coding.get("code") == expected_code["code"]
    ] if isinstance(codings, list) else []
    if len(code_matches) != 1:
        raise ProducerValidationError(
            f"{label} must contain exactly one normalized semantic code"
        )
    for required_coding in expected_code.get("requiredCodings", []):
        required_matches = [
            coding
            for coding in codings
            if isinstance(coding, dict)
            and coding.get("system") == required_coding["system"]
            and coding.get("code") == required_coding["code"]
        ]
        if len(required_matches) != 1:
            raise ProducerValidationError(
                f"{label} must contain exactly one required profile coding "
                f"{required_coding['system']}#{required_coding['code']}"
            )

    expected_effective = vector["effective"]
    if expected_effective["type"] == "dateTime":
        actual_value = resource.get("effectiveDateTime")
        actual_milliseconds = parse_fhir_instant(
            actual_value, f"{label}.effectiveDateTime"
        )
        if actual_milliseconds != round_mobile_epoch_milliseconds(actual_milliseconds):
            raise ProducerValidationError(
                f"{label} effective instant is not millisecond-canonical"
            )
        expected_milliseconds = round_mobile_epoch_milliseconds(parse_fhir_instant(
            expected_effective["value"],
            f"Mobile semantic vector {vector['id']} effectiveDateTime",
        ))
        if actual_milliseconds != expected_milliseconds:
            raise ProducerValidationError(
                f"{label} effective instant does not equal Mobile semantic vector {vector['id']}"
            )
        effective = expected_effective
    else:
        period = resource.get("effectivePeriod")
        if not isinstance(period, dict):
            raise ProducerValidationError(f"{label} must contain an effectivePeriod")
        for endpoint in ("start", "end"):
            actual_milliseconds = parse_fhir_instant(
                period.get(endpoint), f"{label}.effectivePeriod.{endpoint}"
            )
            if actual_milliseconds != round_mobile_epoch_milliseconds(actual_milliseconds):
                raise ProducerValidationError(
                    f"{label} effective Period {endpoint} is not millisecond-canonical"
                )
            expected_milliseconds = round_mobile_epoch_milliseconds(parse_fhir_instant(
                expected_effective[endpoint],
                f"Mobile semantic vector {vector['id']} effectivePeriod.{endpoint}",
            ))
            if actual_milliseconds != expected_milliseconds:
                raise ProducerValidationError(
                    f"{label} effective Period does not equal Mobile semantic vector {vector['id']}"
                )
        effective = expected_effective

    expected_result = vector["result"]
    if expected_result["type"] == "Quantity":
        quantity = resource.get("valueQuantity")
        result = {
            "type": "Quantity",
            "value": quantity.get("value") if isinstance(quantity, dict) else None,
            "system": quantity.get("system") if isinstance(quantity, dict) else None,
            "code": quantity.get("code") if isinstance(quantity, dict) else None,
            "unit": quantity.get("unit") if isinstance(quantity, dict) else None,
        }
    elif expected_result["type"] == "components":
        actual_components = resource.get("component")
        if not isinstance(actual_components, list) or len(actual_components) != len(
            expected_result["components"]
        ):
            raise ProducerValidationError(
                f"{label} must contain exactly the normalized result components"
            )
        projected_components: list[dict[str, Any]] = []
        for expected_component in expected_result["components"]:
            matches = []
            for component in actual_components:
                component_codings = (
                    component.get("code", {}).get("coding", [])
                    if isinstance(component, dict)
                    else []
                )
                if any(
                    isinstance(coding, dict)
                    and coding.get("system") == expected_component["system"]
                    and coding.get("code") == expected_component["code"]
                    for coding in component_codings
                ):
                    matches.append(component)
            if len(matches) != 1:
                raise ProducerValidationError(
                    f"{label} must contain exactly one {expected_component['id']} component"
                )
            quantity = matches[0].get("valueQuantity")
            projected_components.append({
                "id": expected_component["id"],
                "system": expected_component["system"],
                "code": expected_component["code"],
                "value": quantity.get("value") if isinstance(quantity, dict) else None,
                "quantitySystem": quantity.get("system") if isinstance(quantity, dict) else None,
                "quantityCode": quantity.get("code") if isinstance(quantity, dict) else None,
                "unit": quantity.get("unit") if isinstance(quantity, dict) else None,
            })
        result = {"type": "components", "components": projected_components}
    else:
        concept = resource.get("valueCodeableConcept")
        value_codings = concept.get("coding", []) if isinstance(concept, dict) else []
        matches = [
            coding
            for coding in value_codings
            if isinstance(coding, dict)
            and coding.get("system") == expected_result["system"]
            and coding.get("code") == expected_result["code"]
        ] if isinstance(value_codings, list) else []
        if len(matches) != 1:
            raise ProducerValidationError(
                f"{label} must contain exactly one normalized result coding"
            )
        result = {
            "type": "CodeableConcept",
            "system": expected_result["system"],
            "code": expected_result["code"],
        }

    return {
        "profile": vector["profile"],
        "code": expected_code,
        "effective": effective,
        "result": result,
    }


def all_references(value: Any) -> list[str]:
    references: list[str] = []
    if isinstance(value, dict):
        reference = value.get("reference")
        if isinstance(reference, str):
            references.append(reference)
        for child in value.values():
            references.extend(all_references(child))
    elif isinstance(value, list):
        for child in value:
            references.extend(all_references(child))
    return references


def all_reference_nodes(value: Any) -> list[dict[str, Any]]:
    """Return every Reference-shaped object carrying a literal reference."""
    nodes: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("reference"), str):
            nodes.append(value)
        for child in value.values():
            nodes.extend(all_reference_nodes(child))
    elif isinstance(value, list):
        for child in value:
            nodes.extend(all_reference_nodes(child))
    return nodes


def all_reference_nodes_with_paths(
    value: Any, path: str = ""
) -> list[tuple[str, dict[str, Any]]]:
    """Return literal Reference-shaped objects with stable FHIR-style element paths."""
    nodes: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if isinstance(value.get("reference"), str):
            nodes.append((path, value))
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            nodes.extend(all_reference_nodes_with_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nodes.extend(all_reference_nodes_with_paths(child, f"{path}[{index}]"))
    return nodes


def reference_target(
    reference: dict[str, Any],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> dict[str, Any] | None:
    """Resolve one literal reference and enforce an exact declared resource type."""
    literal = reference.get("reference")
    if not isinstance(literal, str):
        return None
    target = resources_by_full_url.get(literal)
    if not isinstance(target, dict):
        raise ProducerValidationError(f"{label} does not resolve inside its exchange graph")
    actual_type = target.get("resourceType")
    declared_type = reference.get("type")
    if declared_type is not None and declared_type != actual_type:
        raise contract_failure(
            "mobile-exchange.reference-declared-type",
            f"{label}.type",
            f"{label}.type must equal the referenced resource type {actual_type}",
        )
    return target


def validate_governed_reference(
    reference: dict[str, Any],
    allowed: set[str],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Validate the protocol's exclusive literal-or-logical Reference shape."""
    literal = reference.get("reference")
    identifier = reference.get("identifier")
    if isinstance(literal, str):
        if identifier is not None:
            raise contract_failure(
                "mobile-exchange.reference-shape",
                label,
                f"{label} must not mix a resolving literal with a logical identifier",
            )
        target = reference_target(reference, resources_by_full_url, label)
        if target is not None and target.get("resourceType") not in allowed:
            if label == "Observation.subject":
                raise contract_failure(
                    "mobile-exchange.reference-target-type",
                    "Observation.subject.reference",
                    f"{label} must reference " + " or ".join(sorted(allowed)),
                )
            raise ProducerValidationError(
                f"{label} must reference " + " or ".join(sorted(allowed))
            )
        return
    if literal is not None:
        raise ProducerValidationError(f"{label}.reference must be a string when present")
    complete_identifier(identifier, f"{label}.identifier")
    declared_type = reference.get("type")
    if declared_type not in allowed:
        if label == "Observation.subject":
            raise contract_failure(
                "mobile-exchange.logical-patient-reference",
                "Observation.subject",
                f"{label} logical reference type must be "
                + " or ".join(sorted(allowed)),
            )
        raise ProducerValidationError(
            f"{label} logical reference type must be " + " or ".join(sorted(allowed))
        )


def reference_values_at_path(resource: dict[str, Any], path: str) -> list[dict[str, Any]]:
    value = resource.get(path)
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def all_extensions(value: Any) -> list[dict[str, Any]]:
    """Return extensions recursively so governed Reference extensions cannot hide."""
    extensions: list[dict[str, Any]] = []
    if isinstance(value, dict):
        nested = value.get("extension")
        if isinstance(nested, list):
            extensions.extend(item for item in nested if isinstance(item, dict))
        for child in value.values():
            extensions.extend(all_extensions(child))
    elif isinstance(value, list):
        for child in value:
            extensions.extend(all_extensions(child))
    return extensions


def validate_reference_policy(
    resource: dict[str, Any],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Enforce the protocol's closed internal-reference target-type table."""
    resource_type = resource.get("resourceType")
    for rule in REFERENCE_POLICY["paths"]:
        if rule["resourceType"] != resource_type:
            continue
        allowed = set(rule["targetTypes"])
        for reference in reference_values_at_path(resource, rule["path"]):
            validate_governed_reference(
                reference,
                allowed,
                resources_by_full_url,
                f"{resource_type}.{rule['path']}",
            )
    extension_rules = {
        rule["url"]: set(rule["targetTypes"])
        for rule in REFERENCE_POLICY["extensionTargets"]
    }
    for index, extension in enumerate(all_extensions(resource)):
        allowed = extension_rules.get(extension.get("url"))
        reference = extension.get("valueReference")
        if allowed is None or not isinstance(reference, dict):
            continue
        validate_governed_reference(
            reference,
            allowed,
            resources_by_full_url,
            f"{label}.extension[{index}].valueReference",
        )


def complete_identifier(value: Any, label: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise ProducerValidationError(f"{label} must be an Identifier")
    system = value.get("system")
    identifier_value = value.get("value")
    if not isinstance(system, str) or not system or not isinstance(identifier_value, str) or not identifier_value:
        raise ProducerValidationError(f"{label} must have a complete system and value")
    try:
        require_absolute_uri(system, f"{label}.system")
    except ExchangeProtocolError as error:
        raise ProducerValidationError(str(error)) from error
    return system, identifier_value


def canonical_json_string(value: str) -> str:
    """Serialize one Unicode scalar-value string using RFC 8785/JCS escaping."""
    escapes = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
    }
    output = ['"']
    for character in value:
        point = ord(character)
        if 0xD800 <= point <= 0xDFFF:
            raise ProducerValidationError("entry identity contains an invalid Unicode surrogate")
        if character in escapes:
            output.append(escapes[character])
        elif point <= 0x1F:
            output.append(f"\\u{point:04x}")
        else:
            output.append(character)
    output.append('"')
    return "".join(output)


def canonical_identifier_name(system: str, value: str) -> str:
    """Return a readable diagnostic form; fullUrl derivation uses framed UTF-8 fields."""
    for text in (system, value):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in text):
            raise ProducerValidationError("identifier contains an invalid Unicode surrogate")
    return f"{system}|{value}"


def canonical_string_array(values: list[str]) -> str:
    """Return the RFC 8785 serialization of one string-only array."""
    if any(not isinstance(value, str) for value in values):
        raise ProducerValidationError("canonical identity arrays contain only strings")
    return "[" + ",".join(canonical_json_string(value) for value in values) + "]"


def expected_entry_full_url(system: str, value: str) -> str:
    try:
        return entry_full_url(system, value)
    except ValueError as error:
        raise ProducerValidationError(str(error)) from error


def identifier_role(identifier: Any, label: str) -> str:
    """Read exactly one Grove role Coding from a complete Identifier."""
    complete_identifier(identifier, label)
    codings = identifier.get("type", {}).get("coding", [])
    matches = [
        coding.get("code")
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
        and isinstance(coding.get("code"), str)
    ] if isinstance(codings, list) else []
    if len(matches) != 1:
        raise ProducerValidationError(
            f"{label} must carry exactly one Grove identifier-role Coding"
        )
    return matches[0]


def typed_resource_identifiers(resource: dict[str, Any], label: str) -> dict[str, tuple[str, str]]:
    """Return the resource's unique typed Grove business identifiers by role."""
    identifiers = resource.get("identifier", [])
    if identifiers is None:
        return {}
    # R4 uses Identifier 0..1 on resources such as QuestionnaireResponse and Bundle,
    # while most exchange output/support resources use Identifier 0..*. Normalize the
    # wire cardinality here so a legitimate singular non-Grove identifier cannot make an
    # otherwise governed QuestionnaireResponse fail before its profile claim is checked.
    if isinstance(identifiers, dict):
        identifiers = [identifiers]
    elif not isinstance(identifiers, list):
        raise ProducerValidationError(
            f"{label}.identifier must be an Identifier or Identifier array"
        )
    result: dict[str, tuple[str, str]] = {}
    for index, identifier in enumerate(identifiers):
        if not isinstance(identifier, dict):
            raise ProducerValidationError(f"{label}.identifier[{index}] must be an Identifier")
        codings = identifier.get("type", {}).get("coding", [])
        roles = [
            coding.get("code")
            for coding in codings
            if isinstance(coding, dict)
            and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
            and isinstance(coding.get("code"), str)
        ] if isinstance(codings, list) else []
        if not roles:
            continue
        if len(roles) != 1 or roles[0] not in OPAQUE_IDENTIFIER_ROLES:
            raise ProducerValidationError(
                f"{label}.identifier[{index}] has an unknown or repeated Grove identifier role"
            )
        role = roles[0]
        if role in result:
            raise ProducerValidationError(f"{label} repeats the {role} identifier role")
        pair = complete_identifier(identifier, f"{label}.identifier[{index}]")
        if HMAC_IDENTITY.fullmatch(pair[1]) is None:
            raise ProducerValidationError(
                f"{label}.identifier[{index}] is not a canonical Grove v2 HMAC identity"
            )
        result[role] = pair
    return result


def selected_entry_identifier(resource: dict[str, Any], label: str) -> tuple[str, tuple[str, str]] | None:
    """Select the deterministic resource business identifier required by protocol v2."""
    by_role = typed_resource_identifiers(resource, label)
    for role in IDENTIFIER_PRIORITY:
        if role in by_role:
            return role, by_role[role]
    return None


def adapter_profile_contract() -> tuple[set[str], set[str]]:
    """Return the exact shared-measurement and adapter profile sets."""
    measurements = read_json(CATALOG_ROOT / "measurement-catalog.json")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    shared = {
        f"https://grovealliance.org/fhir/{entry.get('owner', 'mobile')}"
        f"/StructureDefinition/{entry['profile']}"
        for entry in measurements["measurements"]
    }
    shared.update(claims["observationAdapterClaim"].get("sharedSensorProfiles", []))
    shared.update(
        entry["semanticProfile"]
        for entry in claims["observationAdapterClaim"].get("standardAdapterClaims", [])
    )
    adapters = set(claims["observationAdapterClaim"]["adapterProfiles"])
    return shared, adapters


def validate_quantity_value_domain(
    resource: dict[str, Any], label: str, semantic_profile: str
) -> None:
    """Enforce a reviewed representational domain without inventing clinical ranges."""
    measurement = MEASUREMENT_BY_PROFILE.get(semantic_profile)
    quantity_contract = measurement.get("quantity") if measurement else None
    domain = (
        quantity_contract.get("valueDomain")
        if isinstance(quantity_contract, dict)
        else None
    )
    if not isinstance(domain, dict):
        return
    quantity = resource.get("valueQuantity")
    if not isinstance(quantity, dict) or quantity.get("value") is None:
        return
    raw_value = quantity["value"]
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float, Decimal)):
        raise ProducerValidationError(f"{label}.valueQuantity.value must be a number")
    try:
        value = Decimal(str(raw_value))
    except InvalidOperation as error:
        raise ProducerValidationError(
            f"{label}.valueQuantity.value is not a finite decimal"
        ) from error
    if not value.is_finite():
        raise ProducerValidationError(
            f"{label}.valueQuantity.value is not a finite decimal"
        )
    for name, lower in (("minimum", True), ("maximum", False)):
        boundary = domain.get(name)
        if not isinstance(boundary, dict):
            continue
        expected = Decimal(str(boundary["value"]))
        admitted = (
            value >= expected if lower and boundary["inclusive"]
            else value > expected if lower
            else value <= expected if boundary["inclusive"]
            else value < expected
        )
        if not admitted:
            relation = "minimum" if lower else "maximum"
            qualifier = "inclusive" if boundary["inclusive"] else "exclusive"
            raise ProducerValidationError(
                f"{label}.valueQuantity.value violates the {qualifier} {relation} "
                f"{boundary['value']} for {measurement['id']}"
            )
    if domain["integerOnly"] and value != value.to_integral_value():
        raise ProducerValidationError(
            f"{label}.valueQuantity.value must be an integer for {measurement['id']}"
        )


def validate_adapter_profile_claim(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    """Require an explicitly claimed adapter Observation to claim shared + adapter."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    shared_profiles, adapter_profiles = adapter_profile_contract()
    claimed_adapters = set(profiles) & adapter_profiles
    claimed_shared = set(profiles) & shared_profiles
    if active_adapter_profiles is not None:
        inactive = claimed_adapters - active_adapter_profiles
        if inactive:
            raise ProducerValidationError(
                f"{label} claims an adapter profile whose exact package is absent: "
                + ", ".join(sorted(inactive))
            )
    if not claimed_adapters:
        return
    if (
        len(claimed_adapters) != 1
        or len(claimed_shared) != 1
        or len(profiles) != 2
        or len(set(profiles)) != 2
    ):
        raise ProducerValidationError(
            f"{label} adapter Observation must claim exactly one shared semantic profile "
            "and exactly one adapter profile"
        )


def validate_active_observation_profile_claim(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None,
) -> None:
    """Reject unprofiled or arbitrarily profiled active Observation outputs."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if (
        not isinstance(profiles, list)
        or not profiles
        or any(not isinstance(profile, str) for profile in profiles)
        or len(profiles) != len(set(profiles))
    ):
        raise contract_failure(
            "mobile-output.semantic-profile",
            "Observation.meta.profile",
            f"{label} active Observation must carry a non-repeated direct profile claim",
        )
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    direct = set(profiles)
    healthkit_single = set(
        claims["healthKitSingleProfileObservationClaims"]["profiles"]
    )
    if len(direct) == 1 and direct <= healthkit_single:
        validate_quantity_value_domain(resource, label, next(iter(direct)))
        return
    health_connect_exclusive = set(
        claims["healthConnectPlatformExclusiveClaims"]["profiles"]
    )
    if len(direct) == 1 and direct <= health_connect_exclusive:
        validate_quantity_value_domain(resource, label, next(iter(direct)))
        return
    platform_exclusive = set(claims["sensorKitPlatformExclusiveClaims"]["profiles"])
    if len(direct) == 1 and direct <= platform_exclusive:
        return
    hybrid = set(claims["sensorKitHybridObservationClaims"]["profiles"])
    if direct == hybrid:
        return
    shared_profiles, adapter_profiles = adapter_profile_contract()
    shared = direct & shared_profiles
    adapters = direct & adapter_profiles
    expected = shared | adapters
    if len(shared) != 1 or direct != expected:
        raise ProducerValidationError(
            f"{label} active Observation must claim exactly one admitted shared semantic "
            "profile and no arbitrary direct profile"
        )
    validate_quantity_value_domain(resource, label, next(iter(shared)))
    if adapters and len(adapters) != 1:
        raise ProducerValidationError(
            f"{label} active Observation must claim at most one adapter profile"
        )
    if active_adapter_profiles is not None and adapters:
        if len(adapters) != 1 or not adapters <= active_adapter_profiles:
            raise ProducerValidationError(
                f"{label} active Observation claims a profile from an absent adapter package"
            )


def validate_active_adapter_only_output_profile_claim(
    resource: dict[str, Any], label: str
) -> None:
    """Reject source-neutral or unprofiled use of adapter-only active output types."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    specimen = claims["healthConnectSpecimenClaim"]
    expected_by_type = {
        specimen["resourceType"]: specimen["profile"],
        **{
            claim["resourceType"]: claim["profile"]
            for claim in claims["healthKitPlatformExclusiveResourceClaims"]
        },
    }
    expected = expected_by_type.get(resource.get("resourceType"))
    if expected is None:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if profiles != [expected]:
        raise contract_failure(
            "mobile-output.adapter-only-profile",
            f"{resource.get('resourceType')}.meta.profile",
            f"{label} active {resource.get('resourceType')} must directly claim exactly "
            f"its adapter-only profile {expected}",
        )


def validate_active_document_reference_profile_claim(
    resource: dict[str, Any], label: str
) -> None:
    """Require every active source artifact to match one exact document claim mode."""
    if resource.get("resourceType") != "DocumentReference":
        return
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    admitted = [
        claims["sensorRecordingDocumentClaim"],
        claims["healthKitRecordingDocumentClaim"],
        claims["healthKitClinicalRecordDocumentClaim"],
        claims["sensorKitRecordingDocumentClaim"],
        claims["providerRecordingDocumentClaim"],
    ]
    profiles = resource.get("meta", {}).get("profile", [])
    matches = [
        claim
        for claim in admitted
        if (
            isinstance(profiles, list)
            and len(profiles) == claim["cardinality"]
            and len(profiles) == len(set(profiles))
            and set(profiles) == set(claim["profiles"])
        )
    ]
    if len(matches) != 1:
        raise contract_failure(
            "mobile-output.document-profile",
            "DocumentReference.meta.profile",
            f"{label} active DocumentReference must directly claim exactly one "
            "admitted recording or clinical-document profile mode",
        )
    typed = typed_resource_identifiers(resource, label)
    required = set(matches[0]["requiredIdentifierRoles"])
    unexpected = set(typed) - required - {"writer-record"}
    if required - set(typed) or unexpected:
        raise ProducerValidationError(
            f"{label} active DocumentReference has invalid identifier roles"
        )


def validate_exchange_supporting_profile_claim(
    resource: dict[str, Any], label: str
) -> None:
    """Close direct-profile modes for supporting resources with Grove semantics."""
    resource_type = resource.get("resourceType")
    if resource_type not in {"Device", "QuestionnaireResponse"}:
        return
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    admitted = (
        claims["activeDeviceClaims"]
        if resource_type == "Device"
        else [claims["activeQuestionnaireResponseClaim"]]
    )
    profiles = resource.get("meta", {}).get("profile", [])
    matches = [
        claim
        for claim in admitted
        if (
            isinstance(profiles, list)
            and len(profiles) == claim["cardinality"]
            and len(profiles) == len(set(profiles))
            and set(profiles) == set(claim["profiles"])
        )
    ]
    if len(matches) != 1:
        if resource_type == "Device":
            raise contract_failure(
                "mobile-support.device-profile",
                "Device.meta.profile",
                f"{label} active Device must directly claim exactly one admitted "
                "supporting-resource profile mode",
            )
        raise ProducerValidationError(
            f"{label} active {resource_type} must directly claim exactly one admitted "
            "supporting-resource profile mode"
        )
    required_roles = set(matches[0].get("requiredIdentifierRoles", []))
    if required_roles:
        typed = typed_resource_identifiers(resource, label)
        if set(typed) != required_roles:
            raise ProducerValidationError(
                f"{label} active {resource_type} has invalid Grove identifier roles"
            )


def validate_active_provenance_profile_claim(
    resource: dict[str, Any], label: str
) -> None:
    """Require the sole active lifecycle assertion to declare one exact direct profile."""
    if resource.get("resourceType") != "Provenance":
        return
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    admitted = {
        EXCHANGE_PROTOCOL["profiles"]["conversionProvenance"],
        *(claim["profile"] for claim in claims["adapterConversionProvenanceClaims"]),
    }
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or len(profiles) != 1 or profiles[0] not in admitted:
        raise contract_failure(
            "mobile-exchange.provenance-profile",
            "Provenance.meta.profile",
            f"{label} conversion Provenance must directly claim exactly one admitted "
            "Mobile or adapter conversion profile",
        )


def validate_retraction_provenance_profile_claim(
    resource: dict[str, Any], label: str
) -> None:
    """Require the sole retraction assertion to declare only its Mobile profile."""
    if resource.get("resourceType") != "Provenance":
        return
    expected = EXCHANGE_PROTOCOL["profiles"]["retractionProvenance"]
    if resource.get("meta", {}).get("profile", []) != [expected]:
        raise ProducerValidationError(
            f"{label} retraction Provenance must directly claim exactly {expected}"
        )


def validate_active_measurement_fixed_semantics(
    resource: dict[str, Any], label: str
) -> None:
    """Enforce catalog-fixed quantity system/code pairs in the producer lane."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    matches = [MEASUREMENT_BY_PROFILE[profile] for profile in profiles if profile in MEASUREMENT_BY_PROFILE]
    if len(matches) != 1:
        return
    measurement = matches[0]
    quantity_contract = measurement.get("quantity")
    quantity = resource.get("valueQuantity")
    if not isinstance(quantity_contract, dict) or not isinstance(quantity, dict):
        return
    if (
        quantity.get("system") != quantity_contract["system"]
        or quantity.get("code") != quantity_contract["code"]
    ):
        reason = (
            f"A Grove Mobile {measurement['id']} result must use the fixed UCUM code "
            f"{quantity_contract['code']}."
        )
        entry_match = re.search(r"entry\[([0-9]+)\]", label)
        location = (
            f"Bundle.entry[{entry_match.group(1)}].resource.valueQuantity.code"
            if entry_match is not None
            else "Observation.valueQuantity.code"
        )
        raise contract_failure(
            f"mobile-{measurement['id']}.fixed-unit",
            location,
            f"{label} {measurement['id']} must use fixed quantity "
            f"{quantity_contract['system']}#{quantity_contract['code']}",
            reason=reason,
        )


def validate_adapter_source_marker_claim(resource: dict[str, Any], label: str) -> None:
    """Reject adapter source markers on an Observation without that adapter's profile."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(
        not isinstance(profile, str) for profile in profiles
    ):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    profile_set = set(profiles)
    extensions = resource.get("extension", [])
    extension_urls = {
        extension.get("url")
        for extension in extensions
        if isinstance(extension, dict) and isinstance(extension.get("url"), str)
    } if isinstance(extensions, list) else set()

    healthkit = read_json(CATALOG_ROOT / "healthkit-adapter.json")
    healthkit_system = healthkit["sourceTypeCoding"]["system"]
    codings = resource.get("code", {}).get("coding", [])
    has_healthkit_marker = any(
        isinstance(coding, dict) and coding.get("system") == healthkit_system
        for coding in codings
    ) if isinstance(codings, list) else False
    healthkit_profiles = {
        profile for profile in KNOWN_ADAPTER_PROFILES
        if profile.startswith(
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
        )
    }

    health_connect = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    has_health_connect_marker = (
        health_connect["sourceTypeExtension"]["url"] in extension_urls
    )
    health_connect_profiles = {
        profile for profile in KNOWN_ADAPTER_PROFILES
        if profile.startswith(
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
        )
    }

    providers = read_json(CATALOG_ROOT / "providers-adapter.json")
    has_provider_marker = bool(
        {
            providers["sourceTypeExtension"]["url"],
            providers["providerExtension"]["url"],
        }
        & extension_urls
    )
    provider_profiles = {
        profile for profile in KNOWN_ADAPTER_PROFILES
        if any(
            profile.startswith(
                f"https://grovealliance.org/fhir/{guide}/StructureDefinition/"
            )
            for guide in ("providers", "withings", "oura", "google-health")
        )
    }

    sensorkit = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    sensorkit_marker = sensorkit["sourceTypeExtension"]["url"]
    has_sensorkit_marker = sensorkit_marker in extension_urls
    sensorkit_profiles = {
        profile for profile in KNOWN_ADAPTER_PROFILES
        if profile.startswith(
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        )
    }

    for present, admitted, name in (
        (has_healthkit_marker, healthkit_profiles, "HealthKit"),
        (has_health_connect_marker, health_connect_profiles, "Health Connect"),
        (has_provider_marker, provider_profiles, "Provider"),
        (has_sensorkit_marker, sensorkit_profiles, "SensorKit"),
    ):
        if present and not profile_set & admitted:
            raise ProducerValidationError(
                f"{label} carries a {name} source marker without an exact {name} adapter profile"
            )


def validate_active_adapter_package_claims(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None,
) -> None:
    """Reject every adapter artifact whose exact package is absent from the manifest."""
    if active_adapter_profiles is None:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(
        not isinstance(profile, str) for profile in profiles
    ):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claimed = set(profiles) & KNOWN_ADAPTER_PROFILES
    inactive = claimed - active_adapter_profiles
    if inactive:
        raise ProducerValidationError(
            f"{label} claims an adapter profile whose exact package is absent: "
            + ", ".join(sorted(inactive))
        )


def validate_health_connect_specimen_claim(resource: dict[str, Any], label: str) -> None:
    """Require an exact direct profile claim on synthesized Health Connect Specimens."""
    if resource.get("resourceType") != "Specimen":
        return
    claims = read_json(CATALOG_ROOT / "profile-claims.json")["healthConnectSpecimenClaim"]
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    if claims["profile"] not in profiles:
        return
    if profiles != [claims["profile"]]:
        raise ProducerValidationError(
            f"{label} synthesized Health Connect Specimen must directly claim exactly "
            f"{claims['profile']}"
        )
    identifiers = resource.get("identifier")
    if not isinstance(identifiers, list) or len(identifiers) != 2:
        raise ProducerValidationError(
            f"{label} synthesized Health Connect Specimen must carry exactly two identifiers"
        )
    roles = typed_resource_identifiers(resource, label)
    if len(roles) != len(identifiers) or set(roles) != set(claims["requiredIdentifierRoles"]):
        raise ProducerValidationError(
            f"{label} synthesized Health Connect Specimen must carry exactly the "
            "source-record and source-output identifier roles"
        )
    catalog = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    admitted_types = {
        (coding["system"], coding["code"])
        for item in catalog["contextMappings"]["bloodGlucoseSpecimen"]["values"]
        if item.get("status") == "supported"
        and isinstance((coding := item.get("coding")), dict)
    }
    specimen_type = resource.get("type")
    codings = specimen_type.get("coding", []) if isinstance(specimen_type, dict) else []
    snomed = [
        (coding.get("system"), coding.get("code"))
        for coding in codings
        if isinstance(coding, dict) and coding.get("system") == "http://snomed.info/sct"
    ] if isinstance(codings, list) else []
    if len(snomed) != 1 or snomed[0] not in admitted_types:
        raise ProducerValidationError(
            f"{label} synthesized Health Connect Specimen must carry exactly one admitted "
            "SNOMED CT specimen type"
        )


def validate_sensorkit_profile_claim(resource: dict[str, Any], label: str) -> None:
    """Require exact direct claims for SensorKit-only and native-recording outputs."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")

    hybrid_claim = claims["sensorKitHybridObservationClaims"]
    if hybrid_claim["profiles"][1] in profiles and (
        len(profiles) != hybrid_claim["cardinality"]
        or set(profiles) != set(hybrid_claim["profiles"])
    ):
        raise ProducerValidationError(
            f"{label} SensorKit hybrid Observation must directly claim exactly the "
            "source-neutral Sensor and exact SensorKit adapter profiles"
        )

    provider_claim = claims["sensorKitPlatformExclusiveClaims"]
    claimed_provider_profiles = set(profiles) & set(provider_claim["profiles"])
    if claimed_provider_profiles and (
        len(claimed_provider_profiles) != 1
        or profiles != list(claimed_provider_profiles)
    ):
        raise ProducerValidationError(
            f"{label} SensorKit-only Observation must directly claim exactly one "
            "platform-exclusive SensorKit profile"
        )

    if resource.get("resourceType") != "DocumentReference":
        return
    document_claim = claims["sensorKitRecordingDocumentClaim"]
    if document_claim["profiles"][1] not in profiles:
        return
    if len(profiles) != document_claim["cardinality"] or set(profiles) != set(
        document_claim["profiles"]
    ):
        raise ProducerValidationError(
            f"{label} SensorKit Recording Document must directly claim exactly the "
            "source-neutral and SensorKit recording profiles"
        )


def validate_health_connect_provider_claim(resource: dict[str, Any], label: str) -> None:
    """Require one exact direct profile for Health Connect-only glucose semantics."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "healthConnectPlatformExclusiveClaims"
    ]
    claimed = set(profiles) & set(claims["profiles"])
    if claimed and (len(claimed) != 1 or len(profiles) != 1):
        raise ProducerValidationError(
            f"{label} Health Connect-only glucose Observation must directly claim "
            "exactly one adapter-specific profile"
        )


def validate_healthkit_source_type(resource: dict[str, Any], label: str) -> None:
    """Bind one exact HealthKit source coding to its admitted output contract."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    single_profiles = set(
        claims["healthKitSingleProfileObservationClaims"]["profiles"]
    )
    healthkit_observation_profiles = {
        HEALTHKIT_OBSERVATION_PROFILE,
        HEALTHKIT_ECG_PROFILE,
        *single_profiles,
    }
    if not isinstance(profiles, list) or not set(profiles) & healthkit_observation_profiles:
        return
    if any(not isinstance(profile, str) for profile in profiles) or len(profiles) != len(
        set(profiles)
    ):
        raise ProducerValidationError(f"{label} has invalid or repeated meta.profile")
    catalog = read_json(CATALOG_ROOT / "healthkit-adapter.json")
    coding_system = catalog["sourceTypeCoding"]["system"]
    codings = resource.get("code", {}).get("coding", [])
    source_codings = [
        coding for coding in codings
        if isinstance(coding, dict) and coding.get("system") == coding_system
    ] if isinstance(codings, list) else []
    if len(source_codings) != 1 or not isinstance(source_codings[0].get("code"), str):
        raise ProducerValidationError(
            f"{label} must carry exactly one HealthKit source-type coding"
        )
    rows = {
        row["sourceTypeIdentifier"]: row for row in catalog["rows"]
        if row["status"] == "supported"
    }
    row = rows.get(source_codings[0]["code"])
    if row is None:
        raise ProducerValidationError(
            f"{label} uses a HealthKit source type without an admitted output contract"
        )
    row_profiles = set(row["profiles"])
    if HEALTHKIT_OBSERVATION_PROFILE in row_profiles or HEALTHKIT_ECG_PROFILE in row_profiles:
        admitted_claims = [row_profiles]
    else:
        admitted_claims = [
            {profile}
            if profile in single_profiles
            else {profile, HEALTHKIT_OBSERVATION_PROFILE}
            for profile in row["profiles"]
        ]
    if set(profiles) not in admitted_claims:
        raise ProducerValidationError(
            f"{label} HealthKit source type does not match its exact direct profile claims"
        )


def validate_healthkit_resource_claims(resource: dict[str, Any], label: str) -> None:
    """Close HealthKit direct claims for native documents and structured-only outputs."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")

    def require_claim(claim: dict[str, Any], name: str) -> None:
        expected = claim["profiles"]
        # The adapter-specific child is last; the first member may be the shared Sensor
        # recording parent and therefore cannot identify which adapter claim applies.
        if expected[-1] not in profiles:
            return
        if len(profiles) != claim["cardinality"] or set(profiles) != set(expected):
            raise ProducerValidationError(
                f"{label} {name} must directly claim exactly its admitted profile set"
            )
        identities = typed_resource_identifiers(resource, label)
        required = set(claim["requiredIdentifierRoles"])
        missing = required - set(identities)
        unexpected = set(identities) - required - {"writer-record"}
        if missing or unexpected:
            raise ProducerValidationError(
                f"{label} {name} has invalid identifier roles "
                f"(missing={sorted(missing)}, unexpected={sorted(unexpected)})"
            )

    recording_claim = claims["healthKitRecordingDocumentClaim"]
    require_claim(recording_claim, "HealthKit Recording Document")
    require_claim(
        claims["healthKitClinicalRecordDocumentClaim"],
        "HealthKit Clinical Record Document",
    )

    if HEALTHKIT_RECORDING_PROFILE in profiles:
        catalog = read_json(CATALOG_ROOT / "healthkit-adapter.json")
        source_system = catalog["sourceTypeCoding"]["system"]
        codings = resource.get("type", {}).get("coding", [])
        source_codes = [
            coding.get("code")
            for coding in codings
            if isinstance(coding, dict) and coding.get("system") == source_system
        ] if isinstance(codings, list) else []
        admitted = {
            row["sourceTypeIdentifier"]
            for row in catalog["rows"]
            if row["status"] == "platform-exclusive"
            and HEALTHKIT_RECORDING_PROFILE in row.get("profiles", [])
        }
        if len(source_codes) != 1 or source_codes[0] not in admitted:
            raise ProducerValidationError(
                f"{label} must carry exactly one admitted HealthKit recording source type"
            )

    for claim in claims["healthKitPlatformExclusiveResourceClaims"]:
        if claim["profile"] not in profiles:
            continue
        if resource.get("resourceType") != claim["resourceType"]:
            raise ProducerValidationError(
                f"{label} {claim['profile']} is not valid on {resource.get('resourceType')}"
            )
        if profiles != [claim["profile"]]:
            raise ProducerValidationError(
                f"{label} HealthKit platform-exclusive output must directly claim exactly "
                f"{claim['profile']}"
            )
        identities = typed_resource_identifiers(resource, label)
        missing = set(claim["requiredIdentifierRoles"]) - set(identities)
        unexpected = (
            set(identities) - set(claim["requiredIdentifierRoles"]) - {"writer-record"}
        )
        if missing or unexpected:
            raise ProducerValidationError(
                f"{label} HealthKit platform-exclusive output has invalid identifier roles "
                f"(missing={sorted(missing)}, unexpected={sorted(unexpected)})"
            )


def validate_healthkit_ecg_contract(resource: dict[str, Any], label: str) -> None:
    """Validate lossless HealthKit ECG evidence beyond R4 FHIRPath precision."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or HEALTHKIT_ECG_PROFILE not in profiles:
        return

    extension_urls = {
        "classification": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-classification"
        ),
        "symptomsStatus": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-symptoms-status"
        ),
        "correlatedSymptom": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-correlated-symptom"
        ),
        "averageHeartRate": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-average-heart-rate"
        ),
        "samplingFrequency": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-sampling-frequency"
        ),
        "count": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-voltage-measurement-count"
        ),
        "algorithmVersion": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-algorithm-version"
        ),
        "sourcePeriod": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-source-period"
        ),
    }
    extensions = resource.get("extension", [])
    if not isinstance(extensions, list):
        raise ProducerValidationError(f"{label} has invalid ECG extensions")

    def exact_extension(name: str, required: bool = True) -> dict[str, Any] | None:
        matches = [
            extension
            for extension in extensions
            if isinstance(extension, dict)
            and extension.get("url") == extension_urls[name]
        ]
        if len(matches) > 1 or (required and len(matches) != 1):
            requirement = "exactly one" if required else "at most one"
            raise ProducerValidationError(
                f"{label} HealthKit ECG must carry {requirement} {name} extension"
            )
        return matches[0] if matches else None

    classification = exact_extension("classification")
    classification_code = classification.get("valueCode") if classification else None
    if classification_code not in {
        "notSet",
        "sinusRhythm",
        "atrialFibrillation",
        "inconclusiveLowHeartRate",
        "inconclusiveHighHeartRate",
        "inconclusivePoorReading",
        "inconclusiveOther",
        "unrecognized",
    }:
        raise ProducerValidationError(f"{label} has an unknown HealthKit ECG classification")

    status = exact_extension("symptomsStatus")
    status_code = status.get("valueCode") if status else None
    if status_code not in {"notSet", "none", "present"}:
        raise ProducerValidationError(f"{label} has an unknown HealthKit ECG symptoms status")
    correlated = [
        extension
        for extension in extensions
        if isinstance(extension, dict)
        and extension.get("url") == extension_urls["correlatedSymptom"]
    ]
    if len(correlated) > 7 or (status_code == "present") != bool(correlated):
        raise ProducerValidationError(
            f"{label} HealthKit ECG correlated symptoms must agree with symptomsStatus"
        )
    admitted_symptoms = {
        "HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat",
        "HKCategoryTypeIdentifierSkippedHeartbeat",
        "HKCategoryTypeIdentifierFatigue",
        "HKCategoryTypeIdentifierShortnessOfBreath",
        "HKCategoryTypeIdentifierChestTightnessOrPain",
        "HKCategoryTypeIdentifierFainting",
        "HKCategoryTypeIdentifierDizziness",
    }
    admitted_severities = {"unspecified", "notPresent", "mild", "moderate", "severe"}
    seen_symptom_identifiers: set[str] = set()
    required_symptom_children = {
        "sourceIdentifier",
        "effectivePeriod",
        "symptomType",
        "severity",
        "sourceName",
        "sourceBundleIdentifier",
        "sourceOperatingSystemMajorVersion",
        "sourceOperatingSystemMinorVersion",
        "sourceOperatingSystemPatchVersion",
    }
    optional_symptom_children = {"sourceVersion", "sourceProductType"}
    for index, symptom in enumerate(correlated):
        children = symptom.get("extension")
        if not isinstance(children, list):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] is incomplete"
            )
        by_url = {
            child.get("url"): child
            for child in children
            if isinstance(child, dict) and isinstance(child.get("url"), str)
        }
        if (
            len(by_url) != len(children)
            or not required_symptom_children <= set(by_url)
            or not set(by_url) <= required_symptom_children | optional_symptom_children
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] is incomplete"
            )
        symptom_type = by_url["symptomType"].get("valueCode")
        severity = by_url["severity"].get("valueCode")
        if symptom_type not in admitted_symptoms or severity not in admitted_severities:
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] uses an unknown code"
            )
        source_identifier = by_url["sourceIdentifier"].get("valueIdentifier")
        symptom_role = identifier_role(
            source_identifier,
            f"{label} HealthKit ECG correlated symptom[{index}] source",
        )
        _, symptom_identifier = complete_identifier(
            source_identifier,
            f"{label} HealthKit ECG correlated symptom[{index}] source",
        )
        if (
            symptom_role != "source-record"
            or HMAC_IDENTITY.fullmatch(symptom_identifier) is None
            or symptom_identifier in seen_symptom_identifiers
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] has invalid or repeated source identity"
            )
        seen_symptom_identifiers.add(symptom_identifier)
        symptom_period = by_url["effectivePeriod"].get("valuePeriod")
        if not isinstance(symptom_period, dict):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] has no exact period"
            )
        symptom_start = parse_fhir_instant(
            symptom_period.get("start"),
            f"{label} HealthKit ECG correlated symptom[{index}] start",
        )
        symptom_end = parse_fhir_instant(
            symptom_period.get("end"),
            f"{label} HealthKit ECG correlated symptom[{index}] end",
        )
        if symptom_end < symptom_start:
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] period is reversed"
            )
        for child_name in ("sourceName", "sourceBundleIdentifier"):
            value = by_url[child_name].get("valueString")
            if not isinstance(value, str) or not value:
                raise ProducerValidationError(
                    f"{label} HealthKit ECG correlated symptom[{index}] has incomplete HKSourceRevision"
                )
        for child_name in optional_symptom_children:
            if child_name in by_url:
                value = by_url[child_name].get("valueString")
                if not isinstance(value, str) or not value:
                    raise ProducerValidationError(
                        f"{label} HealthKit ECG correlated symptom[{index}] has incomplete HKSourceRevision"
                    )
        for child_name in (
            "sourceOperatingSystemMajorVersion",
            "sourceOperatingSystemMinorVersion",
            "sourceOperatingSystemPatchVersion",
        ):
            value = by_url[child_name].get("valueInteger")
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ProducerValidationError(
                    f"{label} HealthKit ECG correlated symptom[{index}] has incomplete HKSourceRevision"
                )

    count_extension = exact_extension("count")
    count = count_extension.get("valueInteger") if count_extension else None
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ProducerValidationError(
            f"{label} HealthKit ECG voltage measurement count must be positive"
        )
    components = resource.get("component")
    if not isinstance(components, list) or len(components) != 1:
        raise ProducerValidationError(f"{label} HealthKit ECG must contain exactly one lead")
    component = components[0]
    codings = component.get("code", {}).get("coding", []) if isinstance(component, dict) else []
    lead_codings = [
        coding
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == "urn:iso:std:iso:11073:10101"
        and coding.get("code") == "131329"
    ] if isinstance(codings, list) else []
    if len(lead_codings) != 1:
        raise ProducerValidationError(
            f"{label} HealthKit ECG must use the exact Lead-I-like MDC channel"
        )
    sampled = component.get("valueSampledData") if isinstance(component, dict) else None
    data = sampled.get("data") if isinstance(sampled, dict) else None
    if not isinstance(data, str) or len(re.split(r"\s+", data)) != count:
        raise ProducerValidationError(
            f"{label} HealthKit ECG voltage count does not match SampledData frames"
        )

    for name, code in (("averageHeartRate", "/min"), ("samplingFrequency", "Hz")):
        extension = exact_extension(name, required=False)
        if extension is None:
            continue
        quantity = extension.get("valueQuantity")
        value = quantity.get("value") if isinstance(quantity, dict) else None
        if (
            not isinstance(quantity, dict)
            or quantity.get("system") != "http://unitsofmeasure.org"
            or quantity.get("code") != code
            or isinstance(value, bool)
            or not isinstance(value, (int, float, Decimal))
            or Decimal(str(value)) <= 0
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG {name} must be a positive exact UCUM Quantity"
            )
        if name == "samplingFrequency":
            period = sampled.get("period") if isinstance(sampled, dict) else None
            if not isinstance(period, (int, float, Decimal)) or isinstance(period, bool):
                raise ProducerValidationError(f"{label} HealthKit ECG has no sampling period")
            if Decimal(str(period)) * Decimal(str(value)) != Decimal(1000):
                raise ProducerValidationError(
                    f"{label} HealthKit ECG sampling frequency and SampledData.period disagree"
                )
    algorithm = exact_extension("algorithmVersion", required=False)
    if algorithm is not None and algorithm.get("valueCode") not in {"version1", "version2"}:
        raise ProducerValidationError(
            f"{label} has an unknown HealthKit ECG algorithm version"
        )
    source_period_extension = exact_extension("sourcePeriod")
    source_period = (
        source_period_extension.get("valuePeriod")
        if source_period_extension is not None
        else None
    )
    effective_period = resource.get("effectivePeriod")
    if not isinstance(source_period, dict) or not isinstance(effective_period, dict):
        raise ProducerValidationError(
            f"{label} HealthKit ECG must preserve source and waveform periods"
        )
    source_start = parse_fhir_instant(source_period.get("start"), f"{label} source start")
    source_end = parse_fhir_instant(source_period.get("end"), f"{label} source end")
    waveform_start = parse_fhir_instant(
        effective_period.get("start"), f"{label} waveform start"
    )
    waveform_end = parse_fhir_instant(
        effective_period.get("end"), f"{label} waveform end"
    )
    if not source_start <= waveform_start <= waveform_end <= source_end:
        raise ProducerValidationError(
            f"{label} HealthKit ECG waveform period must lie within its exact source period"
        )


def codeable_concept_codings(value: Any, label: str) -> list[dict[str, Any]]:
    """Return a CodeableConcept's Coding objects without accepting malformed shapes."""
    if not isinstance(value, dict):
        raise ProducerValidationError(f"{label} must be a CodeableConcept")
    codings = value.get("coding")
    if not isinstance(codings, list):
        raise ProducerValidationError(f"{label}.coding must be an array")
    if any(not isinstance(coding, dict) for coding in codings):
        raise ProducerValidationError(f"{label}.coding must contain only Coding objects")
    return codings


def health_connect_context_pairs(mapping: dict[str, Any]) -> tuple[str, set[tuple[str, str]]]:
    """Resolve one catalog context mapping into its exact source-system code pairs."""
    source_system = mapping.get("sourceCodeSystem", mapping.get("codeSystem"))
    pairs: set[tuple[str, str]] = set()
    values = mapping.get("values", [])
    if isinstance(values, list):
        for item in values:
            if not isinstance(item, dict):
                continue
            coding = item.get("coding")
            if isinstance(coding, dict):
                system = coding.get("system", source_system)
                code = coding.get("code")
                if isinstance(system, str) and isinstance(code, str):
                    pairs.add((system, code))
            elif isinstance(source_system, str) and isinstance(item.get("code"), str):
                pairs.add((source_system, item["code"]))
    allowed_codes = mapping.get("allowedSourceCodes", [])
    if isinstance(source_system, str) and isinstance(allowed_codes, list):
        pairs.update(
            (source_system, code) for code in allowed_codes if isinstance(code, str)
        )
    systems = {system for system, _ in pairs}
    if len(systems) != 1:
        raise ProducerValidationError("Health Connect context catalog has no single coding system")
    return next(iter(systems)), pairs


def validate_health_connect_context_concept(
    value: Any,
    mapping: dict[str, Any],
    label: str,
) -> None:
    """Require one admitted exact-source coding while allowing other-system translations."""
    system, admitted = health_connect_context_pairs(mapping)
    codings = codeable_concept_codings(value, label)
    exact = [
        (coding.get("system"), coding.get("code"))
        for coding in codings
        if coding.get("system") == system
    ]
    if len(exact) != 1 or exact[0] not in admitted:
        raise ProducerValidationError(
            f"{label} must carry exactly one admitted {system} coding"
        )


def coding_pairs_recursive(value: Any) -> list[tuple[str, str]]:
    """Collect system/code pairs from every Coding-shaped object in a resource."""
    result: list[tuple[str, str]] = []
    if isinstance(value, dict):
        system = value.get("system")
        code = value.get("code")
        if isinstance(system, str) and isinstance(code, str):
            result.append((system, code))
        for child in value.values():
            result.extend(coding_pairs_recursive(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(coding_pairs_recursive(child))
    return result


def validate_health_connect_source_type(resource: dict[str, Any], label: str) -> None:
    """Bind one exact Health Connect Record class to its output measurement."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    adapter_prefix = (
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
    )
    if not isinstance(profiles, list) or not any(
        isinstance(profile, str) and profile.startswith(adapter_prefix)
        for profile in profiles
    ):
        return
    catalog = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    extension_url = catalog["sourceTypeExtension"]["url"]
    extensions = resource.get("extension", [])
    values = [
        extension.get("valueCode") for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == extension_url
    ] if isinstance(extensions, list) else []
    if len(values) != 1 or not isinstance(values[0], str):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded Health Connect Record type"
        )
    row = next(
        (item for item in catalog["recordTypes"] if item["token"] == values[0]),
        None,
    )
    if row is None or row["status"] != "supported":
        raise ProducerValidationError(
            f"{label} uses a Health Connect Record type without an admitted output contract"
        )
    measurement_profiles = {
        f"https://grovealliance.org/fhir/mobile/StructureDefinition/{item['profile']}": item["id"]
        for item in read_json(CATALOG_ROOT / "measurement-catalog.json")["measurements"]
    }
    measurement_profiles.update(
        {item["profile"]: item["id"] for item in catalog["adapterMeasurements"]}
    )
    claimed = {
        measurement_profiles[profile] for profile in profiles
        if profile in measurement_profiles
    }
    admitted = {output["measurement"] for output in row["outputs"]}
    if len(claimed) != 1 or not claimed <= admitted:
        raise ProducerValidationError(
            f"{label} Health Connect Record type does not admit its claimed measurement"
        )
    measurement = next(iter(claimed))

    identifiers = resource.get("identifier")
    if not isinstance(identifiers, list) or len(identifiers) not in {2, 3}:
        raise ProducerValidationError(
            f"{label} Health Connect Observation must carry exactly two or three identifiers"
        )
    roles = typed_resource_identifiers(resource, label)
    if len(roles) != len(identifiers):
        raise ProducerValidationError(
            f"{label} Health Connect Observation identifiers must all use admitted Grove roles"
        )
    required_roles = {"source-record", "source-output"}
    if not required_roles <= set(roles) or set(roles) - required_roles - {"writer-record"}:
        raise ProducerValidationError(
            f"{label} Health Connect Observation must carry source-record, source-output, "
            "and only the optional writer-record identifier"
        )

    contexts = set(row["context"])
    mappings = catalog["contextMappings"]

    body_position_url = (
        "http://hl7.org/fhir/StructureDefinition/observation-bodyPosition"
    )
    body_positions = [
        item.get("valueCodeableConcept")
        for item in extensions
        if isinstance(item, dict) and item.get("url") == body_position_url
    ] if isinstance(extensions, list) else []
    if len(body_positions) > 1:
        raise ProducerValidationError(f"{label} repeats Health Connect body position")
    if body_positions:
        if "bloodPressureBodyPosition" not in contexts:
            raise ProducerValidationError(
                f"{label} Record type does not admit Health Connect body position"
            )
        validate_health_connect_context_concept(
            body_positions[0], mappings["bloodPressureBodyPosition"],
            f"{label} body position",
        )

    body_site_contexts = [
        name for name in (
            "bloodPressureMeasurementLocation",
            "temperatureMeasurementLocation",
            "skinTemperatureMeasurementLocation",
        )
        if name in contexts
    ]
    body_site = resource.get("bodySite")
    if body_site is not None:
        if len(body_site_contexts) != 1:
            raise ProducerValidationError(
                f"{label} Record type does not admit Health Connect body site"
            )
        validate_health_connect_context_concept(
            body_site, mappings[body_site_contexts[0]], f"{label} bodySite"
        )

    notes = resource.get("note", [])
    if not isinstance(notes, list) or len(notes) > 1:
        raise ProducerValidationError(f"{label} Health Connect note must occur at most once")
    if notes:
        note_contexts = [
            name for name in contexts
            if name.endswith("Notes")
            and mappings[name].get("appliesToMeasurement") == measurement
        ]
        if len(note_contexts) != 1:
            raise ProducerValidationError(
                f"{label} output does not admit source-authored notes"
            )
        note = notes[0]
        if (
            not isinstance(note, dict)
            or not isinstance(note.get("text"), str)
            or not note["text"].strip()
            or "authorReference" in note
            or "authorString" in note
            or "time" in note
        ):
            raise ProducerValidationError(
                f"{label} source note must contain only non-blank text, without invented author or time"
            )

    for context_name, mapping in mappings.items():
        if not isinstance(mapping, dict) or mapping.get("valueType") != "string":
            continue
        context_url = mapping.get("extension")
        if not isinstance(context_url, str):
            continue
        matches = [
            item for item in extensions
            if isinstance(item, dict) and item.get("url") == context_url
        ] if isinstance(extensions, list) else []
        if len(matches) > 1:
            raise ProducerValidationError(f"{label} repeats {context_name}")
        if matches:
            if (
                context_name not in contexts
                or mapping.get("appliesToMeasurement") != measurement
                or not isinstance(matches[0].get("valueString"), str)
                or not matches[0]["valueString"].strip()
            ):
                raise ProducerValidationError(
                    f"{label} carries {context_name} outside its admitted summary output"
                )

    meal_mapping = mappings["bloodGlucoseMealContext"]
    meal_url = meal_mapping["extension"]
    meal_extensions = [
        item for item in extensions
        if isinstance(item, dict) and item.get("url") == meal_url
    ] if isinstance(extensions, list) else []
    if len(meal_extensions) > 1:
        raise ProducerValidationError(f"{label} repeats Health Connect glucose meal context")
    if meal_extensions:
        if "bloodGlucoseMealContext" not in contexts:
            raise ProducerValidationError(
                f"{label} Record type does not admit Health Connect glucose meal context"
            )
        outer = meal_extensions[0]
        nested = outer.get("extension")
        if not isinstance(nested, list) or not nested:
            raise ProducerValidationError(
                f"{label} glucose meal context must contain at least one admitted field"
            )
        nested_by_url: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(nested):
            if not isinstance(item, dict) or item.get("url") not in {
                "relationToMeal", "mealType"
            }:
                raise ProducerValidationError(
                    f"{label} glucose meal context has an unknown nested extension"
                )
            nested_url = item["url"]
            if nested_url in nested_by_url:
                raise ProducerValidationError(
                    f"{label} glucose meal context repeats {nested_url}"
                )
            nested_by_url[nested_url] = item
            mapping_name = (
                "relationToMeal" if nested_url == "relationToMeal" else "mealType"
            )
            validate_health_connect_context_concept(
                {"coding": [item.get("valueCoding")]},
                meal_mapping[mapping_name],
                f"{label} glucose meal context {mapping_name}",
            )

    mindfulness_mapping = mappings["mindfulnessSessionType"]
    mindfulness_url = mindfulness_mapping["extension"]
    mindfulness_extensions = [
        item for item in extensions
        if isinstance(item, dict) and item.get("url") == mindfulness_url
    ] if isinstance(extensions, list) else []
    mindfulness_expected = "mindfulnessSessionType" in contexts
    if len(mindfulness_extensions) != (1 if mindfulness_expected else 0):
        raise ProducerValidationError(
            f"{label} must carry mindfulness session type exactly when its Record type admits it"
        )
    if mindfulness_extensions:
        validate_health_connect_context_concept(
            {"coding": [mindfulness_extensions[0].get("valueCoding")]},
            mindfulness_mapping,
            f"{label} mindfulness session type",
        )

    vo2_mapping = mappings["vo2MaxMeasurementMethod"]
    vo2_expected = "vo2MaxMeasurementMethod" in contexts
    method = resource.get("method")
    vo2_system = vo2_mapping["codeSystem"]
    method_pairs = coding_pairs_recursive(method)
    if vo2_expected:
        validate_health_connect_context_concept(method, vo2_mapping, f"{label} VO2 method")
        if len(codeable_concept_codings(method, f"{label} VO2 method")) != 1:
            raise ProducerValidationError(
                f"{label} VO2 method must contain exactly one exact-source Coding"
            )
    elif any(system == vo2_system for system, _ in method_pairs):
        raise ProducerValidationError(
            f"{label} carries Health Connect VO2 method outside a Vo2MaxRecord"
        )

    source_coded_contexts = {
        name: mapping
        for name, mapping in mappings.items()
        if isinstance(mapping, dict)
        and isinstance(mapping.get("sourceCodeSystem"), str)
        and isinstance(mapping.get("appliesToMeasurement"), str)
    }
    resource_pairs = coding_pairs_recursive(resource)
    for name, mapping in source_coded_contexts.items():
        system, _ = health_connect_context_pairs(mapping)
        applies = name in contexts and mapping["appliesToMeasurement"] == measurement
        if not applies:
            if any(pair[0] == system for pair in resource_pairs):
                raise ProducerValidationError(
                    f"{label} carries {name} coding outside its admitted output"
                )
            continue
        if name == "cervicalMucusSensation":
            components = resource.get("component", [])
            sensation_components = [
                component for component in components
                if isinstance(component, dict)
                and (
                    "https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement",
                    "cervical-mucus-sensation",
                ) in coding_pairs_recursive(component.get("code"))
            ] if isinstance(components, list) else []
            if len(sensation_components) > 1:
                raise ProducerValidationError(
                    f"{label} repeats the cervical-mucus sensation component"
                )
            if sensation_components:
                validate_health_connect_context_concept(
                    sensation_components[0].get("valueCodeableConcept"), mapping,
                    f"{label} cervical-mucus sensation",
                )
                if sum(pair[0] == system for pair in resource_pairs) != 1:
                    raise ProducerValidationError(
                        f"{label} must carry its one exact cervical-mucus sensation "
                        "coding only in the named component"
                    )
            elif any(pair[0] == system for pair in resource_pairs):
                raise ProducerValidationError(
                    f"{label} carries cervical-mucus sensation outside its named component"
                )
            continue
        validate_health_connect_context_concept(
            resource.get("valueCodeableConcept"), mapping, f"{label} {name}"
        )
        if sum(pair[0] == system for pair in resource_pairs) != 1:
            raise ProducerValidationError(
                f"{label} must carry exactly one {name} source coding in its value"
            )


def validate_provider_claim(resource: dict[str, Any], label: str) -> None:
    """Require the exact source-neutral plus adapter pair on connected raw data."""
    if resource.get("resourceType") != "DocumentReference":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claim = read_json(CATALOG_ROOT / "profile-claims.json")[
        "providerRecordingDocumentClaim"
    ]
    if claim["profiles"][1] not in profiles:
        return
    if len(profiles) != claim["cardinality"] or set(profiles) != set(claim["profiles"]):
        raise ProducerValidationError(
            f"{label} Provider Recording Document must directly claim exactly "
            "the source-neutral and connected adapter profiles"
        )


def validate_adapter_conversion_provenance(
    resource: dict[str, Any], label: str
) -> None:
    """Require the exact adapter source entity on conversion Provenance resources."""
    if resource.get("resourceType") != "Provenance":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(
        not isinstance(profile, str) for profile in profiles
    ):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "adapterConversionProvenanceClaims"
    ]
    matches = [claim for claim in claims if claim["profile"] in profiles]
    if not matches:
        return
    if len(matches) != 1 or profiles != [matches[0]["profile"]]:
        raise ProducerValidationError(
            f"{label} adapter conversion Provenance must directly claim exactly "
            "its adapter-specific Provenance profile"
        )
    claim = matches[0]
    targets = resource.get("target")
    if not isinstance(targets, list) or not targets:
        raise ProducerValidationError(f"{label} must contain conversion targets")
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or not isinstance(target.get("reference"), str):
            raise ProducerValidationError(
                f"{label}.target[{index}] must contain an exact reference"
            )
    entities = resource.get("entity")
    if not isinstance(entities, list) or len(entities) != 1:
        raise ProducerValidationError(
            f"{label} must carry exactly one source entity"
        )
    entity = entities[0]
    what = entity.get("what") if isinstance(entity, dict) else None
    if (
        not isinstance(entity, dict)
        or entity.get("role") != "source"
        or not isinstance(what, dict)
        or "reference" in what
    ):
        raise ProducerValidationError(
            f"{label} must carry its source as exactly one Identifier entity"
        )
    identifier = what.get("identifier")
    _, value = complete_identifier(identifier, f"{label} source entity")
    if identifier_role(identifier, f"{label} source entity") != "source-record":
        raise ProducerValidationError(
            f"{label} source entity must carry the source-record role"
        )
    if HMAC_IDENTITY.fullmatch(value) is None:
        raise ProducerValidationError(
            f"{label} source entity must use a canonical Grove v2 HMAC identity"
        )
    if claim["adapter"] == "health-connect":
        agents = entity.get("agent")
        if not isinstance(agents, list) or len(agents) != 1:
            raise ProducerValidationError(
                f"{label} Health Connect source entity must carry exactly one enterer agent"
            )
        agent = agents[0]
        who = agent.get("who") if isinstance(agent, dict) else None
        enterer_codings = [
            code
            for system, code in coding_pairs_recursive(agent.get("type"))
            if system
            == "http://terminology.hl7.org/CodeSystem/provenance-participant-type"
        ] if isinstance(agent, dict) else []
        if (
            not isinstance(agent, dict)
            or not isinstance(who, dict)
            or enterer_codings != ["enterer"]
            or "reference" in who
            or "resource" in who
            or who.get("type") != "Device"
        ):
            raise ProducerValidationError(
                f"{label} Health Connect DataOrigin must be an identifier-only Device Reference"
            )
        system, package_name = complete_identifier(
            who.get("identifier"), f"{label} Health Connect DataOrigin"
        )
        if (
            system
            != "https://grovealliance.org/fhir/health-connect/NamingSystem/android-package-name"
            or not package_name.strip()
        ):
            raise ProducerValidationError(
                f"{label} Health Connect DataOrigin must carry its non-blank Android package name"
            )


# Every connected-provider guide narrows the same adapter Observation, so an output of any of
# them carries the shared provider lineage and source/output business identity checked below.
PROVIDER_IDENTITY_PROFILES = {
    "https://grovealliance.org/fhir/providers/StructureDefinition/providers-observation",
    "https://grovealliance.org/fhir/providers/StructureDefinition/providers-recording-document",
    "https://grovealliance.org/fhir/withings/StructureDefinition/withings-observation",
    "https://grovealliance.org/fhir/oura/StructureDefinition/oura-observation",
    "https://grovealliance.org/fhir/google-health/StructureDefinition/google-health-observation",
}


def validate_provider_identity(resource: dict[str, Any], label: str) -> None:
    """Validate provider lineage and deterministic source/output business identity."""
    if resource.get("resourceType") not in {"Observation", "DocumentReference"}:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    if not set(profiles) & PROVIDER_IDENTITY_PROFILES:
        return
    catalog = read_json(CATALOG_ROOT / "providers-adapter.json")
    typed = typed_resource_identifiers(resource, label)
    if "source-record" not in typed or "source-output" not in typed:
        raise ProducerValidationError(
            f"{label} must carry typed source-record and source-output identifiers"
        )
    business_values = {typed["source-record"][1], typed["source-output"][1]}
    if resource.get("id") in business_values:
        raise ProducerValidationError(
            f"{label} must not copy a Provider business identifier into Resource.id"
        )
    provider_url = (
        "https://grovealliance.org/fhir/providers/StructureDefinition/"
        "provider"
    )
    extensions = resource.get("extension", [])
    providers = [
        item.get("valueCode") for item in extensions
        if isinstance(item, dict) and item.get("url") == provider_url
    ] if isinstance(extensions, list) else []
    admitted_providers = {item["id"] for item in catalog["providers"]}
    if len(providers) != 1 or providers[0] not in admitted_providers:
        raise ProducerValidationError(
            f"{label} must carry exactly one admitted Provider provider"
        )
    source_type_url = catalog["sourceTypeExtension"]["url"]
    source_types = [
        item.get("valueCode") for item in extensions
        if isinstance(item, dict) and item.get("url") == source_type_url
    ] if isinstance(extensions, list) else []
    if len(source_types) != 1 or not isinstance(source_types[0], str):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded Provider source type"
        )
    provider = next(item for item in catalog["providers"] if item["id"] == providers[0])
    ordinary = {
        f"{provider['id']}/{item['token']}": item
        for item in provider["sourceTypes"]
    }
    grouped = {
        f"{provider['id']}/{item['token']}": item
        for item in provider.get("groupedMappings", [])
    }
    source_row = ordinary.get(source_types[0])
    grouped_row = grouped.get(source_types[0])
    if source_row is None and grouped_row is None:
        raise ProducerValidationError(
            f"{label} uses an unknown or cross-provider Provider source type"
        )
    if resource["resourceType"] == "DocumentReference":
        if source_row is None or "raw" not in source_row:
            raise ProducerValidationError(
                f"{label} source type does not admit a native Recording Document"
            )
    else:
        measurement_profiles = {
            f"https://grovealliance.org/fhir/mobile/StructureDefinition/{item['profile']}": item["id"]
            for item in read_json(CATALOG_ROOT / "measurement-catalog.json")["measurements"]
        }
        claimed = [measurement_profiles[item] for item in profiles if item in measurement_profiles]
        if len(claimed) != 1:
            raise ProducerValidationError(
                f"{label} Provider Observation has no exact shared measurement"
            )
        if grouped_row is not None:
            admitted_measurements = set(grouped_row["measurementIds"])
        else:
            admitted_measurements = {
                measurement
                for element in source_row["elements"]
                if element["status"] == "supported"
                for measurement in element.get("measurementIds", [])
            }
        if claimed[0] not in admitted_measurements:
            raise ProducerValidationError(
                f"{label} Provider source type does not admit its claimed measurement"
            )


def validate_sensorkit_identity(resource: dict[str, Any], label: str) -> None:
    """Bind SensorKit source type, source identity, output identity, and status row."""
    if resource.get("resourceType") not in {"Observation", "DocumentReference"}:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    sensorkit_profile_prefix = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
    )
    if not any(
        isinstance(profile, str) and profile.startswith(sensorkit_profile_prefix)
        for profile in profiles
    ):
        return

    catalog = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    typed = typed_resource_identifiers(resource, label)
    if "source-record" not in typed or "source-output" not in typed:
        raise ProducerValidationError(
            f"{label} must carry typed source-record and source-output identifiers"
        )
    source_pair = typed["source-record"]
    output_pair = typed["source-output"]
    if resource.get("id") in {source_pair[1], output_pair[1]}:
        raise ProducerValidationError(
            f"{label} must not copy a SensorKit business identifier into Resource.id"
        )

    source_type_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type"
    )
    extensions = resource.get("extension", [])
    source_types = [
        extension.get("valueCode")
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == source_type_url
    ] if isinstance(extensions, list) else []
    if len(source_types) != 1 or not isinstance(source_types[0], str):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded SensorKit source type"
        )
    rows = {
        row["sourceTypeCode"]: row for row in catalog["entries"]
    }
    row = rows.get(source_types[0])
    if row is None:
        raise ProducerValidationError(f"{label} uses an unknown SensorKit source type")

    if resource["resourceType"] == "DocumentReference":
        representation = row.get("raw")
    else:
        representation = row.get("structured")
        if not isinstance(representation, dict) or "outputDiscriminator" not in representation:
            raise ProducerValidationError(
                f"{label} source type has no admitted structured SensorKit output"
            )
        expected_profile = representation.get("profile")
        if expected_profile is not None and profiles != [expected_profile]:
            raise ProducerValidationError(
                f"{label} must directly claim its exact SensorKit-only profile"
            )
    if not isinstance(representation, dict):
        raise ProducerValidationError(
            f"{label} source type has no admitted SensorKit representation"
        )
    discriminator = representation.get("outputDiscriminator")
    if not isinstance(discriminator, str) or not discriminator:
        raise ProducerValidationError(
            f"{label} admitted SensorKit representation has no output discriminator"
        )


def validate_sensorkit_ecg_contract(resource: dict[str, Any], label: str) -> None:
    """Validate the exact structured portion of the mandatory SensorKit ECG hybrid."""
    if resource.get("resourceType") != "Observation":
        return
    profile = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-ecg-observation"
    )
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or profile not in profiles:
        return
    guidance_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-ecg-session-guidance"
    )
    extensions = resource.get("extension", [])
    guidance = [
        extension.get("valueCode")
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == guidance_url
    ] if isinstance(extensions, list) else []
    if len(guidance) != 1 or guidance[0] not in {"guided", "unguided"}:
        raise ProducerValidationError(
            f"{label} must carry exactly one coded SensorKit ECG session guidance"
        )
    components = resource.get("component")
    if not isinstance(components, list) or len(components) != 1:
        raise ProducerValidationError(f"{label} SensorKit ECG must contain exactly one lead")
    codings = components[0].get("code", {}).get("coding", [])
    source_leads = [
        coding.get("code")
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system")
        == "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-ecg-lead"
    ] if isinstance(codings, list) else []
    if len(source_leads) != 1 or source_leads[0] not in {
        "rightArmMinusLeftArm",
        "leftArmMinusRightArm",
    }:
        raise ProducerValidationError(
            f"{label} must carry exactly one exact SensorKit ECG lead orientation"
        )
    lead_i = [
        coding
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == "urn:iso:std:iso:11073:10101"
        and coding.get("code") == "131329"
    ]
    if (source_leads[0] == "leftArmMinusRightArm" and len(lead_i) != 1) or (
        source_leads[0] == "rightArmMinusLeftArm" and lead_i
    ):
        raise ProducerValidationError(
            f"{label} SensorKit ECG source orientation and standard Lead-I coding disagree"
        )


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


def validate_sensor_contract(resource: dict[str, Any], label: str) -> None:
    """Validate source-neutral Sensor payload rules not expressible in R4 FHIRPath."""
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    if SENSOR_SAMPLED_PROFILE in profiles:
        validate_sampled_data(
            resource.get("valueSampledData"), resource.get("effectivePeriod"), label
        )
    if SENSOR_ECG_PROFILE in profiles:
        components = resource.get("component")
        if not isinstance(components, list) or not components:
            raise ProducerValidationError(f"{label} ECG must contain sampled-data components")
        for index, component in enumerate(components):
            sampled = component.get("valueSampledData") if isinstance(component, dict) else None
            validate_sampled_data(
                sampled, resource.get("effectivePeriod"), f"{label}.component[{index}]"
            )
    is_recording_document = (
        resource.get("resourceType") == "DocumentReference"
        and any(profile.endswith(RECORDING_DOCUMENT_PROFILE_TAIL) for profile in profiles)
    )
    if is_recording_document:
        contents = resource.get("content")
        if not isinstance(contents, list) or len(contents) != 1:
            raise ProducerValidationError(
                f"{label} Recording Document must contain exactly one content entry"
            )
        identities = typed_resource_identifiers(resource, label)
        required = {"source-record", "source-output", "source-artifact"}
        present = set(identities)
        missing = required - present
        unexpected = present - required - {"writer-record"}
        if missing or unexpected:
            raise ProducerValidationError(
                f"{label} Recording Document must carry source-record, source-output, "
                "and source-artifact; only writer-record is an additional typed Grove role "
                f"(missing={sorted(missing)}, unexpected={sorted(unexpected)})"
            )
        for index, content in enumerate(contents):
            attachment = content.get("attachment") if isinstance(content, dict) else None
            validate_recording_attachment(attachment, f"{label}.content[{index}].attachment")

def validate_recording_format(resource: dict[str, Any], label: str) -> None:
    """Require one registered payload format per recording content entry."""
    if resource.get("resourceType") != "DocumentReference":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or not any(
        isinstance(profile, str) and profile.endswith(RECORDING_DOCUMENT_PROFILE_TAIL)
        for profile in profiles
    ):
        return
    registry = read_json(CATALOG_ROOT / "format-registry.json")
    formats = registry["formats"]
    contents = resource.get("content", [])
    if not isinstance(contents, list) or not contents:
        raise ProducerValidationError(f"{label} recording document has no content")
    declared_codes: list[str] = []
    for index, content in enumerate(contents):
        format_coding = content.get("format") if isinstance(content, dict) else None
        if not isinstance(format_coding, dict):
            raise ProducerValidationError(
                f"{label} content[{index}] declares no registry payload format"
            )
        if format_coding.get("system") != registry["codeSystem"]:
            raise ProducerValidationError(
                f"{label} content[{index}] format system is not the Grove "
                "recording-format registry"
            )
        code = format_coding.get("code")
        entry = formats.get(code) if isinstance(code, str) else None
        if entry is None:
            raise ProducerValidationError(
                f"{label} content[{index}] declares unregistered format {code!r}"
            )
        # The code names the schema and never carries a version; the release travels in
        # Coding.version, so a payload always states which registry generation defined it.
        declared_version = format_coding.get("version")
        # A stored document records the generation it was written under; requiring it to equal
        # the current one would invalidate every archive the moment the registry is republished,
        # which is the opposite of this guide's byte-preservation posture. A generation that
        # never defined this code is still rejected.
        if declared_version not in REGISTRY_GENERATIONS.get(code, ()):
            raise ProducerValidationError(
                f"{label} content[{index}] format version {declared_version!r} is not a "
                f"registry generation that defines {code}"
            )
        content_type = content.get("attachment", {}).get("contentType")
        if content_type != entry["contentType"]:
            raise ProducerValidationError(
                f"{label} content[{index}] contentType {content_type!r} does not "
                f"match registry format {code} ({entry['contentType']})"
            )
        declared_codes.append(code)

    sensorkit = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    extension_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-source-type"
    )
    source_codes = [
        extension.get("valueCode")
        for extension in resource.get("extension", [])
        if isinstance(extension, dict) and extension.get("url") == extension_url
    ]
    if len(source_codes) == 1 and isinstance(source_codes[0], str):
        rows = {entry["sourceTypeCode"]: entry for entry in sensorkit["entries"]}
        row = rows.get(source_codes[0])
        admitted = (row or {}).get("raw", {}).get("formats")
        if isinstance(admitted, list):
            for code in declared_codes:
                if code not in admitted:
                    raise ProducerValidationError(
                        f"{label} declares format {code!r}, which the SensorKit "
                        f"stream {source_codes[0]!r} does not admit"
                    )


def validate_resource_profile_claims(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    validate_active_adapter_package_claims(resource, label, active_adapter_profiles)
    validate_adapter_profile_claim(resource, label, active_adapter_profiles)
    validate_adapter_source_marker_claim(resource, label)
    validate_health_connect_specimen_claim(resource, label)
    validate_health_connect_provider_claim(resource, label)
    validate_healthkit_resource_claims(resource, label)
    validate_healthkit_source_type(resource, label)
    validate_healthkit_ecg_contract(resource, label)
    validate_health_connect_source_type(resource, label)
    validate_provider_claim(resource, label)
    validate_adapter_conversion_provenance(resource, label)
    validate_provider_identity(resource, label)
    validate_sensorkit_profile_claim(resource, label)
    validate_sensorkit_identity(resource, label)
    validate_sensorkit_ecg_contract(resource, label)
    validate_sensor_contract(resource, label)
    validate_recording_format(resource, label)


def validate_adapter_provenance_graph(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Bind every adapter output for one source record to one internal Provenance."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "adapterConversionProvenanceClaims"
    ]

    def source_value(resource: dict[str, Any], role: str) -> tuple[str, str]:
        identity = typed_resource_identifiers(resource, f"{label} {role}").get(
            "source-record"
        )
        if identity is None:
            raise ProducerValidationError(
                f"{label} {role} must carry exactly one typed source-record Identifier"
            )
        return identity

    url_by_resource = {id(resource): url for url, resource in resources_by_full_url.items()}
    for claim in claims:
        target_profiles = set(claim["targetAdapterProfiles"])
        outputs_by_source: dict[tuple[str, str], set[str]] = {}
        provenances_by_source: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for resource in entry_resources:
            profiles = resource.get("meta", {}).get("profile", [])
            profile_set = set(profiles) if isinstance(profiles, list) else set()
            if profile_set & target_profiles:
                source = source_value(resource, "output")
                outputs_by_source.setdefault(source, set()).add(url_by_resource[id(resource)])
            if claim["profile"] in profile_set:
                entity = resource["entity"][0]["what"]["identifier"]
                if identifier_role(entity, f"{label} Provenance source entity") != "source-record":
                    raise ProducerValidationError(
                        f"{label} Provenance source entity must carry the source-record role"
                    )
                source = complete_identifier(entity, f"{label} Provenance source entity")
                if HMAC_IDENTITY.fullmatch(source[1]) is None:
                    raise ProducerValidationError(
                        f"{label} Provenance source entity must be a canonical v2 HMAC identity"
                    )
                provenances_by_source.setdefault(source, []).append(resource)

        for source, output_urls in outputs_by_source.items():
            provenances = provenances_by_source.get(source, [])
            if len(provenances) != 1:
                raise ProducerValidationError(
                    f"{label} {claim['adapter']} source record must have exactly one "
                    "conversion Provenance in the same Bundle"
                )
            provenance = provenances[0]
            target_urls = [target["reference"] for target in provenance["target"]]
            if any(not url.startswith("urn:uuid:") for url in target_urls):
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance targets must be internal UUID references"
                )
            if len(target_urls) != len(set(target_urls)):
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance repeats a target"
                )
            for target_url in target_urls:
                target = resources_by_full_url.get(target_url)
                if target is None:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance has an unresolved target"
                    )
                target_profile_set = set(target.get("meta", {}).get("profile", []))
                if not target_profile_set & target_profiles:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance targets a resource "
                        "outside its adapter output contract"
                    )
                if source_value(target, "target") != source:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance source entity and target "
                        "must carry the same source-record Identifier"
                    )
            if set(target_urls) != output_urls:
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance must target every structured "
                    "and raw output for its source record"
                )
        extra_sources = set(provenances_by_source) - set(outputs_by_source)
        if extra_sources:
            raise ProducerValidationError(
                f"{label} adapter conversion Provenance has no output for its source record"
            )


def validate_health_connect_output_graph(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Enforce Health Connect cardinalities visible in one active exchange event."""
    catalog = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    observation_profile = (
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
        "health-connect-observation"
    )
    specimen_profile = (
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
        "health-connect-specimen"
    )
    record_type_url = catalog["sourceTypeExtension"]["url"]
    measurement_profiles = {
        f"https://grovealliance.org/fhir/mobile/StructureDefinition/{item['profile']}": item["id"]
        for item in read_json(CATALOG_ROOT / "measurement-catalog.json")["measurements"]
    }
    measurement_profiles.update(
        {item["profile"]: item["id"] for item in catalog["adapterMeasurements"]}
    )
    health_connect_observation_profiles = {
        observation_profile,
        *{item["profile"] for item in catalog["adapterMeasurements"]},
    }
    row_by_type = {row["token"]: row for row in catalog["recordTypes"]}
    url_by_resource = {id(resource): url for url, resource in resources_by_full_url.items()}
    observations: dict[tuple[str, str], list[tuple[str, str, dict[str, Any]]]] = {}
    specimens: dict[tuple[str, str], list[tuple[str, dict[str, Any]]]] = {}
    record_types_by_source: dict[tuple[str, str], set[str]] = {}

    for resource in entry_resources:
        profiles = resource.get("meta", {}).get("profile", [])
        profile_set = set(profiles) if isinstance(profiles, list) else set()
        if profile_set & health_connect_observation_profiles:
            source = typed_resource_identifiers(resource, f"{label} Health Connect output").get(
                "source-record"
            )
            if source is None:
                raise ProducerValidationError(
                    f"{label} Health Connect output has no source-record identity"
                )
            extensions = resource.get("extension", [])
            record_types = [
                extension.get("valueCode")
                for extension in extensions
                if isinstance(extension, dict) and extension.get("url") == record_type_url
            ] if isinstance(extensions, list) else []
            if len(record_types) != 1 or not isinstance(record_types[0], str):
                raise ProducerValidationError(
                    f"{label} Health Connect output has no unique Record type"
                )
            record_type = record_types[0]
            record_types_by_source.setdefault(source, set()).add(record_type)
            measurements = {
                measurement_profiles[profile]
                for profile in profile_set if profile in measurement_profiles
            }
            if len(measurements) != 1:
                raise ProducerValidationError(
                    f"{label} Health Connect output has no unique measurement claim"
                )
            observations.setdefault(source, []).append(
                (record_type, next(iter(measurements)), resource)
            )
        if specimen_profile in profile_set:
            source = typed_resource_identifiers(resource, f"{label} Health Connect specimen").get(
                "source-record"
            )
            if source is None:
                raise ProducerValidationError(
                    f"{label} Health Connect specimen has no source-record identity"
                )
            specimens.setdefault(source, []).append((url_by_resource[id(resource)], resource))

    for source, record_types in record_types_by_source.items():
        if len(record_types) != 1:
            raise ProducerValidationError(
                f"{label} one Health Connect source-record identity cannot name multiple Record types"
            )
        record_type = next(iter(record_types))
        row = row_by_type[record_type]
        measurement_counts: dict[str, int] = {}
        for _, measurement, _ in observations[source]:
            measurement_counts[measurement] = measurement_counts.get(measurement, 0) + 1
        for output in row["outputs"]:
            if output["countRule"] == "exactly-one" and measurement_counts.get(
                output["measurement"], 0
            ) != 1:
                raise ProducerValidationError(
                    f"{label} {record_type} must emit exactly one {output['measurement']} output"
                )

        source_specimens = specimens.get(source, [])
        if record_type != "BloodGlucoseRecord":
            if source_specimens:
                raise ProducerValidationError(
                    f"{label} only a BloodGlucoseRecord may synthesize a Health Connect Specimen"
                )
            continue
        if len(observations[source]) != 1 or len(source_specimens) != 1:
            raise ProducerValidationError(
                f"{label} BloodGlucoseRecord must emit exactly one Observation and one Specimen"
            )
        _, measurement, observation = observations[source][0]
        specimen_url, specimen = source_specimens[0]
        specimen_reference = observation.get("specimen", {}).get("reference")
        if specimen_reference != specimen_url:
            raise ProducerValidationError(
                f"{label} BloodGlucoseRecord Observation must reference its one synthesized Specimen"
            )
        observation_subject = observation.get("subject", {}).get("reference")
        specimen_subject = specimen.get("subject", {}).get("reference")
        if (
            not isinstance(observation_subject, str)
            or specimen_subject != observation_subject
        ):
            raise ProducerValidationError(
                f"{label} BloodGlucoseRecord Observation and Specimen must reference the same Patient"
            )
        snomed_codes = {
            code
            for system, code in coding_pairs_recursive(specimen.get("type"))
            if system == "http://snomed.info/sct"
        }
        expected_measurements = {
            "258580003": "blood-glucose",
            "122554006": "capillary-blood-glucose",
            "119361006": "serum-plasma-glucose",
            "119364003": "serum-plasma-glucose",
            "258479004": "interstitial-glucose",
        }
        expected = {
            expected_measurements[code]
            for code in snomed_codes if code in expected_measurements
        }
        if expected != {measurement}:
            raise ProducerValidationError(
                f"{label} BloodGlucoseRecord measurement profile and Specimen type disagree"
            )

    extra_specimen_sources = set(specimens) - set(observations)
    if extra_specimen_sources:
        raise ProducerValidationError(
            f"{label} Health Connect Specimen has no Observation for its source record"
        )


def exact_source_entity(
    provenance: dict[str, Any],
    label: str,
) -> tuple[str, str]:
    """Return the sole logical source-record identity of a lifecycle Provenance."""
    entities = provenance.get("entity")
    if not isinstance(entities, list) or len(entities) != 1:
        raise contract_failure(
            "mobile-exchange.single-source-entity",
            "Provenance.entity",
            f"{label} must identify exactly one source record",
        )
    entity = entities[0]
    what = entity.get("what") if isinstance(entity, dict) else None
    if (
        not isinstance(entity, dict)
        or entity.get("role") != "source"
        or not isinstance(what, dict)
        or "reference" in what
        or "resource" in what
    ):
        raise contract_failure(
            "mobile-exchange.logical-source-entity",
            "Provenance.entity[0].what",
            f"{label} source must be exactly one logical Identifier entity with role source",
        )
    identifier = what.get("identifier")
    if identifier_role(identifier, f"{label} source identifier") != "source-record":
        raise ProducerValidationError(
            f"{label} source must carry the source-record role"
        )
    pair = complete_identifier(identifier, f"{label} source identifier")
    if HMAC_IDENTITY.fullmatch(pair[1]) is None:
        raise ProducerValidationError(
            f"{label} source identifier is not a canonical Grove v2 HMAC identity"
        )
    return pair


def validate_exchange_bundle(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    profiles = resource.get("meta", {}).get("profile", [])
    is_active = EXCHANGE_BUNDLE_PROFILE in profiles
    is_retraction = RETRACTION_BUNDLE_PROFILE in profiles
    if not is_active and not is_retraction:
        return
    if is_active and is_retraction:
        raise ProducerValidationError(
            f"{label} cannot claim both active and retraction exchange profiles"
        )
    if resource.get("type") != "collection":
        raise ProducerValidationError(f"{label} exchange Bundle must have type collection")
    event_system, event_value = complete_identifier(
        resource.get("identifier"), f"{label} Bundle.identifier"
    )
    if identifier_role(resource["identifier"], f"{label} Bundle.identifier") != "event":
        raise ProducerValidationError(
            f"{label} Bundle.identifier must carry the event role"
        )
    if EVENT_IDENTITY.fullmatch(event_value) is None:
        raise contract_failure(
            "mobile-exchange.event-identity",
            "Bundle.identifier.value",
            f"{label} Bundle.identifier is not a canonical Grove v2 event identity",
        )
    entries = resource.get("entry")
    if not isinstance(entries, list) or not entries:
        raise ProducerValidationError(f"{label} exchange Bundle must contain entries")
    full_urls: set[str] = set()
    entry_resources: list[dict[str, Any]] = []
    entry_identities: list[tuple[str, str, dict[str, Any]]] = []
    resources_by_full_url: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
            raise ProducerValidationError(f"{label} entry[{index}] must contain a resource")
        entry_resource = entry["resource"]
        resource_type = entry_resource.get("resourceType")
        admitted_types = (
            ACTIVE_ENTRY_RESOURCE_TYPES if is_active else frozenset({"Provenance", "Device"})
        )
        if resource_type not in admitted_types:
            if is_retraction:
                raise contract_failure(
                    "mobile-retraction.no-clinical-copy",
                    f"Bundle.entry[{index}].resource",
                    f"{label} entry[{index}] resource type {resource_type!r} is not "
                    "admitted by the retraction event profile",
                )
            raise contract_failure(
                "mobile-exchange.entry-resource-type",
                f"Bundle.entry[{index}].resource.resourceType",
                f"{label} entry[{index}] resource type {resource_type!r} is not admitted "
                "by the active exchange event profile",
            )
        if "contained" in entry_resource:
            raise contract_failure(
                "mobile-exchange.contained-resource-prohibited",
                f"Bundle.entry[{index}].resource.contained",
                f"{label} entry[{index}] contains a Resource; Mobile event graphs require "
                "addressable Bundle entries",
            )
        if is_active and resource_type in ACTIVE_OUTPUT_RESOURCE_TYPES:
            output_identifiers = typed_resource_identifiers(
                entry_resource, f"{label} entry[{index}].resource"
            )
            if not {"source-record", "source-output"} <= set(output_identifiers):
                raise contract_failure(
                    "mobile-output.source-output-required",
                    f"Bundle.entry[{index}].resource.identifier",
                    f"{label} entry[{index}] active output must carry typed source-record "
                    "and source-output identities",
                )
        extensions = entry.get("extension", [])
        identities = [
            extension.get("valueIdentifier")
            for extension in extensions
            if isinstance(extension, dict) and extension.get("url") == ENTRY_IDENTIFIER_EXTENSION
        ] if isinstance(extensions, list) else []
        if len(identities) != 1:
            raise contract_failure(
                "mobile-exchange.entry-node-key",
                f"Bundle.entry[{index}]",
                f"{label} entry[{index}] must have one entry node key",
            )
        system, value = complete_identifier(identities[0], f"{label} entry[{index}] identity")
        role = identifier_role(identities[0], f"{label} entry[{index}] identity")
        selected = selected_entry_identifier(
            entry_resource, f"{label} entry[{index}].resource"
        )
        if selected is None:
            if role != "entry-node" or ENTRY_NODE_IDENTITY.fullmatch(value) is None:
                raise ProducerValidationError(
                    f"{label} entry[{index}] resource without typed business identity "
                    "must use a canonical entry-node key"
                )
            match = ENTRY_NODE_IDENTITY.fullmatch(value)
            assert match is not None
            try:
                expected_node = entry_node_identity(
                    event_system=event_system,
                    event_value=event_value,
                    role=match.group("role"),
                    ordinal=match.group("ordinal"),
                )
            except ValueError as error:
                raise ProducerValidationError(str(error)) from error
            if value != expected_node:
                raise contract_failure(
                    "mobile-exchange.entry-node-digest",
                    f"Bundle.entry[{index}].extension.valueIdentifier.value",
                    f"{label} entry[{index}] entry-node digest does not match its event, "
                    "role, and ordinal",
                )
        else:
            selected_role, selected_pair = selected
            if role != selected_role or (system, value) != selected_pair:
                raise ProducerValidationError(
                    f"{label} entry[{index}] node key is not the resource's highest-priority typed identifier"
                )
        expected = expected_entry_full_url(system, value)
        if entry.get("fullUrl") != expected:
            raise contract_failure(
                "mobile-exchange.deterministic-full-url",
                f"Bundle.entry[{index}].fullUrl",
                f"{label} entry[{index}] fullUrl is not the deterministic UUID URN",
            )
        if expected in full_urls:
            raise ProducerValidationError(f"{label} repeats entry fullUrl {expected}")
        full_urls.add(expected)
        validate_resource_profile_claims(
            entry_resource,
            f"{label} entry[{index}].resource",
            active_adapter_profiles,
        )
        if is_active:
            validate_active_observation_profile_claim(
                entry_resource,
                f"{label} entry[{index}].resource",
                active_adapter_profiles,
            )
            validate_active_adapter_only_output_profile_claim(
                entry_resource,
                f"{label} entry[{index}].resource",
            )
            validate_active_document_reference_profile_claim(
                entry_resource,
                f"{label} entry[{index}].resource",
            )
            validate_active_provenance_profile_claim(
                entry_resource,
                f"{label} entry[{index}].resource",
            )
            validate_active_measurement_fixed_semantics(
                entry_resource,
                f"{label} entry[{index}].resource",
            )
        else:
            validate_retraction_provenance_profile_claim(
                entry_resource,
                f"{label} entry[{index}].resource",
            )
        validate_exchange_supporting_profile_claim(
            entry_resource,
            f"{label} entry[{index}].resource",
        )
        entry_resources.append(entry_resource)
        entry_identities.append((system, value, entry_resource))
        resources_by_full_url[expected] = entry_resource

    if is_retraction:
        for candidate in entry_resources:
            if candidate.get("resourceType") != "Provenance":
                continue
            targets = candidate.get("target", [])
            if not isinstance(targets, list):
                continue
            for target_index, target in enumerate(targets):
                if isinstance(target, dict) and "reference" in target:
                    raise contract_failure(
                        "mobile-retraction.logical-target",
                        f"Provenance.target[{target_index}]",
                        f"{label} retraction target[{target_index}] must be a typed logical "
                        "Reference without a literal reference",
                    )
    for index, entry_resource in enumerate(entry_resources):
        for reference_path, reference in all_reference_nodes_with_paths(entry_resource):
            literal = reference["reference"]
            if literal not in full_urls:
                raise contract_failure(
                    "mobile-exchange.resolved-reference",
                    f"Bundle.entry[{index}].resource.{reference_path}.reference",
                    f"{label} entry[{index}] reference must resolve to an entry UUID URN: "
                    f"{literal}",
                )
            reference_target(
                reference,
                resources_by_full_url,
                f"{entry_resource.get('resourceType')}.{reference_path}",
            )
        validate_reference_policy(
            entry_resource,
            resources_by_full_url,
            f"{label} entry[{index}].resource",
        )

    if is_active and ACTIVE_ENTRY_POLICY["supportingResourcesMustBeConnected"]:
        full_url_by_resource = {
            id(candidate): full_url
            for full_url, candidate in resources_by_full_url.items()
        }
        adjacency = {full_url: set() for full_url in resources_by_full_url}
        for candidate in entry_resources:
            source_url = full_url_by_resource[id(candidate)]
            for reference in all_reference_nodes(candidate):
                target_url = reference.get("reference")
                if target_url in resources_by_full_url:
                    adjacency[source_url].add(target_url)
                    adjacency[target_url].add(source_url)
        reachable = {
            full_url
            for full_url, candidate in resources_by_full_url.items()
            if candidate.get("resourceType") in ACTIVE_OUTPUT_RESOURCE_TYPES
            or candidate.get("resourceType") == ACTIVE_ENTRY_POLICY["lifecycleResourceType"]
        }
        pending = list(reachable)
        while pending:
            current = pending.pop()
            for connected in adjacency[current] - reachable:
                reachable.add(connected)
                pending.append(connected)
        disconnected = [
            full_url
            for full_url, candidate in resources_by_full_url.items()
            if candidate.get("resourceType") in ACTIVE_SUPPORTING_RESOURCE_TYPES
            and full_url not in reachable
        ]
        if disconnected:
            raise contract_failure(
                "mobile-support.connected",
                "Bundle.entry",
                f"{label} supporting resources are disconnected from every output and "
                f"lifecycle assertion: {', '.join(sorted(disconnected))}",
            )

    provenances = [
        candidate for candidate in entry_resources
        if candidate.get("resourceType") == "Provenance"
    ]
    transform_provenances: list[dict[str, object]] = []
    retraction_provenances: list[dict[str, object]] = []
    iso_lifecycle_system = (
        "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle"
    )
    for provenance_index, candidate in enumerate(provenances):
        activity = candidate.get("activity", {})
        codings = activity.get("coding", []) if isinstance(activity, dict) else []
        codings = codings if isinstance(codings, list) else []
        iso_codings = [
            coding for coding in codings
            if isinstance(coding, dict)
            and coding.get("system") == iso_lifecycle_system
        ]
        grove_codings = [
            coding for coding in codings
            if isinstance(coding, dict)
            and coding.get("system") == LIFECYCLE_EVENT_SYSTEM
        ]
        if not iso_codings and not grove_codings:
            continue
        lifecycle_label = f"{label} Provenance[{provenance_index}] activity"
        if len(iso_codings) + len(grove_codings) != 1:
            raise contract_failure(
                "mobile-exchange.lifecycle-coding",
                "Provenance.activity.coding",
                f"{lifecycle_label} must contain exactly one coding across the ISO "
                "transform and Grove retraction lifecycle systems",
            )
        if iso_codings:
            if iso_codings[0].get("code") != "transform":
                raise ProducerValidationError(
                    f"{lifecycle_label} has an unadmitted ISO lifecycle code"
                )
            transform_provenances.append(candidate)
        else:
            if grove_codings[0].get("code") != SOURCE_RECORD_RETRACTED:
                raise ProducerValidationError(
                    f"{lifecycle_label} has an unadmitted Grove lifecycle code"
                )
            retraction_provenances.append(candidate)
    if is_active:
        if (
            len(provenances) != 1
            or len(transform_provenances) != 1
            or retraction_provenances
        ):
            raise contract_failure(
                "mobile-exchange.transform-provenance",
                "Bundle.entry",
                f"{label} active event must contain exactly one transform Provenance and no retraction",
            )
        output_urls: set[str] = set()
        source_pairs: set[tuple[str, str]] = set()
        for full_url, candidate in resources_by_full_url.items():
            if candidate.get("resourceType") not in ACTIVE_OUTPUT_RESOURCE_TYPES:
                continue
            typed = typed_resource_identifiers(candidate, f"{label} output {full_url}")
            if "source-record" not in typed or "source-output" not in typed:
                raise ProducerValidationError(
                    f"{label} active output {full_url} must carry typed source-record and source-output identities"
                )
            output_urls.add(full_url)
            source_pairs.add(typed["source-record"])
        if not output_urls or len(source_pairs) != 1:
            raise ProducerValidationError(
                f"{label} active event must contain outputs for exactly one source record"
            )
        provenance = transform_provenances[0]
        if exact_source_entity(provenance, f"{label} transform Provenance") not in source_pairs:
            raise ProducerValidationError(
                f"{label} transform source must equal the event output source-record identity"
            )
        targets = provenance.get("target")
        target_urls = [
            target.get("reference") for target in targets
            if isinstance(target, dict) and isinstance(target.get("reference"), str)
        ] if isinstance(targets, list) else []
        if len(target_urls) != len(set(target_urls)) or set(target_urls) != output_urls:
            raise ProducerValidationError(
                f"{label} transform Provenance must target every and only source-derived output"
            )
        validate_health_connect_output_graph(entry_resources, resources_by_full_url, label)
        validate_adapter_provenance_graph(entry_resources, resources_by_full_url, label)
    else:
        if (
            len(provenances) != 1
            or len(retraction_provenances) != 1
            or transform_provenances
        ):
            raise ProducerValidationError(
                f"{label} retraction event must contain exactly one retraction Provenance and no transform"
            )
        if any(
            candidate.get("resourceType") not in {"Provenance", "Device"}
            for candidate in entry_resources
        ):
            raise ProducerValidationError(
                f"{label} retraction event may contain only its Provenance and Device agents"
            )
        provenance = retraction_provenances[0]
        targets = provenance.get("target")
        if not isinstance(targets, list) or not targets:
            raise ProducerValidationError(f"{label} retraction must identify at least one target")
        seen_targets: set[tuple[str, str]] = set()
        for target_index, target in enumerate(targets):
            target_label = f"{label} retraction target[{target_index}]"
            if not isinstance(target, dict) or "reference" in target:
                raise ProducerValidationError(
                    f"{target_label} must be a logical Reference without a literal reference"
                )
            if not isinstance(target.get("type"), str) or not target["type"]:
                raise ProducerValidationError(f"{target_label} must state its resource type")
            identifier = target.get("identifier")
            role = identifier_role(identifier, f"{target_label}.identifier")
            if role not in OPAQUE_IDENTIFIER_ROLES:
                raise ProducerValidationError(f"{target_label} has an invalid identifier role")
            pair = complete_identifier(identifier, f"{target_label}.identifier")
            if HMAC_IDENTITY.fullmatch(pair[1]) is None:
                raise contract_failure(
                    "mobile-retraction.opaque-target",
                    f"Provenance.target[{target_index}].identifier.value",
                    f"{target_label} identity is not a canonical v2 HMAC value",
                )
            if pair in seen_targets:
                raise ProducerValidationError(f"{label} repeats a retraction target")
            seen_targets.add(pair)
            extensions = target.get("extension", [])
            role_extensions = [
                extension for extension in extensions
                if isinstance(extension, dict)
                and extension.get("url") == RETRACTION_TARGET_ROLE_EXTENSION
            ] if isinstance(extensions, list) else []
            if (
                len(role_extensions) != 1
                or role_extensions[0].get("valueCode") not in RETRACTION_TARGET_ROLES
            ):
                raise contract_failure(
                    "mobile-retraction.target-role",
                    f"Provenance.target[{target_index}].extension",
                    f"{target_label} must carry exactly one admitted retraction-target role",
                )
            target_role = role_extensions[0]["valueCode"]
            target_contract = RETRACTION_TARGET_CONTRACTS[target_role]
            if role != target_contract["identifierRole"]:
                raise ProducerValidationError(
                    f"{target_label} role {target_role} requires the "
                    f"{target_contract['identifierRole']} identifier role"
                )
            if target["type"] not in target_contract["resourceTypes"]:
                raise contract_failure(
                    "mobile-retraction.role-target-type",
                    f"Provenance.target[{target_index}].type",
                    f"{target_label} role {target_role} does not admit resource type "
                    f"{target['type']}",
                )
        exact_source_entity(provenance, f"{label} retraction Provenance")

    sensorkit_hybrid_profiles = {
        (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-device-usage-observation"
        ): "device-usage",
        (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-ecg-observation"
        ): "ECG",
    }
    full_url_by_resource = {
        id(entry_resource): full_url
        for full_url, entry_resource in resources_by_full_url.items()
    }
    for index, observation in enumerate(entry_resources):
        direct_profiles = observation.get("meta", {}).get("profile", [])
        matches = [
            (profile, name)
            for profile, name in sensorkit_hybrid_profiles.items()
            if profile in direct_profiles
        ] if isinstance(direct_profiles, list) else []
        if not matches:
            continue
        _, graph_name = matches[0]
        derived_from = observation.get("derivedFrom")
        if not isinstance(derived_from, list) or len(derived_from) != 1:
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} entry[{index}] must derive from "
                "exactly one native Recording Document"
            )
        reference = derived_from[0].get("reference") if isinstance(derived_from[0], dict) else None
        document = resources_by_full_url.get(reference) if isinstance(reference, str) else None
        if not isinstance(document, dict) or document.get("resourceType") != "DocumentReference":
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} entry[{index}] must reference its "
                "native Recording Document in the same Bundle"
            )

        def matching_identifier(candidate: dict[str, Any]) -> tuple[str, str] | None:
            return typed_resource_identifiers(
                candidate, "SensorKit output"
            ).get("source-record")

        observation_identity = matching_identifier(observation)
        document_identity = matching_identifier(document)
        if (
            observation_identity is None
            or document_identity is None
            or observation_identity != document_identity
        ):
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} Observation and native document must "
                "carry the same source-record identifier"
            )
        related = document.get("context", {}).get("related", [])
        observation_url = full_url_by_resource[id(observation)]
        related_urls = [
            item.get("reference")
            for item in related
            if isinstance(item, dict)
        ] if isinstance(related, list) else []
        if related_urls != [observation_url]:
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} native document must relate back to "
                "exactly its structured Observation"
            )

    health_connect = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    glucose_by_profile = {
        measurement["profile"]: measurement
        for measurement in health_connect.get("adapterMeasurements", [])
    }
    for index, observation in enumerate(entry_resources):
        direct_profiles = observation.get("meta", {}).get("profile", [])
        matches = [
            glucose_by_profile[profile]
            for profile in direct_profiles
            if profile in glucose_by_profile
        ] if isinstance(direct_profiles, list) else []
        if not matches:
            continue
        measurement = matches[0]
        specimens = observation.get("specimen")
        reference = specimens.get("reference") if isinstance(specimens, dict) else None
        specimen = resources_by_full_url.get(reference) if isinstance(reference, str) else None
        if not isinstance(specimen, dict) or specimen.get("resourceType") != "Specimen":
            raise ProducerValidationError(
                f"{label} Health Connect glucose entry[{index}] must reference its "
                "synthesized Specimen in the same Bundle"
            )
        admitted = (
            [measurement["specimen"]]
            if "specimen" in measurement
            else measurement["specimenAlternatives"]
        )
        admitted_pairs = {(item["system"], item["code"]) for item in admitted}
        codings = specimen.get("type", {}).get("coding", [])
        actual_pairs = {
            (coding.get("system"), coding.get("code"))
            for coding in codings
            if isinstance(coding, dict)
        } if isinstance(codings, list) else set()
        if len(actual_pairs & admitted_pairs) != 1:
            raise ProducerValidationError(
                f"{label} Health Connect glucose entry[{index}] Specimen meaning "
                "does not match its exact adapter-specific profile"
            )


def exchange_bundle_diagnostics(
    resource: dict[str, Any],
    label: str = "exchange Bundle",
    active_adapter_profiles: set[str] | None = None,
) -> list[dict[str, str]]:
    """Return the one stable structural diagnostic used by the cross-SDK corpus."""
    try:
        validate_exchange_bundle(resource, label, active_adapter_profiles)
    except ProducerValidationError as error:
        if error.diagnostic is not None:
            return [error.diagnostic]
        return [
            {
                "code": "mobile-exchange.unclassified",
                "reason": str(error),
                "location": "Bundle",
                "severity": "error",
            }
        ]
    return []


def validate_mobile_semantic_vectors(
    bindings: Any,
    resources_by_path: dict[str, dict[str, Any]],
) -> None:
    """Require one exact vector fixture for every shared Mobile meaning in scope."""
    if not isinstance(bindings, list):
        raise ProducerValidationError("semanticVectors must be an array")
    corpus = read_json(
        REPOSITORY_ROOT / "Conformance/corpora/mobile-semantics/corpus.json"
    )
    vectors = {vector["id"]: vector for vector in corpus["vectors"]}
    profile_to_id = {vector["profile"]: vector_id for vector_id, vector in vectors.items()}

    observed: set[str] = set()
    for root_resource in resources_by_path.values():
        for resource in nested_fhir_resources(root_resource):
            profiles = resource.get("meta", {}).get("profile", [])
            if isinstance(profiles, list):
                observed.update(
                    profile_to_id[profile]
                    for profile in profiles
                    if profile in profile_to_id
                )

    bound: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"semanticVectors[{index}]"
        if not isinstance(binding, dict):
            raise ProducerValidationError(f"{label} must be an object")
        require_keys(binding, {"id", "path", "resourcePointer"}, label)
        if set(binding) != {"id", "path", "resourcePointer"}:
            raise ProducerValidationError(f"{label} is incomplete")
        vector_id = binding["id"]
        if not isinstance(vector_id, str) or vector_id not in vectors:
            raise ProducerValidationError(f"{label} names an unknown Mobile semantic vector")
        if vector_id in bound:
            raise ProducerValidationError(
                f"Mobile semantic vector {vector_id} is bound more than once"
            )
        resource_path = binding["path"]
        if not isinstance(resource_path, str) or resource_path not in resources_by_path:
            raise ProducerValidationError(
                f"{label}.path must name a declared producer resource"
            )
        selected = json_pointer(
            resources_by_path[resource_path],
            binding["resourcePointer"],
            f"{label}.resourcePointer",
        )
        vector = vectors[vector_id]
        actual = mobile_semantic_projection(selected, vector, label)
        expected = {
            key: vector[key] for key in ("profile", "code", "effective", "result")
        }
        if actual != expected:
            raise ProducerValidationError(
                f"{label} clinical projection does not equal Mobile semantic vector {vector_id}"
            )
        bound.add(vector_id)

    if bound != observed:
        missing = sorted(observed - bound)
        extra = sorted(bound - observed)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("not present " + ", ".join(extra))
        raise ProducerValidationError(
            "semanticVectors must cover exactly the shared Mobile measurements present: "
            + "; ".join(details)
        )


def validate_manifest(path: Path) -> tuple[dict[str, Any], list[Path]]:
    manifest = read_json(path)
    if not isinstance(manifest, dict):
        raise ProducerValidationError("manifest must be a JSON object")
    require_keys(manifest, TOP_LEVEL_KEYS, "manifest")
    if set(manifest) != TOP_LEVEL_KEYS:
        raise ProducerValidationError("manifest is missing required fields")
    if manifest["schemaVersion"] != 1 or manifest["fhirVersion"] != "4.0.1":
        raise ProducerValidationError("manifest must declare schemaVersion 1 and FHIR 4.0.1")

    producer = manifest["producer"]
    if not isinstance(producer, dict):
        raise ProducerValidationError("producer must be an object")
    require_keys(producer, {"name", "version", "revision"}, "producer")
    if not all(isinstance(producer.get(key), str) and producer[key] for key in ("name", "version")):
        raise ProducerValidationError("producer name and version must be non-empty strings")
    if "revision" in producer and (not isinstance(producer["revision"], str) or not producer["revision"]):
        raise ProducerValidationError("producer revision must be a non-empty string")

    packages = manifest["packages"]
    if not isinstance(packages, list) or not packages:
        raise ProducerValidationError("packages must be a non-empty array")
    aliases: set[str] = set()
    package_ids: set[str] = set()
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise ProducerValidationError(f"packages[{index}] must be an object")
        require_keys(package, {"alias", "packageId", "version"}, f"packages[{index}]")
        if set(package) != {"alias", "packageId", "version"}:
            raise ProducerValidationError(f"packages[{index}] is incomplete")
        alias = package["alias"]
        package_id = package["packageId"]
        if not isinstance(alias, str) or not PACKAGE_ALIAS.fullmatch(alias):
            raise ProducerValidationError(f"invalid package alias: {alias!r}")
        if not isinstance(package_id, str) or not PACKAGE_ID.fullmatch(package_id):
            raise ProducerValidationError(f"invalid package id: {package_id!r}")
        if package["version"] != RELEASE_VERSION:
            raise ProducerValidationError(
                f"Grove FHIR producer manifests must use package version {RELEASE_VERSION}"
            )
        if alias in aliases or package_id in package_ids:
            raise ProducerValidationError("package aliases and ids must be unique")
        aliases.add(alias)
        package_ids.add(package_id)

    active_adapter_profiles = {
        profile
        for package_id in package_ids
        if package_id in ADAPTER_PACKAGE_PROFILES
        for profile in ADAPTER_PACKAGE_PROFILES[package_id]
    }

    resources = manifest["resources"]
    if not isinstance(resources, list) or not resources:
        raise ProducerValidationError("resources must be a non-empty array")
    paths: list[Path] = []
    resources_by_path: dict[str, dict[str, Any]] = {}
    relative_paths: set[str] = set()
    for index, entry in enumerate(resources):
        if not isinstance(entry, dict):
            raise ProducerValidationError(f"resources[{index}] must be an object")
        require_keys(entry, {"path", "requiredProfiles"}, f"resources[{index}]")
        if set(entry) != {"path", "requiredProfiles"}:
            raise ProducerValidationError(f"resources[{index}] is incomplete")
        relative = entry["path"]
        if relative in relative_paths:
            raise ProducerValidationError(f"duplicate resource path: {relative}")
        relative_paths.add(relative)
        resource_path = safe_resource_path(path.parent, relative)
        resource = read_json(resource_path)
        if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
            raise ProducerValidationError(f"{relative} is not a FHIR resource")
        required = entry["requiredProfiles"]
        if (
            not isinstance(required, list)
            or not required
            or any(not isinstance(profile, str) or not profile.startswith(GROVE_PROFILE) for profile in required)
            or len(required) != len(set(required))
        ):
            raise ProducerValidationError(f"{relative} has invalid requiredProfiles")
        actual = resource.get("meta", {}).get("profile", []) if isinstance(resource.get("meta"), dict) else []
        if not isinstance(actual, list) or any(not isinstance(profile, str) for profile in actual):
            raise ProducerValidationError(f"{relative} has invalid meta.profile")
        missing = set(required) - set(actual)
        if missing:
            raise ProducerValidationError(f"{relative} is missing required profiles: {', '.join(sorted(missing))}")
        actual_grove_profiles = {
            profile for profile in actual if profile.startswith(GROVE_PROFILE)
        }
        if set(required) != actual_grove_profiles:
            hidden = actual_grove_profiles - set(required)
            raise ProducerValidationError(
                f"{relative} requiredProfiles must equal its direct Grove meta.profile set; "
                f"unlisted: {', '.join(sorted(hidden))}"
            )
        validate_resource_profile_claims(resource, relative, active_adapter_profiles)
        validate_exchange_bundle(resource, relative, active_adapter_profiles)
        resources_by_path[relative] = resource
        paths.append(resource_path)
    validate_mobile_semantic_vectors(manifest["semanticVectors"], resources_by_path)
    return manifest, paths


def package_metadata(path: Path) -> dict[str, Any]:
    path = resolve_unlinked_regular_file(path, "package")
    try:
        with tarfile.open(path, "r:gz") as archive:
            member = archive.extractfile("package/package.json")
            if member is None:
                raise ProducerValidationError(f"package has no package/package.json: {path}")
            return json.load(member, object_pairs_hook=unique_object)
    except (tarfile.TarError, OSError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read package {path}: {error}") from error


def parse_package_arguments(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        alias, separator, raw_path = value.partition("=")
        if not separator or not PACKAGE_ALIAS.fullmatch(alias) or not raw_path:
            raise ProducerValidationError(f"--package must be alias=path: {value!r}")
        if alias in result:
            raise ProducerValidationError(f"duplicate --package alias: {alias}")
        result[alias] = resolve_unlinked_regular_file(
            Path(raw_path), f"{alias} package"
        )
    return result


def validate_packages(manifest: dict[str, Any], supplied: dict[str, Path]) -> list[Path]:
    expected = {entry["alias"]: entry for entry in manifest["packages"]}
    if supplied.keys() != expected.keys():
        missing = expected.keys() - supplied.keys()
        extra = supplied.keys() - expected.keys()
        details = [*(f"missing {item}" for item in sorted(missing)), *(f"unexpected {item}" for item in sorted(extra))]
        raise ProducerValidationError("package arguments do not match manifest: " + ", ".join(details))
    paths: list[Path] = []
    for alias, declaration in expected.items():
        path = supplied[alias]
        metadata = package_metadata(path)
        if metadata.get("name") != declaration["packageId"] or metadata.get("version") != declaration["version"]:
            raise ProducerValidationError(f"{alias} package identity/version does not match the manifest")
        fhir_versions = metadata.get("fhirVersions")
        if fhir_versions != ["4.0.1"]:
            raise ProducerValidationError(f"{alias} package must declare only FHIR 4.0.1")
        paths.append(path)
    return paths


def validator_outcomes(
    value: Any, resources: list[Path]
) -> list[tuple[Path, dict[str, Any]]]:
    """Require Validator's exact one-input or ordered multi-input output shape."""
    if not isinstance(value, dict):
        raise ProducerValidationError("FHIR Validator output must be a JSON resource")
    if len(resources) == 1:
        if value.get("resourceType") != "OperationOutcome":
            raise ProducerValidationError(
                "one-input FHIR Validator output must be one OperationOutcome"
            )
        outcomes = [value]
    else:
        if value.get("resourceType") != "Bundle" or value.get("type") != "collection":
            raise ProducerValidationError(
                "multi-input FHIR Validator output must be a collection Bundle"
            )
        entries = value.get("entry")
        if not isinstance(entries, list) or len(entries) != len(resources):
            actual = len(entries) if isinstance(entries, list) else "invalid"
            raise ProducerValidationError(
                "FHIR Validator output count does not match inputs: "
                f"{actual} != {len(resources)}"
            )
        outcomes = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or set(entry) != {"resource"}:
                raise ProducerValidationError(
                    f"FHIR Validator output Bundle entry[{index}] must contain only resource"
                )
            outcome = entry["resource"]
            if not isinstance(outcome, dict) or outcome.get("resourceType") != "OperationOutcome":
                raise ProducerValidationError(
                    f"FHIR Validator output Bundle entry[{index}] is not one OperationOutcome"
                )
            outcomes.append(outcome)

    result: list[tuple[Path, dict[str, Any]]] = []
    for index, (resource, outcome) in enumerate(zip(resources, outcomes, strict=True)):
        extensions = outcome.get("extension", [])
        matches = [
            extension.get("valueString")
            for extension in extensions
            if isinstance(extension, dict)
            and extension.get("url") == VALIDATOR_FILE_EXTENSION
        ] if isinstance(extensions, list) else []
        if matches != [str(resource)]:
            raise ProducerValidationError(
                f"FHIR Validator output[{index}] file attribution does not match input "
                f"{resource}"
            )
        result.append((resource, outcome))
    return result


def reject_validator_errors(outcome: dict[str, Any], label: str) -> None:
    errors: list[str] = []
    issues = outcome.get("issue")
    if not isinstance(issues, list) or not issues:
        raise ProducerValidationError(
            f"FHIR Validator OperationOutcome has no populated issue array for {label}"
        )
    for issue_index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ProducerValidationError(
                f"FHIR Validator OperationOutcome.issue[{issue_index}] is invalid for {label}"
            )
        severity = issue.get("severity")
        if severity not in {"fatal", "error", "warning", "information"}:
            raise ProducerValidationError(
                f"FHIR Validator issue has invalid severity for {label}: {severity!r}"
            )
        if severity in {"fatal", "error"}:
            diagnostics = issue.get("diagnostics")
            if not isinstance(diagnostics, str) or not diagnostics:
                details = issue.get("details")
                diagnostics = details.get("text") if isinstance(details, dict) else None
            errors.append(
                diagnostics
                if isinstance(diagnostics, str) and diagnostics
                else "unspecified validation error"
            )
    if errors:
        raise ProducerValidationError(
            f"FHIR Validator rejected {label}: " + " | ".join(errors)
        )


def truncated_validator_log(value: str | bytes | None) -> str:
    """Return a bounded, printable process log for a terminal infrastructure failure."""
    if not value:
        return "<empty>"
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    normalized = value.replace("\x00", "\\0").strip()
    if len(normalized) <= VALIDATOR_LOG_LIMIT:
        return normalized
    return "…" + normalized[-VALIDATOR_LOG_LIMIT:]


def run_validator(
    validator: Path,
    packages: list[Path],
    resources: list[Path],
    *,
    allow_example_urls: bool = False,
) -> None:
    validator = resolve_unlinked_regular_file(validator, "Validator JAR")
    packages = [
        resolve_unlinked_regular_file(package, "FHIR package")
        for package in packages
    ]
    fhir_tool_home = resolve_unlinked_directory(FHIR_TOOL_HOME, "private FHIR home")
    resolve_unlinked_directory(
        fhir_tool_home / ".fhir" / "packages", "private FHIR package cache"
    )
    ordered_resources = sorted(resources, key=lambda path: path.as_posix())
    with tempfile.TemporaryDirectory(prefix="grove-fhir-producer-") as directory:
        output = Path(directory) / "operation-outcomes.json"
        command = [
            "java", f"-Duser.home={fhir_tool_home}", "-jar", str(validator),
            "-version", "4.0.1",
            "-tx", "n/a",
            "-no-http-access",
            "-level", "errors",
        ]
        for package in packages:
            command.extend(("-ig", str(package)))
        if allow_example_urls:
            command.extend(("-allow-example-urls", "true"))
        command.extend(("-output", str(output)))
        command.extend(str(resource) for resource in ordered_resources)

        last_failure = ""
        for attempt in range(1, VALIDATOR_ATTEMPTS + 1):
            if output.exists() or output.is_symlink():
                output.unlink()
            try:
                result = subprocess.run(
                    command,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=VALIDATOR_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired as error:
                process_log = truncated_validator_log(error.stdout)
                last_failure = (
                    "FHIR Validator timed out after "
                    f"{VALIDATOR_TIMEOUT_SECONDS} seconds; log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure) from error
            process_log = truncated_validator_log(result.stdout)
            if not output.is_file() or output.is_symlink():
                last_failure = (
                    "FHIR Validator produced no trustworthy OperationOutcome output "
                    f"(exit {result.returncode}); log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure)
            try:
                parsed = read_json(output)
                outcomes = validator_outcomes(parsed, ordered_resources)
            except ProducerValidationError as error:
                last_failure = (
                    f"untrustworthy FHIR Validator output: {error} "
                    f"(exit {result.returncode}); log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure) from error

            # A real FHIR fatal/error is final and is never retried or ignored.
            for resource, outcome in outcomes:
                reject_validator_errors(outcome, resource.name)
            if result.returncode == 0:
                return
            last_failure = (
                "FHIR Validator process failed after producing only error-free, correctly "
                f"attributed OperationOutcomes (exit {result.returncode}); log: {process_log}"
            )
            if attempt == VALIDATOR_ATTEMPTS:
                raise ProducerValidationError(last_failure)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--validator", type=Path)
    parser.add_argument("--structural-only", action="store_true")
    parser.add_argument(
        "--allow-example-urls",
        action="store_true",
        help=(
            "allow example.org identifiers in demonstration fixtures; omitted by "
            "default so producer validation fails closed"
        ),
    )
    arguments = parser.parse_args(argv)
    try:
        manifest_path = resolve_unlinked_regular_file(arguments.manifest, "manifest")
        manifest, resources = validate_manifest(manifest_path)
        if arguments.structural_only:
            if (
                arguments.package
                or arguments.validator is not None
                or arguments.allow_example_urls
            ):
                raise ProducerValidationError(
                    "--structural-only cannot be combined with package, Validator, "
                    "or example-URL arguments"
                )
        else:
            if arguments.validator is None:
                raise ProducerValidationError("--validator is required unless --structural-only is used")
            supplied = parse_package_arguments(arguments.package)
            packages = validate_packages(manifest, supplied)
            run_validator(
                arguments.validator,
                packages,
                resources,
                allow_example_urls=arguments.allow_example_urls,
            )
    except ProducerValidationError as error:
        print(f"Producer conformance failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(resources)} producer resource(s) against FHIR R4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
