<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Publication and release evidence

The Grove FHIR Implementation Guides are release candidates, not yet immutable canonical publications.
The ten guides use canonical URLs under `https://grovealliance.org/fhir`, but that host is not yet operated as the permanent publication origin.
Until ownership, HTTPS availability, retention, and correction governance are approved, `publication/config.json` deliberately keeps `releaseMode: ci-build-only` and the canonical host must not be described as live.

## Mutable preview

Default-branch builds replace one reader-facing preview for each package:

| Package | Preview |
|---|---|
| `org.grovealliance.fhir.mobile` | `/mobile/ci-build/` |
| `org.grovealliance.fhir.questionnaire` | `/questionnaire/ci-build/` |
| `org.grovealliance.fhir.sensor` | `/sensor/ci-build/` |
| `org.grovealliance.fhir.sensorkit` | `/sensorkit/ci-build/` |
| `org.grovealliance.fhir.healthkit` | `/healthkit/ci-build/` |
| `org.grovealliance.fhir.health-connect` | `/health-connect/ci-build/` |
| `org.grovealliance.fhir.providers` | `/providers/ci-build/` |
| `org.grovealliance.fhir.withings` | `/withings/ci-build/` |
| `org.grovealliance.fhir.oura` | `/oura/ci-build/` |
| `org.grovealliance.fhir.google-health` | `/google-health/ci-build/` |

These paths are relative to `https://schmiedmayerlab.github.io/grove-fhir`.
Versionless aliases are previews, not canonical resource URLs and not immutable release history. `publication/config.json` is the sole route inventory; `npm run pages:build` and `Scripts/check-publication.py` verify it.

## Release-candidate evidence

`Scripts/build-release.sh` performs an explicit two-phase release-candidate build for all ten guides from one clean checked-out revision.
The first phase is network-enabled and bootstraps the integrity-locked npm and Bundler closures plus the SHA-256-pinned Publisher, Validator, template, and external FHIR package archives.
The second phase reconstructs or verifies each closure with `npm ci --offline`, `bundle install --local`, and `download-fhir-tools.sh --offline`, then runs Publisher with `-tx n/a -no-network`.
A missing or altered bootstrap input fails the second phase; it cannot be downloaded on demand.

After building the previews, executing repository and Publisher QA gates, and running the producer and Questionnaire corpora through the exact official FHIR Validator, the script calls `Scripts/collect-release-evidence.py`.
The collector requires a clean source tree, validates every input before copying, refuses any existing output path, and emits:

- every exact-version FHIR package;
- Publisher `qa.json` and `qa.html` for every guide;
- the release manifest and Mobile semantic snapshot;
- a deterministic `grove-fhir-machine-contracts-<version>.tar.gz` and its machine-readable index;
- source revision, release/FHIR versions, pinned toolchain, observed runtime versions, lane, and raw QA metadata; and
- `SHA256SUMS` over every evidence artifact.

The machine-contract archive contains every JSON catalog and catalog schema (including every instance and schema listed by `normativeCatalogs` plus local terminology evidence), every Mobile exchange/semantic corpus index and base resource, and every Questionnaire structural/paired-validation index and base resource.
Archive paths are sorted; tar ownership, modes, and timestamps and the gzip timestamp are fixed.
The embedded index binds every entry's path, byte size, and SHA-256 digest to the release version and source revision.
This is the complete language-neutral contract input for producer CI, not a selection of representative files.

The Deployment workflow can only be dispatched manually from the default branch.
It has no `release: published` entry point and cannot accept an already-public release as validation input.
It verifies the source and evidence while no release tag exists, then creates the tag and public GitHub Release as its final two mutations.
Tag creation is an atomic Git-ref API call bound to the verified source SHA; it fails if the name appeared during the build.
Release creation then requires that exact pre-existing tag.
Every asset is uploaded while the release remains a draft, and only a successful complete upload is edited to public/latest.
A release-service failure may therefore leave a verified orphan tag or draft, which deliberately reserves the version for investigation instead of deleting or silently reusing it.
Existing tags/releases are never uploaded to, replaced, or clobbered.
These attachments are release-candidate evidence only; they do not make GitHub Pages the canonical publication host.

## Two validation lanes

The lanes are deliberately distinct and must never silently fall back into one another:

1. `offline-structural` begins only after the explicit online bootstrap.
   It consumes the verified Publisher, Validator, template, npm/Bundler closure, external FHIR packages, and locally built Grove dependency packages without dependency resolution over the network.
   Publisher uses FHIR R4 4.0.1 and `-tx n/a -no-network`.
   The lane proves structure, package closure, generated artifacts, local terminology pins, examples, producer corpora, and exact QA suppressions.
   It cannot make a live terminology-server claim.
