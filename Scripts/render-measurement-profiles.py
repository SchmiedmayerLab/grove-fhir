#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Project Grove semantic measurement profiles from the measurement catalog.

Every measurement's FSH profile is a deterministic projection of its catalog
entry. A measurement with generation.emit true is written into the generated
FSH file; one with emit false must match its hand-written block in
mobile/input/fsh/profiles.fsh byte for byte, so the projection is proven
against the shipped profiles before any cutover.

Generation is review-gated: a measurement without an approved entry in
mobile/input/data/terminology-reviews.json whose digest matches the current
terminology projection is refused with exit code 2.

Usage:
  Scripts/render-measurement-profiles.py           # write + verify parity
  Scripts/render-measurement-profiles.py --check   # verify only
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path

try:
    from Scripts.exchange_protocol import derive_hmac_identity
except ModuleNotFoundError:  # Direct execution places Scripts itself on sys.path.
    from exchange_protocol import derive_hmac_identity

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

OWNERS = {
    "mobile": {
        "patientExample": "GroveMobilePatientExample",
        "parent": "GroveMobileObservation",
        "generated": "mobile/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/grove-mobile-measurement",
        "codeSystem": "GroveMobileMeasurementCS",
        "valueSet": "GroveMobileMeasurementVS",
        "terminologyId": "grove-mobile-measurement",
        "terminologyTitle": "Grove Mobile Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the Grove Mobile contract when an "
            "established code would not faithfully represent the exchanged result."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by Grove Mobile for use in its focused "
            "domain profiles."
        ),
    },
    "healthkit": {
        "patientExample": "HealthKitPatientExample",
        "parent": "HealthKitObservation",
        "generated": "healthkit/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/healthkit-measurement",
        "codeSystem": "HealthKitMeasurementCS",
        "valueSet": "HealthKitMeasurementVS",
        "terminologyId": "healthkit-measurement",
        "terminologyTitle": "HealthKit Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the HealthKit adapter for "
            "platform-specific results for which no established code is sufficiently precise."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the HealthKit adapter for its "
            "platform-exclusive profiles."
        ),
    },
    "withings": {
        "patientExample": "WithingsPatientExample",
        "parent": "GroveMobileObservation",
        "generated": "withings/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/withings-measurement",
        "codeSystem": "WithingsMeasurementCS",
        "valueSet": "WithingsMeasurementVS",
        "terminologyId": "withings-measurement",
        "terminologyTitle": "Withings Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the Withings adapter for "
            "source-specific results for which no established code is sufficiently precise."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the Withings adapter for its "
            "source-specific profiles."
        ),
    },
    "oura": {
        "patientExample": "OuraPatientExample",
        "parent": "GroveMobileObservation",
        "generated": "oura/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/oura-measurement",
        "codeSystem": "OuraMeasurementCS",
        "valueSet": "OuraMeasurementVS",
        "terminologyId": "oura-measurement",
        "terminologyTitle": "Oura Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the Oura adapter for "
            "source-specific results for which no established code is sufficiently precise."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the Oura adapter for its "
            "source-specific profiles."
        ),
    },
    "google-health": {
        "patientExample": "GoogleHealthPatientExample",
        "parent": "GroveMobileObservation",
        "generated": "google-health/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/google-health-measurement",
        "codeSystem": "GoogleHealthMeasurementCS",
        "valueSet": "GoogleHealthMeasurementVS",
        "terminologyId": "google-health-measurement",
        "terminologyTitle": "Google Health Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the Google Health adapter for "
            "source-specific results for which no established code is sufficiently precise."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the Google Health adapter for its "
            "source-specific profiles."
        ),
    },
    "health-connect": {
        "patientExample": "HealthConnectPatientExample",
        "parent": "HealthConnectObservation",
        "generated": "health-connect/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/health-connect-measurement",
        "codeSystem": "HealthConnectMeasurementCS",
        "valueSet": "HealthConnectMeasurementVS",
        "terminologyId": "health-connect-measurement",
        "terminologyTitle": "Health Connect Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the Health Connect adapter for "
            "platform-specific results for which no established code is sufficiently precise."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the Health Connect adapter for its "
            "platform-exclusive profiles."
        ),
    },
}


class Layout:
    """The repo-relative inputs and outputs, bound to one root."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.catalog = root / "catalog/measurement-catalog.json"
        self.reviews = root / "mobile/input/data/terminology-reviews.json"
        self.aliases = root / "mobile/input/fsh/aliases.fsh"
        self.hand_profiles = root / "mobile/input/fsh/profiles.fsh"
        self.generated = root / "mobile/input/fsh/generated-measurement-profiles.fsh"

    def generated_for(self, owner: str) -> Path:
        return self.root / OWNERS[owner]["generated"]

LOINC = "http://loinc.org"

HEADER = """// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

