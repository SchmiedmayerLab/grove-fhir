#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Render the payload format registry into the guides that own its formats.

catalog/format-registry.json is the authoritative closed registry of payload
formats a Grove payload DocumentReference may declare. Mobile publishes the one
format CodeSystem and ValueSet and the shared index; each format names the guide
that owns its definition, and that guide publishes the value set its document
profiles bind and the format's full definition. This renderer projects the
registry into every one of those FSH files and pages so the guides and the
machine contract can never drift apart.

Usage:
  Scripts/render-format-registry.py           # write every output
  Scripts/render-format-registry.py --check   # verify every output is current
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "catalog/format-registry.json"
MOBILE_FSH_OUTPUT = ROOT / "mobile/input/fsh/generated-payload-formats.fsh"
MOBILE_PAGE_OUTPUT = ROOT / "mobile/input/pagecontent/formats.md"
SENSOR_FSH_OUTPUT = ROOT / "sensor/input/fsh/generated-recording-formats.fsh"
SENSOR_PAGE_OUTPUT = ROOT / "sensor/input/pagecontent/formats.md"
MIME_OUTPUT = ROOT / "sensor/input/fsh/generated-recording-mime-types.fsh"
CLINICAL_FSH_OUTPUT = ROOT / "clinical-records/input/fsh/generated-clinical-record-formats.fsh"
CLINICAL_PAGE_OUTPUT = ROOT / "clinical-records/input/pagecontent/formats.md"

# The guides that own a format. Mobile owns the shared index and the formats no
# narrower guide owns; the others publish the value set their document profiles bind.
OWNERS = ("mobile", "sensor", "clinical-records")

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

PATTERN_RULES = ("source-declared", "declared-fhir-release")


def format_content_types(fmt: dict) -> list[str]:
    """Return every exact Attachment.contentType one format enumerates.

    A pattern-ruled format enumerates none: it admits whatever media type its source or its
    producer declares that matches its pattern, so it contributes nothing to a closed MIME
    value set.
    """
    if fmt.get("contentTypeRule") in PATTERN_RULES:
        return []
    if "contentTypes" in fmt:
        return fmt["contentTypes"]
    return [fmt["contentType"]]


def owned_formats(registry: dict, owner: str) -> dict[str, dict]:
    return {code: fmt for code, fmt in registry["formats"].items() if fmt["owner"] == owner}


def fsh_code_literal(code: str) -> str:
    """Quote FSH codes whose MIME parameters contain whitespace."""
    return f'#"{code}"' if any(character.isspace() for character in code) else f"#{code}"


def validate_owners(registry: dict) -> None:
    declared = set(registry["owners"])
    if declared != set(OWNERS):
        raise SystemExit(f"registry owners {sorted(declared)} are not {sorted(OWNERS)}")
    for code, fmt in registry["formats"].items():
        if fmt.get("owner") not in declared:
            raise SystemExit(f"{code}: owner {fmt.get('owner')!r} is not a registry owner")
    previous = registry["previousCodings"]["codes"]
    if sorted(previous.values()) != sorted(registry["formats"]):
        raise SystemExit("previousCodings.codes must map onto every current format exactly once")


def render_mime_fsh(registry: dict) -> str:
    media_types = registry["mediaTypes"]
    used = {
        content_type
        for fmt in registry["formats"].values()
        for content_type in format_content_types(fmt)
    }
    undeclared = used - set(media_types)
    if undeclared:
        raise SystemExit(f"media types used by a format but not declared: {sorted(undeclared)}")
    unused = set(media_types) - used
    if unused:
        raise SystemExit(f"media types declared but used by no format: {sorted(unused)}")
    sensor_used = {
        content_type
        for fmt in owned_formats(registry, "sensor").values()
        for content_type in format_content_types(fmt)
    }
    sensor_media_types = {
        code: display for code, display in media_types.items() if code in sensor_used
    }

    lines = [FSH_HEADER]
    lines.append("ValueSet: GroveRecordingMimeTypeVS")
    lines.append("Id: grove-recording-mime-type")
    lines.append('Title: "Grove Recording MIME Types"')
    lines.append(
        'Description: "The exact MIME content-type values admitted for a Grove sensor recording '
        "payload: the media types of the formats the Sensor guide owns. Base media types use "
        "their IANA identifiers; parameters follow the standard that defines the payload. Grove "
        'does not publish or version the external code system."'
    )
    lines.append("* ^experimental = false")
    for code, display in sensor_media_types.items():
        lines.append(f'* urn:ietf:bcp:13{fsh_code_literal(code)} "{display}"')
    lines.append(f'* ^expansion.timestamp = "{MIME_EXPANSION_TIMESTAMP}"')
    lines.append('* ^expansion.parameter[+].name = "used-codesystem"')
    lines.append('* ^expansion.parameter[=].valueUri = "urn:ietf:bcp:13"')
    lines.append('* ^expansion.parameter[+].name = "includeDesignations"')
    lines.append("* ^expansion.parameter[=].valueBoolean = false")
    for code, display in sensor_media_types.items():
        lines.append('* ^expansion.contains[+].system = "urn:ietf:bcp:13"')
        lines.append(f"* ^expansion.contains[=].code = {fsh_code_literal(code)}")
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


