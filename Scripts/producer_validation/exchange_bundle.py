"""Active/retraction Mobile Exchange Bundle orchestration, record partition, and key checks."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

# One exchange Bundle carries one or more records of one kind and one subject. A record is one
# lifecycle Provenance with its targets (bundle.recordUnit). The checks run structural rules first
# and recompute keys last, so a fixture that breaks a structural rule reports that rule, and one
# whose content changed under an unchanged key reports the key.

from __future__ import annotations

from typing import Any

from .context import (
    ACTIVE_ENTRY_POLICY, ACTIVE_ENTRY_RESOURCE_TYPES, ACTIVE_OUTPUT_RESOURCE_TYPES,
    ACTIVE_SUPPORTING_RESOURCE_TYPES, CATALOG_ROOT, CONTEXT_NODE_ROLES,
    CONTEXT_SNAPSHOT_EXTENSION, DEVICE_NODE_ROLES, ENTRY_IDENTIFIER_EXTENSION,
    EXCHANGE_BUNDLE_PROFILE, HMAC_IDENTITY, IDENTIFIER_ROLE_SYSTEM, LIFECYCLE_EVENT_SYSTEM,
    OPAQUE_IDENTIFIER_ROLES, PROVENANCE_KEY_ROLES, RECORD_VERSION_EXTENSION,
    REFERENCE_POLICY, RETRACTION_BUNDLE_PROFILE,
    RETRACTION_NATIVE_RECORD_IDENTIFIER_EXTENSION, RETRACTION_TARGET_CONTRACTS,
    RETRACTION_TARGET_ROLES, RETRACTION_TARGET_ROLE_EXTENSION, SOURCE_RECORD_RETRACTED,
    SOURCE_RECORD_TARGET_ROLE, TEST_KEY, TEST_KEY_ID, ExchangeProtocolError, content_digest,
    context_snapshot_identity, device_snapshot_identity, parse_hmac_identity,
    record_content_digest, record_retraction_identity, record_version_identity,
    require_absolute_uri,
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
from .healthkit_metadata import validate_healthkit_metadata
from .io import CanonicalJSONError, canonical_bytes, lossless_tree, read_json
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


ISO_LIFECYCLE_SYSTEM = "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle"
SNAPSHOT_ROLE_BY_RESOURCE_TYPE = {
    "Device": "device-snapshot",
    **{resource_type: "context-snapshot" for resource_type in CONTEXT_NODE_ROLES},
}
# The governed Patient paths of active outputs: what a record states as its subject.
OUTPUT_SUBJECT_PATHS = tuple(
    (rule["resourceType"], rule["path"])
    for rule in REFERENCE_POLICY["paths"]
    if rule["targetTypes"] == ["Patient"]
    and rule["resourceType"] in ACTIVE_OUTPUT_RESOURCE_TYPES
)


def validate_retraction_native_record_identifier(
    target: dict[str, Any], target_index: int, label: str
) -> None:
    """Admit at most one source-native record Identifier beside the minted Grove identity."""
    extensions = target.get("extension")
    carried = [
        extension for extension in extensions
        if isinstance(extension, dict)
        and extension.get("url") == RETRACTION_NATIVE_RECORD_IDENTIFIER_EXTENSION
    ] if isinstance(extensions, list) else []
    if not carried:
        return
    location = f"Provenance.target[{target_index}].extension"
    if len(carried) != 1:
        raise contract_failure(
            "mobile-retraction.native-record-identifier",
            location,
            f"{label} may carry at most one native record identifier",
        )
    identifier = carried[0].get("valueIdentifier")
    if not isinstance(identifier, dict) or set(carried[0]) != {"url", "valueIdentifier"}:
        raise contract_failure(
            "mobile-retraction.native-record-identifier",
            location,
            f"{label} native record identifier must be one valueIdentifier",
        )
    system = identifier.get("system")
    value = identifier.get("value")
    try:
        require_absolute_uri(system, "native record identifier system")
    except ExchangeProtocolError as error:
        raise contract_failure(
            "mobile-retraction.native-record-identifier",
            f"{location}.valueIdentifier.system",
            f"{label} native record identifier system must be an absolute URI",
        ) from error
    if not isinstance(value, str) or not value:
        raise contract_failure(
            "mobile-retraction.native-record-identifier",
            f"{location}.valueIdentifier.value",
            f"{label} native record identifier must carry the exact native value",
        )
    codings = (identifier.get("type") or {}).get("coding") or []
    if any(
        isinstance(coding, dict) and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
        for coding in codings
    ):
        raise contract_failure(
            "mobile-retraction.native-record-identifier",
            f"{location}.valueIdentifier.type",
            f"{label} native record identifier is source-native traceability and never "
            "carries a Grove identifier-role coding",
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
    validate_healthkit_metadata(resource, label)
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


def _extension_identifiers(resource: dict[str, Any], url: str) -> list[Any]:
    """Return the valueIdentifier of every top-level extension with this url."""
    extensions = resource.get("extension")
    if not isinstance(extensions, list):
        return []
    return [
        extension.get("valueIdentifier")
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == url
    ]


def _same_pair(identifier: Any, pair: tuple[str, str]) -> bool:
    return (
        isinstance(identifier, dict)
        and identifier.get("system") == pair[0]
        and identifier.get("value") == pair[1]
    )


def validate_entry_key(
    entry: dict[str, Any],
    index: int,
    is_active: bool,
    label: str,
) -> tuple[str, str, str]:
    """Check one entry key's selection and shape; return its role, system and value.

    The key follows entryIdentity.selection. Keys derived from content are recomputed later, by
    validate_derived_keys, and only under the published test key.
    """
    entry_label = f"{label} entry[{index}]"
    resource = entry["resource"]
    resource_type = resource.get("resourceType")
    extensions = entry.get("extension", [])
    identities = [
        extension.get("valueIdentifier")
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == ENTRY_IDENTIFIER_EXTENSION
    ] if isinstance(extensions, list) else []
    if len(identities) != 1:
        raise contract_failure(
            "mobile-exchange.entry-key",
            f"Bundle.entry[{index}]",
            f"{entry_label} must have exactly one Grove exchange entry key",
        )
    key = identities[0]
    key_location = f"Bundle.entry[{index}].extension.valueIdentifier"
    system, value = complete_identifier(key, f"{entry_label} entry key")
    role = identifier_role(key, f"{entry_label} entry key", key_location)

    if resource_type == "Provenance":
        expected_role = PROVENANCE_KEY_ROLES["active" if is_active else "retraction"]
        if role != expected_role:
            raise contract_failure(
                "mobile-exchange.entry-key-selection",
                key_location,
                f"{entry_label} Provenance must be keyed by its {expected_role} Identifier",
            )
        if HMAC_IDENTITY.fullmatch(value) is None:
            raise contract_failure(
                "mobile-exchange.record-version-key" if is_active
                else "mobile-retraction.retraction-key",
                f"{key_location}.value",
                f"{entry_label} {expected_role} key is not a canonical Grove v0 HMAC identity",
            )
        versions = _extension_identifiers(resource, RECORD_VERSION_EXTENSION)
        if is_active and (
            len(versions) != 1
            or not _same_pair(versions[0], (system, value))
            or role_of_typed(versions[0]) != expected_role
        ):
            raise contract_failure(
                "mobile-exchange.record-version-extension",
                f"Bundle.entry[{index}].resource.extension",
                f"{entry_label} conversion Provenance must repeat its record-version entry key "
                "in exactly one grove-record-version extension",
            )
        if not is_active and versions:
            raise contract_failure(
                "mobile-exchange.record-version-extension",
                f"Bundle.entry[{index}].resource.extension",
                f"{entry_label} retraction Provenance carries no grove-record-version extension",
            )
        return role, system, value

    snapshots = _extension_identifiers(resource, CONTEXT_SNAPSHOT_EXTENSION)
    if resource_type == "QuestionnaireResponse":
        if role != "context-snapshot":
            raise contract_failure(
                "mobile-exchange.entry-key-selection",
                key_location,
                f"{entry_label} QuestionnaireResponse must be keyed by its context-snapshot "
                "Identifier, never by its submission identifier",
            )
        if HMAC_IDENTITY.fullmatch(value) is None:
            raise contract_failure(
                "mobile-exchange.content-snapshot-key",
                f"{key_location}.value",
                f"{entry_label} context-snapshot key is not a canonical Grove v0 HMAC identity",
            )
        if len(snapshots) != 1 or not _same_pair(snapshots[0], (system, value)):
            raise contract_failure(
                "mobile-exchange.context-snapshot-extension",
                f"Bundle.entry[{index}].resource.extension",
                f"{entry_label} QuestionnaireResponse must repeat its context-snapshot entry key "
                "in exactly one grove-context-snapshot extension",
            )
        if role_of_typed(snapshots[0]) != "context-snapshot":
            raise contract_failure(
                "mobile-exchange.context-snapshot-extension",
                f"Bundle.entry[{index}].resource.extension",
                f"{entry_label} grove-context-snapshot must carry the context-snapshot role",
            )
        return role, system, value
    if snapshots:
        raise contract_failure(
            "mobile-exchange.context-snapshot-extension",
            f"Bundle.entry[{index}].resource.extension",
            f"{entry_label} {resource_type} carries a grove-context-snapshot extension, which "
            "only a QuestionnaireResponse carries",
        )

    snapshot_role = SNAPSHOT_ROLE_BY_RESOURCE_TYPE.get(resource_type)
    resource_label = f"{entry_label}.resource"
    if snapshot_role is not None and snapshot_role not in typed_resource_identifiers(
        resource, resource_label
    ):
        raise contract_failure(
            "mobile-exchange.content-snapshot-key",
            f"Bundle.entry[{index}].resource.identifier",
            f"{entry_label} shared {resource_type} must carry its typed {snapshot_role} "
            "Identifier",
        )
    selected = selected_entry_identifier(resource, resource_label)
    if selected is None:
        raise contract_failure(
            "mobile-exchange.entry-key-selection",
            key_location,
            f"{entry_label} {resource_type} carries no typed business identity to key it",
        )
    selected_role, selected_pair = selected
    if snapshot_role is not None and selected_role != snapshot_role:
        raise contract_failure(
            "mobile-exchange.entry-key-selection",
            key_location,
            f"{entry_label} shared {resource_type} must be keyed by its {snapshot_role} "
            f"Identifier, not its {selected_role} Identifier",
        )
    if role != selected_role or (system, value) != selected_pair:
        raise contract_failure(
            "mobile-exchange.entry-key-selection",
            key_location,
            f"{entry_label} entry key is not the resource's highest-priority typed identifier",
        )
    return role, system, value


def role_of_typed(identifier: Any) -> str | None:
    """Return the one Grove role of an Identifier, or None when it carries none or several."""
    if not isinstance(identifier, dict):
        return None
    identifier_type = identifier.get("type")
    codings = identifier_type.get("coding", []) if isinstance(identifier_type, dict) else []
    roles = [
        coding.get("code") for coding in codings
        if isinstance(coding, dict) and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
    ] if isinstance(codings, list) else []
    return roles[0] if len(roles) == 1 else None


def has_grove_role(identifier: Any) -> bool:
    """Whether an Identifier carries any coding from the Grove identifier-role system."""
    identifier_type = identifier.get("type") if isinstance(identifier, dict) else None
    codings = identifier_type.get("coding", []) if isinstance(identifier_type, dict) else []
    return isinstance(codings, list) and any(
        isinstance(coding, dict) and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
        for coding in codings
    )


def patient_pseudonym(patient: dict[str, Any]) -> tuple[str, str] | None:
    """The pseudonym of a Patient entry: its one identifier without a Grove role, when complete.

    Complete means a non-empty value under an absolute-URI system, as complete_identifier requires.

    A Patient whose identifiers without a Grove role are none, several, or incomplete names no
    pseudonym (lifecycle.active.studyContext.subject), so it can't state the subject a key was
    minted over.
    """
    identifiers = patient.get("identifier", [])
    plain = [
        identifier for identifier in identifiers
        if isinstance(identifier, dict) and not has_grove_role(identifier)
    ] if isinstance(identifiers, list) else []
    if len(plain) != 1:
        return None
    try:
        return complete_identifier(plain[0], "Patient pseudonym")
    except ProducerValidationError:
        return None


def validate_patient_entries(entry_resources: list[dict[str, Any]], label: str) -> None:
    """Every Patient entry names exactly one pseudonym, under a system the protocol doesn't reserve."""
    reserved = REFERENCE_POLICY["identifierOnlyPatient"]["reservedSystems"]
    for index, candidate in enumerate(entry_resources):
        if candidate.get("resourceType") != "Patient":
            continue
        pseudonym = patient_pseudonym(candidate)
        if pseudonym is None or pseudonym[0] in reserved:
            raise contract_failure(
                "mobile-exchange.patient-pseudonym",
                f"Bundle.entry[{index}].resource.identifier",
                f"{label} entry[{index}] Patient must carry exactly one complete identifier "
                "without a Grove role, the deployment's pseudonym, under a system the protocol "
                "doesn't reserve",
            )


