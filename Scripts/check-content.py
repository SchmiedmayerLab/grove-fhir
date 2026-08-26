#!/usr/bin/env python3
"""Run fast, deterministic repository checks before the expensive guide builds."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import py_compile
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_GUIDE_SOURCES = (
    "mobile",
    "sensor",
    "sensorkit",
    "healthkit",
    "health-connect",
    "providers",
    "questionnaire",
)
MOBILE_ADAPTER_SOURCES = (
    "sensor",
    "sensorkit",
    "healthkit",
    "health-connect",
    "providers",
)
GUIDES = tuple(ROOT / source for source in EXPECTED_GUIDE_SOURCES)
CATALOGS = ROOT / "catalog"
# Grove writes its own version in prose as "vX.Y.Z" or "Version X.Y.Z"; pinned third-party
# versions never take either form, so the pattern separates the two without an exclusion list.
OWN_VERSION_IN_PROSE = re.compile(r"\bv(\d+\.\d+\.\d+)\b|\b[Vv]ersion (\d+\.\d+\.\d+)\b")
# Fields that state when a set was first frozen, and so name the release that froze it rather
# than the current one. Every other prose mention must track the catalog's own version.
# The FHIR release is not Grove's version and never moves with it.
FHIR_VERSION = "4.0.1"

# Prose naming someone else's pinned version: the package or product is named right beside it.
THIRD_PARTY_PIN = re.compile(
    r"\b(hl7\.[a-z0-9.]+|Zstandard|SUSHI|IG Publisher|Node\.js|npm|Swift|Xcode|zod)\b",
    re.IGNORECASE,
)

HISTORICAL_VERSION_FIELDS = {
    ("sensorkit-adapter.json", "sourceEvidence.scope"),
    ("sensorkit-adapter.json", "inventoryScopes.catalog-baseline"),
}
REQUIRED_CONFIGURATION_KEYS = {"id", "canonical", "version", "fhirVersion", "license"}


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    paths = [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]
    return [path for path in paths if path.is_file()]


def stale_version_prose(name: str, node: object, own: str, path: tuple[str, ...] = ()) -> list[str]:
    if isinstance(node, dict):
        return [f for key, value in node.items() for f in stale_version_prose(name, value, own, path + (key,))]
    if isinstance(node, list):
        return [f for index, value in enumerate(node) for f in stale_version_prose(name, value, own, path + (str(index),))]
    if not isinstance(node, str):
        return []
    field = ".".join(path)
    if (name, field) in HISTORICAL_VERSION_FIELDS:
        return []
    return [
        f"catalog/{name} field {field} names version {found}, but the catalog is {own}"
        for match in OWN_VERSION_IN_PROSE.findall(node)
        for found in [match[0] or match[1]]
        if found != own
    ]


def main() -> int:
    failures: list[str] = []
    configurations: dict[Path, dict[str, str]] = {}
    for guide in GUIDES:
        configuration_path = guide / "sushi-config.yaml"
        configuration = scalar_configuration(configuration_path)
        configurations[guide] = configuration
        missing = REQUIRED_CONFIGURATION_KEYS - configuration.keys()
        if missing:
            failures.append(f"{configuration_path.relative_to(ROOT)} is missing: {', '.join(sorted(missing))}")
        if configuration.get("license") != "MIT":
            failures.append(f"{configuration_path.relative_to(ROOT)} must declare the MIT license")

    # Every guide that depends on another Grove guide must pin that guide's current version.
    # Checking only one of them let an adapter keep a stale Sensor pin through a release.
    published = {
        configuration["id"]: configuration.get("version", "<missing>")
        for configuration in configurations.values()
        if "id" in configuration
    }
    for guide in GUIDES:
        source = guide.name
        text = (guide / "sushi-config.yaml").read_text(encoding="utf-8")
        for package, pinned in re.findall(
            r"^  (org\.grovealliance\.fhir\.[a-z-]+):\n    version: (\S+)$", text, re.MULTILINE
        ):
            current = published.get(package)
            if current is None:
                failures.append(f"{source}/sushi-config.yaml depends on unknown guide {package}")
            elif pinned != current:
                failures.append(
                    f"{source}/sushi-config.yaml pins {package} at {pinned}, but it is {current}"
                )

    for catalog_path in sorted(CATALOGS.glob("*.json")):
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog_version = catalog.get("version")
        if isinstance(catalog_version, str):
            failures.extend(stale_version_prose(catalog_path.name, catalog, catalog_version))

    # FSH examples pin the release in content.format.version; a stale literal there would
    # ship an instance claiming a generation the guide no longer publishes.
    mobile_version = configurations[ROOT / "mobile"].get("version")

    # Prose in a guide's own sources names the release too, and several of those strings ship
    # inside published ValueSet and CodeSystem descriptions. The catalog guard cannot see them.
    for guide in GUIDES:
        for pattern in ("input/fsh/*.fsh", "input/pagecontent/*.md"):
            for path in sorted(guide.glob(pattern)):
                relative = str(path.relative_to(ROOT))
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    for match in OWN_VERSION_IN_PROSE.finditer(line):
                        found = match.group(1) or match.group(2)
                        if found in {mobile_version, FHIR_VERSION}:
                            continue
                        # A pinned third-party version is not Grove's and does not move with it.
                        if THIRD_PARTY_PIN.search(line):
                            continue
                        failures.append(
                            f"{relative}:{number} names version {found}, but the release "
                            f"is {mobile_version}"
                        )

    for guide in GUIDES:
        for path in sorted((guide / "input/fsh").glob("*.fsh")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                match = re.match(r'^\* content\.format\.version = "(\S+)"$', line.strip())
                if match and match.group(1) != mobile_version:
                    failures.append(
                        f"{path.relative_to(ROOT)}:{number} pins format version "
                        f"{match.group(1)}, but the release is {mobile_version}"
                    )

    publication_path = ROOT / "publication/config.json"
    publication = json.loads(publication_path.read_text(encoding="utf-8"))
    if publication.get("releaseMode") != "ci-build-only":
        failures.append(
            "publication/config.json must keep releaseMode at ci-build-only until an "
            "immutable release is explicitly approved"
        )
    canonical_base_url = publication.get("canonicalBaseUrl")
    canonical_base = urlparse(canonical_base_url) if isinstance(canonical_base_url, str) else None
    if (
        canonical_base is None
        or canonical_base.scheme != "https"
        or not canonical_base.netloc
        or canonical_base.username is not None
        or canonical_base.password is not None
        or "%" in canonical_base.path
        or "\\" in canonical_base.path
        or "//" in canonical_base.path
        or (
            canonical_base.path not in {"", "/"}
            and any(
                segment in {"", ".", ".."}
                for segment in canonical_base.path.strip("/").split("/")
            )
        )
        or canonical_base.params
        or canonical_base.query
        or canonical_base.fragment
    ):
        failures.append(
            "publication/config.json canonicalBaseUrl must be an HTTPS URL without "
            "credentials, an unsafe path, query, or fragment"
        )
        canonical_base_url = None
    published_sources: set[str] = set()
    aliases: set[str] = set()
    for guide in publication.get("guides", []):
        source = guide.get("source")
        if source not in EXPECTED_GUIDE_SOURCES:
            failures.append(f"publication/config.json has an unknown active guide: {source!r}")
            continue
        published_sources.add(source)
        configuration = configurations[ROOT / source]
        if canonical_base_url is not None:
            expected_canonical = (
                f"{canonical_base_url.rstrip('/')}/{str(guide.get('canonicalPath', '')).strip('/')}"
            )
            if configuration["canonical"].rstrip("/") != expected_canonical:
                failures.append(
                    f"canonical URL for {source} does not use the configured canonical origin: "
                    f"{configuration['canonical']!r} != {expected_canonical!r}"
                )
        for alias in guide.get("aliases", []):
            if alias in aliases:
                failures.append(f"publication alias is declared more than once: {alias!r}")
            aliases.add(alias)
    if published_sources != set(EXPECTED_GUIDE_SOURCES):
        failures.append("publication/config.json must publish exactly the active guides")
    publication_sources = [
        guide.get("source") for guide in publication.get("guides", [])
    ]
    if "mobile" in publication_sources:
        mobile_index = publication_sources.index("mobile")
        for source in MOBILE_ADAPTER_SOURCES:
            if source in publication_sources and publication_sources.index(source) < mobile_index:
                failures.append(
                    f"publication/config.json must build Mobile before its {source} adapter"
                )

    active_paths = {
        str(guide.get("canonicalPath", "")).strip("/")
        for guide in publication.get("guides", [])
    }
    active_paths.update(alias.strip("/") for alias in aliases if alias)
    for retired in publication.get("retiredPreviewPaths", []):
        retired_path = str(retired).strip("/")
        if not retired_path:
            failures.append("publication/config.json contains an empty retired path")
            continue
        if any(
            retired_path == active
            or retired_path.startswith(f"{active}/")
            or active.startswith(f"{retired_path}/")
            for active in active_paths
        ):
            failures.append(
                f"retired publication path overlaps an active path: {retired!r}"
            )

    for path in tracked_files():
        relative = path.relative_to(ROOT)
        if (
            any(
                part in {"output", "temp", "input-cache", "node_modules", ".build"}
                for part in relative.parts
            )
        ):
            failures.append(f"generated file is tracked: {relative}")
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                failures.append(f"invalid JSON in {relative}: {error}")
        if path.suffix == ".py":
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as error:
                failures.append(f"invalid Python in {relative}: {error.msg}")

    if failures:
        print("Repository content checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Checked {len(GUIDES)} guides and {len(tracked_files())} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
