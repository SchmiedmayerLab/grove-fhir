"""FHIR Reference traversal, resolution, and graph-role validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import (
    IDENTIFIER_ROLE_SYSTEM,
    REFERENCE_POLICY,
    ExchangeProtocolError,
    require_absolute_uri,
)
from .diagnostics import ProducerValidationError, contract_failure


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

def extensions_with_url(resource: dict[str, Any], url: str) -> list[dict[str, Any]]:
    """Return only top-level extensions with the requested canonical URL."""
    extensions = resource.get("extension", [])
    if not isinstance(extensions, list):
        return []
    return [
        extension
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == url
    ]

def validate_identity_system_role(resource: dict[str, Any], label: str) -> None:
    """Require every Grove Identifier.system in one graph to retain one role meaning."""
    roles_by_system: dict[str, dict[str, list[str]]] = {}

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            type_value = value.get("type")
            codings = type_value.get("coding", []) if isinstance(type_value, dict) else []
            roles = [
                coding.get("code")
                for coding in codings
                if isinstance(coding, dict)
                and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
                and isinstance(coding.get("code"), str)
            ] if isinstance(codings, list) else []
            system = value.get("system")
            if roles and isinstance(system, str):
                by_role = roles_by_system.setdefault(system, {})
                for role in roles:
                    by_role.setdefault(role, []).append(path)
            for key, child in value.items():
                visit(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    visit(resource, "Bundle")
    for system, role_paths in roles_by_system.items():
        if len(role_paths) <= 1:
            continue
        details = ", ".join(
            f"{role} at {', '.join(paths)}" for role, paths in sorted(role_paths.items())
        )
        raise contract_failure(
            "mobile-exchange.identity-system-role",
            "Bundle",
            f"{label} reuses Grove Identifier.system {system!r} across roles: {details}",
        )

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
