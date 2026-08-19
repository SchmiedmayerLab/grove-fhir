<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Publication

Grove FHIR currently publishes one mutable pre-1.0 continuous build. No release exists.

## Continuous preview

Every default-branch build replaces `ci-build` for all active guides at their current
pre-1.0 canonical paths:

| Package | Mutable preview | Publication metadata |
|---|---|---|
| `org.grovealliance.fhir.mobile` | `/fhir/mobile/ci-build/` | `/fhir/mobile/package-list.json` and `/fhir/mobile/history.html` |
| `org.grovealliance.fhir.healthkit` | `/fhir/healthkit/ci-build/` | `/fhir/healthkit/package-list.json` and `/fhir/healthkit/history.html` |
| `org.grovealliance.fhir.health-connect` | `/fhir/health-connect/ci-build/` | `/fhir/health-connect/package-list.json` and `/fhir/health-connect/history.html` |
| `org.grovealliance.fhir.questionnaire` | `/fhir/questionnaire/ci-build/` | `/fhir/questionnaire/package-list.json` and `/fhir/questionnaire/history.html` |

The GitHub Pages locations at `/`, `/healthkit/`, `/health-connect/`, and `/questionnaire/` are reader-friendly aliases. Each
publication root also exposes the package, its SHA-256 checksum, and HTML plus JSON, XML, and Turtle
routes for every locally owned canonical resource. `publication/config.json` is the single routing
configuration, and `npm run pages:build` verifies the assembled surface before deployment.

GitHub Pages is both the publication host and canonical base during pre-1.0 development. The
canonical base will move only through an explicit breaking-change review before the first stable
release. Deployment checks exercise every canonical route on the Pages host.

Only the latest `ci-build` is deployed during pre-1.0 development. The site does not retain
pre-1.0 version directories, superseded packages, or legacy documentation surfaces.

## Future immutable releases

Immutable-release tooling is present but dormant. It may be activated only through an explicit,
reviewed decision to publish a release. The activation change must update `releaseMode` and its
repository validation in the same pull request. At that point, rendered releases would live on the
orphan `publication` branch under `/fhir/<package>/<version>/`; `Scripts/publish-version.py` refuses
to overwrite an existing version. The default-branch Pages build can overlay that branch, add the
current `/ci-build/`, and regenerate the combined history page. Versionless canonical routes would
then reference the last accepted release rather than a newer CI build.

Activating and publishing an immutable release requires a dedicated reviewed PR and all of the
following:

1. The canonical host resolves over HTTPS and passes the live publication check.
2. The guide contains a reviewed `publication-request.json` whose package ID, version, and path agree
   with `sushi-config.yaml`.
3. The release commit is approved, merged, and tagged. Dependencies use exact versions.
4. `Scripts/build-release.sh <mobile|healthkit|health-connect|questionnaire>` builds once in FHIR Publisher publication mode.
5. `Scripts/publish-version.py` adds that exact output to a clean checkout of the `publication`
   branch. The resulting package, QA report, release notes, and checksums are attached to the matching
   GitHub Release.
6. The publication change is reviewed before the protected branch and Pages environment are updated.

The promotion tool rejects local build paths, CI-only package metadata, invalid versions, mismatched
canonicals, duplicate history entries, and an existing version directory. Release automation may wrap
these commands later, but it must preserve the same review and immutability gates.
