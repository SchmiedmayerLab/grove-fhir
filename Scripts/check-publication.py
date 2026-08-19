#!/usr/bin/env python3
"""Validate the assembled Grove FHIR publication surface."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse


LOCAL_LOCATION = re.compile(r"file://|/(?:Users|home/runner|private/tmp)/")


def safe_path(value: str) -> Path:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe publication path: {value!r}")
    return Path(*path.parts) if value else Path()


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def package_metadata(path: Path) -> dict[str, Any]:
    with tarfile.open(path, "r:gz") as package:
        entry = package.extractfile("package/package.json")
        if entry is None:
            raise ValueError(f"{path} has no package/package.json")
        return json.load(entry)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def appended_suffix(path: Path, suffix: str) -> Path:
    return path.parent / f"{path.name}{suffix}"


def owned_resources(preview: Path, canonical: str) -> list[tuple[str, Path]]:
    resources: list[tuple[str, Path]] = []
    for path in sorted(preview.glob("*.json")):
        try:
            resource = json.loads(path.read_text(encoding="utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(resource, dict):
            continue
        url = resource.get("url")
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        if (
            isinstance(url, str)
            and isinstance(resource_type, str)
            and isinstance(resource_id, str)
            and url.startswith(f"{canonical}/")
        ):
            resources.append((url.removeprefix(f"{canonical}/"), path))
    return resources


def check_site(
    site: Path,
    repository_root: Path,
    configuration: dict[str, Any],
    base_url: str,
) -> list[str]:
    failures: list[str] = []
    for guide in configuration["guides"]:
        source = guide["source"]
        canonical_root = site / safe_path(guide["canonicalPath"])
        preview = canonical_root / "ci-build"
        expected_files = (
            canonical_root / "index.html",
            canonical_root / "history.html",
            canonical_root / "package-list.json",
            canonical_root / "package.tgz",
            canonical_root / "package.tgz.sha256",
            canonical_root / "publication-manifest.json",
            canonical_root / "canonical-routes.json",
            preview / "index.html",
        )
        for path in expected_files:
            if not path.is_file():
                failures.append(f"missing publication file: {path.relative_to(site)}")
        if failures and not (canonical_root / "package.tgz").is_file():
            continue

        source_configuration = scalar_configuration(repository_root / source / "sushi-config.yaml")
        metadata = package_metadata(canonical_root / "package.tgz")
        expected = {
            "name": source_configuration.get("id"),
            "canonical": source_configuration.get("canonical"),
        }
        for key, value in expected.items():
            if metadata.get(key) != value:
                failures.append(
                    f"{source} package {key} is {metadata.get(key)!r}; expected {value!r}"
                )
        fhir_versions = metadata.get("fhirVersions")
        if fhir_versions != [source_configuration.get("fhirVersion")]:
            failures.append(f"{source} package FHIR version does not match sushi-config.yaml")

        history = json.loads((canonical_root / "package-list.json").read_text(encoding="utf-8"))
        expected_preview = f"{base_url}/{guide['canonicalPath']}/ci-build"
        if history.get("package-id") != metadata.get("name"):
            failures.append(f"{source} package-list package id does not match package.tgz")
        if history.get("canonical") != metadata.get("canonical"):
            failures.append(f"{source} package-list canonical does not match package.tgz")
        entries = history.get("list")
        release_entries: list[dict[str, Any]] = []
        if not isinstance(entries, list):
            failures.append(f"{source} package-list has no version list")
        else:
            ci_entries = [entry for entry in entries if entry.get("version") == "current"]
            release_entries = [entry for entry in entries if entry.get("version") != "current"]
            if len(ci_entries) != 1 or ci_entries[0].get("status") != "ci-build":
                failures.append(f"{source} package-list must contain exactly one CI entry")
            elif ci_entries[0].get("path") != expected_preview:
                failures.append(f"{source} CI path does not match the hosted preview")
            versions = [entry.get("version") for entry in release_entries]
            if len(versions) != len(set(versions)):
                failures.append(f"{source} package-list contains duplicate release versions")

        package_url = metadata.get("url")
        allowed_package_urls = {metadata.get("canonical")}
        allowed_package_urls.update(
            f"{metadata.get('canonical')}/{entry.get('version')}" for entry in release_entries
        )
        if package_url not in allowed_package_urls:
            failures.append(f"{source} root package URL is not a current canonical publication")
        if not release_entries and metadata.get("version") != source_configuration.get("version"):
            failures.append(f"{source} preview package version does not match sushi-config.yaml")

        checksum = (canonical_root / "package.tgz.sha256").read_text(encoding="utf-8").split()
        if len(checksum) != 2 or checksum[0] != digest(canonical_root / "package.tgz"):
            failures.append(f"{source} package checksum is invalid")

        manifest = json.loads(
            (canonical_root / "publication-manifest.json").read_text(encoding="utf-8")
        )
        if manifest.get("packageSha256") != digest(canonical_root / "package.tgz"):
            failures.append(f"{source} publication manifest checksum is invalid")
        if manifest.get("canonical") != metadata.get("canonical"):
            failures.append(f"{source} publication manifest canonical is invalid")

        resources = owned_resources(preview, str(metadata["canonical"]))
        route_manifest = json.loads(
            (canonical_root / "canonical-routes.json").read_text(encoding="utf-8")
        )
        route_rows = route_manifest.get("routes") if isinstance(route_manifest, dict) else None
        if not isinstance(route_rows, list):
            failures.append(f"{source} canonical route manifest is invalid")
            route_rows = []
        if not release_entries and len(route_rows) != len(resources):
            failures.append(
                f"{source} canonical route manifest has {len(route_rows)} entries for "
                f"{len(resources)} owned resources"
            )
        for relative, source_json in resources if not release_entries else []:
            route = canonical_root / safe_path(relative)
            for suffix_path in (
                route / "index.html",
                appended_suffix(route, ".html"),
                appended_suffix(route, ".json"),
            ):
                if not suffix_path.is_file():
                    failures.append(
                        f"missing canonical route for {relative}: {suffix_path.relative_to(site)}"
                    )
            for extension in (".xml", ".ttl"):
                source_format = source_json.with_suffix(extension)
                if source_format.is_file() and not appended_suffix(route, extension).is_file():
                    failures.append(f"missing {extension} canonical route for {relative}")

        representative = canonical_root / safe_path(guide["representativeResource"])
        if not (representative / "index.html").is_file() or not appended_suffix(
            representative, ".json"
        ).is_file():
            failures.append(f"{source} representative canonical route is missing")

        preview_index = (preview / "index.html").read_text(encoding="utf-8")
        if "Local Development build" in preview_index:
            failures.append(f"{source} still presents the hosted preview as a local build")
        expected_history = f"{base_url}/{guide['canonicalPath']}/history.html"
        if expected_history not in preview_index:
            failures.append(f"{source} release header does not link to hosted history")

        for alias in guide.get("aliases", []):
            alias_root = site / safe_path(alias)
            if not (alias_root / "index.html").is_file():
                failures.append(f"missing preview alias: {alias or '/'}")
            if not (alias_root / "package-list.json").is_file():
                failures.append(f"missing package-list at preview alias: {alias or '/'}")

    for retired in configuration.get("retiredPreviewPaths", []):
        if (site / safe_path(retired)).exists():
            failures.append(f"retired path is present: {retired}")

    for guide in configuration["guides"]:
        preview = site / safe_path(guide["canonicalPath"]) / "ci-build"
        for path in preview.rglob("*"):
            if not path.is_file() or path.suffix not in {".html", ".json", ".xml", ".ttl"}:
                continue
            try:
                contents = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if LOCAL_LOCATION.search(contents):
                failures.append(f"local filesystem path leaked into {path.relative_to(site)}")
                break
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--base-url")
    arguments = parser.parse_args()
    configuration = json.loads(arguments.config.read_text(encoding="utf-8"))
    base_url = (arguments.base_url or configuration["previewBaseUrl"]).rstrip("/")
    failures = check_site(
        arguments.site.resolve(),
        arguments.repository_root.resolve(),
        configuration,
        base_url,
    )
    if failures:
        print("Publication checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Validated {len(configuration['guides'])} published guide previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
