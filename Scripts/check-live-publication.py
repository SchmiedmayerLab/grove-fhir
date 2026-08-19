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
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


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


def verify(base_url: str, configuration: dict[str, Any], *, canonical_only: bool) -> None:
    base_url = base_url.rstrip("/")
    if not canonical_only:
        for guide in configuration["guides"]:
            for alias in guide.get("aliases", []):
                expect_status(f"{base_url}/{alias}/" if alias else f"{base_url}/", 200)
        for retired in configuration.get("retiredPreviewPaths", []):
            expect_status(f"{base_url}/{retired}", 404)

    for guide in configuration["guides"]:
        root = f"{base_url}/{guide['canonicalPath']}"
        expect_status(f"{root}/", 200)
        expect_status(f"{root}/ci-build/", 200)
        expect_status(f"{root}/history.html", 200)
        package_list = json.loads(expect_status(f"{root}/package-list.json", 200))
        if package_list.get("list", [{}])[0].get("status") != "ci-build":
            raise RuntimeError(f"{root}/package-list.json does not describe a CI build")
        package = expect_status(f"{root}/package.tgz", 200)
        checksum = expect_status(f"{root}/package.tgz.sha256", 200).decode().split()[0]
        if hashlib.sha256(package).hexdigest() != checksum:
            raise RuntimeError(f"{root}/package.tgz checksum does not match")
        representative = guide["representativeResource"]
        expect_status(f"{root}/{representative}", 200)
        resource = json.loads(expect_status(f"{root}/{representative}.json", 200))
        expected_canonical = f"{package_list['canonical'].rstrip('/')}/{representative}"
        if resource.get("url") != expected_canonical:
            raise RuntimeError(
                f"{root}/{representative}.json has {resource.get('url')!r}; "
                f"expected {expected_canonical!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument(
        "--config", type=Path, default=Path("publication/config.json")
    )
    parser.add_argument("--canonical-only", action="store_true")
    arguments = parser.parse_args()
    configuration = json.loads(arguments.config.read_text(encoding="utf-8"))
    verify(arguments.base_url, configuration, canonical_only=arguments.canonical_only)
    print(f"Verified deployed publication at {arguments.base_url.rstrip('/')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
