<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Dependency updates

Use current stable build tools and compatible R4 package releases. Standard npm and Bundler lockfiles record the resolved dependencies; the release manifest records the Publisher, Validator, and template checksums. The schema validates their shape rather than duplicating individual dependency versions.

```sh
npm run dependencies:update
npm test
GROVE_TX_OFFLINE=1 npm run pages:build:parallel
```

The update command requires Node/npm, Ruby/Bundler, Python, and an authenticated GitHub CLI. It refreshes npm and Ruby dependencies, the official Publisher and Validator releases, the selected stable FHIR base template, and the history template. It also synchronizes declared external FHIR package versions, extension aliases, diagnostic version references, the package graph, and the bootstrap package closure. All changes stay local for review. It verifies existing package checksums instead of silently accepting changed bytes under an already recorded version.

Dependabot already groups npm, Bundler, and GitHub Actions updates weekly. CI follows Node LTS, stable Python and Ruby, and the Java 25 LTS line, with current patches selected by the setup actions. Tool versions need not be changed in schema definitions or dependency-version assertions in tests.

FHIR R4 remains the guide's interoperability target. Review the generated semantic diff when changing FHIR package dependencies: tool maintenance must not silently change the published contract. The update command does not accept a new semantic baseline or publish a release.

The supported `fhir2.base.template` remains the base template. Cache preparation repairs malformed markup in its released search page and profile layouts (an unclosed image, duplicate closing tags, and a stray heading). These replacements leave corrected upstream files unchanged. The upstream archive checksum still verifies the downloaded bytes.

Offline terminology diagnostics are accounted for only when the actual generated resource and checked-in terminology evidence establish the code's validity. Required UCUM bindings also need membership in the exact R4 core ValueSet; IANA time-zone codes must exist in the local time-zone database. Changed tool version strings alone do not invalidate those checks. New or unexplained diagnostics still fail the build.

Publisher can also misidentify the LOINC system URL as its all-codes ValueSet when the CodeSystem lookup fails. The QA check accounts for that exact diagnostic only when the reported include uses `http://loinc.org` and explicitly enumerates codes that are all active in the pinned LOINC evidence. Filters, unknown codes, other systems, paths, and diagnostics still fail. These findings appear separately as `verified-terminology-errors`, including in online builds; this local evidence does not constitute an online terminology attestation.

## Reviewed Publisher 3 update

Publisher 3.0.3 and Validator 7.0.6 build with SUSHI 3.21.0, THO R4 7.5.0, and Extensions R4 5.4.0. The Mobile baseline refresh preserves examples and terminology definitions. Its differential changes are extension-version references. The new snapshot generator represents 526 minimum-cardinality and 532 Must Support constraints on their unsliced parent elements rather than repeating them on slices; all remain present on those parents. Official Validator checks accept the valid Device and Observation controls and reject missing identifier systems and values. The other snapshot changes are inherited SimpleQuantity constraints and extension-version references; the ImplementationGuide changes reflect Publisher parameter serialization.
