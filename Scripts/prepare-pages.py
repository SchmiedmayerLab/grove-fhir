#!/usr/bin/env python3
"""Assemble deterministic GitHub Pages previews for the active FHIR guides."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import html
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from fhir_package_semantic_snapshot import is_publisher_generated_resource_date
except ModuleNotFoundError:  # Imported as Scripts.prepare-pages in tests.
    from Scripts.fhir_package_semantic_snapshot import (  # type: ignore[no-redef]
        is_publisher_generated_resource_date,
    )


TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".internals",
    ".json",
    ".js",
    ".map",
    ".md",
    ".mjs",
    ".scss",
    ".svg",
    ".ttl",
    ".txt",
    ".xml",
    ".xhtml",
}
MACHINE_LOCAL_UNIX_PATH = re.compile(
    r"(?<![A-Za-z0-9._~:/?#%+\\-])/(?:Users|home/runner|private/tmp)/"
)
MACHINE_LOCAL_WINDOWS_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:[A-Z]:\\+(?:Users|home\\+runner|private\\+tmp)\\+)"
)
INKSCAPE_EXPORT_FILENAME = re.compile(
    r'(inkscape:export-filename=")[A-Za-z]:\\[^"\r\n]*\\([^"\\\r\n]+)(")'
)
MALFORMED_DATA_URL = re.compile(
    r"url\([^)]*?pagesdata:(image/[^;]+;base64,[A-Za-z0-9+/=]+)\)"
)
BUILT_SUFFIX = re.compile(r"\s*\(built [^)]*\)\s*$")


def _json_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in _json_strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _json_strings(item)]
    return []


def validate_portable_text(text: str, label: str, suffix: str) -> None:
    candidates = [text]
    if suffix.lower() == ".json":
        try:
            candidates.extend(_json_strings(json.loads(text)))
        except json.JSONDecodeError:
            pass
    if any("\x1b" in candidate for candidate in candidates):
        raise ValueError(f"ANSI escape data remains in {label}")
    if any(
        "file://" in candidate
        or MACHINE_LOCAL_UNIX_PATH.search(candidate)
        or MACHINE_LOCAL_WINDOWS_PATH.search(candidate)
        for candidate in candidates
    ):
        raise ValueError(f"local filesystem location remains in {label}")


def load_configuration(path: Path) -> dict[str, Any]:
    configuration = json.loads(path.read_text(encoding="utf-8"))
    if configuration.get("schemaVersion") != 1:
        raise ValueError("publication/config.json must use schemaVersion 1")
    if not isinstance(configuration.get("guides"), list) or not configuration["guides"]:
        raise ValueError("publication/config.json must declare at least one guide")
    if configuration.get("releaseMode") not in {"ci-build-only", "immutable-releases"}:
        raise ValueError("publication/config.json must declare a supported releaseMode")

    sources: set[str] = set()
    canonical_paths: set[str] = set()
    for index, guide in enumerate(configuration["guides"]):
        if not isinstance(guide, dict):
            raise ValueError(f"publication guide[{index}] must be an object")
        source = guide.get("source")
        canonical = guide.get("canonicalPath")
        if not isinstance(source, str) or not isinstance(canonical, str):
            raise ValueError(
                f"publication guide[{index}] must declare string source and canonicalPath"
            )
        source_path = safe_relative_path(source, f"guide[{index}] source").as_posix()
        canonical_path = safe_relative_path(
            canonical, f"guide[{index}] canonicalPath"
        ).as_posix()
        if source_path in sources:
            raise ValueError(f"publication guide source is repeated: {source_path}")
        if canonical_path in canonical_paths:
            raise ValueError(
                f"publication canonicalPath is repeated: {canonical_path}"
            )
        sources.add(source_path)
        canonical_paths.add(canonical_path)

    aliases: set[str] = set()
    for index, guide in enumerate(configuration["guides"]):
        declared_aliases = guide.get("aliases", [])
        if not isinstance(declared_aliases, list) or not all(
            isinstance(alias, str) for alias in declared_aliases
        ):
            raise ValueError(f"publication guide[{index}] aliases must be strings")
        for alias in declared_aliases:
            alias_path = safe_relative_path(
                alias, f"guide[{index}] alias", allow_empty=True
            ).as_posix()
            if alias_path in canonical_paths:
                raise ValueError(
                    f"publication alias collides with canonicalPath: {alias_path}"
                )
            if alias_path in aliases:
                raise ValueError(f"publication alias is repeated: {alias_path}")
            aliases.add(alias_path)
    return configuration


def safe_relative_path(value: str, label: str, *, allow_empty: bool = False) -> Path:
    path = PurePosixPath(value)
    if (not value and not allow_empty) or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be a safe relative path: {value!r}")
    return Path(*path.parts) if value else Path()


def git_value(repository_root: Path, format_string: str) -> str:
    result = subprocess.run(
        ["git", "log", "-1", f"--format={format_string}"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def replace_build_locations(
    text: str,
    repository_root: Path,
    public_urls: dict[str, str],
    source_url: str,
) -> str:
    replacements: list[tuple[str, str]] = []
    for source, public_url in public_urls.items():
        for local in (
            repository_root / source / "output",
            repository_root / source / "temp/pages",
        ):
            replacements.extend(((local.as_uri(), public_url), (str(local), public_url)))

    rewritten = MALFORMED_DATA_URL.sub(r"url(data:\1)", text)
    # The Publisher template currently carries an Inkscape export path from the
    # machine on which its international-language icon was authored. The path is
    # non-functional metadata; retain only the asset name in the hosted copy.
    rewritten = INKSCAPE_EXPORT_FILENAME.sub(r"\1\2\3", rewritten)
    for local, public in sorted(replacements, key=lambda item: len(item[0]), reverse=True):
        rewritten = rewritten.replace(local, public)
    return rewritten.replace(str(repository_root), source_url)


def rewrite_authored_canonical_links(
    text: str,
    canonical_public_urls: dict[str, str],
) -> str:
    """Repoint authored canonical hyperlinks at the host being assembled.

    Only link attributes are rewritten; canonical URLs elsewhere (resource
    identity, narrative text, JSON payloads) are left untouched.
    """
    ordered = sorted(
        canonical_public_urls.items(), key=lambda item: len(item[0]), reverse=True
    )
    # Two phases so a longer mapping (a guide's history page) shields its match
    # from a shorter one (the guide prefix) even when the longer one is identity.
    placeholders: list[tuple[str, str]] = []
    for index, (canonical, public) in enumerate(ordered):
        token = f"\x00authored-link-{index}\x00"
        for quote in ('"', "'"):
            text = text.replace(f"href={quote}{canonical}", f"href={quote}{token}")
        placeholders.append((token, public))
    for token, public in placeholders:
        text = text.replace(token, public)
    return text


def read_package_metadata(path: Path) -> dict[str, Any]:
    with tarfile.open(path, "r:gz") as package:
        package_file = package.extractfile("package/package.json")
        if package_file is None:
            raise ValueError(f"{path} does not contain package/package.json")
        return json.load(package_file)


def normalize_publisher_internals(
    text: str, package_build_timestamp: str | None, source_date_epoch: int
) -> str:
    """Replace the Publisher's private build clock with the reproducible clock.

    Publisher 2.3.2 renders ``spec.internals`` with a 12-hour clock but omits
    the meridiem, while ``package.json`` retains the same local wall clock in
    24-hour form. Bind the date, minute, and second exactly and accept only the
    corresponding 12-hour projection before normalizing both fields.
    """
    try:
        internals = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("package spec.internals must contain JSON") from error
    if not isinstance(internals, dict) or package_build_timestamp is None:
        raise ValueError("package spec.internals has no exact Publisher build timestamp")
    try:
        package_clock = datetime.strptime(package_build_timestamp, "%Y%m%d%H%M%S")
    except ValueError as error:
        raise ValueError("package spec.internals build timestamp is inconsistent") from error
    expected_date = (
        f"{package_build_timestamp[:4]}-{package_build_timestamp[4:6]}-"
        f"{package_build_timestamp[6:8]}"
    )
    expected_internals_timestamp = (
        package_build_timestamp[:8]
        + f"{package_clock.hour % 12 or 12:02d}"
        + package_build_timestamp[10:]
    )
    date_time = internals.get("date-time")
    if (
        internals.get("date") != expected_date
        or not isinstance(date_time, str)
        or not re.fullmatch(
            re.escape(expected_internals_timestamp)
            + r"(?:Z|[+-](?:(?:0[0-9]|1[0-3])[0-5][0-9]|1400))",
            date_time,
        )
    ):
        raise ValueError("package spec.internals build timestamp is inconsistent")
    reproducible = datetime.fromtimestamp(source_date_epoch, tz=timezone.utc)
    internals["date"] = reproducible.strftime("%Y-%m-%d")
    internals["date-time"] = reproducible.strftime("%Y%m%d%H%M%S+0000")
    return json.dumps(internals, indent=2, ensure_ascii=False) + "\n"


def rewrite_package_archive(
    path: Path,
    canonical: str,
    source_date_epoch: int,
    *,
    repository_root: Path,
    public_urls: dict[str, str],
    source_url: str,
) -> None:
    original_metadata = read_package_metadata(path)
    raw_package_date = original_metadata.get("date")
    package_build_timestamp = (
        raw_package_date
        if isinstance(raw_package_date, str)
        and re.fullmatch(r"[0-9]{14}", raw_package_date)
        else None
    )
    entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
    seen_names: set[str] = set()
    with tarfile.open(path, "r:gz") as source:
        for original in source.getmembers():
            if not isinstance(original.name, str) or not original.name or "\\" in original.name:
                raise ValueError(f"unsafe package archive member: {original.name!r}")
            candidate = PurePosixPath(original.name)
            if (
                candidate.is_absolute()
                or ".." in candidate.parts
                or "." in candidate.parts
                or candidate.as_posix() != original.name.rstrip("/")
            ):
                raise ValueError(f"unsafe package archive member: {original.name!r}")
            normalized_name = candidate.as_posix()
            if normalized_name in seen_names:
                raise ValueError(f"duplicate package archive member: {normalized_name}")
            seen_names.add(normalized_name)
            if not original.isfile() and not original.isdir():
                raise ValueError(
                    f"unsupported package archive member type: {original.name}"
                )
            member = copy.copy(original)
            member.name = normalized_name
            if original.isfile():
                extracted = source.extractfile(original)
                if extracted is None:
                    raise ValueError(f"unreadable package archive member: {original.name}")
                payload = extracted.read()
            else:
                payload = None
            if member.name == "package/package.json" and payload is not None:
                package = json.loads(payload)
                package["url"] = canonical
                package["date"] = datetime.fromtimestamp(
                    source_date_epoch, tz=timezone.utc
                ).strftime("%Y%m%d%H%M%S")
                description = package.get("description")
                if isinstance(description, str):
                    package["description"] = BUILT_SUFFIX.sub("", description)
                payload = (json.dumps(package, indent=2, ensure_ascii=False) + "\n").encode()

            if payload is not None and PurePosixPath(member.name).suffix in TEXT_SUFFIXES:
                try:
                    text = payload.decode("utf-8")
                except UnicodeDecodeError:
                    pass
                else:
                    rewritten = replace_build_locations(
                        text,
                        repository_root,
                        public_urls,
                        source_url,
                    )
                    if member.name == "package/other/spec.internals":
                        rewritten = normalize_publisher_internals(
                            rewritten, package_build_timestamp, source_date_epoch
                        )
                    elif (
                        member.name != "package/package.json"
                        and PurePosixPath(member.name).suffix == ".json"
                        and package_build_timestamp is not None
                    ):
                        try:
                            resource = json.loads(rewritten)
                        except json.JSONDecodeError:
                            pass
                        else:
                            if (
                                isinstance(resource, dict)
                                and is_publisher_generated_resource_date(
                                    resource, package_build_timestamp
                                )
                            ):
                                resource.pop("date")
                                rewritten = (
                                    json.dumps(resource, indent=2, ensure_ascii=False)
                                    + "\n"
                                )
                    validate_portable_text(
                        rewritten,
                        f"{path.name}:{member.name}",
                        PurePosixPath(member.name).suffix,
                    )
                    payload = rewritten.encode("utf-8")

            member.uid = 0
            member.gid = 0
            member.uname = ""
            member.gname = ""
            member.mtime = source_date_epoch
            member.pax_headers = {}
            member.linkname = ""
            member.devmajor = 0
            member.devminor = 0
            if member.isdir():
                member.type = tarfile.DIRTYPE
                member.mode = 0o755
                member.size = 0
            else:
                member.type = tarfile.REGTYPE
                member.mode = 0o644
            if payload is not None:
                member.size = len(payload)
            try:
                member.tobuf(format=tarfile.USTAR_FORMAT)
            except (ValueError, UnicodeError) as error:
                raise ValueError(
                    f"package archive member cannot be represented in USTAR: {member.name}"
                ) from error
            entries.append((member, payload))

    uncompressed = io.BytesIO()
    with tarfile.open(fileobj=uncompressed, mode="w", format=tarfile.USTAR_FORMAT) as target:
        for member, payload in sorted(entries, key=lambda entry: entry[0].name):
            target.addfile(member, io.BytesIO(payload) if payload is not None else None)

    with path.open("wb") as destination:
        with gzip.GzipFile(
            filename="",
            fileobj=destination,
            mode="wb",
            mtime=source_date_epoch,
        ) as compressed:
            compressed.write(uncompressed.getvalue())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def package_list(
    metadata: dict[str, Any],
    preview_url: str,
    published_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fhir_versions = metadata.get("fhirVersions")
    if not isinstance(fhir_versions, list) or len(fhir_versions) != 1:
        raise ValueError("each current package must declare exactly one FHIR version")
    description = metadata.get("description", "")
    if not isinstance(description, str):
        raise ValueError("package description must be text")
    releases: list[dict[str, Any]] = []
    if published_history is not None:
        if published_history.get("package-id") != metadata["name"]:
            raise ValueError("published package history belongs to a different package")
        if published_history.get("canonical") != metadata["canonical"]:
            raise ValueError("published package history uses a different canonical URL")
        for entry in published_history.get("list", []):
            if entry.get("version") != "current":
                releases.append(entry)
    return {
        "package-id": metadata["name"],
        "title": metadata["title"],
        "canonical": metadata["canonical"],
        "introduction": BUILT_SUFFIX.sub("", description),
        "list": [
            {
                "version": "current",
                "desc": "Current build from the default branch.",
                "path": preview_url,
                "status": "ci-build",
                "fhirversion": fhir_versions[0],
            },
            *releases,
        ],
    }


def render_history(package_history: dict[str, Any], package_url: str) -> str:
    rows: list[str] = []
    for release in package_history["list"]:
        version = html.escape(str(release["version"]))
        status = html.escape(str(release["status"]))
        description = html.escape(str(release["desc"]))
        path = html.escape(str(release["path"]), quote=True)
        rows.append(
            f'<tr><td><a href="{path}/">{version}</a></td>'
            f"<td>{status}</td><td>{description}</td></tr>"
        )
    title = html.escape(str(package_history["title"]))
    canonical = html.escape(str(package_history["canonical"]))
    package_link = html.escape(package_url, quote=True)
    has_release = any(entry.get("version") != "current" for entry in package_history["list"])
    summary = (
        "Released versions are immutable. The current entry tracks the latest build."
        if has_release
        else "The current entry tracks the latest build. Versioned releases will appear here."
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Publication history</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    body {{ margin: 0 auto; max-width: 70rem; padding: 3rem 1.25rem; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #9996; padding: .75rem; text-align: left; vertical-align: top; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <main>
    <h1>{title} publication history</h1>
    <p>{summary}</p>
    <p>Canonical root: <code>{canonical}</code></p>
    <table>
      <thead><tr><th>Version</th><th>Status</th><th>Description</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <p><a href="{package_link}">Download the current package</a> ·
      <a href="package.tgz.sha256">SHA-256 checksum</a> ·
      <a href="package-list.json">Machine-readable package list</a></p>
  </main>
</body>
</html>
"""