"""

DIGEST_SCOPE = "grove-terminology-projection-3"
PROJECTION_KEYS = (
    "code",
    "components",
    "description",
    "effective",
    "hasMember",
    "method",
    "methodChoice",
    "obeys",
    "quantity",
    "requiredCodings",
    "standardProfile",
    "valueKind",
    "valueSet",
    "resultCodes",
    "resultCodeSystem",
    "allowedValues",
)
GROUND_TRUTH_FILES = (
    "catalog/terminology/loinc-concepts.json",
    "catalog/terminology/ucum-units.json",
    "mobile/input/fsh/terminology.fsh",
    "mobile/input/fsh/profiles.fsh",
)


# Illustrative example values ride along in the catalog but state no terminology, so they stay
# outside the reviewed projection; tuning one must not invalidate a reviewer's terminology sign-off.
UNREVIEWED_KEYS = ("example",)


def without_unreviewed(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: without_unreviewed(nested)
            for key, nested in value.items()
            if key not in UNREVIEWED_KEYS
        }
    if isinstance(value, list):
        return [without_unreviewed(entry) for entry in value]
    return value


def projection_digest(measurement: dict) -> str:
    projection = {
        key: without_unreviewed(measurement.get(key))
        for key in PROJECTION_KEYS
        if measurement.get(key) is not None
    }
    canonical = json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fsh_name(profile_id: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in profile_id.split("-"))


def value_set_name(canonical: str) -> str:
    return fsh_name(canonical.rsplit("/", 1)[1]) + "VS"


def alias_map(layout: Layout) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for match in re.finditer(
        r"^Alias: (\$\w+) = (\S+)$", layout.aliases.read_text(encoding="utf-8"), re.M
    ):
        aliases[match.group(2)] = match.group(1)
    return aliases


def quantity_rules(
    prefix: str, quantity: dict, strict: bool, value_domain: dict | None = None
) -> list[str]:
    rules = [
        f"* {prefix}value[x] only Quantity",
        f"* {prefix}valueQuantity.value 1..1 MS",
    ]
    if strict:
        rules.append(f"* {prefix}valueQuantity.comparator 0..0")
        if quantity.get("unitMustSupport"):
            rules.append(f"* {prefix}valueQuantity.unit MS")
        rules.append(f"* {prefix}valueQuantity.system 1..1 MS")
    rules.append(f"* {prefix}valueQuantity.system = $ucum (exactly)")
    if strict:
        rules.append(f"* {prefix}valueQuantity.code 1..1 MS")
    rules.append(f"* {prefix}valueQuantity.code = #{quantity['code']} (exactly)")
    if value_domain:
        minimum = value_domain.get("minimum")
        maximum = value_domain.get("maximum")
        if minimum and minimum["inclusive"]:
            rules.append(
                f"* {prefix}valueQuantity.value ^minValueDecimal = {minimum['value']}"
            )
        if maximum and maximum["inclusive"]:
            rules.append(
                f"* {prefix}valueQuantity.value ^maxValueDecimal = {maximum['value']}"
            )
    return rules


def quantity_domain_invariant(measurement: dict) -> tuple[str, str] | None:
    domain = measurement["quantity"].get("valueDomain")
    if not domain:
        return None
    key = f"{measurement['profile']}-value-domain-1"
    value = "value.ofType(Quantity).value"
    conditions: list[str] = []
    descriptions: list[str] = []
    minimum = domain.get("minimum")
    if minimum:
        operator = ">=" if minimum["inclusive"] else ">"
        conditions.append(f"{value} {operator} {minimum['value']}")
        descriptions.append(
            f"{operator} {minimum['value']}"
        )
    maximum = domain.get("maximum")
    if maximum:
        operator = "<=" if maximum["inclusive"] else "<"
        conditions.append(f"{value} {operator} {maximum['value']}")
        descriptions.append(
            f"{operator} {maximum['value']}"
        )
    if domain["integerOnly"]:
        conditions.append(f"({value} mod 1) = 0")
        descriptions.append("an integer")
    description = ", ".join(descriptions)
    expression = " and ".join(conditions)
    invariant = "\n".join(
        [
            f"Invariant: {key}",
            f'Description: "A populated {measurement["title"]} value is {description}."',
            f'Expression: "value.empty() or ({expression})"',
            "Severity: #error",
        ]
    )
    return key, invariant


def render_profile(
    measurement: dict,
    aliases: dict[str, str],
    by_id: dict,
    include_domain_definition: bool = True,
) -> str:
    owner = OWNERS[measurement.get("owner", "mobile")]
    name = fsh_name(measurement["profile"])
    lines = [
        f"Profile: {name}",
        f"Parent: {owner['parent']}",
        f"Id: {measurement['profile']}",
        f'Title: "{measurement["title"]}"',
        f'Description: "{measurement["description"]}"',
    ]
    domain_invariant = (
        quantity_domain_invariant(measurement)
        if measurement["valueKind"] == "quantity"
        else None
    )
    invariants = list(measurement.get("obeys", []))
    if domain_invariant:
        invariants.append(domain_invariant[0])
    if invariants:
        lines.append("* obeys " + " and ".join(invariants))
    standard = measurement.get("standardProfile")
    if standard is not None:
        alias = aliases.get(standard)
        if alias is None:
            raise SystemExit(f"{measurement['id']}: no FSH alias for {standard}")
        lines.append(f"* ^extension[+].url = $imposeProfile")
        lines.append(f"* ^extension[=].valueCanonical = {alias}")
    code = measurement["code"]
    if code["system"] == LOINC:
        lines.append(f"* code = $loinc#{code['code']}")
    elif code["system"].endswith(owner["measurementSystemTail"]):
        lines.append(f"* code = {owner['codeSystem']}#{code['code']}")
        lines.append(f"* code from {owner['valueSet']} (required)")
    else:
        raise SystemExit(f"{measurement['id']}: unsupported code system {code['system']}")
    required_codings = measurement.get("requiredCodings", [])
    if required_codings:
        lines.append("* code.coding ^slicing.discriminator.type = #pattern")
        lines.append('* code.coding ^slicing.discriminator.path = "$this"')
        lines.append("* code.coding ^slicing.rules = #open")
        lines.append(
            "* code.coding contains "
            + " and ".join(f"{coding['slice']} 1..1 MS" for coding in required_codings)
        )
        for required_coding in required_codings:
            system = "$loinc" if required_coding["system"] == LOINC else required_coding["system"]
            lines.append(
                f"* code.coding[{required_coding['slice']}] = "
                f"{system}#{required_coding['code']}"
            )
    category = measurement.get("category")
    if category:
        category_system = (
            "$observationCategory"
            if category["system"]
            == "http://terminology.hl7.org/CodeSystem/observation-category"
            else category["system"]
        )
        # Display text is presentation metadata, may be localized, and can change in the
        # authoritative terminology without changing the code. Profiles constrain the
        # semantic system/code pair; generated examples retain the reviewed display.
        lines.append(f"* category = {category_system}#{category['code']}")
    if measurement["effective"] == "Period":
        lines.append("* effective[x] only Period")
        lines.append("* effectivePeriod.end 1..1 MS")
    elif measurement["effective"] == "dateTime-or-Period":
        lines.append("* effective[x] only dateTime or Period")
    else:
        lines.append("* effective[x] only dateTime")
    method = measurement.get("method")
    owner_key = measurement.get("owner", "mobile")
    method_cs = (
        "GroveAggregationMethodCS"
        if owner_key == "mobile"
        else "https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method"
    )
    method_vs = (
        "GroveAggregationMethodVS"
        if owner_key == "mobile"
        else "https://grovealliance.org/fhir/mobile/ValueSet/grove-aggregation-method"
    )
    if method:
        lines.append("* method 1..1 MS")
        lines.append(f"* method = {method_cs}#{method['code']}")
    elif measurement.get("methodChoice"):
        lines.append("* method 1..1 MS")
        lines.append(f"* method from {method_vs} (required)")
    kind = measurement["valueKind"]
    if kind == "quantity":
        # The imposed R4 Vital Signs profiles establish their clinical family, but Grove still
        # exchanges one exact source numeric value. Keep the local system/code cardinalities and
        # prohibit a comparator even when a standard profile is imposed; otherwise adding the
        # authoritative profile would accidentally weaken the adapter contract.
        lines.extend(
            quantity_rules(
                "",
                measurement["quantity"],
                True,
                measurement["quantity"].get("valueDomain"),
            )
        )
    elif kind == "codeableConcept":
        lines.append("* value[x] only CodeableConcept")
        lines.append("* valueCodeableConcept 1..1 MS")
        lines.append(
            f"* valueCodeableConcept from {value_set_name(measurement['valueSet'])} (required)"
        )
    elif kind == "dateTime":
        lines.append("* value[x] only dateTime")
        lines.append("* valueDateTime 1..1 MS")
    elif kind == "components":
        lines.append("* value[x] 0..0")
    elif kind == "grouping":
        # A panel states what its members are, not a value of its own: the members are complete
        # Observations that stand alone, so repeating them here would publish the same fact twice.
        lines.append("* value[x] 0..0")
        lines.append("* hasMember 1..* MS")
        lines.append("* hasMember only Reference(Observation)")
    else:
        raise SystemExit(f"{measurement['id']}: unsupported valueKind {kind}")
    for element in measurement.get("forbiddenElements", []):
        lines.append(f"* {element} 0..0")
    if measurement.get("components"):
        lines.append("* component ^slicing.discriminator.type = #pattern")
        lines.append('* component ^slicing.discriminator.path = "code"')
        lines.append("* component ^slicing.rules = #open")
        contains = " and ".join(
            f"{component['id']} {component.get('cardinality', '1..1')} MS"
            for component in measurement["components"]
        )
        lines.append(f"* component contains {contains}")
        for component in measurement["components"]:
            slice_name = component["id"]
            if component["system"] == LOINC:
                lines.append(
                    f"* component[{slice_name}].code = $loinc#{component['code']}"
                )
            else:
                lines.append(
                    f"* component[{slice_name}].code = "
                    f"{component['system']}#{component['code']}"
                )
            if component.get("quantity"):
                lines.extend(
                    quantity_rules(
                        f"component[{slice_name}].", component["quantity"], False
                    )
                )
            elif component.get("valueSet"):
                lines.append(
                    f"* component[{slice_name}].value[x] only CodeableConcept"
                )
                cardinality = component.get("cardinality", "1..1")
                lines.append(
                    f"* component[{slice_name}].valueCodeableConcept "
                    f"{'1..1 MS' if cardinality == '1..1' else 'MS'}"
                )
                lines.append(
                    f"* component[{slice_name}].valueCodeableConcept from "
                    f"{value_set_name(component['valueSet'])} (required)"
                )
    for member in measurement.get("hasMember", []):
        lines.append(
            f"* hasMember only Reference({fsh_name(by_id[member]['profile'])})"
        )
    rendered = "\n".join(lines) + "\n"
    if domain_invariant and include_domain_definition:
        return domain_invariant[1] + "\n\n" + rendered
    return rendered


def load_catalog(root: Path, name: str) -> dict:
    return json.loads((root / "catalog" / name).read_text(encoding="utf-8"))


# Each connected provider publishes its exclusive measurements in its own guide, but they all
# share the Provider adapter's lineage extensions, source-type terminology, and identity namespaces.
PROVIDER_GUIDES = {
    "google-health-api": "google-health",
    "oura": "oura",
    "withings": "withings",
}
PROVIDER_OWNERS = frozenset(PROVIDER_GUIDES.values())

SOURCE_TYPE_MARKERS = {
    "healthkit": "* extension[healthKitSourceType].valueCode = #{token}",
    "health-connect": "* extension[healthConnectRecordType].valueCode = #{token}",
    **{owner: "* extension[providerSourceType].valueCode = #{token}" for owner in PROVIDER_OWNERS},
}


def example_contract(root: Path) -> dict:
    """Catalog-owned inputs shared by every generated identity example."""
    protocol = load_catalog(root, "exchange-protocol.json")
    vectors = protocol["testVectors"]
    examples = vectors["measurementExamples"]
    system_rows = vectors["identitySystems"]
    systems = {row["identityKind"]: row["system"] for row in system_rows}
    if len(systems) != len(system_rows):
        raise SystemExit("measurement example identitySystems repeat an identity kind")
    if len(set(systems.values())) != len(systems):
        raise SystemExit(
            "measurement example identity systems must be distinct by identity kind"
        )
    required = {row["kind"] for row in protocol["opaqueIdentity"]["identityKinds"]}
    if set(systems) != required:
        missing = sorted(required - set(systems))
        extra = sorted(set(systems) - required)
        raise SystemExit(
            f"measurement example identitySystems mismatch: missing={missing}, extra={extra}"
        )
    return {
        **examples,
        "key": bytes.fromhex(vectors["keyHex"]),
        "keyHex": vectors["keyHex"],
        "keyId": vectors["keyId"],
        "epoch": vectors["epoch"],
        "identitySystemsByKind": systems,
    }


def health_connect_output_identity(
    catalog: dict, output: dict, contract: dict
) -> tuple[str, str]:
    """Project one concrete example tuple from the catalog's count/graph rule."""
    measurement = output["measurement"]
    count_rule = output["countRule"]
    coordinates = contract["coordinates"]
    if count_rule in {"exactly-one", "zero-or-one"}:
        return "single", measurement
    if count_rule == "one-per-present-field":
        return "present-field", measurement
    if count_rule == "one-per-sample":
        return (
            "sample",
            f"{coordinates['canonicalInstant']}|{coordinates['occurrence']}",
        )
    if count_rule == "one-per-stage":
        return (
            "sleep-stage",
            f"{coordinates['canonicalPeriodStart']}|{coordinates['canonicalPeriodEnd']}|"
            f"{coordinates['sleepStageToken']}|{coordinates['occurrence']}",
        )
    if count_rule != "graph-specific":
        raise SystemExit(f"{measurement}: unsupported Health Connect count rule {count_rule}")

    graph_name = output["graphRule"]
    graph_outputs = catalog["graphRules"][graph_name]["outputs"]
    selected = next(
        (row for row in graph_outputs if row["resourceRole"] == "structured-observation"),
        graph_outputs[0],
    )
    role = selected["outputRole"]
    if graph_name == "exactly-one-admitted-specimen-output":
        discriminator = measurement
    elif graph_name == "one-per-source-segment-or-lap":
        discriminator = (
            f"{coordinates['canonicalPeriodStart']}|{coordinates['canonicalPeriodEnd']}|"
            f"{coordinates['exerciseSegmentToken']}|{coordinates['occurrence']}"
        )
    elif graph_name == "one-per-source-delta":
        discriminator = (
            f"{coordinates['canonicalInstant']}|{coordinates['occurrence']}"
        )
    else:
        raise SystemExit(f"{measurement}: unsupported Health Connect graph rule {graph_name}")
    return role, discriminator


