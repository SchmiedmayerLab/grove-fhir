"""Health Connect source context, profile, and multi-output graph validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import CATALOG_ROOT
from .diagnostics import ProducerValidationError
from .identity import typed_resource_identifiers
from .io import read_json
from .profiles import codeable_concept_codings, coding_pairs_recursive


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
    if not isinstance(identifiers, list) or len(identifiers) < 2:
        raise ProducerValidationError(
            f"{label} Health Connect Observation must carry at least its two Grove identifiers"
        )
    roles = typed_resource_identifiers(resource, label)
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
                or measurement not in mapping.get("appliesToMeasurements", [])
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
    mindfulness_expected = "mindfulnessSessionType" in contexts
    method = resource.get("method")
    mindfulness_system = mindfulness_mapping["codeSystem"]
    method_pairs = coding_pairs_recursive(method)
    if mindfulness_expected:
        validate_health_connect_context_concept(
            method,
            mindfulness_mapping,
            f"{label} mindfulness session type",
        )
        if len(codeable_concept_codings(method, f"{label} mindfulness method")) != 1:
            raise ProducerValidationError(
                f"{label} mindfulness method must contain exactly one exact-source Coding"
            )
    elif any(system == mindfulness_system for system, _ in method_pairs):
        raise ProducerValidationError(
            f"{label} carries Health Connect mindfulness method outside a MindfulnessSessionRecord"
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
