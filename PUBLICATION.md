<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Publication

Grove FHIR separates mutable previews from reviewed releases. No release currently exists.

## Continuous preview

Every default-branch build publishes both active guides under their future canonical paths:

| Package | Mutable preview | Publication metadata |
|---|---|---|
| `org.grovealliance.fhir.core` | `/fhir/core/ci-build/` | `/fhir/core/package-list.json` and `/fhir/core/history.html` |
| `org.grovealliance.fhir.platforms` | `/fhir/platforms/ci-build/` | `/fhir/platforms/package-list.json` and `/fhir/platforms/history.html` |

The current GitHub Pages locations at `/` and `/platforms/` remain compatibility aliases. Each
publication root also exposes the package, its SHA-256 checksum, and HTML plus JSON, XML, and Turtle
routes for every locally owned canonical resource. `publication/config.json` is the single routing
configuration, and `npm run pages:build` verifies the assembled surface before deployment.

GitHub Pages is the draft host. It does not make `grovealliance.org` authoritative. The repository
variable `FHIR_CANONICAL_BASE_URL` must remain unset until DNS, TLS, and GitHub Pages custom-domain
configuration are complete. Once set, deployment checks exercise the canonical host as well as the
Pages preview.

## Immutable releases

Rendered releases live on the orphan `publication` branch, separate from source. A release is added
under `/fhir/<package>/<version>/`; `Scripts/publish-version.py` refuses to overwrite an existing
directory. The default-branch Pages build overlays that branch, adds the current `/ci-build/`, and
regenerates the combined history page. Versionless canonical routes continue to reference the last
accepted release, not a newer CI build.

Publishing requires a dedicated reviewed PR and all of the following:

1. The canonical host resolves over HTTPS and passes the live publication check.
2. The guide contains a reviewed `publication-request.json` whose package ID, version, and path agree
   with `sushi-config.yaml`.
3. The release commit is approved, merged, and tagged. Dependencies use exact versions.
4. `Scripts/build-release.sh <ig|platforms>` builds once in FHIR Publisher publication mode.
5. `Scripts/publish-version.py` adds that exact output to a clean checkout of the `publication`
   branch. The resulting package, QA report, release notes, and checksums are attached to the matching
   GitHub Release.
6. The publication change is reviewed before the protected branch and Pages environment are updated.

The promotion tool rejects local build paths, CI-only package metadata, invalid versions, mismatched
canonicals, duplicate history entries, and an existing version directory. Release automation may wrap
these commands later, but it must preserve the same review and immutability gates.
