#!/usr/bin/env python3
"""Verify every release projection against the authoritative manifest."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "catalog/release-manifest.json"
LEGACY_AUTHORITIES = (
    ROOT / "catalog/exchange-identity.json",
    ROOT / "catalog/health-connect-identity.json",
    ROOT / "Scripts/health_connect_identity.py",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def direct_dependencies(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("dependencies:") + 1
    except ValueError:
        return []
    result: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if line and not line.startswith((" ", "#")):
            break
        match = re.match(r"^  ([a-z0-9.-]+):(?:\s+(\S+))?\s*$", line)
        if match:
            package, inline_version = match.groups()
            version = inline_version
            if version is None:
                cursor = index + 1
                while cursor < len(lines) and (
                    not lines[cursor] or lines[cursor].startswith(("    ", "  #"))
                ):
                    nested = re.match(r"^    version:\s+(\S+)\s*$", lines[cursor])
                    if nested:
                        version = nested.group(1)
                        break
                    cursor += 1
            if version is None:
                raise ValueError(f"{path}: dependency {package} has no exact version")
            result.append(f"{package}#{version}")
        index += 1
    return result


def shell_constant(path: Path, name: str) -> str | None:
    match = re.search(
        rf'^readonly {re.escape(name)}="([^"]+)"$',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return match.group(1) if match else None


def repository_source_text() -> list[Path]:
    """Return tracked and non-ignored untracked release sources.

    Release checks commonly run before a contributor stages newly generated or
    authored files.  Limiting the scan to the index would therefore let a new
    legacy authority bypass the guard until after it was staged.
    """
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    ignored_prefixes = ("releases/", "publication/mobile-semantic-baseline.json")
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode()
        if relative == "Scripts/check-release.py" or relative.startswith(ignored_prefixes):
            continue
        path = ROOT / relative
        if path.is_file() and path.suffix.lower() in {".json", ".fsh", ".md", ".py", ".yaml", ".yml"}:
            paths.append(path)
    return paths


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    release = manifest["releaseVersion"]
    fhir = manifest["fhirVersion"]
    failures: list[str] = []

    toolchain = manifest["toolchain"]
    tools_script = ROOT / "Scripts/download-fhir-tools.sh"
    expected_tool_constants = {
        "PUBLISHER_VERSION": toolchain["igPublisher"]["version"],
        "PUBLISHER_SHA256": toolchain["igPublisher"]["sha256"],
        "VALIDATOR_VERSION": toolchain["fhirValidator"]["version"],
        "VALIDATOR_SHA256": toolchain["fhirValidator"]["sha256"],
        "TEMPLATE_ID": toolchain["template"]["packageId"],
        "TEMPLATE_VERSION": toolchain["template"]["version"],
        "TEMPLATE_SHA256": toolchain["template"]["sha256"],
    }
    for name, expected in expected_tool_constants.items():
        actual = shell_constant(tools_script, name)
        if actual != expected:
            failures.append(
                f"download-fhir-tools {name} is {actual!r}, expected {expected!r}"
            )

    guide_rows = manifest["guides"]
    sources = [row["source"] for row in guide_rows]
    if len(sources) != len(set(sources)):
        failures.append("release manifest guide sources must be unique")
    if sources != [
        "mobile", "questionnaire", "sensor", "sensorkit", "healthkit",
        "health-connect", "providers", "withings", "oura", "google-health",
    ]:
        failures.append("release manifest guide order or membership is not canonical")

    for row in guide_rows:
        configuration_path = ROOT / row["source"] / "sushi-config.yaml"
        configuration = scalar_configuration(configuration_path)
        expected = {
            "id": row["packageId"],
            "canonical": row["canonical"],
            "version": release,
            "fhirVersion": fhir,
        }
        for key, value in expected.items():
            if configuration.get(key) != value:
                failures.append(
                    f"{configuration_path.relative_to(ROOT)} {key} is "
                    f"{configuration.get(key)!r}, expected {value!r}"
                )
        actual_dependencies = direct_dependencies(configuration_path)
        if actual_dependencies != row["directDependencies"]:
            failures.append(
                f"{configuration_path.relative_to(ROOT)} direct dependencies are "
                f"{actual_dependencies!r}, expected {row['directDependencies']!r}"
            )

    graph = load_json(ROOT / "catalog/package-graph.json")
    if graph.get("version") != release or graph.get("fhirVersion") != fhir:
        failures.append("package graph release/FHIR version differs from the manifest")
    graph_rows = {row["source"]: row for row in graph.get("packages", [])}
    if list(graph_rows) != sources:
        failures.append("package graph guide order or membership differs from the manifest")
    for row in guide_rows:
        package = graph_rows.get(row["source"], {})
        for key in ("packageId", "canonical"):
            if package.get(key) != row[key]:
                failures.append(f"package graph {row['source']} {key} differs from manifest")
        if package.get("dependencies") != row["directDependencies"]:
            failures.append(
                f"package graph {row['source']} dependencies differ from manifest"
            )

    declared_catalogs = manifest["normativeCatalogs"]
    declared_paths = [row["path"] for row in declared_catalogs]
    if len(declared_paths) != len(set(declared_paths)):
        failures.append("normative catalog paths must be unique")
    for row in declared_catalogs:
        instance_path = ROOT / row["path"]
        schema_path = ROOT / row["schema"]
        if not instance_path.is_file() or not schema_path.is_file():
            failures.append(f"missing catalog/schema pair: {row['path']} / {row['schema']}")
            continue
        instance = load_json(instance_path)
        schema = load_json(schema_path)
        if instance.get("$schema") != schema.get("$id"):
            failures.append(f"{row['path']} does not declare {row['schema']}")
        if instance.get("schemaVersion") != row["schemaVersion"]:
            failures.append(f"{row['path']} schemaVersion differs from manifest")
        instance_release = instance.get("version", instance.get("releaseVersion"))
        if instance_release != release:
            failures.append(f"{row['path']} version {instance_release!r} differs from {release}")
        if instance.get("fhirVersion") != fhir:
            failures.append(f"{row['path']} FHIR version differs from manifest")

    package = load_json(ROOT / "package.json")
    if package.get("version") != release:
        failures.append("package.json version differs from release manifest")
    if package.get("devDependencies", {}).get("fsh-sushi") != toolchain["sushi"]["version"]:
        failures.append("package.json SUSHI version differs from release manifest")
    lock = load_json(ROOT / "package-lock.json")
    if lock.get("packages", {}).get("", {}).get("version") != release:
        failures.append("package-lock root version differs from release manifest")
    if lock.get("packages", {}).get("node_modules/fsh-sushi", {}).get("version") != toolchain["sushi"]["version"]:
        failures.append("package-lock SUSHI version differs from release manifest")

    producer = load_json(ROOT / "Conformance/example-producer/manifest.json")
    for dependency in producer.get("packages", []):
        expected = next(
            (row for row in guide_rows if row["packageId"] == dependency.get("packageId")),
            None,
        )
        if expected is None or dependency.get("version") != release:
            failures.append("example producer package pin differs from release manifest")
    for relative in (
        "Conformance/corpora/mobile-semantics/corpus.json",
        "Conformance/corpora/mobile-exchange/corpus.json",
    ):
        corpus = load_json(ROOT / relative)
        if corpus.get("version") != release:
            failures.append(f"{relative} version differs from release manifest")

    publication = load_json(ROOT / "publication/config.json")
    if publication.get("releaseMode") != manifest["publication"]["previewMode"]:
        failures.append("publication preview mode differs from release manifest")

    for path in LEGACY_AUTHORITIES:
        if path.exists():
            failures.append(f"legacy parallel identity authority still exists: {path.relative_to(ROOT)}")
    legacy_tokens = (
        "catalog/exchange-identity.json",
        "catalog/health-connect-identity.json",
        "health-connect-record-id",
        "health-connect-output-id",
        "sensorkit-record-id",
        "sensorkit-output-id",
        "provider-source-record-id",
        "provider-output-id",
        "provider-conversion-id",
        "provider-exchange-id",
    )
    for path in repository_source_text():
        text = path.read_text(encoding="utf-8", errors="strict")
        for token in legacy_tokens:
            if token in text:
                failures.append(f"{path.relative_to(ROOT)} retains legacy authority {token}")

    if failures:
        for failure in failures:
            print(f"release check: {failure}")
        return 1
    print(
        f"Release manifest verified: {release}, FHIR {fhir}, "
        f"{len(guide_rows)} guides, {len(declared_catalogs)} normative catalogs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