def source_identity_projections(root: Path, contract: dict) -> dict[str, dict[str, dict]]:
    """Project wire source codes and HMAC output tuples from each adapter catalog."""
    projections: dict[str, dict[str, dict]] = {
        owner: {} for owner in SOURCE_TYPE_MARKERS
    }

    healthkit = load_catalog(root, "healthkit-adapter.json")
    for row in healthkit["rows"]:
        source_type = row["sourceTypeIdentifier"]
        for measurement in row.get("measurementIDs", []):
            projections["healthkit"].setdefault(
                measurement,
                {
                    "adapterId": "healthkit",
                    "sourceIdentityKind": "source-record",
                    "preimageSourceType": source_type,
                    "wireSourceType": source_type,
                    "outputRole": measurement,
                    "outputDiscriminator": "single",
                    "countRule": "exactly-one",
                },
            )

    health_connect = load_catalog(root, "health-connect-adapter.json")
    for record in health_connect["recordTypes"]:
        for output in record.get("outputs", []):
            role, discriminator = health_connect_output_identity(
                health_connect, output, contract
            )
            projections["health-connect"].setdefault(
                output["measurement"],
                {
                    "adapterId": "health-connect",
                    "sourceIdentityKind": "source-record",
                    "preimageSourceType": record["token"],
                    "wireSourceType": record["token"],
                    "outputRole": role,
                    "outputDiscriminator": discriminator,
                    "countRule": output["countRule"],
                    **(
                        {"graphRule": output["graphRule"]}
                        if output["countRule"] == "graph-specific"
                        else {}
                    ),
                },
            )

    providers = load_catalog(root, "providers-adapter.json")
    for provider in providers["providers"]:
        provider_code = provider["id"]
        guide = PROVIDER_GUIDES[provider_code]
        if provider["measurementOwner"] != guide:
            raise SystemExit(
                f"{provider_code}: measurementOwner must be {guide!r}"
            )
        # Atomic grouped mappings own their source token and output role; process them before
        # their member rows so a component token can never leak into the example preimage.
        for group in provider.get("groupedMappings", []):
            for measurement in group["measurementIds"]:
                projections[guide][measurement] = {
                    "adapterId": "providers",
                    "providerCode": provider_code,
                    "providerScopeMode": provider["providerScopeMode"],
                    "adapterProfile": provider["observationProfile"],
                    "sourceIdentityKind": "provider-record",
                    "preimageSourceType": group["token"],
                    "wireSourceType": f"{provider_code}/{group['token']}",
                    "outputRole": group["outputRole"],
                    "outputDiscriminator": group["outputDiscriminator"],
                    "countRule": "exactly-one",
                }
        for source_type in provider.get("sourceTypes", []):
            for element in source_type.get("elements", []):
                if element.get("groupedMapping"):
                    continue
                for measurement in element.get("measurementIds", []):
                    projections[guide].setdefault(
                        measurement,
                        {
                            "adapterId": "providers",
                            "providerCode": provider_code,
                            "providerScopeMode": provider["providerScopeMode"],
                            "adapterProfile": provider["observationProfile"],
                            "sourceIdentityKind": "provider-record",
                            "preimageSourceType": source_type["token"],
                            "wireSourceType": f"{provider_code}/{source_type['token']}",
                            "outputRole": measurement,
                            "outputDiscriminator": "single",
                            "countRule": "exactly-one",
                        },
                    )
    return projections


