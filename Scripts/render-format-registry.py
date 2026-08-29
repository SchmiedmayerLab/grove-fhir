#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Render the recording format registry into the sensor guide.

catalog/format-registry.json is the authoritative closed registry of payload
formats a Grove recording DocumentReference may declare; this renderer projects
it into the format terminology FSH and the narrative formats page so the guide
and the machine contract can never drift apart.

Usage:
  Scripts/render-format-registry.py           # write both outputs
  Scripts/render-format-registry.py --check   # verify both outputs are current
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "catalog/format-registry.json"
FSH_OUTPUT = ROOT / "sensor/input/fsh/generated-recording-formats.fsh"
PAGE_OUTPUT = ROOT / "sensor/input/pagecontent/formats.md"
MIME_OUTPUT = ROOT / "sensor/input/fsh/generated-recording-mime-types.fsh"

FSH_HEADER = """//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// GENERATED FILE. Edit catalog/format-registry.json and run
// `python3 Scripts/render-format-registry.py`.
//
"""

PAGE_HEADER = """<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit catalog/format-registry.json and run
`python3 Scripts/render-format-registry.py`.
-->
"""


MIME_EXPANSION_TIMESTAMP = "2026-08-20T00:00:00Z"


def render_mime_fsh(registry: dict) -> str:
    media_types = registry["mediaTypes"]
    used = {fmt["contentType"] for fmt in registry["formats"].values()}
    undeclared = used - set(media_types)
    if undeclared:
        raise SystemExit(f"media types used by a format but not declared: {sorted(undeclared)}")
    unused = set(media_types) - used
    if unused:
        raise SystemExit(f"media types declared but used by no format: {sorted(unused)}")

    lines = [FSH_HEADER]
    lines.append("ValueSet: GroveRecordingMimeTypeVS")
    lines.append("Id: grove-recording-mime-type")
    lines.append('Title: "Grove Recording MIME Types"')
    lines.append(
        'Description: "The exact media types admitted for a Grove sensor recording payload. '
        "The codes are registered media types identified by their IANA registration. Grove "
        "does not publish or version the "
        'external code system."'
    )
    lines.append("* ^experimental = false")
    for code, display in media_types.items():
        lines.append(f'* urn:ietf:bcp:13#{code} "{display}"')
    lines.append(f'* ^expansion.timestamp = "{MIME_EXPANSION_TIMESTAMP}"')
    lines.append('* ^expansion.parameter[+].name = "used-codesystem"')
    lines.append('* ^expansion.parameter[=].valueUri = "urn:ietf:bcp:13"')
    lines.append('* ^expansion.parameter[+].name = "includeDesignations"')
    lines.append("* ^expansion.parameter[=].valueBoolean = false")
    for code, display in media_types.items():
        lines.append('* ^expansion.contains[+].system = "urn:ietf:bcp:13"')
        lines.append(f"* ^expansion.contains[=].code = #{code}")
        lines.append(f'* ^expansion.contains[=].display = "{display}"')
    return "\n".join(lines) + "\n"


def resolved_specification(registry: dict, fmt: dict) -> dict:
    """The format's effective specification, with any shared encoding block folded in.

    Shared encoding rules live once in the registry so they cannot drift between the streams
    that cite them; every rendered output still states them in full.
    """
    specification = dict(registry.get("encodings", {}).get(fmt.get("encoding"), {}))
    specification.update(fmt.get("specification", {}))
    return specification


def concept_definition(fmt: dict, specification: dict) -> str:
    summary = specification.get("structure") or specification.get("file")
    if not summary:
        return ""
    if "columns" not in fmt:
        return summary
    names = ", ".join(column["name"] for column in fmt["columns"])
    return f"{summary} Columns: {names}."


