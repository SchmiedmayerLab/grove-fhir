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
        block = [f'* #{code} "{fsh_text(row["title"])}"']
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
Description: "The {len(rows)} source-type identifiers the {baseline["platform"]} {baseline["version"]} SDK baseline (Xcode {baseline["xcodeVersion"]}, build {baseline["xcodeBuild"]}) hands back at runtime. A code is the identifier a producer reads from the sample, not the name of the constant that holds it. Membership is derived from, and verified against, healthkit/input/data/healthkit-inventory.json; the derived sleep-duration session aggregate is a Grove transformation contract rather than a platform source type and is excluded. A coding preserves exact source semantics and does not replace the shared or standard clinical coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
{definitions}
{concepts}

ValueSet: HealthKitSourceTypeVS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The complete closed set of HealthKit platform source types in the version 0.3.0 catalog."
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
                f'* #{entry["sourceTypeCode"]} "{fsh_text(entry["title"])}"',
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
                f'* #{row["token"]} "{fsh_text(row["title"])}"',
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
    rows: list[tuple[str, str]] = []
    for provider in data["providers"]:
        for source in provider["sourceTypes"]:
            rows.append(
                (
                    f"{provider['id']}/{source['token']}",
                    f"{provider['title']}: {source['token']}",
                )
            )
        for grouped in provider.get("groupedMappings", []):
            rows.append(
                (
                    f"{provider['id']}/{grouped['token']}",
                    f"{provider['title']}: {grouped['token']} (atomic grouped mapping)",
                )
            )
    rows.sort()
    if len(rows) != len({code for code, _ in rows}):
        raise ValueError("connected provider-qualified source-type codes are not unique")
    concepts = "\n".join(
        f'* #{code} "{fsh_text(title)}"' for code, title in rows
    )
    return HEADER + f'''CodeSystem: ProviderSourceTypeCS
Id: provider-source-type
Title: "Provider Source Types"
Description: "The complete provider-qualified Google Health API, Oura, and Withings source inventory admitted or explicitly classified by version 0.3.0. The code is source lineage, not a clinical result code or fetch instruction."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
{concepts}

ValueSet: ProviderSourceTypeVS
Id: provider-source-type
Title: "Provider Source Types"
Description: "The complete closed provider-qualified source-type inventory for the Provider 0.3.0 adapter."
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