def render_mobile_fsh(registry: dict) -> str:
    lines = [FSH_HEADER]
    lines.append("CodeSystem: GrovePayloadFormatCS")
    lines.append("Id: grove-payload-format")
    lines.append('Title: "Grove Payload Format"')
    lines.append(
        'Description: "The closed registry of payload formats a Grove payload '
        "DocumentReference may declare in content.format: a Sensor recording document, a "
        "Clinical Records document or attachment, or an adapter document derived from one of "
        "them. Each code identifies a wire format and structural envelope, and the guide that "
        "owns it states its full definition. Native Recording JSON defines only a JSON "
        'object-or-array container; the carrying source type supplies its category and meaning."'
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
    lines.append("ValueSet: GrovePayloadFormatVS")
    lines.append("Id: grove-payload-format")
    lines.append('Title: "Grove Payload Format"')
    lines.append(
        'Description: "Every registered Grove payload format. A document profile binds the '
        "narrower value set of the guide that owns its formats, or fixes the one format it "
        'carries."'
    )
    lines.append("* ^experimental = false")
    lines.append("* include codes from system GrovePayloadFormatCS")
    return "\n".join(lines) + "\n"


def render_owner_value_set(
    registry: dict, owner: str, name: str, identifier: str, title: str, description: str
) -> str:
    formats = owned_formats(registry, owner)
    if not formats:
        raise SystemExit(f"{owner} owns no format to bind")
    if registry["owners"][owner]["valueSet"] != (
        f"{registry['owners'][owner]['canonical']}/ValueSet/{identifier}"
    ):
        raise SystemExit(f"{owner}: registry valueSet does not name {identifier}")
    lines = [FSH_HEADER]
    lines.append(f"ValueSet: {name}")
    lines.append(f"Id: {identifier}")
    lines.append(f'Title: "{title}"')
    lines.append(f'Description: "{description}"')
    lines.append("* ^experimental = false")
    for code, fmt in formats.items():
        lines.append(f'* {registry["codeSystem"]}#{code} "{fmt["title"]}"')
    return "\n".join(lines) + "\n"


def render_sensor_fsh(registry: dict) -> str:
    return render_owner_value_set(
        registry,
        "sensor",
        "GroveSensorRecordingFormatVS",
        "grove-sensor-recording-format",
        "Grove Sensor Recording Format",
        "Every payload format the Sensor guide owns, drawn from the Mobile payload format "
        "CodeSystem; a Sensor recording document content entry declares one of them.",
    )


def render_clinical_fsh(registry: dict) -> str:
    return render_owner_value_set(
        registry,
        "clinical-records",
        "GroveClinicalRecordFormatVS",
        "grove-clinical-record-format",
        "Grove Clinical Record Format",
        "Every payload format the Clinical Records guide owns, drawn from the Mobile payload "
        "format CodeSystem; a Clinical Record Document content entry declares one of them. A "
        "Clinical Record Attachment fixes the Mobile source-file format instead.",
    )


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


def media_type_summary(fmt: dict) -> str:
    rule = fmt.get("contentTypeRule")
    if rule == "source-declared":
        return (
            "the one the source declares, matching "
            f"`{fmt['contentTypePattern']}`; `{fmt['defaultContentType']}` when it declares none"
        )
    if rule == "declared-fhir-release":
        return (
            "`application/fhir+json` with the FHIR release the producer declares, matching "
            f"`{fmt['contentTypePattern']}`"
        )
    return ", ".join(f"`{content_type}`" for content_type in format_content_types(fmt))


def render_format_sections(registry: dict, formats: dict[str, dict]) -> list[str]:
    lines: list[str] = []
    for code, fmt in formats.items():
        spec = resolved_specification(registry, fmt)
        lines.append("")
        lines.append(f"### `{code}` — {fmt['title']}")
        lines.append("")
        content_types = format_content_types(fmt)
        plural = fmt.get("contentTypeRule") is None and len(content_types) > 1
        lines.append(f"{'Media types' if plural else 'Media type'}: {media_type_summary(fmt)}.")
        for key in (
            "encoding",
            "structure",
            "fhirVersion",
            "mediaType",
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
            for name, rule_text in spec["primitives"].items():
                lines.append(f"| `{name}` | {rule_text} |")
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
    return lines


REGISTRY_LINK = (
    "The complete machine-readable contract is published in "
    "[`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json)."
)


def render_mobile_page(registry: dict) -> str:
    owners = registry["owners"]
    previous = registry["previousCodings"]
    lines = [PAGE_HEADER]
    lines.append(
        "Every Grove payload DocumentReference content entry declares exactly one payload "
        "format from this closed registry in `content.format`, with system "
        f"`{registry['codeSystem']}` and no `Coding.version`. An unregistered payload format "
        "is nonconformant."
    )
    lines.append(
        "Mobile publishes the one format CodeSystem and its ValueSet. Each format belongs to "
        "the guide that owns its definition; a document profile admits only the formats its "
        "guide owns, or fixes the one format it carries."
    )
    lines.append(REGISTRY_LINK)
    lines.append("")
    lines.append("### Carrying the bytes")
    lines.append("")
    lines.append(
        "These rules apply to every payload content entry, whatever its format and whichever "
        "guide's profile carries it."
    )
    lines.append("")
    lines.append(
        "- **Inline or by URL.** `Attachment` carries the exact payload bytes in exactly one of "
        "`data` (base64) or `url`. A URL names an immutable, version-specific location; it may "
        "be relative to the transport unit that carries the Bundle, such as an entry of the same "
        "upload archive. A receiver resolves a URL through its deployment, never through Grove."
    )
    lines.append(
        "- **Media type.** `Attachment.contentType` is always present and is the media type the "
        "format defines: one of its enumerated values, or a value matching its pattern."
    )
    lines.append(
        "- **Size and hash.** `Attachment.size` is the exact byte count and `Attachment.hash` the "
        "base64 SHA-1 digest of the exact payload bytes, inline or by URL alike. A validator "
        "checks both against embedded bytes."
    )
    lines.append(
        "- **No release coupling.** `content.format.version` is absent: the stable CodeSystem "
        "and code identify the wire contract, not an IG release."
    )
    lines.append("")
    lines.append("### Registered formats")
    lines.append("")
    lines.append("| Code | Title | Owner | Media type |")
    lines.append("|---|---|---|---|")
    for code, fmt in registry["formats"].items():
        owner = owners[fmt["owner"]]
        # A guide's own canonical page does not resolve inside its own build; Mobile's formats
        # are defined further down this page.
        owner_cell = (
            f"{owner['title']} (below)"
            if fmt["owner"] == "mobile"
            else f"[{owner['title']}]({owner['page']})"
        )
        lines.append(
            f"| `{code}` | {fmt['title']} | {owner_cell} | {media_type_summary(fmt)} |"
        )
    lines.append("")
    lines.append(
        "The formats Mobile owns are defined below; every other format is defined on its "
        "owner's formats page."
    )
    lines.extend(render_format_sections(registry, owned_formats(registry, "mobile")))
    lines.append("")
    lines.append("### Reading Bundles that use the retired format codes")
    lines.append("")
    lines.append(previous["rule"])
    lines.append("")
    lines.append(
        f"Retired system: `{previous['system']}`. Current system: `{registry['codeSystem']}`."
    )
    lines.append("")
    lines.append("| Retired code | Current code |")
    lines.append("|---|---|")
    for old, new in previous["codes"].items():
        lines.append(f"| `{old}` | `{new}` |")
    return "\n".join(lines) + "\n"


def render_owner_page(registry: dict, owner: str, profiles_sentence: str) -> str:
    lines = [PAGE_HEADER]
    lines.append(profiles_sentence)
    lines.append(
        "The formats are codes of the Mobile "
        f"[payload format registry]({registry['owners']['mobile']['page']}), which also states "
        "the rules for carrying the bytes inline or by URL, their media type, size, and hash."
    )
    lines.append(REGISTRY_LINK)
    lines.extend(render_format_sections(registry, owned_formats(registry, owner)))
    return "\n".join(lines) + "\n"


def render_sensor_page(registry: dict) -> str:
    return render_owner_page(
        registry,
        "sensor",
        "Every Grove Sensor recording DocumentReference content entry declares exactly one "
        "payload format this guide owns in `content.format`. An unregistered payload format is "
        "nonconformant. Each entry defines the payload grammar that a conformant producer "
        "validates before emission and identifies any additional producer or receiver "
        "responsibilities. For `native-recording-json`, the carrying source type selects the "
        "source category and meaning; this generic format defines no per-stream field schema.",
    )


def render_clinical_page(registry: dict) -> str:
    return render_owner_page(
        registry,
        "clinical-records",
        "Every Grove Clinical Record Document content entry declares exactly one payload format "
        "this guide owns in `content.format`; a Clinical Record Attachment carries the Mobile "
        "`source-file` format instead. Grove byte-preserves every clinical payload and never "
        "asserts conformance over another issuer's record.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    validate_owners(registry)
    outputs = {
        MOBILE_FSH_OUTPUT: render_mobile_fsh(registry),
        MOBILE_PAGE_OUTPUT: render_mobile_page(registry),
        SENSOR_FSH_OUTPUT: render_sensor_fsh(registry),
        SENSOR_PAGE_OUTPUT: render_sensor_page(registry),
        MIME_OUTPUT: render_mime_fsh(registry),
        CLINICAL_FSH_OUTPUT: render_clinical_fsh(registry),
        CLINICAL_PAGE_OUTPUT: render_clinical_page(registry),
    }
    stale = []
    for path, rendered in outputs.items():
        if arguments.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                stale.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
    if stale:
        for path in stale:
            print(f"{path} is stale; run Scripts/render-format-registry.py")
        return 1
    print(f"format registry: {len(registry['formats'])} formats rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