def example_projection(
    measurement: dict, owner_key: str, projections: dict[str, dict[str, dict]]
) -> dict:
    if owner_key == "mobile":
        # The source-neutral guide deliberately uses a fictional adapter. Its tuple still follows
        # the same sole-output convention as a real adapter and is recorded in the manifest.
        return {
            "adapterId": "example-mobile",
            "sourceIdentityKind": "source-record",
            "preimageSourceType": measurement["id"],
            "wireSourceType": measurement["id"],
            "outputRole": measurement["id"],
            "outputDiscriminator": "single",
            "countRule": "exactly-one",
        }
    projection = projections.get(owner_key, {}).get(measurement["id"])
    if projection is None:
        raise SystemExit(
            f"{measurement['id']}: {owner_key} has no catalog-owned example identity projection"
        )
    return projection


def handwritten_instances(root: Path, owner_key: str) -> set[str]:
    """Every Instance a guide already defines by hand."""
    generated = root / OWNERS[owner_key]["generated"]
    directory = generated.parent
    names: set[str] = set()
    for source in directory.glob("*.fsh"):
        if source.name == generated.name:
            continue
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.startswith("Instance:"):
                names.add(line.split(":", 1)[1].strip())
    return names


def fsh_definitions(root: Path) -> dict[str, list[str]]:
    """Every hand-written FSH definition, keyed by its `Id`, as its own block of lines."""
    definitions: dict[str, list[str]] = {}
    for source in sorted(root.glob("*/input/fsh/*.fsh")):
        block: list[str] = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if re.match(r"^[A-Za-z]+:\s", line) and not line.startswith(("Id:", "Title:", "Description:")):
                if block:
                    definitions.setdefault(block_identifier(block), []).extend(block)
                block = [line]
            elif block:
                block.append(line)
        if block:
            definitions.setdefault(block_identifier(block), []).extend(block)
    definitions.pop("", None)
    return definitions


