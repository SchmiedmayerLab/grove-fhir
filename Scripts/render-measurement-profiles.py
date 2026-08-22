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


class Layout:
    """The repo-relative inputs and outputs, bound to one root."""

    def __init__(self, root: Path) -> None:
        self.catalog = root / "catalog/measurement-catalog.json"
        self.reviews = root / "mobile/input/data/terminology-reviews.json"
        self.aliases = root / "mobile/input/fsh/aliases.fsh"
        self.hand_profiles = root / "mobile/input/fsh/profiles.fsh"
        self.generated = root / "mobile/input/fsh/generated-measurement-profiles.fsh"

LOINC = "http://loinc.org"
GROVE_MEASUREMENT_CS_TAIL = "/CodeSystem/grove-mobile-measurement"

HEADER = """// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

"""

PROJECTION_KEYS = (
    "code",
    "components",
    "effective",
    "hasMember",
    "quantity",
    "standardProfile",
    "valueSet",
    "resultCodeSystem",
    "allowedValues",
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
    name = fsh_name(measurement["profile"])
    lines = [
        f"Profile: {name}",
        "Parent: GroveMobileObservation",
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
    elif code["system"].endswith(GROVE_MEASUREMENT_CS_TAIL):
        lines.append(f"* code = GroveMobileMeasurementCS#{code['code']}")
        lines.append("* code from GroveMobileMeasurementVS (required)")
    else:
        raise SystemExit(f"{measurement['id']}: unsupported code system {code['system']}")
    if measurement["effective"] == "Period":
        lines.append("* effective[x] only Period")
        lines.append("* effectivePeriod.end 1..1 MS")
    else:
        lines.append("* effective[x] only dateTime")
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
        lines.append("* component ^slicing.discriminator.type = #pattern")
        lines.append('* component ^slicing.discriminator.path = "code"')
        lines.append("* component ^slicing.rules = #open")
        contains = " and ".join(
            f"{component['id']} 1..1 MS" for component in measurement["components"]
        )
        lines.append(f"* component contains {contains}")
        for component in measurement["components"]:
            slice_name = component["id"]
            if component["system"] != LOINC:
                raise SystemExit(
                    f"{measurement['id']}: unsupported component system "
                    f"{component['system']}"
                )
            lines.append(f"* component[{slice_name}].code = $loinc#{component['code']}")
            lines.extend(
                quantity_rules(
                    f"component[{slice_name}].", component["quantity"], False
                )
            )
    else:
        raise SystemExit(f"{measurement['id']}: unsupported valueKind {kind}")
    for member in measurement.get("hasMember", []):
        lines.append(
            f"* hasMember only Reference({fsh_name(by_id[member]['profile'])})"
        )
    return "\n".join(lines) + "\n"


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
    reviews = json.loads(layout.reviews.read_text(encoding="utf-8"))["entries"]
    aliases = alias_map(layout)
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
    emitted: list[str] = []
    for measurement in measurements:
        rendered = render_profile(measurement, aliases, by_id)
        if measurement.get("generation", {}).get("emit"):
            if hand_block(layout, fsh_name(measurement["profile"])) is not None:
                print(
                    f"{measurement['id']}: emitted profile is still hand-written "
                    "in profiles.fsh; remove the hand block"
                )
                problems += 1
            emitted.append(rendered)
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

    if emitted:
        rendered_file = HEADER + "\n".join(emitted)
        if arguments.check:
            if (
                not layout.generated.is_file()
                or layout.generated.read_text(encoding="utf-8") != rendered_file
            ):
                print(
                    f"{layout.generated} is stale; run "
                    "Scripts/render-measurement-profiles.py"
                )
                problems += 1
        else:
            layout.generated.write_text(rendered_file, encoding="utf-8")
    elif layout.generated.exists():
        if arguments.check:
            print(f"{layout.generated} exists but no measurement has generation.emit")
            problems += 1
        else:
            layout.generated.unlink()

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
