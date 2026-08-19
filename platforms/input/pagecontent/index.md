<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

> **Continuous preview**
>
> This package is an unreleased terminology dependency. Its identifiers and contents may
> change before the first stable Grove FHIR release.

The provisional `grovealliance.org` canonical URLs identify draft resources but do not
currently host this preview. Use the GitHub Pages URLs on this site for review and
downloads.

The Grove HealthKit Terminology package contains HealthKit sample-type identifiers,
metadata keys, and enumerated values referenced by Mobile Data Exchange resources. The
code systems support FHIR validation without redefining platform behavior or assigning
clinical meaning.

### Current coverage

| Material | Status |
|---|---|
| HealthKit sample types, metadata keys, and value enumerations | Candidate terminology used by the current Grove Swift mappings |

Enumerated value systems are generated from Grove Swift mappings, and metadata-key
coverage is checked against the values Grove Swift writes. Apple documentation remains
authoritative for the meaning and availability of each platform value.

See [Artifacts](artifacts.html) for the generated definitions and the
[Mobile Data Exchange preview](https://schmiedmayerlab.github.io/grove-fhir/) for the
profiles that reference them.
