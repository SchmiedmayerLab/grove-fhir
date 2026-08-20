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


def healthkit() -> str:
    rows = catalog("healthkit-adapter.json")["rows"]
    concepts = "\n".join(
        f'* #{row["sourceTypeIdentifier"]} "{fsh_text(row["title"])}"'
        for row in rows
    )
    return HEADER + f'''CodeSystem: HealthKitSourceTypeCS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The complete closed HealthKit type inventory consumed by the Grove 0.2.0 adapter. A coding preserves exact source semantics and does not replace the shared or standard clinical coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
{concepts}

ValueSet: HealthKitSourceTypeVS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The complete closed set of HealthKit source types known to the Grove 0.2.0 adapter."
* ^experimental = false
* include codes from system HealthKitSourceTypeCS
'''


def health_connect() -> str:
    rows = catalog("health-connect-adapter.json")["recordTypes"]
    concepts = "\n".join(
        f'* #{row["token"]} "{fsh_text(row["token"])}"'
        for row in rows
    )
    return HEADER + f'''CodeSystem: HealthConnectRecordTypeCS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete AndroidX Health Connect 1.1.0 RecordType.all inventory. The code identifies the exact already-read source Record class; it is not a clinical result code."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
{concepts}

ValueSet: HealthConnectRecordTypeVS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete closed Health Connect 1.1.0 source Record class inventory."
* ^experimental = false
* include codes from system HealthConnectRecordTypeCS
'''


def connected_health() -> str:
    data = catalog("connected-health-adapter.json")
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
    return HEADER + f'''CodeSystem: ConnectedHealthSourceTypeCS
Id: connected-health-source-type
Title: "Connected Health Source Types"
Description: "The complete provider-qualified Google Health API, Oura, and Withings source inventory admitted or explicitly classified by version 0.2.0. The code is source lineage, not a clinical result code or fetch instruction."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
{concepts}

ValueSet: ConnectedHealthSourceTypeVS
Id: connected-health-source-type
Title: "Connected Health Source Types"
Description: "The complete closed provider-qualified source-type inventory for the Connected Health 0.2.0 adapter."
* ^experimental = false
* include codes from system ConnectedHealthSourceTypeCS
'''


OUTPUTS = {
    ROOT / "healthkit/input/fsh/generated-source-types.fsh": healthkit,
    ROOT / "health-connect/input/fsh/generated-source-types.fsh": health_connect,
    ROOT / "connected-health/input/fsh/generated-source-types.fsh": connected_health,
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
