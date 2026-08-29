#!/usr/bin/env python3
"""Generate closed FSH source-type terminologies from adapter inventories."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HEADER = """//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// GENERATED FILE. Edit the adapter catalog and run
// `python3 Scripts/render-adapter-source-terminology.py`.
//

"""


def catalog(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "catalog" / name).read_text(encoding="utf-8"))


def fsh_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def property_definition(
    index: int, code: str, kind: str, description: str, *, guide: str
) -> str:
    uri = (
        f"https://grovealliance.org/fhir/{guide}/CodeSystem/{guide}-concept-property#{code}"
    )
    return "\n".join(
        [
            f"* ^property[{index}].code = #{code}",
            f'* ^property[{index}].uri = "{uri}"',
            f'* ^property[{index}].description = "{description}"',
            f"* ^property[{index}].type = #{kind}",
        ]
    )


def concept_property(code: str, index: int, name: str, value: str) -> str:
    return "\n".join(
        [
            f"* #{code} ^property[{index}].code = #{name}",
            f"* #{code} ^property[{index}].{value}",
        ]
    )


def property_code_system(
    guide: str, name: str, title: str, concepts: list[tuple[str, str, str]]
) -> str:
    lines = [
        f"CodeSystem: {name}ConceptPropertyCS",
        f"Id: {guide}-concept-property",
        f'Title: "{title} Concept Properties"',
        f'Description: "The concept properties the {title} source-type code system carries."',
        "* ^experimental = false",
        "* ^caseSensitive = true",
        "* ^content = #complete",
    ]
    lines += [f'* #{code} "{display}" "{definition}"' for code, display, definition in concepts]
    return "\n".join(lines) + "\n\n"


def source_type_definition(platform: str, symbol: str, outputs: list[str], reason: str | None) -> str:
    """What one platform source type means, and what Grove does with it.

    A `#complete` code system owes every concept a definition. Repeating the display name is not
    one, so each concept states its platform symbol and the disposition the catalog already
    records for it.
    """
    opening = f"The {platform} {symbol} source type."
    # A platform-exclusive type still produces output, just only in its own guide, so the
    # presence of an admitted output decides the wording rather than the status label.
    if outputs:
        return f"{opening} Grove converts it to {human_list(outputs)}."
    if reason:
        return f"{opening} Grove admits no output for it. {reason}"
    return f"{opening} Grove admits no output for it."


def human_list(values: list[str]) -> str:
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + f" and {values[-1]}"


def profile_names(profiles: list[str]) -> list[str]:
    return [profile.rsplit("/", 1)[-1] for profile in profiles]


def sensorkit_definition(entry: dict[str, Any]) -> str:
    structured = entry.get("structured") or {}
    profiles = [structured["profile"]] if structured.get("profile") else []
    return source_type_definition(
        "SensorKit",
        entry["sourceToken"],
        profile_names(profiles),
        structured.get("reason") or entry.get("reason"),
    )


def provider_definition(provider: dict[str, Any], source: dict[str, Any], grouped: bool = False) -> str:
    measurements = sorted(
        {
            measurement
            for element in source.get("elements", [])
            for measurement in element.get("measurementIds", [])
        }
        | set(source.get("measurementIds", []))
    )
    shape = "grouped mapping" if grouped else "source type"
    opening = f"The {provider['title']} {source['token']} {shape}."
    if measurements:
        return f"{opening} Grove converts it to {human_list(measurements)}."
    reason = source.get("reason") or source.get("requirement")
    if reason:
        return f"{opening} Grove admits no output for it. {reason}"
    return f"{opening} Grove admits no output for it."


def healthkit() -> str:
    data = catalog("healthkit-adapter.json")
    rows = data["rows"]
    evidence = json.loads(
        (ROOT / "healthkit/input/data/healthkit-inventory.json").read_text(encoding="utf-8")
    )["sourceTypes"]
    baseline = data["source"]["sdkBaseline"]
    definitions = property_definition(
        0,
        "documentation",
        "string",
        "Canonical Apple documentation page for this source type, recorded verbatim from "
        "Apple's published symbol index.",
        guide="healthkit",
    )
    blocks: list[str] = []
    for row in rows:
        code = row["sourceTypeIdentifier"]
        definition = source_type_definition(
            "HealthKit",
            code,
            profile_names(row.get("profiles", [])),
            row.get("requirement"),
        )
        block = [f'* #{code} "{fsh_text(row["title"])}" "{fsh_text(definition)}"']
        block.append(
            concept_property(
                code, 0, "documentation", f'valueString = "{fsh_text(row["documentation"])}"'
            )
        )
        blocks.append("\n".join(block))
    concepts = "\n".join(blocks)
    properties = property_code_system(
        "healthkit",
        "HealthKit",
        "HealthKit",
        [("documentation", "Documentation", "Canonical Apple documentation page for this source type.")],
    )
    return HEADER + properties + f'''CodeSystem: HealthKitSourceTypeCS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The {len(rows)} source-type identifiers the {baseline["platform"]} {baseline["version"]} SDK baseline (Xcode {baseline["xcodeVersion"]}, build {baseline["xcodeBuild"]}) hands back at runtime. A code is the identifier a producer reads from the sample, not the name of the constant that holds it. Membership is derived from, and verified against, healthkit/input/data/healthkit-inventory.json; the derived sleep-duration session aggregate is a Grove transformation contract rather than a platform source type and is excluded. The exact code is carried in the HealthKit source-type lineage extension and never asserted as an equivalent clinical result coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
{definitions}
{concepts}

ValueSet: HealthKitSourceTypeVS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The complete closed set of HealthKit platform source types in the authoritative catalog."
* ^experimental = false
* include codes from system HealthKitSourceTypeCS
'''


def sensorkit() -> str:
    entries = catalog("sensorkit-adapter.json")["entries"]
    baseline = catalog("sensorkit-adapter.json")["sourceEvidence"]["sdkBaseline"]
    definitions = "\n".join(
        [
            property_definition(
                0,
                "identifier",
                "string",
                "The SRSensor value this token names, which is what a producer reads back.",
                guide="sensorkit",
            ),
            property_definition(
                1,
                "documentation",
                "string",
                "Canonical Apple documentation page for the SRSensor constant, recorded "
                "verbatim from Apple's published symbol index.",
                guide="sensorkit",
            ),
        ]
    )
    concepts = "\n".join(
        "\n".join(
            [
                f'* #{entry["sourceTypeCode"]} "{fsh_text(entry["title"])}" '
                f'"{fsh_text(sensorkit_definition(entry))}"',
                concept_property(
                    entry["sourceTypeCode"], 0, "identifier",
                    f'valueString = "{fsh_text(entry["identifier"])}"',
                ),
                concept_property(
                    entry["sourceTypeCode"], 1, "documentation",
                    f'valueString = "{fsh_text(entry["documentation"])}"',
                ),
            ]
        )
        for entry in entries
    )
    properties = property_code_system(
        "sensorkit",
        "SensorKit",
        "SensorKit",
        [
            ("identifier", "Identifier", "The SRSensor value a producer reads back."),
            ("documentation", "Documentation", "Canonical Apple documentation page for the constant."),
        ],
    )
    return HEADER + properties + f'''CodeSystem: SensorKitSourceTypeCS
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "The {len(entries)} public SensorKit sensors published by the {baseline["platform"]} {baseline["version"]} SDK baseline (Xcode {baseline["xcodeVersion"]}, build {baseline["xcodeBuild"]}). Membership is derived from, and verified against, sensorkit/input/data/sensorkit-inventory.json. A code is a Grove token rather than an Apple string; the SRSensor value a producer reads back is carried as the identifier property."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "SensorKit API symbols originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
{definitions}
{concepts}

ValueSet: SensorKitSourceTypeVS
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "The exact SensorKit source stream token."
* ^experimental = false
* include codes from system SensorKitSourceTypeCS
'''


def health_connect() -> str:
    data = catalog("health-connect-adapter.json")
    rows = data["recordTypes"]
    artifact = json.loads(
        (ROOT / "health-connect/input/data/health-connect-inventory.json").read_text(
            encoding="utf-8"
        )
    )["oracle"]["artifact"]
    definitions = property_definition(
        0,
        "documentation",
        "string",
        "Canonical AndroidX documentation page for this record class.",
        guide="health-connect",
    )
    concepts = "\n".join(
        "\n".join(
            [
                f'* #{row["token"]} "{fsh_text(row["title"])}" '
                f'"{fsh_text(source_type_definition("Health Connect", row["token"], [output["measurement"] for output in row.get("outputs", [])], row.get("reason") or row.get("requirement")))}"',
                concept_property(
                    row["token"],
                    0,
                    "documentation",
                    f'valueString = "{fsh_text(row["documentation"])}"',
                ),
            ]
        )
        for row in rows
    )
    properties = property_code_system(
        "health-connect",
        "HealthConnect",
        "Health Connect",
        [("documentation", "Documentation", "Canonical AndroidX documentation page for this record class.")],
    )
    return HEADER + properties + f'''CodeSystem: HealthConnectRecordTypeCS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "Every concrete Record class published by {artifact}, excluding the abstract supertypes. Membership is derived from, and verified against, health-connect/input/data/health-connect-inventory.json. The code identifies the exact already-read source Record class; it is not a clinical result code."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "Health Connect record class names originate from the AndroidX project and are used here only to identify source API concepts for interoperability. AndroidX is licensed under Apache-2.0. The MIT license applies to Grove-authored definitions."
{definitions}
{concepts}

ValueSet: HealthConnectRecordTypeVS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete closed Health Connect 1.1.0 source Record class inventory."
* ^experimental = false
* include codes from system HealthConnectRecordTypeCS
'''


def providers() -> str:
    data = catalog("providers-adapter.json")
    rows: list[tuple[str, str, str]] = []
    for provider in data["providers"]:
        for source in provider["sourceTypes"]:
            rows.append(
                (
                    f"{provider['id']}/{source['token']}",
                    f"{provider['title']}: {source['token']}",
                    provider_definition(provider, source),
                )
            )
        for grouped in provider.get("groupedMappings", []):
            rows.append(
                (
                    f"{provider['id']}/{grouped['token']}",
                    f"{provider['title']}: {grouped['token']} (atomic grouped mapping)",
                    provider_definition(provider, grouped, grouped=True),
                )
            )
    rows.sort()
    if len(rows) != len({code for code, _, _ in rows}):
        raise ValueError("connected provider-qualified source-type codes are not unique")
    concepts = "\n".join(
        f'* #{code} "{fsh_text(title)}" "{fsh_text(definition)}"'
        for code, title, definition in rows
    )
    return HEADER + f'''CodeSystem: ProviderSourceTypeCS
Id: provider-source-type
Title: "Provider Source Types"
Description: "The complete provider-qualified Google Health API, Oura, and Withings source inventory admitted or explicitly classified by the Grove FHIR contracts. The code is source lineage, not a clinical result code or fetch instruction."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
{concepts}

ValueSet: ProviderSourceTypeVS
Id: provider-source-type
Title: "Provider Source Types"
Description: "The complete closed provider-qualified source-type inventory for the relevant Grove FHIR Implementation Guide."
* ^experimental = false
* include codes from system ProviderSourceTypeCS
'''


OUTPUTS = {
    ROOT / "healthkit/input/fsh/generated-source-types.fsh": healthkit,
    ROOT / "sensorkit/input/fsh/generated-source-types.fsh": sensorkit,
    ROOT / "health-connect/input/fsh/generated-source-types.fsh": health_connect,
    ROOT / "providers/input/fsh/generated-source-types.fsh": providers,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale: list[Path] = []
    for path, renderer in OUTPUTS.items():
        rendered = renderer()
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                stale.append(path.relative_to(ROOT))
        else:
            path.write_text(rendered, encoding="utf-8")
    if stale:
        print("Stale generated adapter source terminologies:", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