def block_identifier(block: list[str]) -> str:
    for line in block:
        if line.startswith("Id:"):
            return line.split(":", 1)[1].strip()
    return ""


def shared_value_set_example(
    canonical: str, root: Path
) -> tuple[str, str, str] | None:
    """A real concept from the terminology a hand-written value set draws on.

    A measurement that binds a shared value set carries no result codes of its own, so its example
    takes a concept the binding actually admits rather than inventing one.
    """
    definitions = fsh_definitions(root)
    block = definitions.get(canonical.rsplit("/", 1)[-1])
    if block is None:
        return None
    for line in block:
        # An enumerated value set names its system inline; an intensional one names it once.
        enumerated = re.match(r"^\* ([A-Za-z][A-Za-z0-9]*)#([^\s]+)", line)
        if enumerated:
            system, code = enumerated.groups()
            return system, code, concept_display(definitions, system, code) or code
        included = re.match(r"^\* include codes from system ([A-Za-z][A-Za-z0-9]*)$", line)
        if included:
            system = included.group(1)
            concept = first_concept(definitions, system)
            if concept:
                return (system, *concept)
    return None


def first_concept(definitions: dict[str, list[str]], system: str) -> tuple[str, str] | None:
    for block in definitions.values():
        if block[0] == f"CodeSystem: {system}":
            for line in block:
                concept = re.match(r'^\* #([^\s]+)\s+"([^"]+)"', line)
                if concept:
                    return concept.group(1), concept.group(2)
    return None


def concept_display(definitions: dict[str, list[str]], system: str, code: str) -> str | None:
    for block in definitions.values():
        if block[0] == f"CodeSystem: {system}":
            for line in block:
                concept = re.match(rf'^\* #{re.escape(code)}\s+"([^"]+)"', line)
                if concept:
                    return concept.group(1)
    return None


def render_example(
    measurement: dict,
    projections: dict[str, dict[str, dict]],
    contract: dict,
    root: Path,
) -> str:
    """One minimal, conformant example per generated profile.

    A profile that ships no instance leaves every reader guessing, and the Publisher reports it
    for each one. Projecting the example from the same catalog entry as the profile means it
    cannot drift from the constraints it exists to satisfy.
    """
    owner_key = measurement.get("owner", "mobile")
    owner = OWNERS[owner_key]
    profile = fsh_name(measurement["profile"])
    lines = [
        f"Instance: {profile}Example",
        f"InstanceOf: {profile}",
        "Usage: #example",
        f'Title: "{measurement["title"]} Example"',
        f'Description: "A conformant {measurement["title"]} instance."',
        *example_adapter_profile_lines(measurement, owner_key, projections),
        *example_identifier_lines(measurement, owner_key, projections, contract),
        "* status = #final",
        f"* code = {example_code(measurement, owner)}",
        *example_required_coding_lines(measurement),
        *example_category_lines(measurement),
        *example_source_type_lines(measurement, owner_key, projections),
        f"* subject = Reference({owner['patientExample']})",
        # Consumer health data is self-recorded, so the participant is also the performer.
        f"* performer = Reference({owner['patientExample']})",
        *example_effective_lines(measurement, owner_key, contract),
    ]
    method = example_method(measurement)
    if method:
        method_system = (
            "GroveAggregationMethodCS"
            if owner_key == "mobile"
            else "https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method"
        )
        lines.append(f"* method = {method_system}#{method}")
    lines.extend(example_result_lines(measurement, root))
    return "\n".join(lines) + "\n"


def example_adapter_profile_lines(
    measurement: dict,
    owner_key: str,
    projections: dict[str, dict[str, dict]],
) -> list[str]:
    """Declare a provider envelope separately from its semantic profile."""
    if owner_key not in PROVIDER_OWNERS:
        return []
    projection = example_projection(measurement, owner_key, projections)
    return [f'* meta.profile[+] = "{projection["adapterProfile"]}"']


def example_code(measurement: dict, owner: dict) -> str:
    code = measurement["code"]
    if code["system"] == LOINC:
        display = code.get("display")
        return f"$loinc#{code['code']}" + (f' "{display}"' if display else "")
    return f"{owner['codeSystem']}#{code['code']}"


def example_required_coding_lines(measurement: dict) -> list[str]:
    lines: list[str] = []
    for coding in measurement.get("requiredCodings", []):
        system = "$loinc" if coding["system"] == LOINC else coding["system"]
        display = f' "{coding["display"]}"' if coding.get("display") else ""
        lines.append(
            f"* code.coding[{coding['slice']}] = {system}#{coding['code']}{display}"
        )
    return lines


