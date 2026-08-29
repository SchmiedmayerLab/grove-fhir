#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

"""Generate safe, deterministic static routes for locally owned FHIR canonicals."""

from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit


MACHINE_FORMATS = ("json", "xml", "ttl")
MANIFEST_NAME = "canonical-routes.json"
SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9._-]+$")


class CanonicalRouteError(RuntimeError):
    """Base error for invalid or unsafe canonical route generation."""


class UnsafeRouteError(CanonicalRouteError):
    """Raised when a canonical or target prefix could escape its publication root."""


class RouteCollisionError(CanonicalRouteError):
    """Raised when two routes, or a route and an existing path, collide."""


class MissingRepresentationError(CanonicalRouteError):
    """Raised when Publisher output lacks a representation required by a route."""


def _normalized_canonical(canonical: str) -> tuple[str, SplitResult]:
    value = canonical.rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise UnsafeRouteError(f"canonical must be an absolute HTTP(S) URL: {canonical!r}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise UnsafeRouteError(f"canonical contains unsupported URL components: {canonical!r}")
    if "\\" in parsed.path or "%" in parsed.path:
        raise UnsafeRouteError(f"canonical contains an ambiguous path: {canonical!r}")
    _safe_path_segments(parsed.path, "canonical")
    normalized = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, "", ""))
    return normalized, urlsplit(normalized)


def _safe_path_segments(path: str, label: str) -> tuple[str, ...]:
    trimmed = path.strip("/")
    if not trimmed:
        return ()
    segments = tuple(trimmed.split("/"))
    for segment in segments:
        if (
            not segment
            or segment in {".", ".."}
            or "\\" in segment
            or "%" in segment
            or not SAFE_SEGMENT.fullmatch(segment)
        ):
            raise UnsafeRouteError(f"{label} contains an unsafe path segment: {segment!r}")
    return segments


def _safe_target_prefix(target_prefix: str) -> PurePosixPath:
    if not target_prefix:
        return PurePosixPath()
    if target_prefix.startswith(("/", "\\")):
        raise UnsafeRouteError(f"target prefix must be relative: {target_prefix!r}")
    segments = _safe_path_segments(target_prefix, "target prefix")
    return PurePosixPath(*segments)


def _safe_identifier(value: str, label: str) -> None:
    segments = _safe_path_segments(value, label)
    if len(segments) != 1 or segments[0] != value:
        raise UnsafeRouteError(f"{label} must be one safe path segment: {value!r}")


def _owned_route(
    resource_url: str,
    canonical: SplitResult,
    resource_type: str,
) -> tuple[str, ...] | None:
    parsed = urlsplit(resource_url)
    if parsed.scheme.lower() != canonical.scheme or parsed.netloc.lower() != canonical.netloc:
        return None

    canonical_path = canonical.path.rstrip("/")
    prefix = f"{canonical_path}/" if canonical_path else "/"
    if not parsed.path.startswith(prefix):
        return None
    if parsed.query or parsed.fragment:
        raise UnsafeRouteError(f"owned resource URL contains a query or fragment: {resource_url!r}")

    suffix = parsed.path[len(prefix) :]
    segments = _safe_path_segments(suffix, f"resource URL {resource_url!r}")
    if len(segments) < 2:
        raise UnsafeRouteError(
            f"owned resource URL must contain a resource type and id: {resource_url!r}"
        )
    if segments[0] != resource_type:
        raise UnsafeRouteError(
            f"owned resource URL type {segments[0]!r} does not match {resource_type!r}: "
            f"{resource_url!r}"
        )
    return segments


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CanonicalRouteError(f"cannot read Publisher JSON {path}: {error}") from error
    return value if isinstance(value, dict) else None


def _relative_href(source: PurePosixPath, target: PurePosixPath) -> str:
    start = source.parent.as_posix() or "."
    return posixpath.relpath(target.as_posix(), start=start)


def _redirect_document(
    *,
    canonical_url: str,
    route: PurePosixPath,
    redirect: PurePosixPath,
    human: PurePosixPath,
    formats: dict[str, str],
) -> bytes:
    target_href = _relative_href(redirect, human)
    package_href = _relative_href(redirect, PurePosixPath("package.tgz"))
    format_links = " · ".join(
        f'<a href="{html.escape(_relative_href(redirect, PurePosixPath(path)), quote=True)}">'
        f"{name.upper()}</a>"
        for name, path in sorted(formats.items())
    )
    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={html.escape(target_href, quote=True)}">
  <link rel="canonical" href="{html.escape(canonical_url, quote=True)}">
  <title>{html.escape(route.as_posix())}</title>
