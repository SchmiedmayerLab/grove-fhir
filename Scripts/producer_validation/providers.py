"""Connected-provider profile, issued, lineage, and identity validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import CATALOG_ROOT, MEASUREMENT_BY_PROFILE
from .diagnostics import ProducerValidationError
from .identity import typed_resource_identifiers
from .io import read_json


PROVIDER_IDENTITY_PROFILES = {
    "https://grovealliance.org/fhir/providers/StructureDefinition/providers-observation",
    "https://grovealliance.org/fhir/providers/StructureDefinition/providers-recording-document",
    "https://grovealliance.org/fhir/withings/StructureDefinition/withings-observation",
    "https://grovealliance.org/fhir/oura/StructureDefinition/oura-observation",
    "https://grovealliance.org/fhir/google-health/StructureDefinition/google-health-observation",
}

ADMITTED_OBSERVATION_STATUSES = frozenset({"supported", "platform-exclusive"})

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
                f"{label} source type does not admit a Recording Document"
            )
    else:
        if "issued" in resource:
            raise ProducerValidationError(
                f"{label} Provider Observation must omit issued because the Grove FHIR "
                "contracts declare no authoritative provider availability field"
            )
        claimed = [
            (profile, MEASUREMENT_BY_PROFILE[profile])
            for profile in profiles
            if profile in MEASUREMENT_BY_PROFILE
        ]
        if len(claimed) != 1:
            raise ProducerValidationError(
                f"{label} Provider Observation must claim exactly one catalog semantic "
                "profile (shared or provider-owned)"
            )
        semantic_profile, measurement = claimed[0]
        expected_profiles = {semantic_profile, provider["observationProfile"]}
        if len(profiles) != 2 or set(profiles) != expected_profiles:
            raise ProducerValidationError(
                f"{label} Provider Observation must directly claim exactly its semantic "
                f"profile and {provider['observationProfile']}"
            )
        if measurement.get("owner", "mobile") not in {
            "mobile",
            provider["measurementOwner"],
        }:
            raise ProducerValidationError(
                f"{label} Provider Observation claims a semantic profile owned by "
                "another source"
            )
        if grouped_row is not None:
            admitted_measurements = {
                measurement_id: grouped_row["status"]
                for measurement_id in grouped_row["measurementIds"]
            }
        else:
            admitted_measurements = {
                measurement_id: element["status"]
                for element in source_row["elements"]
                if element["status"] in ADMITTED_OBSERVATION_STATUSES
                for measurement_id in element.get("measurementIds", [])
            }
        status = admitted_measurements.get(measurement["id"])
        if status is None:
            raise ProducerValidationError(
                f"{label} Provider source type does not admit its claimed measurement"
            )
        if status == "platform-exclusive" and (
            source_row is None
            or semantic_profile not in source_row.get("profiles", [])
        ):
            raise ProducerValidationError(
                f"{label} Provider platform-exclusive source type does not list its "
                "claimed provider-owned profile"
            )
