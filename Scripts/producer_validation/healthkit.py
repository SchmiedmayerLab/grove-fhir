"""HealthKit-specific lineage, ECG resource, and output-graph validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

from .context import (
    CATALOG_ROOT, HEALTHKIT_CLINICAL_RECORD_PROFILE,
    HEALTHKIT_ECG_AVERAGE_HEART_RATE_PROFILE, HEALTHKIT_ECG_PROFILE,
    HEALTHKIT_OBSERVATION_PROFILE, HEALTHKIT_RECORDING_PROFILE,
    HMAC_IDENTITY, SAMPLED_DECIMAL,
)
from .diagnostics import ProducerValidationError, contract_failure
from .identity import identifier_role, typed_resource_identifiers
from .io import read_json
from .payloads import parse_fhir_instant
from .profiles import codeable_concept_codings
from .references import complete_identifier, extensions_with_url, validate_governed_reference


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
        HEALTHKIT_ECG_AVERAGE_HEART_RATE_PROFILE,
        *single_profiles,
    }
    if not isinstance(profiles, list) or not set(profiles) & healthkit_observation_profiles:
        return
    if any(not isinstance(profile, str) for profile in profiles) or len(profiles) != len(
        set(profiles)
    ):
        raise ProducerValidationError(f"{label} has invalid or repeated meta.profile")
    catalog = read_json(CATALOG_ROOT / "healthkit-adapter.json")
    source_extensions = extensions_with_url(
        resource, catalog["sourceTypeExtension"]["url"]
    )
    if (
        len(source_extensions) != 1
        or not isinstance(source_extensions[0].get("valueCode"), str)
        or not source_extensions[0]["valueCode"]
        or set(source_extensions[0]) != {"url", "valueCode"}
    ):
        raise ProducerValidationError(
            f"{label} must carry exactly one valueCode-only HealthKit source-type extension"
        )
    source_type = source_extensions[0]["valueCode"]
    rows = {
        row["sourceTypeIdentifier"]: row for row in catalog["rows"]
        if row["status"] == "supported"
    }
    row = rows.get(source_type)
    if row is None:
        raise ProducerValidationError(
            f"{label} uses a HealthKit source type without an admitted output contract"
        )
    row_profiles = set(row["profiles"])
    if (
        set(profiles) == {
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate",
            HEALTHKIT_ECG_AVERAGE_HEART_RATE_PROFILE,
        }
        and source_type == "HKDataTypeIdentifierElectrocardiogram"
    ):
        return
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

    catalog = read_json(CATALOG_ROOT / "healthkit-adapter.json")
    non_observation_profiles = {
        HEALTHKIT_RECORDING_PROFILE,
        HEALTHKIT_CLINICAL_RECORD_PROFILE,
        *(claim["profile"] for claim in claims["healthKitPlatformExclusiveResourceClaims"]),
    }
    matched_non_observation = set(profiles) & non_observation_profiles
    if matched_non_observation:
        source_extensions = extensions_with_url(
            resource, catalog["sourceTypeExtension"]["url"]
        )
        source_codes = [
            extension.get("valueCode")
            for extension in source_extensions
            if set(extension) == {"url", "valueCode"}
        ]
        admitted = {
            row["sourceTypeIdentifier"]: set(row.get("profiles", []))
            for row in catalog["rows"]
            if row["status"] == "platform-exclusive"
        }
        if (
            len(source_codes) != 1
            or source_codes[0] not in admitted
            or not matched_non_observation <= admitted[source_codes[0]]
        ):
            raise ProducerValidationError(
                f"{label} must carry exactly one admitted HealthKit source-type extension matching its direct profile"
            )

    if HEALTHKIT_CLINICAL_RECORD_PROFILE in profiles:
        admission = catalog["clinicalRecordAdmission"]
        if resource.get("resourceType") != "DocumentReference":
            raise ProducerValidationError(
                f"{label} HealthKit clinical record must be a FHIR R4 DocumentReference"
            )
        release_extensions = extensions_with_url(
            resource, admission["fhirRepresentation"]["extensionUrl"]
        )
        releases = [
            extension.get("valueCode")
            for extension in release_extensions
            if set(extension) == {"url", "valueCode"}
        ]
        if (
            len(release_extensions) != 1
            or len(releases) != 1
            or releases[0] not in admission["admittedFHIRReleases"]
        ):
            admitted = ", ".join(admission["admittedFHIRReleases"])
            raise ProducerValidationError(
                f"{label} must carry exactly one valueCode-only HealthKit clinical "
                f"FHIR release extension with an admitted HKFHIRVersion.fhirRelease "
                f"value ({admitted})"
            )
        contents = resource.get("content")
        if (
            not isinstance(contents, list)
            or len(contents) != 1
            or not isinstance(contents[0], dict)
            or not isinstance(contents[0].get("format"), dict)
            or contents[0]["format"].get("code") != admission["payloadFormat"]
        ):
            raise ProducerValidationError(
                f"{label} HealthKit clinical record must carry exactly one "
                f"{admission['payloadFormat']} payload"
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
    """Validate the native-R4 HealthKit ECG projection beyond FHIRPath precision."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return

    if HEALTHKIT_ECG_AVERAGE_HEART_RATE_PROFILE in profiles:
        codings = resource.get("code", {}).get("coding", [])
        loinc = [
            coding for coding in codings
            if isinstance(coding, dict)
            and coding.get("system") == "http://loinc.org"
            and coding.get("code") == "8867-4"
        ] if isinstance(codings, list) else []
        quantity = resource.get("valueQuantity")
        value = quantity.get("value") if isinstance(quantity, dict) else None
        if (
            len(loinc) != 1
            or not isinstance(quantity, dict)
            or quantity.get("system") != "http://unitsofmeasure.org"
            or quantity.get("code") != "/min"
            or isinstance(value, bool)
            or not isinstance(value, (int, float, Decimal))
            or Decimal(str(value)) <= 0
            or not isinstance(resource.get("effectivePeriod"), dict)
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG average heart rate must be a positive LOINC 8867-4 /min Period Observation"
            )
        derived = resource.get("derivedFrom")
        if (
            not isinstance(derived, list)
            or len(derived) != 1
            or not isinstance(derived[0], dict)
            or not isinstance(derived[0].get("reference"), str)
            or "identifier" in derived[0]
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG average heart rate must derive from exactly one resolving ECG Observation"
            )
        return

    if HEALTHKIT_ECG_PROFILE not in profiles:
        return

    ecg_claim = read_json(CATALOG_ROOT / "healthkit-adapter.json")[
        "sensorAdapterClaims"
    ]["electrocardiogram"]
    value_mappings = ecg_claim["closedValueMappings"]
    graph_claim = read_json(CATALOG_ROOT / "profile-claims.json")[
        "healthKitEcgGraphClaim"
    ]

    extension_urls = {
        "symptomsStatus": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-symptoms-status"
        ),
        "sourcePeriod": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-source-period"
        ),
    }
    obsolete_urls = {
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-classification",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-correlated-symptom",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-average-heart-rate",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-sampling-frequency",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-voltage-measurement-count",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-algorithm-version",
    }
    extensions = resource.get("extension", [])
    if not isinstance(extensions, list):
        raise ProducerValidationError(f"{label} has invalid ECG extensions")
    if any(
        isinstance(extension, dict) and extension.get("url") in obsolete_urls
        for extension in extensions
    ):
        raise ProducerValidationError(
            f"{label} HealthKit ECG uses an obsolete extension instead of native R4 structure"
        )

    def exact_extension(name: str) -> dict[str, Any]:
        matches = [
            extension
            for extension in extensions
            if isinstance(extension, dict)
            and extension.get("url") == extension_urls[name]
        ]
        if len(matches) != 1:
            raise ProducerValidationError(
                f"{label} HealthKit ECG must carry exactly one {name} extension"
            )
        return matches[0]

    interpretation = resource.get("interpretation")
    if not isinstance(interpretation, list) or len(interpretation) != 1:
        raise ProducerValidationError(
            f"{label} must carry exactly one HealthKit ECG interpretation"
        )
    interpretation_codings = codeable_concept_codings(
        interpretation[0], f"{label} HealthKit ECG interpretation"
    )
    classification_codes = [
        coding.get("code") for coding in interpretation_codings
        if coding.get("system") == value_mappings["classification"]["system"]
    ]
    admitted_classifications = {
        item["code"] for item in value_mappings["classification"]["values"]
    }
    if (
        len(interpretation_codings) != 1
        or len(classification_codes) != 1
        or classification_codes[0] not in admitted_classifications
    ):
        raise ProducerValidationError(f"{label} has an unknown HealthKit ECG classification")

    status = exact_extension("symptomsStatus")
    status_code = status.get("valueCode")
    admitted_statuses = {
        item["code"] for item in value_mappings["symptomsStatus"]["values"]
    }
    if status_code not in admitted_statuses:
        raise ProducerValidationError(f"{label} has an unknown HealthKit ECG symptoms status")

    symptom_claim = graph_claim["correlatedSymptoms"]
    members = resource.get(symptom_claim["r4Path"].split(".")[-1], [])
    symptom_cardinality = symptom_claim["cardinality"]
    symptom_maximum = symptom_cardinality["max"]
    if (
        not isinstance(members, list)
        or len(members) < symptom_cardinality["min"]
        or (symptom_maximum != "*" and len(members) > symptom_maximum)
    ):
        raise ProducerValidationError(f"{label} HealthKit ECG has invalid symptom members")
    conditioned = {
        item["status"]: item for item in symptom_claim["statusConditionedCardinality"]
    }
    status_cardinality = conditioned[status_code]
    status_maximum = status_cardinality["max"]
    if (
        len(members) < status_cardinality["min"]
        or (status_maximum != "*" and len(members) > status_maximum)
    ):
        raise ProducerValidationError(
            f"{label} HealthKit ECG correlated symptoms must agree with symptomsStatus"
        )
    seen_symptom_identifiers: set[tuple[str, str]] = set()
    waveform_output = typed_resource_identifiers(resource, label).get("source-output")
    for index, member in enumerate(members):
        if not isinstance(member, dict):
            raise ProducerValidationError(f"{label} HealthKit ECG symptom member is invalid")
        validate_governed_reference(
            member, {symptom_claim["targetType"]}, {}, f"{label}.hasMember[{index}]"
        )
        identifier = member.get("identifier")
        if (
            identifier_role(identifier, f"{label}.hasMember[{index}].identifier")
            != symptom_claim["identifierRole"]
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG symptom member must use a source-output Identifier"
            )
        pair = complete_identifier(identifier, f"{label}.hasMember[{index}].identifier")
        if HMAC_IDENTITY.fullmatch(pair[1]) is None or pair in seen_symptom_identifiers:
            raise ProducerValidationError(
                f"{label} HealthKit ECG has an invalid or repeated symptom source-output Identifier"
            )
        if waveform_output is not None and pair == waveform_output:
            raise ProducerValidationError(
                f"{label} HealthKit ECG symptom member must not reference the waveform itself"
            )
        seen_symptom_identifiers.add(pair)

    method = resource.get("method")
    if method is not None:
        method_codings = codeable_concept_codings(method, f"{label} HealthKit ECG method")
        algorithm_codes = [
            coding.get("code") for coding in method_codings
            if coding.get("system") == value_mappings["algorithmVersion"]["system"]
        ]
        admitted_algorithms = {
            item["code"] for item in value_mappings["algorithmVersion"]["values"]
        }
        if (
            len(method_codings) != 1
            or len(algorithm_codes) != 1
            or algorithm_codes[0] not in admitted_algorithms
        ):
            raise ProducerValidationError(f"{label} has an unknown HealthKit ECG algorithm version")

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
    dimensions = sampled.get("dimensions") if isinstance(sampled, dict) else None
    period = sampled.get("period") if isinstance(sampled, dict) else None
    tokens = re.split(r"\s+", data.strip()) if isinstance(data, str) and data.strip() else []
    if (
        dimensions != 1
        or isinstance(period, bool)
        or not isinstance(period, (int, float, Decimal))
        or Decimal(str(period)) <= 0
        or not tokens
        or any(SAMPLED_DECIMAL.fullmatch(token) is None for token in tokens)
    ):
        raise ProducerValidationError(
            f"{label} HealthKit ECG must carry one positive-period decimal SampledData channel"
        )
    source_period_extension = exact_extension("sourcePeriod")
    source_period = source_period_extension.get("valuePeriod")
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

