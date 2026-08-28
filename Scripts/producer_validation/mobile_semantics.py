"""Catalog-bound Mobile semantic-vector projection and verification."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import REPOSITORY_ROOT
from .diagnostics import ProducerValidationError
from .io import json_pointer, read_json, require_keys
from .payloads import parse_fhir_instant, round_mobile_epoch_milliseconds


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
