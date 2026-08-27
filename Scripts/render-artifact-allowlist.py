#!/usr/bin/env python3
"""Render the reviewed public artifact surface from exact SUSHI output.

The generated allowlist is deliberately checked in.  SUSHI is the source of
resource identities, while explicit FSH ``Usage`` declarations decide whether
an Instance is a package definition or example.  Publication tests then prove
that the packaged surface is exactly this projection.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PUBLICATION = ROOT / "publication/config.json"
OUTPUT = ROOT / "publication/artifact-allowlist.json"
INSTANCE_BLOCK = re.compile(
    r"^Instance:\s+(?P<name>\S+)(?P<body>.*?)(?=^(?:Profile|Extension|Logical|Resource|"
    r"CodeSystem|ValueSet|Instance|Invariant|RuleSet|Mapping|Alias):|\Z)",
    re.MULTILINE | re.DOTALL,
)
USAGE = re.compile(r"^Usage:\s+#(definition|example)\s*$", re.MULTILINE)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def instance_usage(source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((ROOT / source / "input/fsh").rglob("*.fsh")):
        text = path.read_text(encoding="utf-8")
        for match in INSTANCE_BLOCK.finditer(text):
            name = match.group("name")
            usage = USAGE.search(match.group("body"))
            if usage is None:
                raise ValueError(
                    f"{path.relative_to(ROOT)}: Instance {name} must declare Usage"
                )
            if name in result:
                raise ValueError(f"{source}: duplicate Instance declaration {name}")
            result[name] = usage.group(1)
    return result


def package_projection(source: str) -> dict[str, Any]:
    configuration = scalar_configuration(ROOT / source / "sushi-config.yaml")
    index_path = ROOT / source / "fsh-generated/data/fsh-index.json"
    resources = ROOT / source / "fsh-generated/resources"
    if not index_path.is_file():
        raise ValueError(f"{index_path.relative_to(ROOT)} is absent; run SUSHI first")

    usage_by_instance = instance_usage(source)
    artifacts: list[dict[str, str]] = []
    seen_declarations: set[tuple[str, str]] = set()
    seen_resources: set[tuple[str, str]] = set()
    for entry in load_json(index_path):
        declaration = (entry["fshType"], entry["fshName"])
        if declaration in seen_declarations:
            raise ValueError(f"{source}: duplicate SUSHI declaration {declaration}")
        seen_declarations.add(declaration)

        resource_path = resources / entry["outputFile"]
        resource = load_json(resource_path)
        identity = (resource.get("resourceType"), resource.get("id"))
        if not all(isinstance(value, str) and value for value in identity):
            raise ValueError(f"{resource_path.relative_to(ROOT)} has no resourceType/id")
        if identity in seen_resources:
            raise ValueError(f"{source}: duplicate generated resource identity {identity}")
        seen_resources.add(identity)

        classification = "definition"
        if entry["fshType"] == "Instance":
            try:
                classification = usage_by_instance[entry["fshName"]]
            except KeyError as error:
                raise ValueError(
                    f"{source}: generated Instance {entry['fshName']} has no FSH Usage"
                ) from error
        artifacts.append(
            {
                "fshName": entry["fshName"],
                "fshType": entry["fshType"],
                "resourceType": identity[0],
                "id": identity[1],
                "classification": classification,
            }
        )

    artifacts.sort(key=lambda row: (row["fshType"], row["fshName"]))
    return {
        "source": source,
        "packageId": configuration["id"],
        "canonical": configuration["canonical"],
        "artifacts": artifacts,
    }


def render() -> str:
    publication = load_json(PUBLICATION)
    document = {
        "schemaVersion": 1,
        "packages": [
            package_projection(guide["source"]) for guide in publication["guides"]
        ],
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="fail if the checked-in projection is stale"
    )
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("artifact allowlist is stale; run npm run artifacts:refresh")
            return 1
        print("Artifact allowlist matches exact SUSHI output.")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Rendered {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