def example_category_lines(measurement: dict) -> list[str]:
    category = measurement.get("category")
    if not category:
        return []
    system = (
        "$observationCategory"
        if category["system"]
        == "http://terminology.hl7.org/CodeSystem/observation-category"
        else category["system"]
    )
    display = f' "{category["display"]}"' if category.get("display") else ""
    return [f"* category = {system}#{category['code']}{display}"]


def example_effective_lines(
    measurement: dict, owner_key: str, contract: dict
) -> list[str]:
    if measurement["effective"] == "Period":
        lines = [
            f'* effectivePeriod.start = "{contract["effectivePeriodStart"]}"',
            f'* effectivePeriod.end = "{contract["effectivePeriodEnd"]}"',
        ]
    else:
        lines = [f'* effectiveDateTime = "{contract["effectiveInstant"]}"']
    # Health Connect exposes the current source Record's store-availability time. HealthKit has no
    # equivalent, and no provider row names one; converter time is never Observation.issued.
    if owner_key == "health-connect":
        lines.append(
            f'* issued = "{contract["healthConnectLastModifiedTime"]}"'
        )
    return lines


def example_identity_record(
    measurement: dict,
    owner_key: str,
    projections: dict[str, dict[str, dict]],
    contract: dict,
) -> dict:
    """Build the manifest row and exact FSH identity pairs for one example."""
    projection = example_projection(measurement, owner_key, projections)
    native_id = f"{contract['nativeRecordPrefix']}{measurement['id']}"
    source_kind = projection["sourceIdentityKind"]
    if source_kind == "provider-record":
        scope = (
            contract["providerScope"]
            if projection["providerScopeMode"]
            == "deployment-scoped-account-pseudonym"
            else contract["globalProviderScope"]
        )
        source_components = [
            projection["providerCode"],
            projection["preimageSourceType"],
            scope["system"],
            scope["value"],
            native_id,
        ]
    else:
        scope = contract["repositoryScope"]
        source_components = [
            projection["adapterId"],
            projection["preimageSourceType"],
            scope["system"],
            scope["value"],
            native_id,
        ]
    output_components = [
        *source_components,
        projection["outputRole"],
        projection["outputDiscriminator"],
    ]
    output_kind = (
        "provider-output" if source_kind == "provider-record" else "source-output"
    )
    source_value = derive_hmac_identity(
        key=contract["key"],
        key_id=contract["keyId"],
        epoch=contract["epoch"],
        identity_kind=source_kind,
        components=source_components,
    )
    output_value = derive_hmac_identity(
        key=contract["key"],
        key_id=contract["keyId"],
        epoch=contract["epoch"],
        identity_kind=output_kind,
        components=output_components,
    )
    source_type = {
        "preimageToken": projection["preimageSourceType"],
        "wireCode": projection["wireSourceType"],
    }
    if "providerCode" in projection:
        source_type["providerCode"] = projection["providerCode"]
    availability = (
        {
            "fhirElement": "Observation.issued",
            "sourceField": "Metadata.lastModifiedTime",
            "value": contract["healthConnectLastModifiedTime"],
        }
        if owner_key == "health-connect"
        else {"fhirElement": "Observation.issued", "sourceField": "omitted"}
    )
    return {
        "guide": owner_key,
        "instance": f"{fsh_name(measurement['profile'])}Example",
        "measurementId": measurement["id"],
        "sourceType": source_type,
        "countRule": projection["countRule"],
        **({"graphRule": projection["graphRule"]} if "graphRule" in projection else {}),
        "sourceRecord": {
            "identityKind": source_kind,
            "identifierRole": "source-record",
            "system": contract["identitySystemsByKind"][source_kind],
            "components": source_components,
            "value": source_value,
        },
        "sourceOutput": {
            "identityKind": output_kind,
            "identifierRole": "source-output",
            "system": contract["identitySystemsByKind"][output_kind],
            "components": output_components,
            "value": output_value,
        },
        "availability": availability,
    }


def example_identifier_lines(
    measurement: dict,
    owner_key: str,
    projections: dict[str, dict[str, dict]],
    contract: dict,
) -> list[str]:
    """The business identity each guide's Observation profile requires of an instance."""
    record = example_identity_record(measurement, owner_key, projections, contract)
    return [
        f'* identifier[sourceRecord].system = "{record["sourceRecord"]["system"]}"',
        f'* identifier[sourceRecord].value = "{record["sourceRecord"]["value"]}"',
        f'* identifier[sourceOutput].system = "{record["sourceOutput"]["system"]}"',
        f'* identifier[sourceOutput].value = "{record["sourceOutput"]["value"]}"',
    ]


def example_source_type_lines(
    measurement: dict,
    owner_key: str,
    projections: dict[str, dict[str, dict]],
) -> list[str]:
    """The exact platform type an adapter Observation came from, which its profile requires."""
    projection = example_projection(measurement, owner_key, projections)
    token = projection["wireSourceType"]
    if owner_key in PROVIDER_OWNERS:
        # The semantic profile deliberately does not inherit the provider envelope, so its
        # InstanceOf has no named adapter slices. Add the canonical extensions directly; the
        # explicit adapter meta.profile claim makes Publisher validate their cardinality/value.
        return [
            '* extension[+].url = "https://grovealliance.org/fhir/providers/StructureDefinition/provider"',
            f"* extension[=].valueCode = #{projection['providerCode']}",
            '* extension[+].url = "https://grovealliance.org/fhir/providers/StructureDefinition/provider-source-type"',
            f"* extension[=].valueCode = #{token}",
        ]
    marker = SOURCE_TYPE_MARKERS.get(owner_key)
    return [marker.format(token=token)] if marker else []


