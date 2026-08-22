#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""The offline terminology gate over the pinned LOINC and UCUM tables.

Guides build with -tx n/a, so nothing checks codes at build time; this gate is
the deterministic replacement. It fails when a catalog or FSH source uses a
LOINC code missing from the pinned excerpt, a display that drifted from the
pinned one, a UCUM code the pinned atom table cannot parse, an {annotation}
outside the closed allowlist, or a unit whose dimension contradicts the LOINC
PROPERTY of the code it quantifies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "Scripts"))
from ucum_expression import UcumError, UcumTable  # noqa: E402

LOINC = "http://loinc.org"
UCUM = "http://unitsofmeasure.org"
FSH_LOINC = re.compile(r"\$loinc#(\S+)\s+\"([^\"]+)\"")


def load(root: Path, name: str) -> dict:
    return json.loads((root / "catalog/terminology" / name).read_text(encoding="utf-8"))


def collect_codings(value: object, where: str, loinc: list, ucum: list) -> None:
    if isinstance(value, dict):
        if value.get("system") == LOINC and isinstance(value.get("code"), str):
            loinc.append((value["code"], value.get("display"), where))
        if value.get("system") == UCUM and isinstance(value.get("code"), str):
            ucum.append((value["code"], where))
        for key, child in value.items():
            collect_codings(child, f"{where}.{key}", loinc, ucum)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            collect_codings(child, f"{where}[{index}]", loinc, ucum)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    root = parser.parse_args().root.resolve()
    concepts = load(root, "loinc-concepts.json")
    annotations = load(root, "ucum-annotations.json")["annotations"]
    table = UcumTable(load(root, "ucum-units.json"))
    pinned = concepts["concepts"]
    property_dimensions = concepts["propertyDimensions"]

    problems: list[str] = []
    loinc_uses: list[tuple[str, str | None, str]] = []
    ucum_uses: list[tuple[str, str]] = []

    for catalog in sorted((root / "catalog").glob("*.json")):
        collect_codings(
            json.loads(catalog.read_text(encoding="utf-8")),
            catalog.name,
            loinc_uses,
            ucum_uses,
        )
    for fsh in sorted(root.glob("*/input/fsh/*.fsh")):
        for match in FSH_LOINC.finditer(fsh.read_text(encoding="utf-8")):
            loinc_uses.append(
                (match.group(1), match.group(2), str(fsh.relative_to(root)))
            )

    for code, display, where in loinc_uses:
        row = pinned.get(code)
        if row is None:
            problems.append(f"{where}: LOINC {code} is not pinned")
            continue
        if display is not None and display != row["display"]:
            problems.append(
                f"{where}: LOINC {code} display {display!r} differs from the "
                f"pinned {row['display']!r}"
            )

    parsed_units: dict[str, object] = {}
    for code, where in ucum_uses:
        try:
            parsed = table.parse(code)
        except UcumError as error:
            problems.append(f"{where}: UCUM {code!r}: {error}")
            continue
        parsed_units[code] = parsed
        for annotation in parsed.annotations:
            if annotation not in annotations:
                problems.append(
                    f"{where}: UCUM annotation {{{annotation}}} is not allowlisted"
                )

    measurement_catalog = json.loads(
        (root / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
    )
    quantified: list[tuple[str, dict, dict | None, str]] = []
    for measurement in measurement_catalog["measurements"]:
        quantified.append(
            (measurement["id"], measurement["code"], measurement.get("quantity"), "")
        )
        for component in measurement.get("components") or []:
            quantified.append(
                (
                    measurement["id"],
                    {"system": component.get("system"), "code": component.get("code")},
                    component.get("quantity"),
                    f".components.{component.get('id')}",
                )
            )
    for measurement_id, code, quantity, suffix in quantified:
        if code.get("system") != LOINC or not quantity:
            continue
        row = pinned.get(code["code"])
        if row is None:
            continue  # already reported above
        if row["property"] not in property_dimensions:
            problems.append(
                f"measurement-catalog.json:{measurement_id}{suffix}: LOINC "
                f"{code['code']} PROPERTY {row['property']} has no dimension "
                "mapping; add it to propertyDimensions"
            )
            continue
        expected = property_dimensions[row["property"]]
        if expected is None:
            continue
        parsed = parsed_units.get(quantity["code"])
        if parsed is None:
            continue  # unparseable unit already reported above
        if parsed.dimension != expected:
            problems.append(
                f"measurement-catalog.json:{measurement_id}{suffix}: unit "
                f"{quantity['code']!r} has dimension {parsed.dimension}, but "
                f"LOINC {code['code']} PROPERTY {row['property']} requires {expected}"
            )

    for problem in problems:
        print(problem)
    print(
        f"terminology gate: loinc-uses={len(loinc_uses)} ucum-uses={len(ucum_uses)} "
        f"pinned-concepts={len(pinned)} problems={len(problems)}"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
