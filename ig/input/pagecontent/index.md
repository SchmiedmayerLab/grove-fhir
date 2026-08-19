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

This preview contains candidates for a reusable FHIR R4 exchange contract. Grove Swift
is the first reference implementation evaluated against the definitions. No package in
this preview is a released specification.

### Scope

The proposed contract has three domains:

| Domain | Purpose |
|---|---|
| Mobile Data Exchange | Represent HealthKit observations, source-record identity, recording hardware, gateway software, capture method, and typed source metadata |
| Questionnaire Exchange | Exchange FHIR Questionnaire and QuestionnaireResponse resources independently of a particular renderer |
| Platform Terminology | Preserve source-platform identifiers used by exchanged resources without assigning clinical meaning |

The current `org.grovealliance.fhir.core` package predates those boundaries and contains
additional prototype material. Its generated artifact list is a record of the current
build, not an endorsed stable contract.

### Current boundaries

| Current material | Review status |
|---|---|
| HealthKit observation exchange | Candidate Mobile contract |
| Questionnaire and QuestionnaireResponse exchange | Candidate Questionnaire contract; annotation-specific constraints are not included in that scope |
| HealthKit identifiers used by the Swift mapping | Candidate Platform Terminology |
| SensorKit observations and raw sensor batches | Experimental |
| Health Connect definitions | No Grove Swift implementation evidence |
| Image annotation | Grove application feature, outside the proposed FHIR contract |
| Receiver CapabilityStatement | No corresponding Grove receiver implementation |

### Use this preview

| Goal | Page |
|---|---|
| Validate a resource against the current build | [Validate Preview Resources](consuming.html) |
| Understand the scope and release status | [Preview Status](publication-status.html) |
| Browse generated FHIR resources | [Artifacts](artifacts.html) |
| Review source-platform identifiers | [Platform Terminology](https://schmiedmayerlab.github.io/grove-fhir/platforms/) |

### Contract and guidance

Only profiles, extensions, terminology resources, and invariants in a future reviewed,
versioned package can define conformance requirements. Examples and explanatory pages
are informative. Grove product capabilities and roadmap work are outside this guide.

### Dependencies

{% include dependency-table.xhtml %}

{% include globals-table.xhtml %}

### Cross-Version Analysis

{% include cross-version-analysis.xhtml %}

### Intellectual Property Statements

{% include ip-statements.xhtml %}
