#!/usr/bin/env python3
"""Render and verify the reviewed public artifact surface.

The generated allowlist is deliberately checked in. SUSHI is the source of
resource identities, while explicit FSH ``Usage`` declarations decide whether
an Instance is a package definition or example. A clean checkout can verify
the tracked allowlist against authored FSH and publication metadata. A build
runner must additionally verify each guide against its exact SUSHI output.
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
PUBLIC_DECLARATION = re.compile(
    r"^(Profile|Extension|Logical|Resource|CodeSystem|ValueSet|Instance):\s+(\S+)",
    re.MULTILINE,
)
INSTANCE_BLOCK = re.compile(
    r"^Instance:\s+(?P<name>\S+)(?P<body>.*?)(?=^(?:Profile|Extension|Logical|Resource|"
    r"CodeSystem|ValueSet|Instance|Invariant|RuleSet|Mapping|Alias):|\Z)",
    re.MULTILINE | re.DOTALL,
)
USAGE = re.compile(r"^Usage:\s+#(definition|example)\s*$", re.MULTILINE)
FHIR_ID = re.compile(r"^[A-Za-z0-9.-]{1,64}$")
PACKAGE_KEYS = {"source", "packageId", "canonical", "artifacts"}
ARTIFACT_KEYS = {"fshName", "fshType", "resourceType", "id", "classification"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def instance_usage(source: str, root: Path = ROOT) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / source / "input/fsh").rglob("*.fsh")):
        text = path.read_text(encoding="utf-8")
        for match in INSTANCE_BLOCK.finditer(text):
            name = match.group("name")
            usage = USAGE.search(match.group("body"))
            if usage is None:
                raise ValueError(
                    f"{path.relative_to(root)}: Instance {name} must declare Usage"
                )
            if name in result:
                raise ValueError(f"{source}: duplicate Instance declaration {name}")
            result[name] = usage.group(1)
    return result


def fsh_declarations(source: str, root: Path = ROOT) -> dict[tuple[str, str], str]:
    """Return every resource-producing declaration and its reviewed usage."""
    usages = instance_usage(source, root)
    declarations: dict[tuple[str, str], str] = {}
    for path in sorted((root / source / "input/fsh").rglob("*.fsh")):
        text = path.read_text(encoding="utf-8")
        for fsh_type, name in PUBLIC_DECLARATION.findall(text):
            key = (fsh_type, name)
            if key in declarations:
                raise ValueError(
                    f"{source}: duplicate FSH declaration {fsh_type} {name}"
                )
            declarations[key] = usages[name] if fsh_type == "Instance" else "definition"
    return declarations


def package_projection(source: str, root: Path = ROOT) -> dict[str, Any]:
    configuration = scalar_configuration(root / source / "sushi-config.yaml")
    index_path = root / source / "fsh-generated/data/fsh-index.json"
    resources = root / source / "fsh-generated/resources"
    if not index_path.is_file():
        raise ValueError(f"{index_path.relative_to(root)} is absent; run SUSHI first")

    usage_by_instance = instance_usage(source, root)
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
            raise ValueError(f"{resource_path.relative_to(root)} has no resourceType/id")
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


def validate_authored_allowlist(
    document: Any, publication: Any, root: Path = ROOT
) -> None:
    """Validate everything knowable from tracked authored files alone."""
    if not isinstance(document, dict) or set(document) != {"schemaVersion", "packages"}:
        raise ValueError("artifact allowlist must contain only schemaVersion and packages")
    if document.get("schemaVersion") != 1 or not isinstance(
        document.get("packages"), list
    ):
        raise ValueError("artifact allowlist must use schemaVersion 1 and list packages")
    if not isinstance(publication, dict) or not isinstance(publication.get("guides"), list):
        raise ValueError("publication config must list guides")

    guides = publication["guides"]
    if not all(isinstance(guide, dict) for guide in guides):
        raise ValueError("every publication guide must be an object")
    expected_sources = [guide.get("source") for guide in guides]
    if not all(isinstance(source, str) and source for source in expected_sources):
        raise ValueError("every publication guide must declare a source")
    if len(set(expected_sources)) != len(expected_sources):
        raise ValueError("publication config contains duplicate guide sources")

    packages = document["packages"]
    actual_sources = [
        package.get("source") if isinstance(package, dict) else None
        for package in packages
    ]
    if actual_sources != expected_sources:
        raise ValueError(
            "artifact allowlist package order/sources differ from active publication"
        )

    canonical_base = publication.get("canonicalBaseUrl")
    if not isinstance(canonical_base, str) or not canonical_base:
        raise ValueError("publication config must declare canonicalBaseUrl")

    for guide, package in zip(guides, packages, strict=True):
        source = guide["source"]
        if set(package) != PACKAGE_KEYS:
            raise ValueError(f"{source}: package must contain exactly {sorted(PACKAGE_KEYS)}")
        configuration = scalar_configuration(root / source / "sushi-config.yaml")
        if package.get("packageId") != configuration.get("id"):
            raise ValueError(f"{source}: packageId differs from sushi-config.yaml")
        if package.get("canonical") != configuration.get("canonical"):
            raise ValueError(f"{source}: canonical differs from sushi-config.yaml")
        expected_canonical = (
            f"{canonical_base.rstrip('/')}/{guide.get('canonicalPath', '')}"
        )
        if package.get("canonical") != expected_canonical:
            raise ValueError(f"{source}: canonical differs from publication config")

        artifacts = package.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError(f"{source}: artifacts must be a non-empty list")
        expected_order = sorted(
            artifacts,
            key=lambda row: (
                row.get("fshType", "") if isinstance(row, dict) else "",
                row.get("fshName", "") if isinstance(row, dict) else "",
            ),
        )
        if artifacts != expected_order:
            raise ValueError(f"{source}: artifacts are not in deterministic FSH order")

        allowlisted: dict[tuple[str, str], str] = {}
        resource_identities: set[tuple[str, str]] = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict) or set(artifact) != ARTIFACT_KEYS:
                raise ValueError(
                    f"{source}: every artifact must contain exactly "
                    f"{sorted(ARTIFACT_KEYS)}"
                )
            string_keys = ("fshName", "fshType", "resourceType", "id", "classification")
            if not all(
                isinstance(artifact.get(key), str) and artifact[key]
                for key in string_keys
            ):
                raise ValueError(f"{source}: artifact fields must be non-empty strings")
            if artifact["classification"] not in {"definition", "example"}:
                raise ValueError(f"{source}: unsupported artifact classification")
            if FHIR_ID.fullmatch(artifact["id"]) is None:
                raise ValueError(f"{source}: invalid FHIR id {artifact['id']!r}")
            declaration = (artifact["fshType"], artifact["fshName"])
            if declaration in allowlisted:
                raise ValueError(f"{source}: duplicate allowlisted declaration {declaration}")
            identity = (artifact["resourceType"], artifact["id"])
            if identity in resource_identities:
                raise ValueError(f"{source}: duplicate resource identity {identity}")
            allowlisted[declaration] = artifact["classification"]
            resource_identities.add(identity)

        if allowlisted != fsh_declarations(source, root):
            raise ValueError(
                f"{source}: artifact declarations/classifications differ from authored FSH"
            )


def check_generated(
    document: dict[str, Any], sources: list[str], root: Path = ROOT
) -> None:
    """Require selected guides to match their exact generated SUSHI projection."""
    if len(set(sources)) != len(sources):
        raise ValueError("generated check contains duplicate guide sources")
    packages = {package["source"]: package for package in document["packages"]}
    for source in sources:
        if source not in packages:
            raise ValueError(f"{source}: guide is not in the active artifact allowlist")
        if package_projection(source, root) != packages[source]:
            raise ValueError(
                f"{source}: generated SUSHI projection differs from the artifact allowlist; "
                "build every guide and run npm run artifacts:refresh"
            )


def render(root: Path = ROOT) -> str:
    publication = load_json(root / "publication/config.json")
    document = {
        "schemaVersion": 1,
        "packages": [
            package_projection(guide["source"], root) for guide in publication["guides"]
        ],
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="check the allowlist against tracked FSH and publication metadata",
    )
    mode.add_argument(
        "--check-generated",
        nargs="+",
        metavar="SOURCE",
        help="require selected guides to match their exact generated SUSHI output",
    )
    args = parser.parse_args(argv)
    publication_path = root / "publication/config.json"
    output = root / "publication/artifact-allowlist.json"

    try:
        if args.check or args.check_generated:
            if not output.is_file():
                raise ValueError("publication/artifact-allowlist.json is absent")
            document = load_json(output)
            publication = load_json(publication_path)
            validate_authored_allowlist(document, publication, root)
            if args.check_generated:
                check_generated(document, args.check_generated, root)
                print(
                    "Artifact allowlist matches exact generated SUSHI output for: "
                    + ", ".join(args.check_generated)
                )
            else:
                print(
                    "Artifact allowlist matches authored FSH declarations and "
                    "publication metadata."
                )
            return 0

        publication = load_json(publication_path)
        rendered = render(root)
        validate_authored_allowlist(json.loads(rendered), publication, root)
        output.write_text(rendered, encoding="utf-8")
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"artifact allowlist operation failed: {error}")
        if args.check:
            print("run npm run artifacts:refresh after building every guide")
            return 1
        return 1

    print(f"Rendered {output.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
