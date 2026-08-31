<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Naming and versioning conventions

Grove FHIR publishes contracts, not code.
A name that reaches a database, a serialized payload, or another team's source tree is part of the contract, and the cost of changing it is paid by everyone who stored it.
These conventions say when a name may still change and how a client is expected to depend on one.

## Persisted identifiers are named once

A persisted identifier is any name that outlives the process that produced it: a canonical URL, a CodeSystem or ValueSet URL, an extension URL, a `linkId`, a storage key or key prefix, a schema version, an identity component name, a diagnostic rule code, a package id.

Name each one once.
Rename it only with a migration that reads both spellings for a stated period, or with a recorded statement that no data exists under the old name.
Record whichever applies in the pull request that performs the rename; a rename with neither is not admitted.

Two consequences follow.
A name is worth arguing about before it ships and not after, so review the spelling when the identifier is introduced.
An asymmetry that survives review is deliberate: if two sibling artifacts are named differently on purpose, say why in the artifact's own description rather than leaving a reader to guess.

`healthkit-source-type-extension` became `healthkit-source-type` in 0.6.0 under the no-shipping-data statement: publication is CI-build-only, no immutable release had been cut, and the HealthKit CodeSystem and ValueSet already shared the plain id, so the suffix never bought uniqueness.
This was the last free window for that name.

## Clients pin tagged releases

The canonical namespace `https://grovealliance.org/fhir` is an identifier, not a download location, and the CI-build preview is not release history.
An implementation depends on a Grove FHIR **tag**: it resolves the exact package version from `catalog/release-manifest.json`, verifies the published checksum, and records the source revision it built against.
Nothing depends on `main`, on a branch build, or on a versionless preview route.

The catalogs are the machine-readable half of the same contract.
A client generating code from `catalog/` reads it out of the tagged source revision whose packages it also installed, so its generated types and the profiles it validates against always come from one release.

## 0.6.0 is the first artifact of this policy

The `0.6.0` tag of this repository and the matching `0.6.0` tags of the Grove client repositories are the first releases published under these conventions.
Every identifier they carry is now a named-once identifier: from this tag forward a rename needs its migration or its no-data statement, and a client that pins the tag is entitled to rely on the spelling.

[PUBLICATION.md](PUBLICATION.md) documents how a release is built, verified, and published.