def example_method(measurement: dict) -> str | None:
    """The aggregation method an example has to choose for itself.

    A profile that fixes one method already supplies it to every instance; only a profile offering
    a choice leaves the required element for the example to fill.
    """
    choice = measurement.get("methodChoice")
    return choice[0] if choice else None


def example_result_lines(measurement: dict, root: Path) -> list[str]:
    """The value the profile requires, in the exact shape the profile admits.

    Only components the profile requires are rendered. A workout declares every statistic any
    activity could carry, each optional, so emitting them all would publish a running workout
    that also counted swimming strokes.
    """
    kind = measurement.get("valueKind", "quantity")
    lines: list[str] = []
    if kind == "grouping":
        # A panel example must carry a member: the profile requires one, and an example without
        # members would not show what the panel is for.
        for member in measurement["exampleMembers"]:
            lines.append(f"* hasMember[+] = Reference({member})")
    if kind == "quantity":
        lines.append(f"* valueQuantity = {example_quantity(measurement['quantity'])}")
    elif kind == "codeableConcept":
        system, code, display = coded_example(measurement, root)
        lines.append(f'* valueCodeableConcept = {system}#{code} "{display}"')
    elif kind == "dateTime":
        lines.append(f'* valueDateTime = "{measurement["example"]}"')
    components = measurement.get("components", [])
    required = [c for c in components if not c.get("cardinality", "1..1").startswith("0")]
    # A components-valued measurement whose components are every one optional still has to show
    # some: an instance with no value, no component and no member fails grove-mobile-result-1, and
    # an example that carries nothing would not demonstrate the shape either. The first pair stands
    # for the rest, the way a workout example states the statistics that workout actually recorded.
    # Only a measurement whose value *is* its components needs the fallback. Everywhere else the
    # optional components stay out, so a running workout does not also report swimming strokes.
    if kind == "components" and not required:
        exemplary = components[: measurement.get("exampleComponentCount", 2)]
    else:
        exemplary = required
    for component in components:
        if component not in exemplary:
            continue
        slice_name = component["id"]
        if component["system"] == LOINC:
            lines.append(f"* component[{slice_name}].code = $loinc#{component['code']}")
        else:
            lines.append(
                f"* component[{slice_name}].code = {component['system']}#{component['code']}"
            )
        if component.get("quantity"):
            lines.append(
                f"* component[{slice_name}].valueQuantity = "
                f"{example_quantity(component['quantity'])}"
            )
        elif component.get("valueSet"):
            system, code, display = coded_example(component, root)
            lines.append(
                f"* component[{slice_name}].valueCodeableConcept = "
                f'{system}#{code} "{display}"'
            )
    return lines


def coded_example(source: dict, root: Path) -> tuple[str, str, str]:
    """The code system, code, and display an example uses for one coded value."""
    results = source.get("resultCodes")
    if results:
        return value_set_name(source["valueSet"])[:-2] + "CS", results[0]["code"], results[0]["display"]
    shared = shared_value_set_example(source["valueSet"], root)
    if shared is None:
        raise SystemExit(f"no example concept available for value set {source['valueSet']}")
    return shared


def example_quantity(quantity: dict) -> str:
    """A physiologically plausible value, so an example never reads as a placeholder."""
    unit = quantity.get("unit")
    rendered_unit = f' "{unit}"' if unit and unit != quantity["code"] else ""
    return f"{quantity['example']} '{quantity['code']}'{rendered_unit}"


def render_owner_terminology(owner_key: str, measurements: list[dict]) -> str | None:
    owner = OWNERS[owner_key]
    concepts = [
        m["code"]
        for m in measurements
        if m["code"]["system"].endswith(owner["measurementSystemTail"])
    ]
    for m in measurements:
        for component in m.get("components") or []:
            if str(component.get("system", "")).endswith(
                owner["measurementSystemTail"]
            ) and component.get("display"):
                concepts.append(
                    {
                        "code": component["code"],
                        "display": component["display"],
                        "definition": component.get("definition", component["display"]),
                    }
                )
    if not concepts:
        return None
    lines = [
        f"CodeSystem: {owner['codeSystem']}",
        f"Id: {owner['terminologyId']}",
        f'Title: "{owner["terminologyTitle"]}"',
        f'Description: "{owner["codeSystemDescription"]}"',
        "* ^experimental = false",
        "* ^caseSensitive = true",
        "* ^content = #complete",
    ]
    for code in concepts:
        lines.append(f'* #{code["code"]} "{code["display"]}" "{code["definition"]}"')
    lines.append("")
    lines.append(f"ValueSet: {owner['valueSet']}")
    lines.append(f"Id: {owner['terminologyId']}")
    lines.append(f'Title: "{owner["terminologyTitle"]}"')
    lines.append(f'Description: "{owner["valueSetDescription"]}"')
    lines.append("* ^experimental = false")
    lines.append(f"* include codes from system {owner['codeSystem']}")
    return "\n".join(lines) + "\n"


def render_code_set(name: str, terminology_id: str, title: str, codes: list) -> str:
    lines = [
        f"CodeSystem: {name}CS",
        f"Id: {terminology_id}",
        f'Title: "{title} Result"',
        f'Description: "The closed result codes of the {title} measurement."',
        "* ^experimental = false",
        "* ^caseSensitive = true",
        "* ^content = #complete",
    ]
    for code in codes:
        lines.append(f'* #{code["code"]} "{code["display"]}" "{code["definition"]}"')
    lines.append("")
    lines.append(f"ValueSet: {name}VS")
    lines.append(f"Id: {terminology_id}")
    lines.append(f'Title: "{title} Result"')
    lines.append(
        f'Description: "Every admitted result code of the {title} measurement."'
    )
    lines.append("* ^experimental = false")
    lines.append(f"* include codes from system {name}CS")
    return "\n".join(lines) + "\n"


