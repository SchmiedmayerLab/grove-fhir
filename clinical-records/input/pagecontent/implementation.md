<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Clinical Records package depends on the Grove Mobile package. Validate producer output against both packages with the official HL7 FHIR Validator.
Resolve the exact Mobile and Clinical Records package versions from `catalog/release-manifest.json`; both packages target FHIR R4 `4.0.1`.

A source-neutral producer declares exactly one profile on each clinical output: `grove-clinical-record-document` or `grove-clinical-record-attachment`.
An adapter output declares the shared profile and its one adapter profile, such as `healthkit-clinical-record-document`.
The record's conversion Provenance is `grove-mobile-conversion-provenance` or the adapter's conversion profile, and it targets every clinical output of the record.

Producer implementations consume [`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json) and [`catalog/profile-claims.json`](https://grovealliance.org/fhir/catalog/profile-claims.json) as normative machine-readable contracts.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
