#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Project the shared Mobile measurement profiles from the measurement catalog.

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

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

OWNERS = {
    "mobile": {
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
        "parent": "HealthKitObservation",
        "generated": "healthkit/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/healthkit-measurement",
        "codeSystem": "HealthKitMeasurementCS",
        "valueSet": "HealthKitMeasurementVS",
        "terminologyId": "healthkit-measurement",
        "terminologyTitle": "HealthKit Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the HealthKit adapter for "
            "platform-exclusive results no established code represents faithfully."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the HealthKit adapter for its "
            "platform-exclusive profiles."
        ),
    },
    "providers": {
        "parent": "ProviderObservation",
        "generated": "providers/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/provider-measurement",
        "codeSystem": "ProviderMeasurementCS",
        "valueSet": "ProviderMeasurementVS",
        "terminologyId": "provider-measurement",
        "terminologyTitle": "Provider Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the providers adapter for "
            "provider-scoped results no established code represents faithfully."
        ),
        "valueSetDescription": (
            "Measurement concepts defined by the providers adapter for its "
            "provider-scoped profiles."
        ),
    },
    "health-connect": {
        "parent": "HealthConnectObservation",
        "generated": "health-connect/input/fsh/generated-measurement-profiles.fsh",
        "measurementSystemTail": "/CodeSystem/health-connect-measurement",
        "codeSystem": "HealthConnectMeasurementCS",
        "valueSet": "HealthConnectMeasurementVS",
        "terminologyId": "health-connect-measurement",
        "terminologyTitle": "Health Connect Measurement",
        "codeSystemDescription": (
            "Measurement concepts defined by the Health Connect adapter for "
            "platform-exclusive results no established code represents faithfully."
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


def projection_digest(measurement: dict) -> str:
    projection = {
        key: measurement.get(key)
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


def quantity_rules(prefix: str, quantity: dict, strict: bool) -> list[str]:
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
    return rules


def render_profile(measurement: dict, aliases: dict[str, str], by_id: dict) -> str:
    owner = OWNERS[measurement.get("owner", "mobile")]
    name = fsh_name(measurement["profile"])
    lines = [
        f"Profile: {name}",
        f"Parent: {owner['parent']}",
        f"Id: {measurement['profile']}",
        f'Title: "{measurement["title"]}"',
        f'Description: "{measurement["description"]}"',
    ]
    if measurement.get("obeys"):
        lines.append("* obeys " + " and ".join(measurement["obeys"]))
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
    if measurement["effective"] == "Period":
        lines.append("* effective[x] only Period")
        lines.append("* effectivePeriod.end 1..1 MS")
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
        lines.append(
            f"* method = {method_cs}#{method['code']} "
            f'"{method["display"]}"'
        )
    elif measurement.get("methodChoice"):
        lines.append("* method 1..1 MS")
        lines.append(f"* method from {method_vs} (required)")
    kind = measurement["valueKind"]
    if kind == "quantity":
        lines.extend(quantity_rules("", measurement["quantity"], standard is None))
    elif kind == "codeableConcept":
        lines.append("* value[x] only CodeableConcept")
        lines.append("* valueCodeableConcept 1..1 MS")
        lines.append(
            f"* valueCodeableConcept from {value_set_name(measurement['valueSet'])} (required)"
        )
    elif kind == "components":
        lines.append("* value[x] 0..0")
    else:
        raise SystemExit(f"{measurement['id']}: unsupported valueKind {kind}")
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
    return "\n".join(lines) + "\n"


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
        rendered = render_profile(measurement, aliases, by_id)
        owner_key = measurement.get("owner", "mobile")
        if measurement.get("generation", {}).get("emit"):
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
