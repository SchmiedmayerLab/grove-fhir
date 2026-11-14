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

Every push to `main` runs **Build and Test**. After a successful build, **Development Preview** verifies the `pages-site` artifact and reports its expanded size before deploying it without rebuilding. Completed builds superseded on `main` are skipped, and deployments are serialized. Output above GitHub Pages' supported size produces a warning; see the [hosting considerations](#future-website-integration).

Each full guide page displays a high-contrast **Development build — not a published release** banner, the source commit, and links to its published guide and publication history. The banner uses the standard FHIR `publish-box` location; custom full HTML pages receive the same notice. Canonical publication links become available when the website is deployed.

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

The legacy Mobile root is a set of small HTML redirects to `/mobile/ci-build/`, including nested pages and browser query strings/anchors. It no longer duplicates the guide's images, scripts, or raw resources. Use the guide's preview or canonical URLs for individual JSON, XML, Turtle, and tabular files; these remain intact. The root `package.tgz`, checksum, package list, and publication manifest remain available for package consumers.

Publisher ZIP bundles (including `full-ig.zip`, definitions, examples, and spreadsheet archives) and legacy `.pack` Validator bundles are copied byte-for-byte to `.build/pages-downloads/<guide>/`. The main build uploads them as **fhir-bulk-downloads**, separately from **pages-site**. Each guide's `bulk-downloads.html` links to the exact producing run and lists filenames, sizes, and SHA-256 hashes; existing HTML download links are rewritten to this page. Actions downloads require GitHub sign-in and expire after 14 days. Local builds show the local download directory instead. Packages (`*.tgz`) and all individual resource formats stay on the website.

## Release-candidate evidence

`Scripts/build-release.sh` is the local mirror of the release-candidate build: it performs an explicit two-phase build for all ten guides from one clean checked-out revision.
The Release Publication workflow reimplements the same two phases inline rather than calling the script, and it omits the script's `npm run inventory:check` step; `Tests/test_release_pipeline.py` holds the two lanes to the same steps.
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

## Standard FHIR publication

**Release Publication** (`.github/workflows/deployment.yml`) is manually dispatched from the default branch with a bare numeric version, for example `0.9.0`. The version must match every guide and `catalog/release-manifest.json`. `dryRun` defaults to `true`; a dry run uploads a review artifact and creates no tag or GitHub Release.

