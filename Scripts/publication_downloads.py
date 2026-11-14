"""Separate Publisher bulk downloads from the static website without changing their bytes."""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit


def redirect_page(target: str) -> str:
    """Static-host fallback plus a browser redirect preserving queries and anchors."""
    escaped = html.escape(target, quote=True)
    script_target = json.dumps(target).replace("<", "\\u003c")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>Page moved</title>'
            f'<link rel="canonical" href="{escaped}">'
            f'<meta http-equiv="refresh" content="0;url={escaped}">'
            f'<script>location.replace({script_target} + location.search + location.hash);</script>'
            f'</head><body><p>This page has moved. <a href="{escaped}">Continue</a>.</p></body></html>\n')


def offload_downloads(site: Path, destination: Path, *, public_url: str,
                      asset_prefix: str = "", release_url: str | None = None,
                      run_url: str | None = None,
                      excluded_directories: set[str] | None = None) -> list[dict]:
    """Offload ZIP and legacy Validator bundles; retain every individual resource/package.

    Called only on disposable assembled output. Development links explain how to
    retrieve the matching run artifact; release links resolve to immutable assets.
    """
    excluded = excluded_directories or set()
    files = sorted(p for p in site.rglob("*")
                   if p.is_file() and p.relative_to(site).parts[0] not in excluded)
    bundles = [p for p in files if p.suffix in {".zip", ".pack"}]
    if not bundles:
        return []
    rows = []
    names = set()
    for path in bundles:
        relative = path.relative_to(site).as_posix()
        asset = asset_prefix + relative.replace("/", "__") if release_url else relative
        if asset in names:
            raise ValueError(f"bulk asset name collision: {asset}")
        names.add(asset)
        target = destination / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError(f"bulk asset already exists: {target}")
        shutil.copy2(path, target)
        with path.open("rb") as original:
            digest = hashlib.file_digest(original, "sha256").hexdigest()
        with target.open("rb") as copied:
            if hashlib.file_digest(copied, "sha256").hexdigest() != digest:
                raise ValueError(f"bulk asset copy failed: {relative}")
        rows.append({"path": relative, "asset": asset, "bytes": path.stat().st_size,
                     "sha256": digest,
                     "url": f"{release_url}/{quote(asset)}" if release_url else None})
        path.unlink()

    by_url = {urljoin(public_url.rstrip("/") + "/", quote(row["path"])): row for row in rows}
    for page in (p for p in files if p.suffix == ".html"):
        relative = page.relative_to(site).as_posix()
        page_url = urljoin(public_url.rstrip("/") + "/", quote(relative))
        landing = posixpath.relpath("bulk-downloads.html", posixpath.dirname(relative) or ".")

        changed_link = False

        def replace_link(match: re.Match) -> str:
            nonlocal changed_link
            original = html.unescape(match[2])
            resolved = urlsplit(urljoin(page_url, original))
            clean = resolved._replace(query="", fragment="").geturl()
            row = by_url.get(clean)
            if row is None:
                return match[0]
            changed_link = True
            target = row["url"] or f'{landing}#{quote(row["path"], safe="")}'
            return f'{match[1]}{html.escape(target, quote=True)}{match[3]}'

        def replace_tag(match: re.Match) -> str:
            nonlocal changed_link
            changed_link = False
            tag = re.sub(r'''(\bhref\s*=\s*["'])([^"']*)(["'])''', replace_link, match[0], flags=re.I)
            if changed_link and not release_url:
                # The preview target is an instruction page, not a downloadable archive.
                tag = re.sub(r'''\s+download(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?(?=\s|/?>)''',
                             "", tag, flags=re.I)
            return tag

        text = page.read_text(encoding="utf-8")
        text = re.sub(r"<(?:a|area|link)\b[^>]*>", replace_tag, text, flags=re.I)
        if page.name == "index.html":
            text = re.sub(r"</body\s*>", lambda m: (
                f'<p><a href="{landing}">Bulk downloads</a></p>' + m[0]), text, count=1, flags=re.I)
        page.write_text(text, encoding="utf-8")

    if release_url:
        explanation = "These unchanged Publisher bundles are hosted as assets of this version's GitHub Release."
    elif run_url:
        explanation = (f'Download the <strong>fhir-bulk-downloads</strong> artifact from '
                       f'<a href="{html.escape(run_url, quote=True)}#artifacts">this build run</a>. '
                       'GitHub sign-in is required. Artifacts expire after 14 days; '
                       'use a newer preview or a published release after expiry. '
                       'The artifact contains one folder per guide, with the original filenames.')
    else:
        explanation = ('Local build: bundles are in <code>.build/pages-downloads/</code>, '
                       'in one folder per guide. CI previews link to their matching build artifact.')
    items = "".join(
        f'<tr id="{html.escape(row["path"], quote=True)}"><td>'
        + (f'<a href="{html.escape(row["url"], quote=True)}">{html.escape(row["path"])}</a>'
           if row["url"] else html.escape(row["path"]))
        + f'</td><td>{row["bytes"]:,}</td><td><code>{row["sha256"]}</code></td></tr>' for row in rows)
    (site / "bulk-downloads.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Bulk downloads</title></head><body><h1>Bulk downloads</h1>'
        f'<p>{explanation}</p><p><a href="index.html">Guide home</a> · '
        '<a href="package.tgz">FHIR package</a> · <a href="bulk-downloads.json">Download manifest</a></p>'
        '<p>Individual FHIR resources and packages remain available on this site.</p>'
        '<table><thead><tr><th>File</th><th>Bytes</th><th>SHA-256</th></tr></thead>'
        f'<tbody>{items}</tbody></table></body></html>\n', encoding="utf-8")
    (site / "bulk-downloads.json").write_text(json.dumps(
        {"schemaVersion": 1, "runUrl": run_url, "files": rows}, indent=2) + "\n", encoding="utf-8")
    return rows