def classify_lifecycle(
    provenances: list[tuple[int, dict[str, Any]]], label: str
) -> tuple[list[tuple[int, dict[str, Any]]], list[tuple[int, dict[str, Any]]], int]:
    """Split Provenances into transform and retraction assertions; count unclassified ones."""
    transforms: list[tuple[int, dict[str, Any]]] = []
    retractions: list[tuple[int, dict[str, Any]]] = []
    unclassified = 0
    for index, candidate in provenances:
        activity = candidate.get("activity", {})
        codings = activity.get("coding", []) if isinstance(activity, dict) else []
        codings = codings if isinstance(codings, list) else []
        iso_codings = [
            coding for coding in codings
            if isinstance(coding, dict) and coding.get("system") == ISO_LIFECYCLE_SYSTEM
        ]
        grove_codings = [
            coding for coding in codings
            if isinstance(coding, dict) and coding.get("system") == LIFECYCLE_EVENT_SYSTEM
        ]
        if not iso_codings and not grove_codings:
            unclassified += 1
            continue
        lifecycle_label = f"{label} entry[{index}] Provenance activity"
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
            transforms.append((index, candidate))
        else:
            if grove_codings[0].get("code") != SOURCE_RECORD_RETRACTED:
                raise ProducerValidationError(
                    f"{lifecycle_label} has an unadmitted Grove lifecycle code"
                )
            retractions.append((index, candidate))
    return transforms, retractions, unclassified


