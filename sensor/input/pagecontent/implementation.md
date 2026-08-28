<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Build the Mobile package before Sensor and validate output with the official HL7 FHIR
Validator. The package identities are exactly `org.grovealliance.fhir.mobile#0.6.0`
and `org.grovealliance.fhir.sensor#0.6.0` for FHIR R4 `4.0.1`.

An adapter Observation declares exactly two profiles: one shared semantic profile
from Mobile or Sensor and one adapter profile. It never repeats the inherited Grove
Mobile Observation, PHD RTSA, or a core profile unless the resource independently
conforms to a distinct workflow that explicitly requires that profile.

Producer implementations consume [`catalog/sensor-catalog.json`](https://grovealliance.org/fhir/catalog/sensor-catalog.json) and
[`catalog/profile-claims.json`](https://grovealliance.org/fhir/catalog/profile-claims.json); these are normative machine-readable contracts, not
generated implementation constants.

Structured Sensor Observations and native Recording Documents use the same auditable
conversion graph shape. `grove-sensor-conversion-provenance` identifies the assembler,
targets every produced representation, and carries the complete source Identifier as a
source entity. Adapter packages narrow that source identity and require internal UUID
targets when the resources are exchanged in a Mobile collection Bundle.

## Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
