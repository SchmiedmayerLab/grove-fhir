#!/usr/bin/env python3
"""Promote a publication-mode FHIR Publisher build into an immutable site tree."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import re
import shutil
import tarfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse


SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$")
LOCAL_LOCATION = re.compile(r"file://|/(?:Users|home/runner|private/tmp)/")


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def safe_path(value: str) -> Path:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe publication path: {value!r}")
    return Path(*path.parts)


def package_metadata(path: Path) -> dict[str, Any]:
    with tarfile.open(path, "r:gz") as package:
        entry = package.extractfile("package/package.json")
        if entry is None:
            raise ValueError(f"{path} has no package/package.json")
        return json.load(entry)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_local_paths(source: Path) -> None:
    leaked: list[str] = []
    for path in source.rglob("*"):
        if not path.is_file() or path.suffix not in {".html", ".json", ".xml", ".ttl"}:
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LOCAL_LOCATION.search(contents):
            leaked.append(str(path.relative_to(source)))
    if leaked:
        raise ValueError("release output contains local paths: " + ", ".join(leaked[:10]))


def remove_generated_routes(root: Path) -> None:
    manifest_path = root / "canonical-routes.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates: set[Path] = {manifest_path}
    for route in manifest.get("routes", []):
        for value in route.get("redirects", {}).values():
            candidates.add(root / safe_path(value))
        for value in route.get("formats", {}).values():
            candidates.add(root / safe_path(value))
    for candidate in sorted(candidates, key=lambda path: len(path.parts), reverse=True):
        if candidate.is_file():
            candidate.unlink()
    directories = sorted(
        {parent for candidate in candidates for parent in candidate.parents if root in parent.parents},
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        if directory != root and directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def release_redirect(title: str, canonical: str, version: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url={html.escape(version, quote=True)}/">
<link rel="canonical" href="{html.escape(canonical, quote=True)}">
<title>{html.escape(title)}</title></head>
<body><p>Open the current release, <a href="{html.escape(version, quote=True)}/">
{html.escape(version)}</a>, or the <a href="history.html">publication history</a>.</p></body></html>
"""