def validate_healthkit_ecg_output_graph(
    resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Enforce the catalog-owned ECG waveform/average-HR relationship and closure."""
    claim = read_json(CATALOG_ROOT / "profile-claims.json")["healthKitEcgGraphClaim"]
    waveform_profiles = set(claim["waveform"]["profiles"])
    average_profiles = set(claim["averageHeartRate"]["profiles"])
    waveforms: dict[tuple[str, str], list[dict[str, Any]]] = {}
    averages: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for resource in resources:
        if resource.get("resourceType") != "Observation":
            continue
        profiles = resource.get("meta", {}).get("profile", [])
        profile_set = set(profiles) if isinstance(profiles, list) else set()
        if profile_set == waveform_profiles:
            source = typed_resource_identifiers(resource, f"{label} ECG waveform").get(
                "source-record"
            )
            if source is None:
                raise contract_failure(
                    "healthkit-ecg.output-graph", "Bundle.entry.resource.identifier",
                    f"{label} ECG waveform has no source-record identity",
                )
            waveforms.setdefault(source, []).append(resource)
        elif profile_set == average_profiles:
            source = typed_resource_identifiers(resource, f"{label} ECG average heart rate").get(
                "source-record"
            )
            if source is None:
                raise contract_failure(
                    "healthkit-ecg.output-graph", "Bundle.entry.resource.identifier",
                    f"{label} ECG average heart rate has no source-record identity",
                )
            averages.setdefault(source, []).append(resource)

    for source in set(waveforms) | set(averages):
        source_waveforms = waveforms.get(source, [])
        source_averages = averages.get(source, [])
        waveform_cardinality = claim["waveform"]["cardinality"]
        average_cardinality = claim["averageHeartRate"]["cardinality"]
        if (
            not waveform_cardinality["min"]
            <= len(source_waveforms)
            <= waveform_cardinality["max"]
            or not average_cardinality["min"]
            <= len(source_averages)
            <= average_cardinality["max"]
        ):
            raise contract_failure(
                "healthkit-ecg.output-graph", "Bundle.entry",
                f"{label} HealthKit ECG source must have one waveform and at most one average-heart-rate output",
            )
        waveform = source_waveforms[0]
        if not source_averages:
            continue
        average = source_averages[0]
        reference_claim = claim["averageHeartRate"]["reference"]
        derived = average.get(reference_claim["r4Path"].split(".")[-1])
        reference = (
            derived[0].get("reference")
            if isinstance(derived, list)
            and reference_claim["min"] <= len(derived) <= reference_claim["max"]
            and isinstance(derived[0], dict)
            else None
        )
        if not isinstance(reference, str) or resources_by_full_url.get(reference) is not waveform:
            raise contract_failure(
                "healthkit-ecg.output-graph", "Observation.derivedFrom",
                f"{label} HealthKit ECG average heart rate must derive from its same-source waveform",
            )
        if average.get("effectivePeriod") != waveform.get("effectivePeriod"):
            raise contract_failure(
                "healthkit-ecg.output-graph", "Observation.effectivePeriod",
                f"{label} HealthKit ECG waveform and average heart rate must use the exact same effectivePeriod",
            )
        waveform_output = typed_resource_identifiers(waveform, f"{label} ECG waveform").get(
            "source-output"
        )
        average_output = typed_resource_identifiers(average, f"{label} ECG average heart rate").get(
            "source-output"
        )
        if waveform_output is None or average_output is None or waveform_output == average_output:
            raise contract_failure(
                "healthkit-ecg.output-graph", "Observation.identifier",
                f"{label} HealthKit ECG waveform and average heart rate need distinct source-output identities",
            )
        for candidate in waveform.get("derivedFrom", []):
            if (
                isinstance(candidate, dict)
                and isinstance(candidate.get("reference"), str)
                and resources_by_full_url.get(candidate["reference"]) is average
            ):
                raise contract_failure(
                    "healthkit-ecg.output-graph", "Observation.derivedFrom",
                    f"{label} HealthKit ECG relationship is reversed; average heart rate derives from waveform",
                )
