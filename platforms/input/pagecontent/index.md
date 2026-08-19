<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

> **Continuous preview**
>
> This package is an unreleased terminology dependency. Its identifiers and contents may
> change before the first stable Grove FHIR release.

The Grove Platform Terminology package carries source-platform identifiers referenced by
Grove FHIR resources. These code systems support validation of codes used by the reviewed
Grove mapping. They do not define platform behavior or assign clinical meaning.

### Current coverage

| Source | Status |
|---|---|
| HealthKit sample types and metadata keys | Candidate; emitted by Grove Swift |
| HealthKit value enumerations | Candidate; generated from the current Swift mappings |
| Health Connect record types and metadata | Evidence pending; not implemented by Grove Swift |
| SensorKit sensor identifiers | Experimental; excluded from the first stable Mobile contract |

The current HealthKit definitions are generated from mappings in Grove Swift and checked
for drift in CI.

Vendor documentation remains authoritative for the meaning and availability of each
platform value. Before a stable release, every retained vocabulary will record its source
SDK version, extraction method, provenance, and redistribution basis.

See [Artifacts](artifacts.html) for the generated definitions,
[Preview Status](publication-status.html) for their release status, and the
[main Grove FHIR preview](https://schmiedmayerlab.github.io/grove-fhir/) for the proposed
exchange contract.

### Dependencies

{% include dependency-table.xhtml %}

{% include globals-table.xhtml %}

{% include cross-version-analysis.xhtml %}

{% include ip-statements.xhtml %}
