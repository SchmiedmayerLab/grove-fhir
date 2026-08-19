<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

> **Continuous preview**
>
> This site is an unreleased build used to review the Grove FHIR contract. Its package
> identifiers, canonical URLs, and resource definitions may change before the first
> stable release. Applications should not depend on these packages yet.

The provisional `grovealliance.org` canonical URLs identify draft resources but do not
currently host this preview. Use the GitHub Pages URLs on this site for review and
downloads.

Grove FHIR Mobile Data Exchange is a draft FHIR R4 contract for observations imported
from HealthKit. Grove Swift is the first implementation used to evaluate the
definitions. No package in this preview is a released specification.

### Scope

| Material | Status in Mobile Data Exchange |
|---|---|
| HealthKit observations, source-record identity, devices, capture method, and typed source metadata | Candidate contract, evaluated against Grove Swift |
| HealthKit sample-type identifiers, metadata keys, and enumerated values | Terminology dependency published in the separate HealthKit guide |

Questionnaires, image annotation, SensorKit, Health Connect, and receiver behavior are
outside this guide.

### Use this preview

| Goal | Page |
|---|---|
| Validate a resource against the current build | [Validate Resources](consuming.html) |
| Browse generated FHIR resources | [Artifacts](artifacts.html) |
| Review HealthKit sample types, metadata keys, and values | [HealthKit Terminology](https://schmiedmayerlab.github.io/grove-fhir/platforms/) |

### Contract and guidance

Profiles, extensions, and terminology resources define the current preview. Explanatory
prose is informative. Grove product behavior is outside this guide.
