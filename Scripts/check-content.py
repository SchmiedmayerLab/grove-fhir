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
EXPECTED_GUIDE_SOURCES = ("mobile", "healthkit", "health-connect")
MOBILE_ADAPTER_SOURCES = ("healthkit", "health-connect")
GUIDES = tuple(ROOT / source for source in EXPECTED_GUIDE_SOURCES)
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

    mobile_configuration = configurations[ROOT / "mobile"]
    expected_dependency = (
        "org.grovealliance.fhir.mobile:\n"
        f"    version: {mobile_configuration.get('version', '<missing>')}"
    )
    for source in MOBILE_ADAPTER_SOURCES:
        adapter_configuration_text = (ROOT / source / "sushi-config.yaml").read_text(
            encoding="utf-8"
        )
        if expected_dependency not in adapter_configuration_text:
            failures.append(
                f"{source}/sushi-config.yaml does not pin the current Mobile guide version"
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
        if any(part in {"output", "temp", "input-cache", "node_modules", ".build"} for part in relative.parts):
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
