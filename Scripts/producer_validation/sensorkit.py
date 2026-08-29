"""SensorKit source context, identity, waveform, and payload validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from .context import (
    CATALOG_ROOT, IDENTIFIER_ROLE_SYSTEM, SENSOR_ECG_PROFILE, SENSOR_SAMPLED_PROFILE,
)
from .diagnostics import ProducerValidationError
from .identity import typed_resource_identifiers
from .io import read_json
from .payloads import validate_sampled_data
from .profiles import admitted_document_reference_claim, codeable_concept_codings
from .references import complete_identifier, extensions_with_url, validate_governed_reference


def validate_sensorkit_quantity_domains(resource: dict[str, Any], label: str) -> None:
    """Enforce catalog-reviewed source domains for SensorKit summary Quantities."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    contract = read_json(CATALOG_ROOT / "sensorkit-adapter.json")[
        "quantityValueDomains"
    ]
    matched = set(profiles) & set(contract["nonNegativeProfiles"])
    if not matched:
        return
    quantities: list[tuple[str, dict[str, Any]]] = []
    root_quantity = resource.get("valueQuantity")
    if isinstance(root_quantity, dict):
        quantities.append((f"{label}.valueQuantity", root_quantity))
    components = resource.get("component", [])
    if isinstance(components, list):
        for index, component in enumerate(components):
            quantity = (
                component.get("valueQuantity")
                if isinstance(component, dict)
                else None
            )
            if isinstance(quantity, dict):
                quantities.append((f"{label}.component[{index}].valueQuantity", quantity))
    count_contract = contract["countQuantity"]
    integer_counts = bool(set(profiles) & set(contract["integerCountProfiles"]))
    for path, quantity in quantities:
        raw_value = quantity.get("value")
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float, Decimal)):
            raise ProducerValidationError(
                f"{path}.value must be a present non-negative number"
            )
        try:
            value = Decimal(str(raw_value))
        except InvalidOperation as error:
            raise ProducerValidationError(
                f"{path}.value must be a present non-negative number"
            ) from error
        if not value.is_finite() or value < 0:
            raise ProducerValidationError(
                f"{path}.value must be a present non-negative number"
            )
        if (
            integer_counts
            and quantity.get("system") == count_contract["system"]
            and quantity.get("code") == count_contract["code"]
            and value != value.to_integral_value()
        ):
            raise ProducerValidationError(
                f"{path}.value must be an integer for UCUM {count_contract['code']}"
            )


def validate_sensorkit_profile_claim(resource: dict[str, Any], label: str) -> None:
    """Require exact direct claims for SensorKit-only and Recording Document outputs."""
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

def exact_sensorkit_source_type(resource: dict[str, Any], label: str) -> str:
    """Return the one valueCode-only SensorKit source-type marker."""
    catalog = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    source_extensions = [
        extension
        for extension in resource.get("extension", [])
        if isinstance(extension, dict)
        and extension.get("url") == catalog["sourceTypeExtension"]["url"]
    ] if isinstance(resource.get("extension", []), list) else []
    value_keys = [
        key for key in source_extensions[0] if key.startswith("value")
    ] if len(source_extensions) == 1 else []
    if (
        len(source_extensions) != 1
        or value_keys != ["valueCode"]
        or not isinstance(source_extensions[0].get("valueCode"), str)
        or not source_extensions[0]["valueCode"]
    ):
        raise ProducerValidationError(
            f"{label} must carry exactly one valueCode-only SensorKit source type"
        )
    return source_extensions[0]["valueCode"]


def validate_sensorkit_identity(resource: dict[str, Any], label: str) -> None:
    """Bind SensorKit source type, source identity, output identity, and status row."""
    if resource.get("resourceType") not in {"Observation", "DocumentReference"}:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")

    catalog = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    sensorkit_profile_prefix = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
    )
    has_sensorkit_profile = any(
        isinstance(profile, str) and profile.startswith(sensorkit_profile_prefix)
        for profile in profiles
    )
    extensions = resource.get("extension", [])
    has_sensorkit_marker = isinstance(extensions, list) and any(
        isinstance(extension, dict)
        and extension.get("url") == catalog["sourceTypeExtension"]["url"]
        for extension in extensions
    )
    if not has_sensorkit_profile and not has_sensorkit_marker:
        return

    if resource["resourceType"] == "DocumentReference":
        claim = catalog["profileClaims"]["recordingDocument"]
        expected_profiles = {
            claim["sourceNeutralProfile"],
            claim["adapterProfile"],
        }
        if len(profiles) != len(expected_profiles) or set(profiles) != expected_profiles:
            raise ProducerValidationError(
                f"{label} SensorKit Recording Document must directly claim exactly the "
                "source-neutral and SensorKit recording profiles"
            )
    elif not has_sensorkit_profile:
        raise ProducerValidationError(
            f"{label} SensorKit source type requires an admitted SensorKit profile"
        )

    source_type = exact_sensorkit_source_type(resource, label)
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

    rows = {
        row["sourceTypeCode"]: row for row in catalog["entries"]
    }
    row = rows.get(source_type)
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
        expected_shared_profiles = {
            representation.get("sourceNeutralProfile"),
            representation.get("adapterProfile"),
        }
        if isinstance(expected_profile, str) and profiles != [expected_profile]:
            raise ProducerValidationError(
                f"{label} must directly claim its exact SensorKit-only profile"
            )
        if all(isinstance(profile, str) for profile in expected_shared_profiles) and (
            len(profiles) != 2 or set(profiles) != expected_shared_profiles
        ):
            raise ProducerValidationError(
                f"{label} must directly claim the exact source-neutral and SensorKit "
                "profiles admitted for its source type"
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
    catalog = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    ecg_row = next(
        row for row in catalog["entries"] if row["sourceTypeCode"] == "ecg"
    )
    guidance_mapping = next(
        mapping for mapping in ecg_row["structured"]["nativeR4Mappings"]
        if mapping["sourceField"] == "SRElectrocardiogramSample.session.guidance"
    )
    extensions = resource.get("extension", [])
    obsolete_guidance_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-ecg-session-guidance"
    )
    if isinstance(extensions, list) and any(
        isinstance(extension, dict) and extension.get("url") == obsolete_guidance_url
        for extension in extensions
    ):
        raise ProducerValidationError(
            f"{label} uses the obsolete SensorKit ECG guidance extension instead of Observation.method"
        )
    method = resource.get("method")
    if not isinstance(method, dict):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded SensorKit ECG session guidance in Observation.method"
        )
    method_codings = codeable_concept_codings(method, f"{label} SensorKit ECG method")
    guidance = [
        coding.get("code") for coding in method_codings
        if coding.get("system") == guidance_mapping["codingSystem"]
    ]
    if (
        len(method_codings) != 1
        or len(guidance) != 1
        or guidance[0] not in set(guidance_mapping["allowedCodes"])
    ):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded SensorKit ECG session guidance in Observation.method"
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