def render_preview_redirect(title: str, canonical: str) -> str:
    escaped_title = html.escape(title)
    escaped_canonical = html.escape(canonical, quote=True)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=ci-build/">
<link rel="canonical" href="{escaped_canonical}">
<title>{escaped_title} current build</title></head>
<body><p>Open the
<a href="ci-build/">current build</a> or the
<a href="history.html">publication history</a>.</p></body></html>
"""


def load_redirect_generator(repository_root: Path) -> Any:
    script = repository_root / "tools/make-canonical-redirects.py"
    specification = importlib.util.spec_from_file_location("canonical_redirects", script)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {script}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def safe_site_output(site: Path, repository_root: Path) -> Path:
    """Reject output aliases before any recursive deletion or publication write."""
    lexical_repository = Path(os.path.abspath(repository_root))
    lexical_site = Path(os.path.abspath(site))
    if lexical_site == lexical_repository or not lexical_site.is_relative_to(
        lexical_repository
    ):
        raise ValueError("site output must be a dedicated directory below the repository")
    current = lexical_repository
    for component in lexical_site.relative_to(lexical_repository).parts:
        current = current / component
        if current.is_symlink():
            raise ValueError(f"site output path may not traverse a symlink: {current}")
        if current.exists() and not current.is_dir():
            raise ValueError(f"site output path component is not a directory: {current}")
    resolved_site = lexical_site.resolve(strict=False)
    resolved_repository = lexical_repository.resolve()
    if resolved_site == resolved_repository or not resolved_site.is_relative_to(
        resolved_repository
    ):
        raise ValueError("site output escapes the repository")
    return resolved_site


def prepare_guide(
    stage: Path,
    repository_root: Path,
    source: str,
    public_urls: dict[str, str],
    source_url: str,
    canonical: str,
    history_url: str,
    source_date_epoch: int,
    canonical_public_urls: dict[str, str] | None = None,
) -> None:
    # package.db is Publisher's local package-cache database. It is not part of
    # an IG publication and embeds absolute build paths, so it must never reach
    # the public site or an alias.
    (stage / "package.db").unlink(missing_ok=True)

    for path in stage.rglob("*"):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            rewritten = replace_build_locations(text, repository_root, public_urls, source_url)
            rewritten = rewritten.replace(f"{canonical}/history.html", history_url)
            rewritten = rewritten.replace("Local Development build", "Continuous Build")
            if canonical_public_urls and path.suffix == ".html":
                rewritten = rewrite_authored_canonical_links(rewritten, canonical_public_urls)
            path.write_text(rewritten, encoding="utf-8")

    for archive in stage.glob("package*.tgz"):
        rewrite_package_archive(
            archive,
            canonical,
            source_date_epoch,
            repository_root=repository_root,
            public_urls=public_urls,
            source_url=source_url,
        )

    leaked_locations: list[str] = []
    for path in stage.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        try:
            validate_portable_text(
                text, f"{source}:{path.relative_to(stage)}", path.suffix
            )
        except ValueError:
            leaked_locations.append(str(path.relative_to(stage)))
    if leaked_locations:
        raise RuntimeError(
            f"local filesystem locations remain in {source}: "
            + ", ".join(leaked_locations[:10])
        )


def assemble_site(
    site: Path,
    repository_root: Path,
    configuration: dict[str, Any],
    base_url: str,
    revision: str,
    source_date_epoch: int,
    published_root: Path | None = None,
) -> None:
    site = safe_site_output(site, repository_root)
    repository_root = repository_root.resolve()

    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    (site / ".nojekyll").touch()

    catalog_source = repository_root / "catalog"
    if catalog_source.is_dir():
        catalog_destination = site / "catalog"
        catalog_destination.mkdir()
        for catalog_file in sorted(catalog_source.glob("*.json")):
            shutil.copy2(catalog_file, catalog_destination / catalog_file.name)

    if published_root is not None:
        published_root = published_root.resolve()
        published_fhir = published_root / "fhir"
        if published_fhir.exists():
            for path in published_fhir.rglob("*"):
                if path.is_symlink():
                    raise ValueError(f"published site contains a symbolic link: {path}")
            shutil.copytree(published_fhir, site / "fhir", dirs_exist_ok=True)

    if configuration.get("releaseMode") == "ci-build-only":
        for guide in configuration["guides"]:
            canonical_root = site / safe_relative_path(
                guide["canonicalPath"], "canonicalPath"
            )
            if canonical_root.exists():
                if canonical_root.is_dir():
                    shutil.rmtree(canonical_root)
                else:
                    canonical_root.unlink()

    guides = configuration["guides"]
    public_urls = {
        guide["source"]: f"{base_url}/{guide['canonicalPath']}/ci-build"
        for guide in guides
    }
    canonical_base = str(configuration["canonicalBaseUrl"]).rstrip("/")
    canonical_public_urls = {
        f"{canonical_base}/{guide['canonicalPath']}": public_urls[guide["source"]]
        for guide in guides
    }
    # History pages live at each guide root, not under ci-build; the longer key
    # wins over the guide prefix during longest-first replacement.
    for guide in guides:
        canonical_public_urls[
            f"{canonical_base}/{guide['canonicalPath']}/history.html"
        ] = f"{base_url}/{guide['canonicalPath']}/history.html"
    canonical_public_urls[f"{canonical_base}/catalog/"] = f"{base_url}/catalog/"
    source_url = f"{configuration['sourceRepository']}/tree/{revision}"
    redirect_generator = load_redirect_generator(repository_root)

    with tempfile.TemporaryDirectory(prefix="grove-fhir-pages-", dir=site.parent) as temp:
        staging_root = Path(temp)
        for guide in guides:
            source = guide["source"]
            source_path = safe_relative_path(source, "guide source")
            output = repository_root / source_path / "output"
            if not (output / "index.html").is_file() or not (output / "package.tgz").is_file():
                raise FileNotFoundError(f"{source}/output is not a complete Publisher build")

            canonical_path = safe_relative_path(guide["canonicalPath"], "canonicalPath")
            stage = staging_root / source
            shutil.copytree(output, stage)
            metadata = read_package_metadata(stage / "package.tgz")
            canonical = metadata.get("canonical")
            if not isinstance(canonical, str):
                raise ValueError(f"{source} package has no canonical URL")
            expected_canonical = (
                f"{str(configuration['canonicalBaseUrl']).rstrip('/')}/"
                f"{guide['canonicalPath']}"
            )
            if canonical.rstrip("/") != expected_canonical:
                raise ValueError(
                    f"{source} canonical {canonical!r} does not match configured "
                    f"canonical {expected_canonical!r}"
                )

            preview_url = public_urls[source]
            history_url = f"{base_url}/{guide['canonicalPath']}/history.html"
            prepare_guide(
                stage,
                repository_root,
                source,
                public_urls,
                source_url,
                canonical,
                history_url,
                source_date_epoch,
                canonical_public_urls,
            )
            metadata = read_package_metadata(stage / "package.tgz")
            if metadata.get("url") != canonical:
                raise ValueError(f"{source} package URL must equal its canonical URL")

            canonical_root = site / canonical_path
            preview_destination = canonical_root / "ci-build"
            canonical_root.mkdir(parents=True, exist_ok=True)
            published_history: dict[str, Any] | None = None
            if (canonical_root / "package-list.json").is_file():
                published_history = json.loads(
                    (canonical_root / "package-list.json").read_text(encoding="utf-8")
                )
            if preview_destination.exists():
                shutil.rmtree(preview_destination)
            shutil.copytree(stage, preview_destination)

            release_entries = [] if published_history is None else [
                entry
                for entry in published_history.get("list", [])
                if entry.get("version") != "current"
            ]
            routes: list[dict[str, object]] = []
            if not release_entries:
                routes = redirect_generator.generate_routes(
                    output=stage,
                    site=canonical_root,
                    canonical=canonical,
                    target_prefix="ci-build",
                )

            history = package_list(metadata, preview_url, published_history)
            write_json(canonical_root / "package-list.json", history)
            (canonical_root / "history.html").write_text(
                render_history(history, f"{base_url}/{guide['canonicalPath']}/package.tgz"),
                encoding="utf-8",
            )
            ci_digest = sha256(stage / "package.tgz")
            ci_manifest = {
                "schemaVersion": 1,
                "packageId": metadata["name"],
                "packageVersion": metadata["version"],
                "canonical": canonical,
                "preview": preview_url,
                "sourceRevision": revision,
                "sourceDate": datetime.fromtimestamp(
                    source_date_epoch, tz=timezone.utc
                ).isoformat().replace("+00:00", "Z"),
                "packageSha256": ci_digest,
                "canonicalRouteCount": len(routes),
            }
            (preview_destination / "package.tgz.sha256").write_text(
                f"{ci_digest}  package.tgz\n", encoding="utf-8"
            )
            write_json(preview_destination / "publication-manifest.json", ci_manifest)
            if not release_entries:
                (canonical_root / "index.html").write_text(
                    render_preview_redirect(str(metadata["title"]), canonical), encoding="utf-8"
                )
                shutil.copy2(stage / "package.tgz", canonical_root / "package.tgz")
                (canonical_root / "package.tgz.sha256").write_text(
                    f"{ci_digest}  package.tgz\n", encoding="utf-8"
                )
                write_json(canonical_root / "publication-manifest.json", ci_manifest)

            publication_files = (
                "package-list.json",
                "history.html",
            )
            for alias in guide.get("aliases", []):
                alias_path = safe_relative_path(alias, "alias", allow_empty=True)
                alias_root = site / alias_path
                alias_root.mkdir(parents=True, exist_ok=True)
                shutil.copytree(stage, alias_root, dirs_exist_ok=True)
                for filename in publication_files:
                    shutil.copy2(canonical_root / filename, alias_root / filename)
                (alias_root / "package.tgz.sha256").write_text(
                    f"{ci_digest}  package.tgz\n", encoding="utf-8"
                )
                write_json(alias_root / "publication-manifest.json", ci_manifest)

    for retired in configuration.get("retiredPreviewPaths", []):
        retired_path = site / safe_relative_path(retired, "retiredPreviewPath")
        if retired_path.exists():
            if retired_path.is_dir():
                shutil.rmtree(retired_path)
            else:
                retired_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--revision")
    parser.add_argument("--source-date-epoch", type=int)
    parser.add_argument("--published-root", type=Path)
    arguments = parser.parse_args()

    repository_root = arguments.repository_root.resolve()
    configuration = load_configuration(arguments.config.resolve())
    base_url = (arguments.base_url or configuration["previewBaseUrl"]).rstrip("/")
    revision = arguments.revision or git_value(repository_root, "%H")
    source_date_epoch = arguments.source_date_epoch
    if source_date_epoch is None:
        source_date_epoch = int(git_value(repository_root, "%ct"))
    assemble_site(
        arguments.site,
        repository_root,
        configuration,
        base_url,
        revision,
        source_date_epoch,
        arguments.published_root,
    )
    print(f"Assembled GitHub Pages site at {arguments.site.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
