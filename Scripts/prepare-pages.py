#!/usr/bin/env python3
"""Remove local build locations from an assembled FHIR Publisher site."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import tarfile
from pathlib import Path


TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".json",
    ".md",
    ".svg",
    ".ttl",
    ".txt",
    ".xml",
}
GUIDE_PATHS = {
    "platforms": "platforms",
    "ig": "",
}
LOCAL_LOCATION = re.compile(r"file://|/(?:Users|home/runner|private/tmp)/")
MALFORMED_DATA_URL = re.compile(r"url\([^)]*?pagesdata:(image/[^;]+;base64,[A-Za-z0-9+/=]+)\)")
PROVISIONAL_HISTORY_URLS = {
    "https://grovealliance.org/fhir/core/history.html":
        "https://github.com/SchmiedmayerLab/grove-fhir/releases",
    "https://grovealliance.org/fhir/platforms/history.html":
        "https://github.com/SchmiedmayerLab/grove-fhir/releases",
}


def replace_build_locations(text: str, repository_root: Path, base_url: str) -> str:
    replacements: list[tuple[str, str]] = []
    for source, destination in GUIDE_PATHS.items():
        public_url = f"{base_url}/{destination}".rstrip("/")
        for local in (repository_root / source / "output", repository_root / source / "temp/pages"):
            replacements.extend(((local.as_uri(), public_url), (str(local), public_url)))

    rewritten = MALFORMED_DATA_URL.sub(r"url(data:\1)", text)
    for local, public in sorted(replacements, key=lambda item: len(item[0]), reverse=True):
        rewritten = rewritten.replace(local, public)
    for canonical_history, releases in PROVISIONAL_HISTORY_URLS.items():
        rewritten = rewritten.replace(canonical_history, releases)
    rewritten = rewritten.replace("Local Development build", "Continuous preview build")
    return rewritten.replace(
        str(repository_root),
        "https://github.com/SchmiedmayerLab/grove-fhir/tree/main",
    )


def rewrite_package_archive(path: Path, public_url: str) -> None:
    output = io.BytesIO()
    with tarfile.open(path, "r:gz") as source, tarfile.open(fileobj=output, mode="w") as target:
        for member in source.getmembers():
            payload = source.extractfile(member).read() if member.isfile() else None
            if member.name == "package/package.json" and payload is not None:
                package = json.loads(payload)
                package["url"] = public_url
                payload = (json.dumps(package, indent=2, ensure_ascii=False) + "\n").encode()
                member.size = len(payload)
            target.addfile(member, io.BytesIO(payload) if payload is not None else None)

    with path.open("wb") as destination:
        with gzip.GzipFile(fileobj=destination, mode="wb", mtime=0) as compressed:
            compressed.write(output.getvalue())


def prepare_site(site: Path, repository_root: Path, base_url: str) -> None:
    for path in site.rglob("*"):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            path.write_text(
                replace_build_locations(text, repository_root, base_url),
                encoding="utf-8",
            )

    for guide_path, public_path in GUIDE_PATHS.items():
        guide_site = site / public_path
        public_url = f"{base_url}/{public_path}".rstrip("/")
        for archive in guide_site.glob("package*.tgz"):
            rewrite_package_archive(archive, public_url)

    leaked_locations: list[str] = []
    for path in site.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LOCAL_LOCATION.search(text):
            leaked_locations.append(str(path.relative_to(site)))
    if leaked_locations:
        raise RuntimeError(
            "local filesystem locations remain in Pages files: "
            + ", ".join(leaked_locations[:10])
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    arguments = parser.parse_args()

    prepare_site(
        arguments.site.resolve(),
        arguments.repository_root.resolve(),
        arguments.base_url.rstrip("/"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