def validate_sensorkit_native_r4_context(resource: dict[str, Any], label: str) -> None:
    """Validate SensorKit source context placed in native R4 elements."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    prefix = "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
    extensions = resource.get("extension", [])
    extensions = extensions if isinstance(extensions, list) else []
    obsolete = {
        prefix + "sensorkit-visit-location",
        prefix + "sensorkit-ecg-session-guidance",
    }
    if any(
        isinstance(extension, dict) and extension.get("url") in obsolete
        for extension in extensions
    ):
        raise ProducerValidationError(
            f"{label} uses an obsolete SensorKit extension instead of native R4 structure"
        )

    visit_profile = prefix + "sensorkit-visit-observation"
    if visit_profile in profiles:
        focus = resource.get("focus", [])
        if not isinstance(focus, list) or len(focus) > 1:
            raise ProducerValidationError(
                f"{label} SensorKit visit focus must be zero or one logical Location Reference"
            )
        if focus:
            reference = focus[0]
            validate_governed_reference(reference, {"Location"}, {}, f"{label}.focus[0]")
            identifier = reference.get("identifier") if isinstance(reference, dict) else None
            complete_identifier(identifier, f"{label}.focus[0].identifier")
            type_codings = identifier.get("type", {}).get("coding", [])
            if isinstance(type_codings, list) and any(
                isinstance(coding, dict)
                and coding.get("system") == IDENTIFIER_ROLE_SYSTEM
                for coding in type_codings
            ):
                raise ProducerValidationError(
                    f"{label} SensorKit visit location Identifier must not claim a Grove graph role"
                )

    wrist_profile = prefix + "sensorkit-wrist-temperature-observation"
    if wrist_profile in profiles:
        catalog = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
        wrist_row = next(
            row for row in catalog["entries"]
            if row["sourceToken"] == "SRSensor.wristTemperature"
        )
        mapping = wrist_row["structured"]["extensionMappings"][0]
        version_extensions = extensions_with_url(resource, mapping["url"])
        if (
            len(version_extensions) != 1
            or set(version_extensions[0]) != {"url", mapping["valueElement"]}
            or not isinstance(version_extensions[0].get("valueString"), str)
            or not version_extensions[0]["valueString"].strip()
            or "method" in resource
        ):
            raise ProducerValidationError(
                f"{label} SensorKit wrist temperature must carry the exact non-blank algorithm version only in its governed valueString extension"
            )

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
        channel_identities: set[tuple[tuple[str, str], ...]] = set()
        for index, component in enumerate(components):
            component_label = f"{label}.component[{index}]"
            code = component.get("code") if isinstance(component, dict) else None
            codings = code.get("coding") if isinstance(code, dict) else None
            if not isinstance(codings, list) or not codings:
                raise ProducerValidationError(
                    f"{component_label}.code must contain at least one complete channel coding"
                )
            identity_pairs: list[tuple[str, str]] = []
            for coding_index, coding in enumerate(codings):
                system = coding.get("system") if isinstance(coding, dict) else None
                code_value = coding.get("code") if isinstance(coding, dict) else None
                if (
                    not isinstance(system, str)
                    or not system
                    or not isinstance(code_value, str)
                    or not code_value
                ):
                    raise ProducerValidationError(
                        f"{component_label}.code.coding[{coding_index}] must contain "
                        "non-empty system and code"
                    )
                identity_pairs.append((system, code_value))
            identity = tuple(sorted(identity_pairs))
            if len(identity) != len(set(identity)):
                raise ProducerValidationError(
                    f"{component_label}.code repeats a channel identity coding"
                )
            if identity in channel_identities:
                raise ProducerValidationError(
                    f"{component_label}.code duplicates another ECG channel identity"
                )
            channel_identities.add(identity)
            sampled = component.get("valueSampledData") if isinstance(component, dict) else None
            validate_sampled_data(
                sampled, resource.get("effectivePeriod"), component_label
            )
    if admitted_document_reference_claim(resource) is not None:
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
