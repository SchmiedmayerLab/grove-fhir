#!/usr/bin/env python3
"""Smoke-test the deployed Grove FHIR publication over HTTPS."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


USER_AGENT = "grove-fhir-publication-check/1"


def request(url: str, *, attempts: int = 6, pause: float = 5.0) -> tuple[int, bytes]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            call = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(call, timeout=30) as response:
                return response.status, response.read()
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(pause)
    assert last_error is not None
    raise last_error


def expect_status(url: str, expected: int) -> bytes:
    try:
        status, body = request(url)
    except urllib.error.HTTPError as error:
        status, body = error.code, error.read()
    if status != expected:
        raise RuntimeError(f"{url} returned HTTP {status}; expected {expected}")
    return body


def canonical_for_guide(configuration: dict[str, Any], guide: dict[str, Any]) -> str:
    base_url = configuration.get("canonicalBaseUrl")
    if not isinstance(base_url, str):
        raise RuntimeError("publication configuration has no canonicalBaseUrl")
    parsed = urlparse(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or "%" in parsed.path
        or "\\" in parsed.path
        or "//" in parsed.path
        or (
            parsed.path not in {"", "/"}
            and any(
                segment in {"", ".", ".."}
                for segment in parsed.path.strip("/").split("/")
            )
        )
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError("publication canonicalBaseUrl is not a valid HTTPS base URL")
    path = str(guide.get("canonicalPath", "")).strip("/")
    if not path or any(segment in {"", ".", ".."} for segment in path.split("/")):
        raise RuntimeError(f"invalid canonicalPath: {guide.get('canonicalPath')!r}")
    return f"{base_url.rstrip('/')}/{path}"


def package_metadata(package: bytes, url: str) -> dict[str, Any]:
    try:
        with tarfile.open(fileobj=io.BytesIO(package), mode="r:gz") as archive:
            package_json = archive.extractfile("package/package.json")
            if package_json is None:
                raise RuntimeError(f"{url} has no package/package.json")
            metadata = json.load(package_json)
    except (json.JSONDecodeError, KeyError, tarfile.TarError) as error:
        raise RuntimeError(f"{url} is not a valid FHIR package: {error}") from error
    if not isinstance(metadata, dict):
        raise RuntimeError(f"{url} package metadata is not a JSON object")
    return metadata


def checksum(body: bytes, url: str) -> str:
    fields = body.decode().split()
    if len(fields) != 2 or fields[1] != "package.tgz":
        raise RuntimeError(f"{url} is not a package.tgz SHA-256 checksum")
    return fields[0]


def verify_package(
    *,
    root: str,
    manifest: dict[str, Any],
    expected_canonical: str,
    expected_revision: str | None,
) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise RuntimeError(f"{root}/publication-manifest.json is not a JSON object")
    package_url = f"{root}/package.tgz"
    package = expect_status(package_url, 200)
    package_digest = hashlib.sha256(package).hexdigest()
    published_checksum = checksum(
        expect_status(f"{root}/package.tgz.sha256", 200),
        f"{root}/package.tgz.sha256",
    )
    if package_digest != published_checksum:
        raise RuntimeError(f"{root}/package.tgz checksum does not match")

    metadata = package_metadata(package, package_url)
    expected_manifest = {
        "packageId": metadata.get("name"),
        "packageVersion": metadata.get("version"),
        "canonical": expected_canonical,
        "packageSha256": package_digest,
    }
    for key, expected in expected_manifest.items():
        if manifest.get(key) != expected:
            raise RuntimeError(
                f"{root}/publication-manifest.json has {key}={manifest.get(key)!r}; "
                f"expected {expected!r}"
            )
    if metadata.get("canonical") != expected_canonical:
        raise RuntimeError(
            f"{package_url} has canonical {metadata.get('canonical')!r}; "
            f"expected {expected_canonical!r}"
        )
    if expected_revision is not None and manifest.get("sourceRevision") != expected_revision:
        raise RuntimeError(
            f"{root}/publication-manifest.json has sourceRevision="
            f"{manifest.get('sourceRevision')!r}; expected {expected_revision!r}"
        )
    return metadata


def verify(
    base_url: str,
    configuration: dict[str, Any],
    *,
    canonical_only: bool,
    expected_revision: str,
) -> None:
    base_url = base_url.rstrip("/")
    release_mode = configuration.get("releaseMode")
    if release_mode not in {"ci-build-only", "immutable-releases"}:
        raise RuntimeError("publication configuration has an unsupported releaseMode")
    if not canonical_only:
        for guide in configuration["guides"]:
            for alias in guide.get("aliases", []):
                expect_status(f"{base_url}/{alias}/" if alias else f"{base_url}/", 200)
        for retired in configuration.get("retiredPreviewPaths", []):
            expect_status(f"{base_url}/{retired}", 404)

    for guide in configuration["guides"]:
        root = f"{base_url}/{guide['canonicalPath']}"
        expected_canonical = canonical_for_guide(configuration, guide)
        expect_status(f"{root}/", 200)
        expect_status(f"{root}/ci-build/", 200)
        expect_status(f"{root}/history.html", 200)
        package_list = json.loads(expect_status(f"{root}/package-list.json", 200))
        entries = package_list.get("list")
        if (
            not isinstance(entries, list)
            or not entries
            or not isinstance(entries[0], dict)
            or entries[0].get("version") != "current"
            or entries[0].get("status") != "ci-build"
            or entries[0].get("path") != f"{root}/ci-build"
            or (release_mode == "ci-build-only" and len(entries) != 1)
        ):
            raise RuntimeError(f"{root}/package-list.json does not describe a CI build")
        if package_list.get("canonical") != expected_canonical:
            raise RuntimeError(
                f"{root}/package-list.json has canonical {package_list.get('canonical')!r}; "
                f"expected {expected_canonical!r}"
            )

        root_manifest = json.loads(
            expect_status(f"{root}/publication-manifest.json", 200)
        )
        root_metadata = verify_package(
            root=root,
            manifest=root_manifest,
            expected_canonical=expected_canonical,
            expected_revision=None,
        )
        preview_root = f"{root}/ci-build"
        preview_manifest = json.loads(
            expect_status(f"{preview_root}/publication-manifest.json", 200)
        )
        preview_metadata = verify_package(
            root=preview_root,
            manifest=preview_manifest,
            expected_canonical=expected_canonical,
            expected_revision=expected_revision,
        )
        package_id = package_list.get("package-id")
        if package_id != root_metadata.get("name") or package_id != preview_metadata.get("name"):
            raise RuntimeError(
                f"{root}/package-list.json package-id is inconsistent with published packages"
            )

        representative = guide["representativeResource"]
        expect_status(f"{root}/{representative}", 200)
        resource = json.loads(expect_status(f"{root}/{representative}.json", 200))
        expected_resource_canonical = f"{expected_canonical}/{representative}"
        if resource.get("url") != expected_resource_canonical:
            raise RuntimeError(
                f"{root}/{representative}.json has {resource.get('url')!r}; "
                f"expected {expected_resource_canonical!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument(
        "--config", type=Path, default=Path("publication/config.json")
    )
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--canonical-only", action="store_true")
    arguments = parser.parse_args()
    configuration = json.loads(arguments.config.read_text(encoding="utf-8"))
    verify(
        arguments.base_url,
        configuration,
        canonical_only=arguments.canonical_only,
        expected_revision=arguments.expected_revision,
    )
    print(f"Verified deployed publication at {arguments.base_url.rstrip('/')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