</head>
<body>
  <p>This is the canonical URL of a FHIR artifact. Continue to the
    <a href="{html.escape(target_href, quote=True)}">human-readable rendering</a>.
  </p>
  <p>Machine-readable forms: {format_links}. Full package:
    <a href="{html.escape(package_href, quote=True)}">package.tgz</a>.
  </p>
</body>
</html>
"""
    return document.encode("utf-8")


def _ensure_safe_destination(site: Path, relative: PurePosixPath) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise UnsafeRouteError(f"route escapes publication root: {relative.as_posix()!r}")
    destination = site.joinpath(*relative.parts)
    for parent in (destination, *destination.parents):
        if parent == site.parent:
            break
        if parent.is_symlink():
            raise UnsafeRouteError(f"route traverses a symbolic link: {parent}")
        if parent == site:
            break
    return destination


def _validate_plan(site: Path, files: dict[PurePosixPath, bytes]) -> None:
    targets = set(files)
    for relative in sorted(targets, key=lambda path: path.as_posix()):
        for parent in relative.parents:
            if parent == PurePosixPath("."):
                break
            if parent in targets:
                raise RouteCollisionError(
                    f"route requires {parent.as_posix()!r} to be both a file and a directory"
                )

        destination = _ensure_safe_destination(site, relative)
        for parent in destination.parents:
            if parent == site.parent:
                break
            if parent.exists() and not parent.is_dir():
                raise RouteCollisionError(f"route parent is an existing file: {parent}")
            if parent == site:
                break
        if destination.exists():
            if not destination.is_file() or destination.read_bytes() != files[relative]:
                raise RouteCollisionError(f"route collides with existing content: {destination}")


def _add_file(
    files: dict[PurePosixPath, bytes],
    relative: PurePosixPath,
    content: bytes,
    owner: str,
) -> None:
    if relative in files:
        raise RouteCollisionError(
            f"multiple canonical resources claim {relative.as_posix()!r}; latest is {owner}"
        )
    files[relative] = content


def generate_routes(
    output: Path,
    site: Path,
    canonical: str,
    target_prefix: str = "",
) -> list[dict[str, object]]:
    """Generate routes and return their deterministic JSON-serializable manifest rows.

    ``output`` is a FHIR Publisher output directory. ``site`` is the root at which the
    supplied canonical is hosted. ``target_prefix`` locates the copied Publisher site
    below that root (for example ``ci-build``); canonical routes themselves always live
    directly below ``site``.
    """

    output = output.resolve()
    site = site.resolve()
    if not output.is_dir():
        raise CanonicalRouteError(f"Publisher output directory does not exist: {output}")

    normalized_canonical, canonical_parts = _normalized_canonical(canonical)
    human_prefix = _safe_target_prefix(target_prefix)
    discovered: list[dict[str, Any]] = []
    claimed_routes: dict[str, str] = {}

    for source_json in sorted(output.glob("*.json"), key=lambda path: path.name):
        resource = _load_json(source_json)
        if resource is None or not isinstance(resource.get("url"), str):
            continue
        resource_url = resource["url"]
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        if not isinstance(resource_type, str) or not isinstance(resource_id, str):
            continue

        route_segments = _owned_route(resource_url, canonical_parts, resource_type)
        if route_segments is None:
            continue
        _safe_identifier(resource_type, f"resource type in {source_json.name}")
        _safe_identifier(resource_id, f"resource id in {source_json.name}")

        expected_json = output / f"{resource_type}-{resource_id}.json"
        if source_json != expected_json:
            if expected_json.is_file():
                continue
            raise MissingRepresentationError(
                f"owned resource does not use the Publisher primary filename: {source_json.name}"
            )

        route = PurePosixPath(*route_segments)
        route_key = route.as_posix()
        previous = claimed_routes.get(route_key)
        if previous is not None:
            raise RouteCollisionError(
                f"canonical route {route_key!r} is claimed by both {previous} and "
                f"{source_json.name}"
            )
        claimed_routes[route_key] = source_json.name

        human_name = f"{resource_type}-{resource_id}.html"
        source_human = output / human_name
        if not source_human.is_file():
            source_human = output / "index.html"
            human_name = source_human.name
        if not source_human.is_file():
            raise MissingRepresentationError(
                f"missing artifact rendering and guide landing page for {source_json.name}"
            )
        human = human_prefix / human_name
        hosted_human = _ensure_safe_destination(site, human)
        if not hosted_human.is_file():
            raise MissingRepresentationError(
                f"human rendering has not been copied into the site: {hosted_human}"
            )

        source_formats: dict[str, Path] = {}
        destination_formats: dict[str, str] = {}
        for format_name in MACHINE_FORMATS:
            source = output / f"{resource_type}-{resource_id}.{format_name}"
            if not source.is_file():
                raise MissingRepresentationError(f"missing machine representation: {source}")
            source_formats[format_name] = source
            destination_formats[format_name] = f"{route.as_posix()}.{format_name}"

        canonical_url = f"{normalized_canonical}/{route.as_posix()}"
        directory_redirect = route / "index.html"
        html_redirect = PurePosixPath(f"{route.as_posix()}.html")
        discovered.append(
            {
                "canonical": canonical_url,
                "resourceType": resource_type,
                "id": resource_id,
                "source": source_json.name,
                "route": route.as_posix(),
                "human": human.as_posix(),
                "redirects": {
                    "directory": directory_redirect.as_posix(),
                    "html": html_redirect.as_posix(),
                },
                "formats": dict(sorted(destination_formats.items())),
                "_route_path": route,
                "_human_path": human,
                "_redirect_paths": (directory_redirect, html_redirect),
                "_source_formats": source_formats,
            }
        )

    discovered.sort(key=lambda row: (str(row["canonical"]), str(row["source"])))
    files: dict[PurePosixPath, bytes] = {}
    manifest_rows: list[dict[str, object]] = []

    for row in discovered:
        route = row.pop("_route_path")
        human = row.pop("_human_path")
        redirect_paths = row.pop("_redirect_paths")
        source_formats = row.pop("_source_formats")
        assert isinstance(route, PurePosixPath)
        assert isinstance(human, PurePosixPath)
        assert isinstance(redirect_paths, tuple)
        assert isinstance(source_formats, dict)
        formats = row["formats"]
        assert isinstance(formats, dict)

        for format_name, source in sorted(source_formats.items()):
            destination = PurePosixPath(str(formats[format_name]))
            _add_file(files, destination, source.read_bytes(), str(row["source"]))
        for redirect in redirect_paths:
            _add_file(
                files,
                redirect,
                _redirect_document(
                    canonical_url=str(row["canonical"]),
                    route=route,
                    redirect=redirect,
                    human=human,
                    formats={str(key): str(value) for key, value in formats.items()},
                ),
                str(row["source"]),
            )
        manifest_rows.append(row)

    manifest = {
        "schemaVersion": 0,
        "canonical": normalized_canonical,
        "routes": manifest_rows,
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    _add_file(files, PurePosixPath(MANIFEST_NAME), manifest_bytes, "route manifest")

    _validate_plan(site, files)
    site.mkdir(parents=True, exist_ok=True)
    for relative, content in sorted(files.items(), key=lambda item: item[0].as_posix()):
        destination = _ensure_safe_destination(site, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    return manifest_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="FHIR Publisher output directory")
    parser.add_argument(
        "site",
        type=Path,
        nargs="?",
        help="canonical publication root (defaults to the Publisher output directory)",
    )
    parser.add_argument("--canonical", required=True, help="canonical URL hosted at site")
    parser.add_argument(
        "--target-prefix",
        default="",
        help="relative path from site to the copied Publisher human-readable output",
    )
    arguments = parser.parse_args(argv)
    site = arguments.site or arguments.output

    try:
        routes = generate_routes(
            arguments.output,
            site,
            arguments.canonical,
            arguments.target_prefix,
        )
    except CanonicalRouteError as error:
        parser.exit(1, f"error: {error}\n")
    print(
        f"generated {len(routes)} canonical routes under {site.resolve()} "
        f"({MANIFEST_NAME})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