def subject_statement(
    reference: Any, resources_by_full_url: dict[str, dict[str, Any]]
) -> tuple[str, ...] | None:
    """Return the subject one governed Patient reference states.

    A logical reference states its pseudonym pair, and a literal reference the referenced Patient
    entry's pseudonym (patient_pseudonym), which validate_patient_entries already required.
    """
    if not isinstance(reference, dict):
        return None
    literal = reference.get("reference")
    if isinstance(literal, str):
        patient = resources_by_full_url.get(literal)
        if not isinstance(patient, dict) or patient.get("resourceType") != "Patient":
            return None
        pseudonym = patient_pseudonym(patient)
        return None if pseudonym is None else ("pair", *pseudonym)
    identifier = reference.get("identifier")
    if isinstance(identifier, dict):
        system, value = complete_identifier(identifier, "subject identifier")
        return ("pair", system, value)
    return None


def record_unit(
    start: set[str],
    resources_by_full_url: dict[str, dict[str, Any]],
) -> set[str]:
    """Return the directed literal closure of a record unit (bundle.recordUnit)."""
    research_subjects = {
        full_url: resource for full_url, resource in resources_by_full_url.items()
        if resource.get("resourceType") == "ResearchSubject"
    }
    unit: set[str] = set()
    pending = [full_url for full_url in start if full_url in resources_by_full_url]
    while True:
        while pending:
            current = pending.pop()
            if current in unit:
                continue
            unit.add(current)
            for reference in all_reference_nodes(resources_by_full_url[current]):
                target = reference.get("reference")
                if target in resources_by_full_url and target not in unit:
                    pending.append(target)
        # A ResearchSubject joins every record whose closure contains the study it references.
        joining = [
            full_url for full_url, subject in research_subjects.items()
            if full_url not in unit
            and isinstance(subject.get("study"), dict)
            and subject["study"].get("reference") in unit
        ]
        if not joining:
            return unit
        pending.extend(joining)


