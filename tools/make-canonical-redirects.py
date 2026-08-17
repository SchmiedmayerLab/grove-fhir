#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

"""Generate the canonical-URL redirect tree for static hosting of a FHIR IG ci-build.

Only needed when serving a raw `output/` directory at the canonical root. Milestone
publications made with the IG Publisher's -go-publish mode generate their own redirect
tree (use "server": "cloud" in publish-setup.json for static-host HTML redirects).

The IG Publisher emits flat files (StructureDefinition-<id>.html/.json/...). FHIR
canonicals are directory-shaped (<base>/StructureDefinition/<id>), so a static host
needs a page at each canonical path redirecting humans to the rendered page. Machines
do not fetch canonicals over HTTP — they resolve definitions from the NPM package
(package.tgz / a package registry) — so an HTML meta-refresh suffices; no content
negotiation is required.

Usage: make-canonical-redirects.py <ig-output-dir> [<site-dir>]
"""
import json
import pathlib
import shutil
import sys

out = pathlib.Path(sys.argv[1]).resolve()
site = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else out

REDIRECT = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
<title>{title}</title></head>
<body><p>This is the canonical URL of a FHIR artifact. Its human-readable rendering
lives at <a href="{target}">{target}</a>. Machine-readable forms: replace <code>.html</code>
with <code>.json</code>, <code>.xml</code>, or <code>.ttl</code>; the full package is
<a href="{root}package.tgz">package.tgz</a>.</p></body></html>
"""

TYPES = {
    "StructureDefinition", "CodeSystem", "ValueSet", "ImplementationGuide",
    "CapabilityStatement", "OperationDefinition", "SearchParameter",
    "Questionnaire", "Observation", "Patient", "Device", "Provenance",
}

made = 0
for f in sorted(out.glob("*.json")):
    name = f.name
    if "-" not in name or name.startswith((".", "qa", "expansions", "usage-stats")):
        continue
    rtype, _, rest = name.partition("-")
    rid = rest[:-5]
    if rtype not in TYPES or not (out / f"{rtype}-{rid}.html").exists():
        continue
    dest = site / rtype / rid
    dest.mkdir(parents=True, exist_ok=True)
    root = "../" * len(dest.relative_to(site).parts)
    (dest / "index.html").write_text(
        REDIRECT.format(target=f"{root}{rtype}-{rid}.html", title=f"{rtype}/{rid}", root=root)
    )
    shutil.copyfile(f, dest / f"{rid}.json")
    made += 1

# special-url artifacts (canonical deviates from <base>/<Type>/<id>) live deeper:
for f in sorted(out.glob("StructureDefinition-*.json")):
    try:
        d = json.loads(f.read_text())
    except Exception:
        continue
    url, rid = d.get("url", ""), d.get("id", "")
    tail = url.split("/StructureDefinition/", 1)[-1] if "/StructureDefinition/" in url else ""
    if "/" not in tail:
        continue
    dest = site / "StructureDefinition" / tail
    dest.mkdir(parents=True, exist_ok=True)
    root = "../" * len(dest.relative_to(site).parts)
    (dest / "index.html").write_text(
        REDIRECT.format(target=f"{root}StructureDefinition-{rid}.html", title=f"StructureDefinition/{tail}", root=root)
    )
    shutil.copyfile(f, dest / f"{tail.rsplit('/', 1)[-1]}.json")
    made += 1

print(f"generated {made} canonical redirect entries under {site}")
