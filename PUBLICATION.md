<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Publication

Grove FHIR currently publishes one mutable pre-1.0 continuous preview. No immutable
release exists. Version 0.2.0 is the package contract used by the coordinated
implementation pull requests.

## Continuous preview

Every default-branch build replaces `ci-build` for all active guides at their current
pre-1.0 canonical paths:

| Package | Mutable preview | Publication metadata |
|---|---|---|
| `org.grovealliance.fhir.mobile` | `/fhir/mobile/ci-build/` | `/fhir/mobile/package-list.json` and `/fhir/mobile/history.html` |
| `org.grovealliance.fhir.sensor` | `/fhir/sensor/ci-build/` | `/fhir/sensor/package-list.json` and `/fhir/sensor/history.html` |
| `org.grovealliance.fhir.sensorkit` | `/fhir/sensorkit/ci-build/` | `/fhir/sensorkit/package-list.json` and `/fhir/sensorkit/history.html` |
| `org.grovealliance.fhir.healthkit` | `/fhir/healthkit/ci-build/` | `/fhir/healthkit/package-list.json` and `/fhir/healthkit/history.html` |
| `org.grovealliance.fhir.health-connect` | `/fhir/health-connect/ci-build/` | `/fhir/health-connect/package-list.json` and `/fhir/health-connect/history.html` |
| `org.grovealliance.fhir.providers` | `/fhir/providers/ci-build/` | `/fhir/providers/package-list.json` and `/fhir/providers/history.html` |
| `org.grovealliance.fhir.questionnaire` | `/fhir/questionnaire/ci-build/` | `/fhir/questionnaire/package-list.json` and `/fhir/questionnaire/history.html` |

The GitHub Pages locations at `/`, `/sensor/`, `/sensorkit/`, `/healthkit/`,
`/health-connect/`, `/providers/`, and `/questionnaire/` are reader-friendly
preview aliases. Each
publication root also exposes the package, its SHA-256 checksum, and HTML plus JSON, XML, and Turtle
routes for every locally owned canonical resource. `publication/config.json` is the single routing
configuration, and `npm run pages:build` verifies the assembled surface before deployment.
That command creates the guide-only local preview. Producer repositories validate
their own emitted resources with the producer-neutral kit; Grove FHIR does not fetch,
patch, build, or attest those repositories.

The canonical namespace is `https://grovealliance.org/fhir`; hosting that namespace is
deliberately out of scope for this iteration. GitHub Pages is only the mutable preview
host. Deploying or redirecting the canonical host requires a separate reviewed change.

Only the latest `ci-build` is deployed during pre-1.0 development. The site does not retain
pre-1.0 version directories, superseded packages, or legacy documentation surfaces.

## Offline terminology reproducibility

Publisher and Validator runs are pinned to FHIR R4 4.0.1 and execute without network
access. No generated terminology transaction is tracked or redistributed, and Grove
does not publish or version an external IANA, LOINC, UCUM, or ISO/IEEE CodeSystem.
External terminology and language diagnostics that the offline Publisher cannot resolve
are reviewed only through exact resource-scoped messages in each guide's
`ignoreWarnings.txt`; the QA gate requires every configured message to be exercised
exactly once and rejects any unconfigured suppression.

The QA ledger reports three separate values for each severity: raw Publisher findings,
exact-suppressed findings, and unsuppressed findings. Readiness requires zero
unsuppressed errors and warnings. Two pinned Publisher/dependency defect families remain
visible in the raw error count:

- with `-tx n/a`, Publisher 2.3.2 can raise the exact `tc is null` error while checking
  the required R4 MIME binding on the published raw-recording examples; and
- SDC 4.0.0 generates definition-table links to retired anchors in that frozen
  dependency's own `2025Jan` pages.

The MIME errors are accepted only when the resource path, element path, MIME code,
ValueSet version, and complete diagnostic all match once. The SDC errors are accepted
only at the exact generated profile, DOM path, line, column, anchor, and link text. The
documentation never describes either build as having zero raw errors. FSH, package,
catalog, and producer-corpus tests enforce the normative codes and units independently.
A suppressed offline lookup diagnostic neither replaces a terminology license nor
grants access to an attachment.

## Moving an adapter to a new platform baseline

Each adapter catalog enumerates a platform's source concepts exactly, and
`*/input/data/*-inventory.json` records what the platform published when the catalog was
frozen. `Tests/test_platform_inventory.py` holds the two to each other offline, and
`Scripts/build-release.sh` re-reads the platforms before publishing, so an inventory that
drifts cannot reach a release.

A new SDK or artifact version is a version change, not an in-place edit:

1. Point the baseline at the new platform — `source.sdkBaseline` for the Apple catalogs,
   `source.version` for `catalog/health-connect-adapter.json`.
2. `npm run inventory:refresh` to re-record the evidence.
3. `npm run inventory:verify-sdk` on a Mac, which cross-checks the Apple evidence against
   the installed SDK headers and re-hashes the recorded header inputs.
4. Reconcile each catalog against the regenerated evidence; the expected counts in
   `Tests/test_platform_inventory.py` move with it.
5. Refresh `healthkit/input/data/terminology-provenance.json` and every count stated in
   guide prose, then `python3 Scripts/render-adapter-source-terminology.py` and
   `python3 Scripts/render-status-matrices.py`.

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
4. `Scripts/build-release.sh <guide>` builds once in FHIR Publisher publication mode.
5. `Scripts/publish-version.py` adds that exact output to a clean checkout of the `publication`
   branch. The resulting package, QA report, release notes, and checksums are attached to the matching
   GitHub Release.
6. The publication change is reviewed before the protected branch and Pages environment are updated.

The promotion tool rejects local build paths, CI-only package metadata, invalid versions, mismatched
canonicals, duplicate history entries, and an existing version directory. Release automation may wrap
these commands later, but it must preserve the same review and immutability gates.