def render_result_terminology(measurement: dict) -> list[str]:
    """Generate the CS/VS pairs for a measurement's coded result and components."""
    blocks: list[str] = []
    if measurement.get("resultCodes"):
        blocks.append(
            render_code_set(
                value_set_name(measurement["valueSet"])[:-2],
                measurement["valueSet"].rsplit("/", 1)[1],
                measurement["title"],
                measurement["resultCodes"],
            )
        )
    for component in measurement.get("components") or []:
        if component.get("resultCodes"):
            blocks.append(
                render_code_set(
                    value_set_name(component["valueSet"])[:-2],
                    component["valueSet"].rsplit("/", 1)[1],
                    component.get("title", measurement["title"] + " " + component["id"]),
                    component["resultCodes"],
                )
            )
    return blocks


def hand_block(layout: Layout, name: str) -> str | None:
    text = layout.hand_profiles.read_text(encoding="utf-8")
    match = re.search(
        rf"^Profile: {re.escape(name)}\n.*?(?=\n\n|\Z)", text, re.S | re.M
    )
    return None if match is None else match.group(0) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    arguments = parser.parse_args()
    layout = Layout(arguments.root.resolve())
    contract = example_contract(layout.root)
    projections = source_identity_projections(layout.root, contract)

    catalog = json.loads(layout.catalog.read_text(encoding="utf-8"))
    review_file = json.loads(layout.reviews.read_text(encoding="utf-8"))
    reviews = review_file["entries"]
    aliases = alias_map(layout)
    if review_file.get("digestScope") != DIGEST_SCOPE:
        print(
            f"terminology reviews declare digest scope "
            f"{review_file.get('digestScope')!r}, but this generator computes "
            f"{DIGEST_SCOPE!r}; re-mint the review digests"
        )
        return 2
    ground_truth = hashlib.sha256()
    for name in GROUND_TRUTH_FILES:
        ground_truth.update((layout.root / name).read_bytes())
    expected_ground_truth = "sha256:" + ground_truth.hexdigest()
    if review_file.get("groundTruthDigest") != expected_ground_truth:
        print(
            "the reviewed terminology ground truth changed "
            f"(recorded {review_file.get('groundTruthDigest')}, current "
            f"{expected_ground_truth}); re-review and re-mint"
        )
        return 2
    measurements = catalog["measurements"]
    by_id = {measurement["id"]: measurement for measurement in measurements}

    for measurement in measurements:
        entry = reviews.get(measurement["id"])
        if entry is None or entry.get("status") != "approved":
            print(
                f"{measurement['id']}: no approved terminology review entry; "
                "generation refused"
            )
            return 2
        digest = projection_digest(measurement)
        if entry.get("digest") != digest:
            print(
                f"{measurement['id']}: terminology changed since its review "
                f"(recorded {entry.get('digest')}, current {digest}); "
                "generation refused"
            )
            return 2

    problems = 0
    emitted: dict[str, list[str]] = {}
    for measurement in measurements:
        emitted_profile = measurement.get("generation", {}).get("emit", False)
        rendered = render_profile(
            measurement,
            aliases,
            by_id,
            include_domain_definition=emitted_profile,
        )
        owner_key = measurement.get("owner", "mobile")
        if emitted_profile:
            if owner_key == "mobile" and hand_block(
                layout, fsh_name(measurement["profile"])
            ) is not None:
                print(
                    f"{measurement['id']}: emitted profile is still hand-written "
                    "in profiles.fsh; remove the hand block"
                )
                problems += 1
            emitted.setdefault(owner_key, []).append(rendered)
            continue
        hand = hand_block(layout, fsh_name(measurement["profile"]))
        if hand is None:
            print(f"{measurement['id']}: no hand-written profile block to verify")
            problems += 1
        elif hand != rendered:
            print(f"{measurement['id']}: projection differs from the hand profile:")
            print(
                "".join(
                    difflib.unified_diff(
                        hand.splitlines(keepends=True),
                        rendered.splitlines(keepends=True),
                        "profiles.fsh",
                        "projected",
                    )
                )
            )
            problems += 1

    for owner_key in OWNERS:
        target = layout.generated_for(owner_key)
        owner_measurements = [
            m for m in measurements if m.get("owner", "mobile") == owner_key
        ]
        blocks: list[str] = []
        terminology = render_owner_terminology(owner_key, owner_measurements)
        if terminology and any(
            m.get("generation", {}).get("emit") for m in owner_measurements
        ):
            blocks.append(terminology)
        for measurement in owner_measurements:
            if measurement.get("generation", {}).get("emit"):
                blocks.extend(render_result_terminology(measurement))
        blocks.extend(emitted.get(owner_key, []))
        # Every generated profile ships one instance, so no profile reaches a reader unexemplified.
        # A hand-written example is richer than anything projected from the catalog, so it wins.
        handwritten = handwritten_instances(layout.root, owner_key)
        example_measurements = [
            measurement
            for measurement in owner_measurements
            if measurement.get("generation", {}).get("emit")
            and f"{fsh_name(measurement['profile'])}Example" not in handwritten
        ]
        blocks.extend(
            render_example(measurement, projections, contract, layout.root)
            for measurement in example_measurements
        )
        if blocks:
            rendered_file = HEADER + "\n".join(blocks)
            if arguments.check:
                if (
                    not target.is_file()
                    or target.read_text(encoding="utf-8") != rendered_file
                ):
                    print(
                        f"{target} is stale; run "
                        "Scripts/render-measurement-profiles.py"
                    )
                    problems += 1
            else:
                target.write_text(rendered_file, encoding="utf-8")
        elif target.exists():
            if arguments.check:
                print(f"{target} exists but no measurement has generation.emit")
                problems += 1
            else:
                target.unlink()

    emit_count = sum(
        1 for measurement in measurements if measurement.get("generation", {}).get("emit")
    )
    print(
        f"measurement profiles: {len(measurements)} measurements, "
        f"{emit_count} emitted, {len(measurements) - emit_count} parity-checked, "
        f"problems={problems}"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
