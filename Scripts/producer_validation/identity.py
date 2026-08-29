"""Opaque graph identity and optional governed source-identifier validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from typing import Any

from .context import (
    ACTIVE_OUTPUT_RESOURCE_TYPES, CATALOG_ROOT, EXCHANGE_PROTOCOL, HMAC_IDENTITY,
    IDENTIFIER_PRIORITY, IDENTIFIER_ROLE_SYSTEM, MEASUREMENT_BY_PROFILE,
    OPAQUE_IDENTIFIER_ROLES, REPOSITORY_ROOT, ExchangeProtocolError,
    entry_full_url, require_absolute_uri,
)
from .diagnostics import ProducerValidationError
from .io import read_json
from .references import complete_identifier, extensions_with_url


FHIR_CODE = re.compile(r"^[^\s]+(?: [^\s]+)*$")


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
        identifier_type = identifier.get("type")
        codings = identifier_type.get("coding", []) if isinstance(identifier_type, dict) else []
        grove_codings = [
            coding
            for coding in codings
            if isinstance(coding, dict)
            and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
        ] if isinstance(codings, list) else []
        roles = [
            coding.get("code")
            for coding in grove_codings
            if isinstance(coding.get("code"), str)
        ]
        if not grove_codings:
            continue
        if (
            len(grove_codings) != 1
            or len(roles) != 1
            or roles[0] not in OPAQUE_IDENTIFIER_ROLES
        ):
            raise ProducerValidationError(
                f"{label}.identifier[{index}] has an unknown or repeated Grove identifier role"
            )
        role = roles[0]
        if role in result:
            raise ProducerValidationError(f"{label} repeats the {role} identifier role")
        pair = complete_identifier(identifier, f"{label}.identifier[{index}]")
        if HMAC_IDENTITY.fullmatch(pair[1]) is None:
            raise ProducerValidationError(
                f"{label}.identifier[{index}] is not a canonical Grove v0 HMAC identity"
            )
        result[role] = pair
    return result


def validate_governed_identifier_type(identifier: dict[str, Any], label: str) -> None:
    """Validate optional source Identifier.type without inventing a second key space."""
    identifier_type = identifier.get("type")
    if identifier_type is None:
        return
    if not isinstance(identifier_type, dict):
        raise ProducerValidationError(f"{label}.type must be a CodeableConcept")
    codings = identifier_type.get("coding", [])
    if not isinstance(codings, list):
        raise ProducerValidationError(f"{label}.type.coding must be an array")
    text = identifier_type.get("text")
    text_present = isinstance(text, str) and bool(text.strip())
    if not codings and not text_present:
        raise ProducerValidationError(
            f"{label}.type must contain a non-blank text or at least one Coding"
        )
    for index, coding in enumerate(codings):
        coding_label = f"{label}.type.coding[{index}]"
        if not isinstance(coding, dict):
            raise ProducerValidationError(f"{coding_label} must be a Coding")
        system = coding.get("system")
        code = coding.get("code")
        if system == IDENTIFIER_ROLE_SYSTEM:
            raise ProducerValidationError(
                f"{coding_label} must not claim a Grove identifier role"
            )
        if not isinstance(system, str) or not system:
            raise ProducerValidationError(
                f"{coding_label}.system is required for governed source Identifier.type"
            )
        try:
            require_absolute_uri(system, f"{coding_label}.system")
        except ExchangeProtocolError as error:
            raise ProducerValidationError(str(error)) from error
        if not isinstance(code, str) or FHIR_CODE.fullmatch(code) is None:
            raise ProducerValidationError(
                f"{coding_label}.code must use the FHIR code lexical form"
            )

def non_grove_resource_identifiers(
    resource: dict[str, Any], label: str
) -> list[tuple[str, str]]:
    """Classify every non-Grove Identifier on an active output as governed source identity."""
    # Validate every Grove-coded identifier first so a source-native value cannot evade this
    # policy by falsely claiming a graph role.
    typed_resource_identifiers(resource, label)
    identifiers = resource.get("identifier", [])
    if identifiers is None:
        return []
    if isinstance(identifiers, dict):
        identifiers = [identifiers]
    if not isinstance(identifiers, list):
        raise ProducerValidationError(f"{label}.identifier must be an Identifier array")
    pairs: list[tuple[str, str]] = []
    for index, identifier in enumerate(identifiers):
        if not isinstance(identifier, dict):
            raise ProducerValidationError(f"{label}.identifier[{index}] must be an Identifier")
        identifier_type = identifier.get("type")
        codings = identifier_type.get("coding", []) if isinstance(identifier_type, dict) else []
        grove_codings = [
            coding for coding in codings
            if isinstance(coding, dict) and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
        ] if isinstance(codings, list) else []
        if grove_codings:
            continue
        validate_governed_identifier_type(
            identifier, f"{label}.identifier[{index}]"
        )
        pairs.append(complete_identifier(identifier, f"{label}.identifier[{index}]"))
    return pairs

def identifier_pair_occurrences(value: Any, pair: tuple[str, str]) -> int:
    """Count exact Identifier-shaped pair occurrences anywhere in a graph."""
    if isinstance(value, dict):
        count = int(value.get("system") == pair[0] and value.get("value") == pair[1])
        return count + sum(identifier_pair_occurrences(child, pair) for child in value.values())
    if isinstance(value, list):
        return sum(identifier_pair_occurrences(child, pair) for child in value)
    return 0

def exact_marker_code(resource: dict[str, Any], marker: dict[str, Any]) -> str | None:
    """Return one exact catalog marker code, or None when this is not that adapter output."""
    matches = extensions_with_url(resource, marker["url"])
    if len(matches) != 1:
        return None
    value = matches[0].get(marker["valueElement"])
    return value if isinstance(value, str) and value else None

def output_measurement_ids(resource: dict[str, Any]) -> set[str]:
    """Return catalog measurement ids directly claimed by one Observation."""
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return set()
    result = {
        MEASUREMENT_BY_PROFILE[profile]["id"]
        for profile in profiles
        if profile in MEASUREMENT_BY_PROFILE
    }
    health_connect = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    result.update(
        measurement["id"]
        for measurement in health_connect["adapterMeasurements"]
        if measurement["profile"] in profiles
    )
    return result

def catalog_designated_primary(
    outputs: list[dict[str, Any]], designated: dict[str, Any]
) -> dict[str, Any] | None:
    """Select a primary independently of native-Identifier presence, or require omission."""
    selectors = designated["adapterSelectors"]

    healthkit_selector = selectors["healthkit"]
    healthkit_codes = {
        code
        for output in outputs
        if (code := exact_marker_code(output, healthkit_selector["sourceMarker"]))
        is not None
    }
    if healthkit_codes:
        if len(healthkit_codes) != 1:
            return None
        catalog = read_json(REPOSITORY_ROOT / healthkit_selector["catalog"])
        row = next(
            (
                item for item in catalog[healthkit_selector["rowCollection"]]
                if item[healthkit_selector["rowKey"]] == next(iter(healthkit_codes))
            ),
            None,
        )
        if row is None:
            return None
        row_profiles = set(row.get("profiles", []))
        excluded = set(healthkit_selector["excludedProfiles"])
        candidates = [
            output for output in outputs
            if exact_marker_code(output, healthkit_selector["sourceMarker"])
            == row[healthkit_selector["rowKey"]]
            and not set(output.get("meta", {}).get("profile", [])) & excluded
            and bool(set(output.get("meta", {}).get("profile", [])) & row_profiles)
        ]
        return candidates[0] if len(candidates) == 1 else None

    health_connect_selector = selectors["health-connect"]
    health_connect_codes = {
        code
        for output in outputs
        if (code := exact_marker_code(output, health_connect_selector["sourceMarker"]))
        is not None
    }
    if health_connect_codes:
        if len(health_connect_codes) != 1:
            return None
        catalog = read_json(REPOSITORY_ROOT / health_connect_selector["catalog"])
        row = next(
            (
                item for item in catalog[health_connect_selector["rowCollection"]]
                if item[health_connect_selector["rowKey"]]
                == next(iter(health_connect_codes))
            ),
            None,
        )
        if row is None:
            return None
        eligible_counts = set(health_connect_selector["eligibleCountRules"])
        eligible_graphs = set(health_connect_selector["eligibleGraphRules"])
        eligible_measurements = {
            item["measurement"] for item in row["outputs"]
            if item["countRule"] in eligible_counts
            or item.get("graphRule") in eligible_graphs
        }
        candidates = [
            output for output in outputs
            if output.get("resourceType")
            not in set(health_connect_selector["excludedResourceTypes"])
            and exact_marker_code(output, health_connect_selector["sourceMarker"])
            == row[health_connect_selector["rowKey"]]
            and len(output_measurement_ids(output) & eligible_measurements) == 1
        ]
        return candidates[0] if len(candidates) == 1 else None

    provider_selector = selectors["providers"]
    provider_pairs = {
        (
            exact_marker_code(output, provider_selector["providerMarker"]),
            exact_marker_code(output, provider_selector["sourceMarker"]),
        )
        for output in outputs
        if exact_marker_code(output, provider_selector["providerMarker"])
        and exact_marker_code(output, provider_selector["sourceMarker"])
    }
    if provider_pairs:
        if len(provider_pairs) != 1:
            return None
        provider_id, wire_token = next(iter(provider_pairs))
        if not isinstance(provider_id, str) or not isinstance(wire_token, str):
            return None
        prefix = provider_id + "/"
        if not wire_token.startswith(prefix):
            return None
        token = wire_token[len(prefix):]
        catalog = read_json(REPOSITORY_ROOT / provider_selector["catalog"])
        provider = next(
            (item for item in catalog["providers"] if item["id"] == provider_id), None
        )
        if provider is None:
            return None
        grouped = next(
            (item for item in provider.get("groupedMappings", []) if item["token"] == token),
            None,
        )
        row = next(
            (item for item in provider.get("sourceTypes", []) if item["token"] == token),
            None,
        )
        if grouped is not None:
            admitted_measurements = set(grouped.get("measurementIds", []))
        elif row is not None:
            admitted_measurements = {
                measurement
                for element in row.get("elements", [])
                if element.get("status") in {"supported", "platform-exclusive"}
                for measurement in element.get("measurementIds", [])
            }
        else:
            return None
        observations = [
            output for output in outputs
            if output.get("resourceType") == "Observation"
            and exact_marker_code(output, provider_selector["providerMarker"])
            == provider_id
            and exact_marker_code(output, provider_selector["sourceMarker"])
            == wire_token
            and bool(output_measurement_ids(output) & admitted_measurements)
        ]
        if len(admitted_measurements) == 1 and len(observations) == 1:
            return observations[0]
        documents = [
            output for output in outputs
            if output.get("resourceType") == "DocumentReference"
            and exact_marker_code(output, provider_selector["providerMarker"])
            == provider_id
            and exact_marker_code(output, provider_selector["sourceMarker"])
            == wire_token
        ]
        return documents[0] if not observations and len(documents) == 1 else None

    sensorkit_selector = selectors["sensorkit"]
    sensorkit_codes = {
        code
        for output in outputs
        if (code := exact_marker_code(output, sensorkit_selector["sourceMarker"]))
        is not None
    }
    if sensorkit_codes:
        if len(sensorkit_codes) != 1:
            return None
        source_code = next(iter(sensorkit_codes))
        catalog = read_json(REPOSITORY_ROOT / sensorkit_selector["catalog"])
        row = next(
            (
                item for item in catalog[sensorkit_selector["rowCollection"]]
                if item[sensorkit_selector["rowKey"]] == source_code
            ),
            None,
        )
        if row is None:
            return None
        structured_profile = row.get("structured", {}).get("profile")
        structured = [
            output for output in outputs
            if isinstance(structured_profile, str)
            and structured_profile in output.get("meta", {}).get("profile", [])
            and exact_marker_code(output, sensorkit_selector["sourceMarker"])
            == source_code
        ]
        if len(structured) == 1:
            return structured[0]
        documents = [
            output for output in outputs
            if output.get("resourceType") == "DocumentReference"
            and exact_marker_code(output, sensorkit_selector["sourceMarker"])
            == source_code
        ]
        return documents[0] if not structured and len(documents) == 1 else None

    return None

def validate_governed_source_identifiers(
    resources: list[dict[str, Any]], label: str
) -> None:
    """Enforce the optional exact source-native Identifier placement contract."""
    policy = EXCHANGE_PROTOCOL["governedSourceIdentifier"]["validation"]
    designated = policy["designatedNode"]
    active_outputs = [
        resource for resource in resources
        if resource.get("resourceType") in ACTIVE_OUTPUT_RESOURCE_TYPES
    ]
    outputs_by_source: dict[tuple[str, str], list[dict[str, Any]]] = {}
    source_by_output: dict[int, tuple[str, str]] = {}
    for resource in active_outputs:
        source = typed_resource_identifiers(
            resource, f"{label} {resource.get('resourceType')} output"
        ).get("source-record")
        if source is None:
            raise ProducerValidationError(
                f"{label} active output has no source-record identity for primary selection"
            )
        outputs_by_source.setdefault(source, []).append(resource)
        source_by_output[id(resource)] = source
    primary_by_source = {
        source: catalog_designated_primary(outputs, designated)
        for source, outputs in outputs_by_source.items()
    }
    governed: list[tuple[dict[str, Any], tuple[str, str]]] = []
    for resource in active_outputs:
        pairs = non_grove_resource_identifiers(
            resource, f"{label} {resource.get('resourceType')} output"
        )
        if len(pairs) > designated["maxPerPrimaryOutput"]:
            raise ProducerValidationError(
                f"{label} active output carries more than one governed source Identifier"
            )
        governed.extend((resource, pair) for pair in pairs)
    if len(governed) > designated["maxPrimaryOutputsPerEvent"]:
        raise ProducerValidationError(
            f"{label} governed source Identifier may designate only one primary output"
        )

    health_connect = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    health_connect_rows = {row["token"]: row for row in health_connect["recordTypes"]}
    for resource, pair in governed:
        source = source_by_output[id(resource)]
        if primary_by_source[source] is not resource:
            raise ProducerValidationError(
                f"{label} governed source Identifier is not on the exact catalog-designated primary output"
            )
        resource_type = resource.get("resourceType")
        profiles = resource.get("meta", {}).get("profile", [])
        profile_set = set(profiles) if isinstance(profiles, list) else set()
        if resource_type in set(policy["neverResourceTypes"]) or profile_set & set(
            policy["neverProfiles"]
        ):
            raise ProducerValidationError(
                f"{label} governed source Identifier is not allowed on a secondary or support output"
            )
        if resource_type == "DocumentReference" and len(active_outputs) != 1:
            raise ProducerValidationError(
                f"{label} companion source artifact must not carry the governed source Identifier"
            )

        record_type_url = health_connect["sourceTypeExtension"]["url"]
        extensions = resource.get("extension", [])
        record_types = [
            extension.get("valueCode")
            for extension in extensions
            if isinstance(extension, dict) and extension.get("url") == record_type_url
        ] if isinstance(extensions, list) else []
        if len(record_types) == 1 and record_types[0] in health_connect_rows:
            measurement = next(
                (
                    item["id"] for profile, item in MEASUREMENT_BY_PROFILE.items()
                    if profile in profile_set
                ),
                None,
            )
            output = next(
                (
                    item for item in health_connect_rows[record_types[0]]["outputs"]
                    if item["measurement"] == measurement
                ),
                None,
            )
            if output is not None and (
                output["countRule"] in set(policy["healthConnectChildCountRules"])
                or output.get("graphRule") in set(policy["healthConnectChildGraphRules"])
            ):
                raise ProducerValidationError(
                    f"{label} Health Connect child output must not carry the record's governed source Identifier"
                )

        if identifier_pair_occurrences(resources, pair) != 1:
            raise ProducerValidationError(
                f"{label} governed source Identifier must appear exactly once on its designated primary output"
            )

def selected_entry_identifier(resource: dict[str, Any], label: str) -> tuple[str, tuple[str, str]] | None:
    """Select the deterministic resource business identifier required by protocol v0."""
    by_role = typed_resource_identifiers(resource, label)
    for role in IDENTIFIER_PRIORITY:
        if role in by_role:
            return role, by_role[role]
    return None