def validate_connected(
    lifecycle: list[tuple[int, dict[str, Any]]],
    supporting_types: frozenset[str],
    full_url_by_index: dict[int, str],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    connected: set[str] = set()
    for index, provenance in lifecycle:
        targets = provenance.get("target")
        start = {full_url_by_index[index]}
        if isinstance(targets, list):
            start.update(
                target["reference"] for target in targets
                if isinstance(target, dict) and isinstance(target.get("reference"), str)
            )
        connected |= record_unit(start, resources_by_full_url)
    disconnected = [
        full_url
        for full_url, candidate in resources_by_full_url.items()
        if candidate.get("resourceType") in supporting_types and full_url not in connected
    ]
    if disconnected:
        raise contract_failure(
            "mobile-support.connected",
            "Bundle.entry",
            f"{label} supporting resources lie in no record unit: "
            f"{', '.join(sorted(disconnected))}",
        )


def validate_active_records(
    transforms: list[tuple[int, dict[str, Any]]],
    entry_resources: list[dict[str, Any]],
    full_url_by_index: dict[int, str],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Partition an active Bundle into records: one conversion Provenance and its outputs each."""
    record_by_source: dict[tuple[str, str], int] = {}
    source_by_record: dict[int, tuple[str, str]] = {}
    for index, provenance in transforms:
        source = exact_source_entity(provenance, f"{label} entry[{index}] transform Provenance")
        if source in record_by_source:
            raise contract_failure(
                "mobile-exchange.distinct-source-record",
                f"Bundle.entry[{index}].resource.entity",
                f"{label} entry[{index}] names the source record of "
                f"entry[{record_by_source[source]}]; two versions of one source record travel "
                "in different Bundles",
            )
        record_by_source[source] = index
        source_by_record[index] = source
    outputs = {
        full_url: candidate for full_url, candidate in resources_by_full_url.items()
        if candidate.get("resourceType") in ACTIVE_OUTPUT_RESOURCE_TYPES
    }
    if not outputs:
        raise contract_failure(
            "mobile-exchange.output-required",
            "Bundle.entry",
            f"{label} active Bundle must contain at least one output",
        )
    record_by_output: dict[str, int] = {}
    targets_by_record: dict[int, list[str]] = {}
    for index, provenance in transforms:
        targets = provenance.get("target")
        if not isinstance(targets, list) or not targets:
            raise contract_failure(
                "mobile-exchange.output-required",
                f"Bundle.entry[{index}].resource.target",
                f"{label} entry[{index}] conversion Provenance targets no output",
            )
        target_urls: list[str] = []
        for target_index, target in enumerate(targets):
            reference = target.get("reference") if isinstance(target, dict) else None
            if not isinstance(reference, str) or reference not in outputs:
                raise contract_failure(
                    "mobile-exchange.provenance-targets",
                    "Provenance.target",
                    f"{label} entry[{index}] Provenance.target[{target_index}] is not a literal "
                    "reference to an active output",
                )
            if reference in target_urls:
                raise contract_failure(
                    "mobile-exchange.output-targeted-once",
                    f"Bundle.entry[{index}].resource.target[{target_index}]",
                    f"{label} entry[{index}] conversion Provenance repeats the target {reference}",
                )
            target_urls.append(reference)
        targets_by_record[index] = target_urls
    for index, target_urls in targets_by_record.items():
        for reference in target_urls:
            if reference in record_by_output:
                raise contract_failure(
                    "mobile-exchange.output-targeted-once",
                    "Bundle.entry",
                    f"{label} output {reference} is targeted by entry[{record_by_output[reference]}] "
                    f"and entry[{index}]",
                )
            record_by_output[reference] = index
    untargeted = sorted(set(outputs) - set(record_by_output))
    if untargeted:
        raise contract_failure(
            "mobile-exchange.output-targeted-once",
            "Bundle.entry",
            f"{label} outputs are targeted by no conversion Provenance: {', '.join(untargeted)}",
        )
    for index, target_urls in targets_by_record.items():
        for reference in target_urls:
            typed = typed_resource_identifiers(outputs[reference], f"{label} output {reference}")
            if typed.get("source-record") != source_by_record[index]:
                raise contract_failure(
                    "mobile-exchange.provenance-targets",
                    "Provenance.target",
                    f"{label} entry[{index}] conversion Provenance targets an output of another "
                    "source record",
                )

    # Decision 7: a literal reference stays inside its record or reaches a shared node. A
    # conversion Provenance is neither an output nor a shared node, so nothing references one;
    # a reference to another record's Provenance would pull that whole record into this one.
    record_by_provenance = {full_url_by_index[index]: index for index, _ in transforms}
    for entry_index, candidate in enumerate(entry_resources):
        referrer = full_url_by_index[entry_index]
        own_record = record_by_output.get(referrer, record_by_provenance.get(referrer))
        for reference_path, reference in all_reference_nodes_with_paths(candidate):
            if reference["reference"] in record_by_provenance:
                raise provenance_reference_failure(entry_index, reference_path, label)
            target_record = record_by_output.get(reference["reference"])
            if target_record is not None and target_record != own_record:
                raise contract_failure(
                    "mobile-exchange.cross-record-reference",
                    f"Bundle.entry[{entry_index}].resource.{reference_path}.reference",
                    f"{label} entry[{entry_index}] references an output of another record; "
                    "a reference between records is identifier-only",
                )

    statements: set[tuple[str, ...]] = set()
    for candidate in outputs.values():
        for resource_type, path in OUTPUT_SUBJECT_PATHS:
            if candidate.get("resourceType") == resource_type:
                statement = subject_statement(candidate.get(path), resources_by_full_url)
                if statement is not None:
                    statements.add(statement)
    if len(statements) > 1:
        raise contract_failure(
            "mobile-exchange.single-subject",
            "Bundle.entry",
            f"{label} records state {len(statements)} different subjects",
        )


def provenance_reference_failure(
    entry_index: int, reference_path: str, label: str
) -> ProducerValidationError:
    """A literal reference to a lifecycle Provenance, which is neither an output nor a shared node."""
    return contract_failure(
        "mobile-exchange.cross-record-reference",
        f"Bundle.entry[{entry_index}].resource.{reference_path}.reference",
        f"{label} entry[{entry_index}] references a lifecycle Provenance; a literal reference "
        "reaches only an output of its own record or a shared node",
    )


def validate_patients_name_the_subject(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Every Patient entry of an active Bundle names the one subject its records state.

    A Patient that no output's subject reaches, such as one a QuestionnaireResponse names, is held
    to the same subject. It runs after connectivity, so a disconnected Patient reports that first.
    """
    subject = bundle_subject(entry_resources, resources_by_full_url)
    if subject is None:
        return
    for index, candidate in enumerate(entry_resources):
        if candidate.get("resourceType") == "Patient" and patient_pseudonym(candidate) != subject:
            raise contract_failure(
                "mobile-exchange.patient-pseudonym",
                f"Bundle.entry[{index}].resource.identifier",
                f"{label} entry[{index}] Patient names another pseudonym than the subject its "
                "Bundle's records state",
            )


def validate_retraction_references(
    retractions: list[tuple[int, dict[str, Any]]],
    entry_resources: list[dict[str, Any]],
    full_url_by_index: dict[int, str],
    label: str,
) -> None:
    """literalClosure in a retraction Bundle: nothing references a retraction Provenance."""
    provenance_urls = {full_url_by_index[index] for index, _ in retractions}
    for entry_index, candidate in enumerate(entry_resources):
        for reference_path, reference in all_reference_nodes_with_paths(candidate):
            if reference["reference"] in provenance_urls:
                raise provenance_reference_failure(entry_index, reference_path, label)


def validate_retraction_records(
    retractions: list[tuple[int, dict[str, Any]]], label: str
) -> None:
    """Check each retraction assertion; each addresses one whole source record once."""
    sources: dict[tuple[str, str], int] = {}
    for index, provenance in retractions:
        provenance_label = f"{label} entry[{index}] retraction"
        targets = provenance.get("target")
        if not isinstance(targets, list) or not targets:
            raise contract_failure(
                "mobile-retraction.target-required",
                "Provenance.target",
                f"{provenance_label} must identify at least one target",
            )
        seen_targets: set[tuple[str, str]] = set()
        source_record_targets: list[tuple[int, tuple[str, str]]] = []
        for target_index, target in enumerate(targets):
            target_label = f"{provenance_label} target[{target_index}]"
            if not isinstance(target, dict) or "reference" in target:
                raise ProducerValidationError(
                    f"{target_label} must be a logical Reference without a literal reference"
                )
            identifier = target.get("identifier")
            role = identifier_role(
                identifier,
                f"{target_label}.identifier",
                f"Provenance.target[{target_index}].identifier",
            )
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
                raise contract_failure(
                    "mobile-retraction.distinct-target",
                    f"Provenance.target[{target_index}].identifier",
                    f"{provenance_label} repeats a retraction target",
                )
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
                if target_role == SOURCE_RECORD_TARGET_ROLE:
                    # Any other identity, an output's included, fails to repeat the source entity.
                    raise contract_failure(
                        "mobile-retraction.source-record-target",
                        f"Provenance.target[{target_index}].identifier",
                        f"{target_label} role {target_role} requires the "
                        f"{target_contract['identifierRole']} identifier role",
                    )
                raise ProducerValidationError(
                    f"{target_label} role {target_role} requires the "
                    f"{target_contract['identifierRole']} identifier role"
                )
            if target_role == SOURCE_RECORD_TARGET_ROLE:
                # The source record as a whole is no one resource, so its target is untyped,
                # stands alone, and is checked against the source entity once that is known.
                if "type" in target:
                    raise contract_failure(
                        "mobile-retraction.source-record-target",
                        f"Provenance.target[{target_index}].type",
                        f"{target_label} role {target_role} must not state a resource type",
                    )
                if len(targets) != 1:
                    raise contract_failure(
                        "mobile-retraction.source-record-target",
                        "Provenance.target",
                        f"{target_label} role {target_role} must be the only retraction target",
                    )
                source_record_targets.append((target_index, pair))
            elif not isinstance(target.get("type"), str) or not target["type"]:
                raise ProducerValidationError(f"{target_label} must state its resource type")
            elif target["type"] not in target_contract["resourceTypes"]:
                raise contract_failure(
                    "mobile-retraction.role-target-type",
                    f"Provenance.target[{target_index}].type",
                    f"{target_label} role {target_role} does not admit resource type "
                    f"{target['type']}",
                )
            validate_retraction_native_record_identifier(
                target, target_index, target_label
            )
        source = exact_source_entity(provenance, f"{provenance_label} Provenance")
        for target_index, pair in source_record_targets:
            if pair != source:
                raise contract_failure(
                    "mobile-retraction.source-record-target",
                    f"Provenance.target[{target_index}].identifier",
                    f"{provenance_label} target[{target_index}] must repeat the source-record "
                    "Identifier of the Provenance source entity",
                )
        if source in sources:
            raise contract_failure(
                "mobile-retraction.provenance",
                f"Bundle.entry[{index}].resource.entity",
                f"{provenance_label} retracts the source record of entry[{sources[source]}] "
                "under the same record-retraction key",
            )
        sources[source] = index


def bundle_subject(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
) -> tuple[str, str] | None:
    """Return the one subject pair the Bundle's records state, if they state exactly one."""
    statements = {
        statement
        for candidate in entry_resources
        for resource_type, path in OUTPUT_SUBJECT_PATHS
        if candidate.get("resourceType") == resource_type
        and (statement := subject_statement(candidate.get(path), resources_by_full_url))
        is not None
    }
    if len(statements) != 1:
        return None
    statement = next(iter(statements))
    return (statement[1], statement[2]) if statement[0] == "pair" else None


def validate_derived_keys(
    lossless: Any,
    is_active: bool,
    keys: list[tuple[str, str, str]],
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Canonicalize every resource and recompute every content-derived key under the test key.

    A key under any other key id is checked for shape only: a receiver never holds a
    deployment's key, so it compares record versions and never recomputes them.
    """
    lossless_entries = lossless.get("entry") if isinstance(lossless, dict) else None
    if not isinstance(lossless_entries, list) or len(lossless_entries) != len(entry_resources):
        raise contract_failure(
            "mobile-exchange.canonical-json",
            "Bundle.entry",
            f"{label} lossless form does not match the parsed Bundle",
        )
    lossless_resources = [entry.get("resource") for entry in lossless_entries]
    for index, candidate in enumerate(lossless_resources):
        try:
            canonical_bytes(candidate)
        except CanonicalJSONError as error:
            raise contract_failure(
                "mobile-exchange.canonical-json",
                f"Bundle.entry[{index}].resource",
                f"{label} entry[{index}] has no grove-canonical-json-v0 form: {error}",
            ) from error

    def recomputes(value: str) -> tuple[str, str] | None:
        key_id, epoch, _ = parse_hmac_identity(value)
        return (key_id, epoch) if key_id == TEST_KEY_ID else None

    subject = bundle_subject(entry_resources, resources_by_full_url)
    for index, (role, _system, value) in enumerate(keys):
        candidate = entry_resources[index]
        resource_type = candidate.get("resourceType")
        snapshot_role = SNAPSHOT_ROLE_BY_RESOURCE_TYPE.get(resource_type)
        if resource_type == "QuestionnaireResponse":
            snapshot_role = "context-snapshot"
        if snapshot_role is None or role != snapshot_role:
            continue
        scope = recomputes(value)
        if scope is None:
            continue
        if subject is None:
            if not is_active:
                # A retraction states no subject, so its test-key Device snapshots can't be
                # recomputed here (Conformance/README.md).
                continue
            raise contract_failure(
                "mobile-exchange.content-snapshot-key",
                f"Bundle.entry[{index}].extension.valueIdentifier.value",
                f"{label} entry[{index}] {snapshot_role} key is under the test key, but the "
                "Bundle's records state no one subject to recompute it over",
            )
        if resource_type == "Device":
            profiles = candidate.get("meta", {}).get("profile", [])
            node_roles = {DEVICE_NODE_ROLES[profile] for profile in profiles if profile in DEVICE_NODE_ROLES}
            if len(node_roles) != 1:
                continue
            derive, node_role = device_snapshot_identity, next(iter(node_roles))
        else:
            derive, node_role = context_snapshot_identity, CONTEXT_NODE_ROLES[resource_type]
        try:
            expected = derive(
                key=TEST_KEY, key_id=scope[0], epoch=scope[1], subject_system=subject[0],
                subject_value=subject[1], node_role=node_role,
                content_digest=content_digest(lossless_resources[index]),
            )
        except (ExchangeProtocolError, CanonicalJSONError) as error:
            raise contract_failure(
                "mobile-exchange.content-snapshot-key",
                f"Bundle.entry[{index}].extension.valueIdentifier.value",
                f"{label} entry[{index}] content snapshot cannot be recomputed: {error}",
            ) from error
        if value != expected:
            raise contract_failure(
                "mobile-exchange.content-snapshot-key",
                f"Bundle.entry[{index}].extension.valueIdentifier.value",
                f"{label} entry[{index}] {snapshot_role} key does not recompute from the "
                f"{resource_type}'s canonical content under the test key",
            )

    for index, (role, _system, value) in enumerate(keys):
        candidate = entry_resources[index]
        if candidate.get("resourceType") != "Provenance":
            continue
        scope = recomputes(value)
        if scope is None:
            continue
        source = exact_source_entity(candidate, f"{label} entry[{index}] Provenance")
        location = f"Bundle.entry[{index}].extension.valueIdentifier.value"
        if is_active:
            try:
                outputs = [
                    lossless_resources[resources_index]
                    for resources_index in _target_indexes(candidate, entry_resources, resources_by_full_url)
                ]
                expected = record_version_identity(
                    key=TEST_KEY, key_id=scope[0], epoch=scope[1],
                    source_record_system=source[0], source_record_value=source[1],
                    record_content_digest=record_content_digest(lossless_resources[index], outputs),
                )
            except (ExchangeProtocolError, CanonicalJSONError) as error:
                raise contract_failure(
                    "mobile-exchange.record-version-key", location,
                    f"{label} entry[{index}] record version cannot be recomputed: {error}",
                ) from error
            if value != expected:
                raise contract_failure(
                    "mobile-exchange.record-version-key", location,
                    f"{label} entry[{index}] record-version key does not recompute from its "
                    "source record and the canonical content of its Provenance and outputs",
                )
        else:
            try:
                expected = record_retraction_identity(
                    key=TEST_KEY, key_id=scope[0], epoch=scope[1],
                    source_record_system=source[0], source_record_value=source[1],
                )
            except ExchangeProtocolError as error:
                raise contract_failure(
                    "mobile-retraction.retraction-key", location,
                    f"{label} entry[{index}] record-retraction key cannot be recomputed: {error}",
                ) from error
            if value != expected:
                raise contract_failure(
                    "mobile-retraction.retraction-key", location,
                    f"{label} entry[{index}] record-retraction key is not the key of its "
                    "source-record entity under the test key",
                )


def _target_indexes(
    provenance: dict[str, Any],
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
) -> list[int]:
    """Return the entry index of each Provenance.target, in target order."""
    index_by_resource = {id(candidate): index for index, candidate in enumerate(entry_resources)}
    return [
        index_by_resource[id(resources_by_full_url[target["reference"]])]
        for target in provenance["target"]
    ]


def validate_exchange_bundle(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
    lossless_resource: Any = None,
) -> None:
    """Validate one exchange Bundle; lossless_resource is its loads_lossless tree, if read."""
    profiles = resource.get("meta", {}).get("profile", [])
    is_active = EXCHANGE_BUNDLE_PROFILE in profiles
    is_retraction = RETRACTION_BUNDLE_PROFILE in profiles
    if not is_active and not is_retraction:
        return
    if is_active and is_retraction:
        raise contract_failure(
            "mobile-exchange.bundle-profile",
            "Bundle.meta.profile",
            f"{label} cannot claim both active and retraction exchange profiles",
        )
    if resource.get("type") != "collection":
        raise ProducerValidationError(f"{label} exchange Bundle must have type collection")
    if "identifier" in resource:
        # An optional, untyped transport id with no format: it names no record and enters
        # no identity. Any type is refused, a Grove identifier role or another.
        if not isinstance(resource["identifier"], dict):
            raise ProducerValidationError(f"{label} Bundle.identifier must be an Identifier")
        if "type" in resource["identifier"]:
            raise contract_failure(
                "mobile-exchange.bundle-identifier",
                "Bundle.identifier",
                f"{label} Bundle.identifier is an untyped transport id and carries no type, "
                "Grove identifier role or other",
            )
    validate_identity_system_role(resource, label)
    entries = resource.get("entry")
    if not isinstance(entries, list) or not entries:
        raise contract_failure(
            "mobile-exchange.entry-required",
            "Bundle.entry",
            f"{label} exchange Bundle must contain entries",
        )
    full_urls: set[str] = set()
    entry_resources: list[dict[str, Any]] = []
    keys: list[tuple[str, str, str]] = []
    full_url_by_index: dict[int, str] = {}
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
                    "admitted by the retraction Bundle profile",
                )
            raise contract_failure(
                "mobile-exchange.entry-resource-type",
                f"Bundle.entry[{index}].resource.resourceType",
                f"{label} entry[{index}] resource type {resource_type!r} is not admitted "
                "by the active exchange Bundle profile",
            )
        if "contained" in entry_resource:
            raise contract_failure(
                "mobile-exchange.contained-resource-prohibited",
                f"Bundle.entry[{index}].resource.contained",
                f"{label} entry[{index}] contains a Resource; Mobile exchange Bundles require "
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
        role, system, value = validate_entry_key(entry, index, is_active, label)
        key_location = f"Bundle.entry[{index}].extension.valueIdentifier"
        expected = expected_entry_full_url(system, value)
        if entry.get("fullUrl") != expected:
            raise contract_failure(
                "mobile-exchange.deterministic-full-url",
                f"Bundle.entry[{index}].fullUrl",
                f"{label} entry[{index}] fullUrl is not the deterministic UUID URN",
            )
        if expected in full_urls:
            raise contract_failure(
                "mobile-exchange.distinct-entry-key",
                key_location,
                f"{label} entry[{index}] repeats the entry key behind fullUrl {expected}",
            )
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
        keys.append((role, system, value))
        full_url_by_index[index] = expected
        resources_by_full_url[expected] = entry_resource

    if is_retraction:
        for index, candidate in enumerate(entry_resources):
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
                        f"{label} entry[{index}] retraction target[{target_index}] must be a "
                        "typed logical Reference without a literal reference",
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

    validate_patient_entries(entry_resources, label)

    provenances = [
        (index, candidate) for index, candidate in enumerate(entry_resources)
        if candidate.get("resourceType") == "Provenance"
    ]
    transforms, retractions, unclassified = classify_lifecycle(provenances, label)
    if is_active:
        if not transforms or retractions or unclassified:
            raise contract_failure(
                "mobile-exchange.transform-provenance",
                "Bundle.entry",
                f"{label} active Bundle must contain at least one transform Provenance, one for "
                "each record, and no retraction",
            )
        validate_active_records(
            transforms, entry_resources, full_url_by_index, resources_by_full_url, label
        )
        if ACTIVE_ENTRY_POLICY["supportingResourcesMustBeConnected"]:
            validate_connected(
                transforms, ACTIVE_SUPPORTING_RESOURCE_TYPES, full_url_by_index,
                resources_by_full_url, label,
            )
        validate_patients_name_the_subject(entry_resources, resources_by_full_url, label)
        validate_governed_source_identifiers(entry_resources, label)
        validate_health_connect_output_graph(entry_resources, resources_by_full_url, label)
        validate_healthkit_ecg_output_graph(entry_resources, resources_by_full_url, label)
        validate_adapter_provenance_graph(entry_resources, resources_by_full_url, label)
    else:
        if not retractions or transforms or unclassified:
            raise contract_failure(
                "mobile-retraction.provenance",
                "Bundle.entry",
                f"{label} retraction Bundle must contain at least one retraction Provenance "
                "and no transform",
            )
        validate_retraction_records(retractions, label)
        validate_retraction_references(retractions, entry_resources, full_url_by_index, label)
        validate_connected(
            retractions, frozenset({"Device"}), full_url_by_index, resources_by_full_url, label
        )

    validate_adapter_companion_graphs(entry_resources, resources_by_full_url, label)
    try:
        lossless = lossless_tree(resource) if lossless_resource is None else lossless_resource
    except CanonicalJSONError as error:
        raise contract_failure(
            "mobile-exchange.canonical-json",
            "Bundle",
            f"{label} has no grove-canonical-json-v0 form: {error}",
        ) from error
    validate_derived_keys(lossless, is_active, keys, entry_resources, resources_by_full_url, label)


def validate_adapter_companion_graphs(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Close the SensorKit hybrid and Health Connect glucose companion graphs."""
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
    lossless_resource: Any = None,
) -> list[dict[str, str]]:
    """Return the one stable structural diagnostic used by the cross-SDK corpus."""
    try:
        validate_exchange_bundle(resource, label, active_adapter_profiles, lossless_resource)
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
