"""Active/retraction Mobile Exchange Bundle orchestration and graph closure."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import (
    ACTIVE_ENTRY_POLICY, ACTIVE_ENTRY_RESOURCE_TYPES, ACTIVE_OUTPUT_RESOURCE_TYPES,
    ACTIVE_SUPPORTING_RESOURCE_TYPES, CATALOG_ROOT, ENTRY_IDENTIFIER_EXTENSION,
    ENTRY_NODE_IDENTITY, EVENT_IDENTITY, EXCHANGE_BUNDLE_PROFILE, HMAC_IDENTITY,
    LIFECYCLE_EVENT_SYSTEM, OPAQUE_IDENTIFIER_ROLES, RETRACTION_BUNDLE_PROFILE,
    RETRACTION_TARGET_CONTRACTS, RETRACTION_TARGET_ROLES,
    RETRACTION_TARGET_ROLE_EXTENSION, SOURCE_RECORD_RETRACTED, entry_node_identity,
)
from .diagnostics import (
    PRODUCER_RULE_REASONS,
    ProducerValidationError,
    contract_failure,
)
from .graphs import exact_source_entity, validate_adapter_provenance_graph
from .health_connect import (
    validate_health_connect_output_graph, validate_health_connect_provider_claim,
    validate_health_connect_source_type, validate_health_connect_specimen_claim,
)
from .healthkit import (
    validate_healthkit_ecg_contract, validate_healthkit_ecg_output_graph,
    validate_healthkit_resource_claims, validate_healthkit_source_type,
)
from .identity import (
    expected_entry_full_url, identifier_role, selected_entry_identifier,
    typed_resource_identifiers, validate_governed_source_identifiers,
)
from .io import read_json
from .profiles import (
    validate_active_adapter_only_output_profile_claim,
    validate_active_adapter_package_claims, validate_active_document_reference_profile_claim,
    validate_active_measurement_fixed_semantics, validate_active_observation_profile_claim,
    validate_active_provenance_profile_claim, validate_adapter_conversion_provenance,
    validate_adapter_profile_claim, validate_adapter_source_marker_claim,
    validate_exchange_supporting_profile_claim, validate_recording_format,
    validate_retraction_provenance_profile_claim, validate_writer_record_revision,
)
from .providers import validate_provider_claim, validate_provider_identity
from .references import (
    all_reference_nodes, all_reference_nodes_with_paths, complete_identifier,
    reference_target, validate_identity_system_role, validate_reference_policy,
)
from .sensorkit import (
    exact_sensorkit_source_type, validate_sensor_contract, validate_sensorkit_ecg_contract,
    validate_sensorkit_identity, validate_sensorkit_native_r4_context,
    validate_sensorkit_profile_claim, validate_sensorkit_quantity_domains,
)


def validate_resource_profile_claims(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    validate_writer_record_revision(resource, label)
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
    validate_sensorkit_native_r4_context(resource, label)
    validate_sensorkit_quantity_domains(resource, label)
    validate_sensor_contract(resource, label)
    validate_recording_format(resource, label)

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
            f"{label} Bundle.identifier is not a canonical Grove v0 event identity",
        )
    validate_identity_system_role(resource, label)
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
            match = ENTRY_NODE_IDENTITY.fullmatch(value)
            if role != "entry-node" or match is None:
                raise ProducerValidationError(
                    f"{label} entry[{index}] resource without typed business identity "
                    "must use a canonical entry-node key"
                )
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
        validate_governed_source_identifiers(entry_resources, label)
        validate_health_connect_output_graph(entry_resources, resources_by_full_url, label)
        validate_healthkit_ecg_output_graph(entry_resources, resources_by_full_url, label)
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
                    f"{target_label} identity is not a canonical v0 HMAC value",
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

    sensorkit = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    sensorkit_hybrid_profiles: dict[str, tuple[str, dict[str, Any]]] = {}
    sensorkit_hybrid_contracts: dict[str, dict[str, Any]] = {}
    for entry in sensorkit["entries"]:
        structured = entry.get("structured")
        if not isinstance(structured, dict):
            continue
        graph_contract = structured.get("graphContract")
        if not isinstance(graph_contract, dict):
            continue
        sensorkit_hybrid_contracts[entry["sourceTypeCode"]] = graph_contract
        for profile_key in ("profile", "adapterProfile"):
            profile = structured.get(profile_key)
            if isinstance(profile, str):
                sensorkit_hybrid_profiles[profile] = (
                    entry["sourceTypeCode"],
                    graph_contract,
                )
    full_url_by_resource = {
        id(entry_resource): full_url
        for full_url, entry_resource in resources_by_full_url.items()
    }
    validated_hybrid_documents: set[int] = set()
    for index, observation in enumerate(entry_resources):
        direct_profiles = observation.get("meta", {}).get("profile", [])
        matches = [
            (profile, name)
            for profile, name in sensorkit_hybrid_profiles.items()
            if profile in direct_profiles
        ] if isinstance(direct_profiles, list) else []
        if not matches:
            continue
        _, (graph_name, graph_contract) = matches[0]
        derived_from = observation.get("derivedFrom")
        if not isinstance(derived_from, list) or len(derived_from) != 1:
            raise contract_failure(
                "mobile-output.hybrid-companion", "Observation.derivedFrom",
                f"{label} SensorKit {graph_name} entry[{index}] must derive from "
                "exactly one Recording Document",
            )
        reference = derived_from[0].get("reference") if isinstance(derived_from[0], dict) else None
        document = resources_by_full_url.get(reference) if isinstance(reference, str) else None
        if not isinstance(document, dict) or document.get("resourceType") != "DocumentReference":
            raise contract_failure(
                "mobile-output.hybrid-companion", "Observation.derivedFrom",
                f"{label} SensorKit {graph_name} entry[{index}] must reference its "
                "Recording Document in the same Bundle",
            )
        if (
            exact_sensorkit_source_type(observation, f"{label} entry[{index}]")
            != graph_name
            or exact_sensorkit_source_type(document, f"{label} linked Recording Document")
            != graph_name
        ):
            raise contract_failure(
                "mobile-output.hybrid-companion", "Resource.extension",
                f"{label} SensorKit {graph_name} Observation and Recording Document "
                "must carry the same matching SensorKit source type",
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
            raise contract_failure(
                "mobile-output.hybrid-companion", "Resource.identifier",
                f"{label} SensorKit {graph_name} Observation and Recording Document must "
                "carry the same source-record identifier",
            )
        related = document.get("context", {}).get("related", [])
        observation_url = full_url_by_resource[id(observation)]
        related_reference = (
            related[0]
            if isinstance(related, list)
            and len(related) == 1
            and isinstance(related[0], dict)
            else None
        )
        valid_backlink = (
            isinstance(related_reference, dict)
            and related_reference.get("reference") == observation_url
            and "identifier" not in related_reference
            and (
                "type" not in related_reference
                or related_reference["type"] == "Observation"
            )
        )
        if graph_contract["bidirectional"] and not valid_backlink:
            raise contract_failure(
                "mobile-output.hybrid-companion", "DocumentReference.context.related",
                f"{label} SensorKit {graph_name} Recording Document must relate back to "
                "exactly its structured Observation",
            )
        validated_hybrid_documents.add(id(document))

    sensorkit_document_profile = sensorkit["profileClaims"]["recordingDocument"][
        "adapterProfile"
    ]
    for index, document in enumerate(entry_resources):
        if document.get("resourceType") != "DocumentReference":
            continue
        profiles = document.get("meta", {}).get("profile", [])
        if not isinstance(profiles, list) or sensorkit_document_profile not in profiles:
            continue
        source_type = exact_sensorkit_source_type(document, f"{label} entry[{index}]")
        if (
            source_type in sensorkit_hybrid_contracts
            and id(document) not in validated_hybrid_documents
        ):
            raise contract_failure(
                "mobile-output.hybrid-companion", "DocumentReference.context.related",
                f"{label} SensorKit {source_type} Recording Document requires exactly "
                "one linked structured Observation in the same Bundle",
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
                "reason": PRODUCER_RULE_REASONS["mobile-exchange.unclassified"],
                "location": "Bundle",
                "severity": "error",
            }
        ]
    return []