def publish_version(
    *,
    site: Path,
    source: Path,
    configuration: dict[str, Any],
    guide_source: str,
    status: str,
    sequence: str,
    publication_date: str,
    description: str,
    current: bool,
    revision: str,
    repository_root: Path,
) -> str:
    if configuration.get("releaseMode") != "immutable-releases":
        raise ValueError(
            "immutable release publication is disabled by publication releaseMode"
        )
    guide = next(
        (entry for entry in configuration["guides"] if entry["source"] == guide_source), None
    )
    if guide is None:
        raise ValueError(f"unknown active guide: {guide_source}")
    date.fromisoformat(publication_date)
    if not sequence.strip() or not description.strip():
        raise ValueError("sequence and description must not be empty")
    if status == "ci-build":
        raise ValueError("immutable versions cannot use ci-build status")

    source = source.resolve()
    package_path = source / "package.tgz"
    if not (source / "index.html").is_file() or not package_path.is_file():
        raise ValueError("source is not a complete FHIR Publisher output")
    reject_local_paths(source)
    metadata = package_metadata(package_path)
    package_id = metadata.get("name")
    version = metadata.get("version")
    canonical = metadata.get("canonical")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise ValueError(f"package version is not publishable SemVer: {version!r}")
    if not isinstance(canonical, str):
        raise ValueError("package has no canonical URL")
    canonical_base = configuration.get("canonicalBaseUrl")
    parsed_base = urlparse(canonical_base) if isinstance(canonical_base, str) else None
    if (
        parsed_base is None
        or parsed_base.scheme != "https"
        or not parsed_base.netloc
        or parsed_base.username is not None
        or parsed_base.password is not None
        or "%" in parsed_base.path
        or "\\" in parsed_base.path
        or "//" in parsed_base.path
        or (
            parsed_base.path not in {"", "/"}
            and any(
                segment in {"", ".", ".."}
                for segment in parsed_base.path.strip("/").split("/")
            )
        )
        or parsed_base.params
        or parsed_base.query
        or parsed_base.fragment
    ):
        raise ValueError("publication canonicalBaseUrl is not a valid HTTPS base URL")
    expected_canonical = (
        f"{canonical_base.rstrip('/')}/{safe_path(guide['canonicalPath']).as_posix()}"
    )
    if canonical.rstrip("/") != expected_canonical:
        raise ValueError(
            f"package canonical {canonical!r} does not match configured canonical "
            f"{expected_canonical!r}"
        )
    expected_url = f"{canonical}/{version}"
    if metadata.get("url") != expected_url or metadata.get("notForPublication") is True:
        raise ValueError(
            "release package must be built in Publisher publication mode for its version URL"
        )

    canonical_root = site.resolve() / safe_path(guide["canonicalPath"])
    if (canonical_root / version).exists():
        raise FileExistsError(
            f"immutable version already exists: {canonical_root / version}"
        )
    package_list_path = canonical_root / "package-list.json"
    if package_list_path.is_file():
        history = json.loads(package_list_path.read_text(encoding="utf-8"))
        if history.get("package-id") != package_id or history.get("canonical") != canonical:
            raise ValueError("existing publication history belongs to a different package")
        releases = [entry for entry in history.get("list", []) if entry.get("version") != "current"]
    else:
        history = {
            "package-id": package_id,
            "title": metadata["title"],
            "canonical": canonical,
            "introduction": metadata.get("description", ""),
        }
        releases = []
    if any(entry.get("version") == version for entry in releases):
        raise ValueError(f"version {version} already exists in package-list.json")

    canonical_root.parent.mkdir(parents=True, exist_ok=True)
    transaction_root = canonical_root.with_name(
        f".{canonical_root.name}.{version}.publish.tmp"
    )
    backup_root = canonical_root.with_name(
        f".{canonical_root.name}.{version}.backup.tmp"
    )
    for temporary in (transaction_root, backup_root):
        if temporary.exists():
            raise FileExistsError(
                f"stale publication transaction directory exists: {temporary}"
            )
    redirects = load_module(
        "canonical_redirects", repository_root / "tools/make-canonical-redirects.py"
    )
    try:
        if canonical_root.exists():
            shutil.copytree(canonical_root, transaction_root)
        else:
            transaction_root.mkdir()

        version_root = transaction_root / version
        staging_root = transaction_root / f".{version}.tmp"
        shutil.copytree(source, staging_root)
        package_digest = sha256(staging_root / "package.tgz")
        (staging_root / "package.tgz.sha256").write_text(
            f"{package_digest}  package.tgz\n", encoding="utf-8"
        )
        redirects.generate_routes(source, staging_root, canonical)
        staging_root.rename(version_root)

        if current:
            for entry in releases:
                entry.pop("current", None)
        release = {
            "version": version,
            "path": expected_url,
            "status": status,
            "sequence": sequence,
            "fhirversion": metadata["fhirVersions"][0],
            "date": publication_date,
            "desc": description,
        }
        if current:
            release["current"] = True
        history["list"] = [release, *releases]
        (transaction_root / "package-list.json").write_text(
            json.dumps(history, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        prepare_pages = load_module(
            "prepare_pages", repository_root / "Scripts/prepare-pages.py"
        )
        (transaction_root / "history.html").write_text(
            prepare_pages.render_history(history, f"{canonical}/package.tgz"),
            encoding="utf-8",
        )
        if current:
            remove_generated_routes(transaction_root)
            routes = redirects.generate_routes(
                source, transaction_root, canonical, target_prefix=version
            )
            (transaction_root / "index.html").write_text(
                release_redirect(str(metadata["title"]), canonical, version),
                encoding="utf-8",
            )
            shutil.copy2(version_root / "package.tgz", transaction_root / "package.tgz")
            (transaction_root / "package.tgz.sha256").write_text(
                f"{package_digest}  package.tgz\n", encoding="utf-8"
            )
            (transaction_root / "publication-manifest.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "packageId": package_id,
                        "packageVersion": version,
                        "canonical": canonical,
                        "publication": expected_url,
                        "sourceRevision": revision,
                        "packageSha256": package_digest,
                        "canonicalRouteCount": len(routes),
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

        if canonical_root.exists():
            canonical_root.rename(backup_root)
        try:
            transaction_root.rename(canonical_root)
        except Exception:
            if backup_root.exists() and not canonical_root.exists():
                backup_root.rename(canonical_root)
            raise
        if backup_root.exists():
            shutil.rmtree(backup_root, ignore_errors=True)
    except Exception:
        if transaction_root.exists():
            shutil.rmtree(transaction_root)
        if backup_root.exists() and not canonical_root.exists():
            backup_root.rename(canonical_root)
        raise
    return version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--guide-source", required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    arguments = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[1]
    configuration = json.loads(arguments.config.read_text(encoding="utf-8"))
    request = json.loads(arguments.request.read_text(encoding="utf-8"))
    metadata = package_metadata(arguments.source / "package.tgz")
    expected_request = {
        "package-id": metadata.get("name"),
        "version": metadata.get("version"),
        "path": f"{metadata.get('canonical')}/{metadata.get('version')}",
    }
    for key, expected in expected_request.items():
        if request.get(key) != expected:
            raise ValueError(
                f"publication request {key} is {request.get(key)!r}; expected {expected!r}"
            )
    version = publish_version(
        site=arguments.site,
        source=arguments.source,
        configuration=configuration,
        guide_source=arguments.guide_source,
        status=request["status"],
        sequence=request["sequence"],
        publication_date=request["date"],
        description=request["desc"],
        current=bool(request.get("current")),
        revision=arguments.revision,
        repository_root=repository_root,
    )
    print(f"Published immutable {arguments.guide_source} version {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