2. `online-terminology` is an accountable validation performed with the manifest-pinned FHIR Validator against an explicitly approved terminology endpoint.
   Its evidence must satisfy the closed `catalog/schemas/terminology-evidence.schema.json` before it is copied.
   The record binds the exact source revision and every built package checksum to the Validator version/checksum, HTTPS endpoint software/version, licensed terminology systems and editions, validation date, checksum-bound request policy, exact arguments, and passed result/counts.
   Cross-file checks require all ten package digests, the release Validator pin, unique terminology systems, and a completion timestamp on the declared validation date.
   Pass it to `collect-release-evidence.py --lane online-terminology --terminology-evidence ...`; an invalid, incomplete, duplicate, stale, or package-drifted record is rejected before evidence output is created.
   The declared endpoint must be a credential-free HTTPS URL selected by the recorded Validator arguments; credentials and bearer tokens must never be written to evidence.
   The record must name a sibling JSON Validator report and match its SHA-256 digest; the collector validates and copies that raw report as a separately checksummed release artifact.

The current repository provides deterministic local LOINC/UCUM checks and reviewed terminology records.
Selecting the accountable licensed online environment remains an external release governance decision; no public terminology server is silently treated as authoritative.

## CI input hardening and residuals

The release workflow uses reviewed stable-major aliases for each GitHub Action; repository tests enumerate the expected aliases and reject unexpected action references.
Node.js, Python, Java, Ruby, Bundler, SUSHI, npm dependencies, Ruby dependencies, Publisher, Validator, template, and FHIR package versions are exact; lockfile or archive checksums protect the dependency bytes.
Cache fallback prefixes are prohibited in the release job, so a differently keyed cache is not accepted merely because it is warm.

Repository checkout and all dependency/build execution occur in a read-only verification job.
Only checksum-bound evidence crosses into the publication job through pinned artifact actions; that job rechecks `SHA256SUMS`, does not check out the repository, and alone receives `contents: write`.
Consequently an npm/Ruby/Publisher build input never receives the token capable of tagging or publishing the repository.

Two managed-runner inputs remain outside repository byte pinning: GitHub's rolling `ubuntu-24.04` image implementation and its preinstalled GitHub CLI.
The runner is restricted to an exact OS release family rather than `ubuntu-latest`; the CLI is used only for the final release creation after evidence is complete and does not build or validate an artifact.
The dependency offline phase is enforced by each package/tool consumer and Publisher's `-no-network`; the hosted runner itself is not claimed to be packet-filtered.
The operating-system layer is not reproducible unless the runner image is content-addressed.

## Publisher QA accounting

Offline Publisher diagnostics are reported as raw, exact-suppressed, and unsuppressed counts. `Scripts/check-guide-qa.py` requires zero unsuppressed errors and warnings, requires every exact suppression to be exercised once, and rejects unexpected broken links.
Suppression never proves terminology membership or attachment authorization.

## Immutable canonical promotion

Canonical promotion may be activated only by a separately reviewed change that switches `publication/config.json` to `immutable-releases` and supplies all of the following:

1. an accountable canonical-host owner and successful live HTTPS checks for owned canonical JSON, XML, Turtle, HTML, package, history, and package-list routes;
2. approved permanence, correction, withdrawal, key-retention, and security policies;
3. a clean signed/tagged source revision matching the release manifest and evidence checksums;
4. complete offline structural and approved online terminology evidence;
5. reviewed publication requests for all ten packages; and
6. promotion through `Scripts/publish-version.py`, which refuses an existing version directory or history entry.

The protected publication branch and environment must review the staged diff before deployment.
Versionless canonical routes may point only to the last accepted immutable release, never to a newer CI build.
No release asset or version directory may be overwritten; a correction receives a new version.

## Moving an adapter baseline

A new SDK or source artifact baseline is a versioned contract change:

1. update the adapter catalog's exact baseline and evidence inputs;
2. run `npm run inventory:refresh`, then the applicable installed-SDK verification;
3. reconcile every added, removed, or changed source token explicitly;
4. refresh terminology provenance, generated source terminology, status matrices, profiles, examples, conformance corpora, and language fixtures; and
5. rerun both release lanes before promotion.

Grove FHIR does not fetch, modify, build, or attest producer repositories.
Swift, Kotlin, and TypeScript producers consume the exact packages and shared language-neutral corpora in their own CI.
