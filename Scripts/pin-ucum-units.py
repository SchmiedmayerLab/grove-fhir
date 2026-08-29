#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Derive the pinned UCUM atom table from a version-pinned ucum-essence.xml.

The committed table at catalog/terminology/ucum-units.json is the offline
authority the terminology gate validates unit codes against. It is derived,
never hand-transcribed: every atom's dimension vector is resolved from the
essence file's own definitions, and the source version and sha256 are recorded
so a refresh against a different essence file is an explicit reviewed change.

Usage:
  Scripts/pin-ucum-units.py --source <ucum-essence.xml>          # refresh
  Scripts/pin-ucum-units.py --source <ucum-essence.xml> --check  # verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINNED_TABLE = ROOT / "catalog/terminology/ucum-units.json"
NAMESPACE = "{http://unitsofmeasure.org/ucum-essence}"
SOURCE_URL = "https://raw.githubusercontent.com/ucum-org/ucum/main/ucum-essence.xml"

sys.path.insert(0, str(ROOT / "Scripts"))
from ucum_expression import UcumError, UcumTable  # noqa: E402


def derive_table(source: Path) -> dict:
    tree = ElementTree.parse(source)
    root = tree.getroot()

    prefixes: dict[str, dict] = {}
    for prefix in root.iter(f"{NAMESPACE}prefix"):
        value = prefix.find(f"{NAMESPACE}value")
        prefixes[prefix.attrib["Code"]] = {"factor": value.attrib["value"]}

    units: dict[str, dict] = {}
    for base in root.iter(f"{NAMESPACE}base-unit"):
        units[base.attrib["Code"]] = {
            "dimension": {base.attrib["Code"]: 1},
            "isMetric": True,
            "property": base.findtext(f"{NAMESPACE}property"),
        }

    pending: list[tuple[str, dict, str]] = []
    for unit in root.iter(f"{NAMESPACE}unit"):
        code = unit.attrib["Code"]
        entry = {
            "isMetric": unit.attrib.get("isMetric") == "yes",
            "property": unit.findtext(f"{NAMESPACE}property"),
        }
        if unit.attrib.get("isSpecial") == "yes":
            entry["isSpecial"] = True
        if unit.attrib.get("isArbitrary") == "yes":
            entry["isArbitrary"] = True
        value = unit.find(f"{NAMESPACE}value")
        function = value.find(f"{NAMESPACE}function")
        if function is not None:
            definition = function.attrib["Unit"]
        else:
            definition = value.attrib["Unit"]
        if entry.get("isArbitrary"):
            entry["dimension"] = {}
            units[code] = entry
        else:
            pending.append((code, entry, definition))

    # Definitions reference other defined units; resolve to base-unit vectors
    # by fixpoint iteration over the growing table.
    while pending:
        table = UcumTable({"prefixes": prefixes, "units": units})
        remaining: list[tuple[str, dict, str]] = []
        for code, entry, definition in pending:
            try:
                parsed = table.parse(definition)
            except UcumError:
                remaining.append((code, entry, definition))
                continue
            entry["dimension"] = parsed.dimension
            units[code] = entry
        if len(remaining) == len(pending):
            unresolved = ", ".join(sorted(code for code, _, _ in remaining))
            raise SystemExit(f"unresolvable unit definitions: {unresolved}")
        pending = remaining

    return {
        "schemaVersion": 0,
        "ucumVersion": root.attrib["version"],
        "revisionDate": root.attrib["revision-date"],
        "source": {
            "url": SOURCE_URL,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
        "baseUnits": sorted(
            base.attrib["Code"] for base in root.iter(f"{NAMESPACE}base-unit")
        ),
        "prefixes": dict(sorted(prefixes.items())),
        "units": dict(sorted(units.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    derived = derive_table(arguments.source)
    rendered = json.dumps(derived, indent=2, ensure_ascii=False) + "\n"
    if arguments.check:
        if not PINNED_TABLE.is_file() or PINNED_TABLE.read_text() != rendered:
            print(f"{PINNED_TABLE} is stale; run Scripts/pin-ucum-units.py")
            return 1
        print(f"{PINNED_TABLE} matches {arguments.source}")
        return 0
    PINNED_TABLE.parent.mkdir(parents=True, exist_ok=True)
    PINNED_TABLE.write_text(rendered)
    print(f"pinned {len(derived['units'])} atoms from UCUM {derived['ucumVersion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