After collecting the source-build evidence above, `Scripts/stage-publication.py` invokes the pinned HL7 IG Publisher's standard `-go-publish` process for each guide in dependency order. It creates standard `publication-request.json` files in temporary source copies, uses `publication/publish-setup.json` for the website layout, and renders history with a checksum-pinned revision of [HL7's history template](https://github.com/HL7/fhir-ig-history-template). The website registry is local to staging; the command does not submit anything to the upstream IG registry.

Publisher builds both the versioned publication and the current milestone copy, producing routes such as:

| Route under `https://grovealliance.org/fhir` | Purpose |
|---|---|
| `/mobile/0.9.0/` | Permanent version |
| `/mobile/` | Current published version |
| `/mobile/history.html` | Standard FHIR publication history |
| `/mobile/package-list.json` | Machine-readable publication history |
| `/mobile/0.9.0/package.tgz` | Exact versioned FHIR package |

The same layout applies to all ten guides. The archive root is the `/fhir/` subtree, leaving `/` and other routes available for the future website.

`publication/release.json` supplies the publication status, sequence, description, and previous publication. `draft` is a FHIR maturity status, independent of whether the artifact is a development preview or a published version. Before each release:

1. Update the guide and release-manifest versions and the reviewed release description.
2. For the first website publication, leave `previousPublication` as `null`. For subsequent releases, set it to `{"tag": "0.9.0", "sha256": "<SHA-256 of grove-fhir-publication-0.9.0.tar.gz>"}`. The script requires the latest published website archive and verifies its checksum before extraction; it refuses to drop history or reuse a version directory.
3. Run the default dry run and review the archive and QA. This stages publications but does not change `publication/config.json`'s preview mode or deploy the canonical host.
4. Before a real release, create and verify a signed annotated tag identifying that exact default-branch revision. GitHub must verify the tag signature; the tagger email must be `PSchmiedmayer@users.noreply.github.com`. The workflow creates no commits or tags and rechecks the tag immediately before release creation.
5. Dispatch with `dryRun: false` only when ready to publish the release. Configure required reviewers on the `fhir-release` GitHub environment before using this path; declaring its name in YAML does not configure protection.

Local staging, from a clean reviewed checkout with the documented build prerequisites and an authenticated GitHub CLI:

```sh
./Scripts/build-release.sh --output .build/release
python3 Scripts/stage-publication.py \
  --evidence .build/release \
  --output .build/publication-release \
  --date YYYY-MM-DD
(cd .build/publication-release && shasum -a 256 --check SHA256SUMS)
```

Use a fresh checkout or fresh `.build` workspace for another attempt: staging refuses existing output and `.build/publication-<version>` directories. The publication date is explicit. No tracked source file is changed by staging.

The release assets include:

- `grove-fhir-publication-<version>.tar.gz`: the complete static `/fhir/` subtree, including prior version directories, current copies, histories, feeds, and the catalog;
- unchanged ZIP and Validator bundles as individual `grove-<guide>-<version>-<filename>` assets, with separate `current-` assets when produced by the native current build; website download links use that exact release tag, and `bulk-downloads.json` records their original filenames and checksums;
- each final published package and its QA reports, plus `publication-manifest-<version>.json` binding package checksums, source revision, publication date, and tooling;
- the existing machine-contract archive/index and release manifest, plus a Mobile semantic snapshot generated from the final published package for producer CI;
- `grove-fhir-source-evidence-<version>.tar.gz`: the earlier offline source-build evidence, kept separate because native publication rebuilds the packages; and
- `SHA256SUMS` covering every release asset.

The final packages are audited again with the repository QA checks and official Validator corpora. Missing Publisher outputs fail staging even if the process returns success. Historical version directories retain their sealed bytes; their banners name the version and link to the current publication and history without claiming to remain current.

The isolated publication job uploads all assets to a new draft GitHub Release, then makes the complete release public/latest. Existing releases are never overwritten. An upload failure may leave a draft for investigation; do not automatically delete or reuse it.

### Future website integration

The ten-guide preview built with Publisher 3.0.3 occupies approximately **2.60 GB expanded**, down from **3.83 GB** before alias/download optimization (32% smaller). The [prior successful deployment](https://github.com/SchmiedmayerLab/grove-fhir/actions/runs/43200603008) used a **4.11 GB** expanded artifact; its Pages upload was approximately **909 MB compressed**. Compressed artifact size and expanded website size are different measurements.

[GitHub Pages documents a 1 GB supported site size](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). [The official upload action](https://github.com/actions/upload-pages-artifact#artifact-validation) explains that larger deployments can succeed, with an absolute rejection threshold of 10 GB for the deployment tarball. They are not guaranteed and remain subject to the deployment timeout. The preview workflow therefore reports expanded size and warns above 1 GB without imposing a new hard stop on the existing deployment.

GitHub Pages remains the deployment target. Root HTML redirects and offloaded bulk downloads reduce duplication while preserving all rendered FHIR pages, packages, and canonical resource routes. The complete guide content still exceeds 1 GB, so the size warning remains. Versioned publications offload only new/current bundles; older sealed version directories keep their original bytes and download locations. The website receiver can mount the publication archive under `/fhir/` while ordinary website pages occupy the other routes.

The optional notification job is disabled unless `GROVE_WEBSITE_APP_ID` is configured. Once `grove-website` implements the receiver, configure that repository variable and the `GROVE_WEBSITE_APP_PRIVATE_KEY` secret for a GitHub App installed on `SchmiedmayerLab/grove-website` with **Actions: write**. After a successful release, it dispatches the website's `pages.yml` workflow on `main` with `releaseTag=<version>`.

The receiver should download that exact release's archive and checksums, verify them, extract the archive under its site's `/fhir/` output directory, and deploy the complete website. It must preserve the selected publication when ordinary website changes rebuild the site. The notification performs no website deployment itself; the receiver and canonical-host checks belong to the separate website work.

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

The native publication-rendering step follows the offline source-build lane. Publisher `-go-publish` rebuilds with `-tx n/a`, but its nested builds do not forward `-no-network`; publication rendering can access the network and is not described as an offline build. Its final packages receive structural QA and corpus validation, not an online terminology attestation. Any future online evidence must bind these final package bytes.

The current repository provides deterministic local LOINC/UCUM checks and reviewed terminology records.
Selecting the accountable licensed online environment remains an external release governance decision; no public terminology server is silently treated as authoritative.

## CI input hardening and residuals

The release workflow uses stable-major GitHub Action aliases, maintained by Dependabot.
CI uses maintained runtime lines and current patches. npm and Bundler lockfiles plus archive checksums record dependency bytes. `npm run dependencies:update` refreshes the managed metadata and dependencies together; see [dependency updates](publication/dependency-compatibility.md).
Cache fallback prefixes are prohibited in the release job, so a differently keyed cache is not accepted merely because it is warm.

Repository checkout and all dependency/build execution occur in a read-only verification job.
Only checksum-bound evidence crosses into the publication job through pinned artifact actions; that job rechecks `SHA256SUMS`, does not check out the repository, and alone receives `contents: write`.
Consequently an npm/Ruby/Publisher build input never receives the token capable of tagging or publishing the repository.

Two managed-runner inputs remain outside repository byte pinning: GitHub's rolling `ubuntu-24.04` image implementation and its preinstalled GitHub CLI.
The release runner is restricted to an exact OS release family rather than `ubuntu-latest`; the CLI reads prior publication assets and signed-tag metadata, creates the release, and optionally dispatches the website workflow.
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
6. a reviewed archive from `Scripts/stage-publication.py` and a website deployment that verifies its checksums and preserves all version directories.

The earlier `Scripts/publish-version.py` remains available for its existing manually gated promotion contract; the Release Publication workflow uses native `-go-publish` instead.

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
