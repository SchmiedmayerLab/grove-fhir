"""Source-neutral profile, fixed-semantic, provenance, and format claims."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from .context import (
    CATALOG_ROOT, EXCHANGE_PROTOCOL, HMAC_IDENTITY, KNOWN_ADAPTER_PROFILES,
    MEASUREMENT_BY_PROFILE, RECORDING_DOCUMENT_PROFILE_TAIL, REGISTRY_GENERATIONS,
    WRITER_RECORD_VERSION_EXTENSION,
)
from .diagnostics import ProducerValidationError, contract_failure
from .identity import identifier_role, typed_resource_identifiers
from .io import read_json
from .references import complete_identifier, extensions_with_url


def validate_writer_record_revision(resource: dict[str, Any], label: str) -> None:
    """Validate source-neutral and adapter-specific writer revision semantics."""
    identifiers = resource.get("identifier", [])
    identifiers = identifiers if isinstance(identifiers, list) else [identifiers]
    has_writer_marker = any(
        isinstance(identifier, dict)
        and isinstance(identifier.get("type"), dict)
        and isinstance(identifier["type"].get("coding"), list)
        and any(
            isinstance(coding, dict)
            and coding.get("system")
            == "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
            and coding.get("code") == "writer-record"
            for coding in identifier["type"]["coding"]
        )
        for identifier in identifiers
    )
    versions = extensions_with_url(resource, WRITER_RECORD_VERSION_EXTENSION)
    if not has_writer_marker and not versions:
        return
    roles = typed_resource_identifiers(resource, label)
    writer_present = "writer-record" in roles
    if len(versions) > 1 or (versions and not writer_present):
        raise ProducerValidationError(
            f"{label} writer record version requires exactly one writer-record identity"
        )
    profiles = resource.get("meta", {}).get("profile", [])
    profiles = profiles if isinstance(profiles, list) else []
    paired_adapter = any(
        isinstance(profile, str)
        and profile.startswith(
            (
                "https://grovealliance.org/fhir/healthkit/StructureDefinition/",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/",
            )
        )
        for profile in profiles
    )
    if paired_adapter and writer_present != (len(versions) == 1):
        raise ProducerValidationError(
            f"{label} adapter requires writer-record identity and version together"
        )
    if not versions:
        return
    extension = versions[0]
    value = extension.get("valueString")
    if (
        set(extension) != {"url", "valueString"}
        or not isinstance(value, str)
        or re.fullmatch(r"0|[1-9][0-9]*", value) is None
    ):
        raise ProducerValidationError(
            f"{label} writer record version must be a canonical non-negative decimal integer"
        )
    if (
        any(
            isinstance(profile, str)
            and profile.startswith(
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            )
            for profile in profiles
        )
    ):
        maximum = read_json(CATALOG_ROOT / "health-connect-adapter.json")["identity"][
            "writerRecord"
        ]["revision"]["versionMaximum"]
        if int(value) > maximum:
            raise ProducerValidationError(
                f"{label} Health Connect writer record version exceeds Long.MAX_VALUE"
            )


def adapter_profile_contract() -> tuple[set[str], set[str]]:
    """Return the exact semantic-measurement and adapter profile sets."""
    measurements = read_json(CATALOG_ROOT / "measurement-catalog.json")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    semantic = {
        f"https://grovealliance.org/fhir/{entry.get('owner', 'mobile')}"
        f"/StructureDefinition/{entry['profile']}"
        for entry in measurements["measurements"]
    }
    semantic.update(claims["observationAdapterClaim"].get("sharedSensorProfiles", []))
    semantic.update(
        entry["semanticProfile"]
        for entry in claims["observationAdapterClaim"].get("standardAdapterClaims", [])
    )
    adapters = set(claims["observationAdapterClaim"]["adapterProfiles"])
    return semantic, adapters

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
    entry_match = re.search(r"entry\[([0-9]+)\]", label)
    location = (
        f"Bundle.entry[{entry_match.group(1)}].resource.valueQuantity.value"
        if entry_match is not None
        else "Observation.valueQuantity.value"
    )

    def domain_failure(message: str) -> ProducerValidationError:
        return contract_failure(
            "mobile-output.quantity-value-domain", location, message
        )

    raw_value = quantity["value"]
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float, Decimal)):
        raise domain_failure(f"{label}.valueQuantity.value must be a number")
    try:
        value = Decimal(str(raw_value))
    except InvalidOperation as error:
        raise domain_failure(
            f"{label}.valueQuantity.value is not a finite decimal"
        ) from error
    if not value.is_finite():
        raise domain_failure(
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
            raise domain_failure(
                f"{label}.valueQuantity.value violates the {qualifier} {relation} "
                f"{boundary['value']} for {measurement['id']}"
            )
    if domain["integerOnly"] and value != value.to_integral_value():
        raise domain_failure(
            f"{label}.valueQuantity.value must be an integer for {measurement['id']}"
        )

def validate_adapter_profile_claim(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    """Require an explicitly claimed adapter Observation to claim semantic + adapter."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    semantic_profiles, adapter_profiles = adapter_profile_contract()
    claimed_adapters = set(profiles) & adapter_profiles
    claimed_semantic = set(profiles) & semantic_profiles
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
        or len(claimed_semantic) != 1
        or len(profiles) != 2
        or len(set(profiles)) != 2
    ):
        raise ProducerValidationError(
            f"{label} adapter Observation must claim exactly one semantic profile "
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
    semantic_profiles, adapter_profiles = adapter_profile_contract()
    semantic = direct & semantic_profiles
    adapters = direct & adapter_profiles
    expected = semantic | adapters
    if len(semantic) != 1 or direct != expected:
        raise ProducerValidationError(
            f"{label} active Observation must claim exactly one admitted semantic "
            "profile and no arbitrary direct profile"
        )
    semantic_profile = next(iter(semantic))
    measurement = MEASUREMENT_BY_PROFILE.get(semantic_profile)
    if measurement is not None:
        provider_adapters = {
            provider["measurementOwner"]: provider["observationProfile"]
            for provider in read_json(CATALOG_ROOT / "providers-adapter.json")["providers"]
        }
        expected_provider_adapter = provider_adapters.get(
            measurement.get("owner", "mobile")
        )
        if expected_provider_adapter is not None and adapters != {
            expected_provider_adapter
        }:
            raise ProducerValidationError(
                f"{label} provider-owned semantic profile must be paired with "
                f"{expected_provider_adapter}"
            )
    validate_quantity_value_domain(resource, label, semantic_profile)
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
        entry_match = re.search(r"entry\[([0-9]+)\]", label)
        location = (
            f"Bundle.entry[{entry_match.group(1)}].resource.valueQuantity.code"
            if entry_match is not None
            else "Observation.valueQuantity.code"
        )
        raise contract_failure(
            "mobile-output.fixed-quantity-unit",
            location,
            f"{label} {measurement['id']} must use fixed quantity "
            f"{quantity_contract['system']}#{quantity_contract['code']}",
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
    has_healthkit_marker = (
        healthkit["sourceTypeExtension"]["url"] in extension_urls
    )
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
        provider["observationProfile"] for provider in providers["providers"]
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