def render_fsh(registry: dict) -> str:
    lines = [FSH_HEADER]
    lines.append("CodeSystem: GroveRecordingFormatCS")
    lines.append("Id: grove-recording-format")
    lines.append('Title: "Grove Recording Format"')
    lines.append(
        'Description: "The closed registry of payload formats a Grove recording '
        "DocumentReference may declare in content.format. Each code identifies a wire "
        "format and structural envelope. Native Recording defines only a JSON object-or-array "
        'container; the carrying source type supplies its category and meaning."'
    )
    lines.append("* ^experimental = false")
    lines.append("* ^caseSensitive = true")
    lines.append("* ^content = #complete")
    for code, fmt in registry["formats"].items():
        # A #complete code system owes each concept a definition; repeating the title is not
        # one. A binary format describes its layout under `file` rather than `structure`.
        definition = concept_definition(fmt, resolved_specification(registry, fmt))
        if not definition:
            raise SystemExit(f"{code}: the registry states no structure or file layout to define it by")
        lines.append(f'* #{code} "{fmt["title"]}" "{definition}"')
    lines.append("")
    lines.append("ValueSet: GroveRecordingFormatVS")
    lines.append("Id: grove-recording-format")
    lines.append('Title: "Grove Recording Format"')
    lines.append(
        'Description: "Every payload format admitted for a Grove recording '
        'DocumentReference content entry."'
    )
    lines.append("* ^experimental = false")
    lines.append("* include codes from system GroveRecordingFormatCS")
    return "\n".join(lines) + "\n"


def render_column_table(fmt: dict) -> list[str]:
    lines = [
        "",
        "| Column | Type | Nullable | Unit | Meaning |",
        "|---|---|---|---|---|",
    ]
    for column in fmt["columns"]:
        unit = f"`{column['unit']}`" if "unit" in column else "—"
        nullable = "yes" if column["nullable"] else "no"
        lines.append(
            f"| `{column['name']}` | {column['type']} | {nullable} | {unit} | {column['meaning']} |"
        )
    return lines


def render_record_table(title: str, fields: list[dict]) -> list[str]:
    lines = ["", f"**{title}**", "", "| Field | Encoding | Unit | Meaning |", "|---|---|---|---|"]
    for field in fields:
        unit = f"`{field['unit']}`" if "unit" in field else "—"
        meaning = field.get("meaning", "")
        lines.append(
            f"| `{field['field']}` | `{field['encoding']}` | {unit} | {meaning} |"
        )
    return lines


def render_page(registry: dict) -> str:
    lines = [PAGE_HEADER]
    lines.append(
        "Every Grove recording DocumentReference content entry declares exactly one "
        "payload format from this closed registry in `content.format`."
    )
    lines.append(
        "An unregistered payload format is nonconformant. Each entry defines the payload "
        "grammar that a conformant producer validates before emission and identifies any "
        "additional producer or receiver responsibilities. For `native-recording`, the "
        "carrying source type selects the source category and meaning; this generic format "
        "defines no per-stream field schema."
    )
    lines.append(
        "The complete machine-readable contract is published in "
        "[`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json)."
    )
    for code, fmt in registry["formats"].items():
        spec = resolved_specification(registry, fmt)
        lines.append("")
        lines.append(f"### `{code}` — {fmt['title']}")
        lines.append("")
        lines.append(f"Media type: `{fmt['contentType']}`.")
        for key in (
            "encoding",
            "structure",
            "schema",
            "rowTerminator",
            "separator",
            "quoting",
            "numbers",
            "numberPattern",
            "integers",
            "integerPattern",
            "timestamps",
            "emptyFields",
            "columns",
            "resources",
            "emptyBatch",
            "validationScope",
            "provenance",
            "scope",
            "tar",
            "compression",
            "determinism",
            "file",
        ):
            value = spec.get(key)
            if isinstance(value, str):
                lines.append(f"`{value}`" if key.endswith("Pattern") else value)
        if "primitives" in spec:
            lines.append("")
            lines.append("**Primitive encodings**")
            lines.append("")
            lines.append("| Primitive | Encoding |")
            lines.append("|---|---|")
            for name, rule in spec["primitives"].items():
                lines.append(f"| `{name}` | {rule} |")
        for key, title in (
            ("record", "Record layout"),
            ("opticalSample", "Optical sample layout"),
            ("noiseTerms", "Noise terms layout"),
            ("accelerometerSample", "Accelerometer sample layout"),
        ):
            if key in spec:
                lines.extend(render_record_table(title, spec[key]))
        if "columns" in fmt:
            lines.extend(render_column_table(fmt))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    outputs = {
        FSH_OUTPUT: render_fsh(registry),
        PAGE_OUTPUT: render_page(registry),
        MIME_OUTPUT: render_mime_fsh(registry),
    }
    stale = []
    for path, rendered in outputs.items():
        if arguments.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                stale.append(path)
        else:
            path.write_text(rendered, encoding="utf-8")
    if stale:
        for path in stale:
            print(f"{path} is stale; run Scripts/render-format-registry.py")
        return 1
    print(f"format registry: {len(registry['formats'])} formats rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
