#!/usr/bin/env python3
"""Render the authoritative adapter inventories as published Markdown tables."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from collections import Counter
from functools import partial
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HEADER = """<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

"""


def load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "catalog" / name).read_text(encoding="utf-8"))


def cell(value: Any) -> str:
    if value is None or value == "" or value == []:
        return "—"
    if isinstance(value, list):
        value = "; ".join(str(item) for item in value) or "—"
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def profile_names(profiles: list[str]) -> str:
    return "; ".join(profile.rsplit("/", 1)[-1] for profile in profiles) or "—"


def healthkit() -> str:
    catalog = load("healthkit-adapter.json")
    rows = []
    for item in catalog["rows"]:
        requirement = item.get("requirement")
        admission_contract = item.get("clinicalAdmissionContract")
        if admission_contract is not None:
            requirement = catalog[admission_contract]["rule"]
        rows.append(
            [
                f"`{item['sourceTypeIdentifier']}`",
                item["title"],
                f"`{item['status']}`",
                ", ".join(item["measurementIDs"]),
                profile_names(item["profiles"]),
                requirement,
            ]
        )
    source = catalog["source"]
    sdk = source["sdkBaseline"]
    result = (
        HEADER
        + "### Authoritative HealthKit status matrix\n\n"
        + f"This table is the complete, closed inventory of all {source['rowCount']} "
        f"Apple HealthKit platform source types frozen against {sdk['platform']} "
        f"{sdk['version']} from Xcode {sdk['xcodeVersion']} build `{sdk['xcodeBuild']}`. "
        "The evidence is the official Apple platform documentation and the exact SDK "
        "provenance declared by the catalog. Each row has one definitive contract status; "
        "this is part of the Grove FHIR contracts, not a roadmap. `supported`, "
        "`platform-exclusive`, and `mapped-standard` each admit only the output "
        "contract(s) named in that row. `unmodeled`, `deferred`, and "
        "`intentionally-unsupported` admit no output; producers fail closed.\n\n"
        + table(
            [
                "HealthKit type",
                "Title",
                "Contract status",
                "Measurement",
                "Direct profile claim(s)",
                "Binding reason / requirement",
            ],
            rows,
        )
    )
    derived_rows = [
        [
            f"`{item['id']}`",
            item["title"],
            [f"`{identifier}`" for identifier in item["sourceTypeIdentifiers"]],
            f"`{item['status']}`",
            item["measurementIDs"],
            profile_names(item["profiles"]),
            item["requirement"],
        ]
        for item in catalog["derivedAggregates"]
    ]
    result += (
        "\n#### Derived aggregate contracts\n\n"
        "These rows are derived mappings, not HealthKit platform source identifiers, and "
        "are excluded from the source-type count and source-type CodeSystem.\n\n"
        + table(
            [
                "Aggregate",
                "Title",
                "Input source type(s)",
                "Contract status",
                "Measurement",
                "Target profile",
                "Binding reason / requirement",
            ],
            derived_rows,
        )
    )
    return result


def health_connect() -> str:
    catalog = load("health-connect-adapter.json")
    count_cardinalities = {
        "exactly-one": "1",
        "zero-or-one": "0..1",
        "one-per-sample": "0..*; one per sample",
        "one-per-stage": "0..*; one per stage",
        "one-per-present-field": "0..*; one per present field",
    }
    rows = []
    for item in catalog["recordTypes"]:
        outputs = []
        for output in item["outputs"]:
            if output["countRule"] == "graph-specific":
                cardinality = catalog["graphRules"][output["graphRule"]][
                    "shortCardinality"
                ]
            else:
                cardinality = count_cardinalities[output["countRule"]]
            detail = f"{output['measurement']} ({cardinality}"
            if output.get("when"):
                detail += f"; {output['when']}"
            outputs.append(detail + ")")
        rows.append(
            [
                f"`{item['token']}`",
                f"`{item['status']}`",
                outputs,
                [f"`{context}`" for context in item["context"]],
            ]
        )
    return (
        HEADER
        + "### Authoritative Health Connect status matrix\n\n"
        + "This table is the complete, closed AndroidX Health Connect 1.1.0 "
        "`RecordType.all` inventory. Each of the 41 record classes has exactly one "
        "definitive status under the Grove FHIR contracts. An empty output cell means the relevant Grove FHIR Implementation Guide admits no "
        "FHIR producer output for that class; it is not an implementation queue.\n\n"
        + table(
            ["Record class", "Status", "Admitted output(s)", "Exact context mapping(s)"],
            rows,
        )
    )


def sensorkit() -> str:
    catalog = load("sensorkit-adapter.json")
    entries = catalog["entries"]
    scope_counts = Counter(entry["scope"] for entry in entries)
    rows = []
    for item in catalog["entries"]:
        structured = item.get("structured", {})
        raw = item.get("raw", {})
        structured_contract = (
            structured.get("profile")
            or structured.get("adapterProfile")
            or structured.get("status")
        )
        raw_contract = raw.get("profile") or raw.get("status")
        reasons = [item.get("reason"), structured.get("reason")]
        rows.append(
            [
                f"`{item['sourceToken']}`",
                f"`{item['sourceTypeCode']}`",
                item["scope"],
                item["minimumIOS"],
                f"`{item['status']}`",
                structured_contract.rsplit("/", 1)[-1] if structured_contract else None,
                raw_contract.rsplit("/", 1)[-1] if raw_contract else None,
                next((reason for reason in reasons if reason), None),
            ]
        )
    return (
        HEADER
        + "### Authoritative SensorKit status matrix\n\n"
        + "This table is the complete SensorKit inventory under the Grove FHIR contracts: "
        f"{scope_counts.get('catalog-baseline', 0)} catalog-baseline platform symbols and "
        f"{scope_counts.get('stable-addition', 0)} stable additions in the stated Apple SDK "
        f"baseline. Each of the {len(entries)} rows has one definitive status. "
        "Recording Document support is distinct from a structured semantic mapping and "
        "never implies that fetching occurs in FHIR; `content.format` states whether its "
        "payload is CSV, FHIR, binary, native JSON, or another admitted format.\n\n"
        + table(
            [
                "SensorKit source",
                "Adapter code",
                "Inventory scope",
                "Minimum iOS",
                "Status",
                "Structured contract",
                "Raw contract",
                "Binding reason",
            ],
            rows,
        )
    )


def providers() -> str:
    catalog = load("providers-adapter.json")
    rows = []
    grouped_rows = []
    for provider in catalog["providers"]:
        for source in provider["sourceTypes"]:
            for element in source["elements"]:
                representation = element.get("unitConversion") or element.get("sensorProfile")
                rows.append(
                    [
                        f"`{provider['id']}`",
                        f"`{source['token']}`",
                        f"`{source['status']}`",
                        f"`{element['path']}`",
                        f"`{element['status']}`",
                        element.get("measurementIds"),
                        representation,
                        element.get("reason") or element.get("effective"),
                    ]
                )
        for grouped in provider.get("groupedMappings", []):
            grouped_rows.append(
                [
                    f"`{provider['id']}`",
                    f"`{grouped['token']}`",
                    [f"`{member}`" for member in grouped["members"]],
                    grouped["measurementIds"],
                    grouped["outputDiscriminator"],
                    grouped["rule"],
                ]
            )
    result = (
        HEADER
        + "### Authoritative connected-provider status matrix\n\n"
        + "This table lists every provider field in the published Google "
        "Health API, Oura, and Withings inventory. Each field has one definitive "
        "status. This adapter maps data already obtained before FHIR conversion; it contains no "
        "provider authentication, network, pagination, or fetching implementation.\n\n"
        + table(
            [
                "Provider",
                "Source type",
                "Source status",
                "Provider field",
                "Field status",
                "Measurement",
                "Representation / conversion",
                "Binding reason / effective time",
            ],
            rows,
        )
    )
    if grouped_rows:
        result += "\n#### Atomic grouped mappings\n\n"
        result += table(
            ["Provider", "Grouped source token", "Required members", "Measurement", "Output discriminator", "Rule"],
            grouped_rows,
        )
    return result


# Each vendor guide publishes the slice of the provider catalog it profiles, so the guide's own
# status matrix answers "what does this vendor carry" without the reader filtering three vendors.
VENDOR_GUIDES = {
    "withings": ("withings", "Withings Health Mate"),
    "oura": ("oura", "Oura"),
    "google-health": ("google-health-api", "Google Health API"),
}


def vendor(guide: str) -> str:
    provider_id, label = VENDOR_GUIDES[guide]
    catalog = load("providers-adapter.json")
    provider = next(p for p in catalog["providers"] if p["id"] == provider_id)
    rows = [
        [
            f"`{source['token']}`",
            f"`{source['status']}`",
            f"`{element['path']}`",
            f"`{element['status']}`",
            element.get("measurementIds"),
            element.get("unitConversion") or element.get("sensorProfile"),
            element.get("reason") or element.get("effective"),
        ]
        for source in provider["sourceTypes"]
        for element in source["elements"]
    ]
    result = (
        HEADER
        + f"### Authoritative {label} status matrix\n\n"
        + f"This table lists every {label} field in the published Grove inventory. "
        "Each field has one definitive status. This guide profiles data already obtained "
        "before FHIR conversion; it contains no authentication, network, pagination, or fetching "
        "implementation.\n\n"
        + table(
            [
                "Source type",
                "Source status",
                "Provider field",
                "Field status",
                "Measurement",
                "Representation / conversion",
                "Binding reason / effective time",
            ],
            rows,
        )
    )
    grouped = provider.get("groupedMappings", [])
    if grouped:
        result += "\n#### Atomic grouped mappings\n\n"
        result += table(
            ["Grouped source token", "Required members", "Measurement", "Output discriminator", "Rule"],
            [
                [
                    f"`{item['token']}`",
                    [f"`{member}`" for member in item["members"]],
                    item["measurementIds"],
                    item["outputDiscriminator"],
                    item["rule"],
                ]
                for item in grouped
            ],
        )
    return result


OUTPUTS = {
    ROOT / "healthkit/input/pagecontent/status-matrix.md": healthkit,
    ROOT / "health-connect/input/pagecontent/status-matrix.md": health_connect,
    ROOT / "sensorkit/input/pagecontent/status-matrix.md": sensorkit,
    ROOT / "providers/input/pagecontent/status-matrix.md": providers,
    **{
        ROOT / f"{guide}/input/pagecontent/status-matrix.md": partial(vendor, guide)
        for guide in VENDOR_GUIDES
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed matrices are stale")
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
        print("Stale generated status matrices:", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
